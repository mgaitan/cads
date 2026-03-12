#!/usr/bin/env python3
from __future__ import annotations
import csv, json, os, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'site'
ASSETS = SITE / 'assets'
IMG = ASSETS / 'screenshots'
CUT = ASSETS / 'cutting'
DATA = SITE / 'data'

MODULE_META = {
    'ENS': {'title': 'Ensamble cocina principal', 'kind': 'ensamble'},
    'ENSI': {'title': 'Ensamble isla', 'kind': 'ensamble'},
    'H': {'title': 'Columna horno + micro', 'kind': 'modulo'},
    'AA': {'title': 'Alacena izquierda', 'kind': 'modulo'},
    'AB': {'title': 'Alacena derecha + AC', 'kind': 'modulo'},
    'L': {'title': 'Armario lavarropas', 'kind': 'modulo'},
    'BA': {'title': 'Bajo mesada izquierdo', 'kind': 'modulo'},
    'BB': {'title': 'Bajo mesada derecho', 'kind': 'modulo'},
    'F': {'title': 'Heladera + modular', 'kind': 'modulo'},
    'I': {'title': 'Bajo mesada isla', 'kind': 'modulo'},
    'M': {'title': 'Mesada', 'kind': 'modulo'},
}

for p in [SITE, ASSETS, IMG, CUT, DATA]:
    p.mkdir(parents=True, exist_ok=True)

for shot in (ROOT/'screenshots').glob('*.png'):
    shutil.copy2(shot, IMG/shot.name)
for asset in (ROOT/'outputs'/'cutting').glob('*'):
    if asset.suffix.lower() in {'.svg', '.csv'}:
        shutil.copy2(asset, CUT/asset.name)
for fname in ['COCINA_manual.pdf', 'COCINA_manual.html']:
    src = ROOT/'manuals'/'out'/fname
    if src.exists():
        shutil.copy2(src, ASSETS/fname)

modules = []
for code, meta in MODULE_META.items():
    views = {}
    for v in ['iso','front','left','right','rear','top','bottom']:
        f = IMG / f'{code}_{v}.png'
        if f.exists():
            views[v] = f'assets/screenshots/{f.name}'
    modules.append({'code': code, **meta, 'views': views})
modules.sort(key=lambda x: (0 if x['kind']=='ensamble' else 1, x['code']))

bom_rows = []
for path in sorted((ROOT/'bom').glob('*_bom.csv')):
    module = path.stem.replace('_bom','')
    with path.open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            if r.get('codigo') == 'TOTAL':
                continue
            r['module'] = module
            bom_rows.append(r)

summary = []
sp = ROOT/'outputs'/'cutting'/'summary.csv'
if sp.exists():
    with sp.open(encoding='utf-8', newline='') as f:
        summary = list(csv.DictReader(f))
layouts = []
for svg in sorted(CUT.glob('*_layout.svg')):
    group = svg.name.replace('_layout.svg','')
    layouts.append({'group': group, 'svg': f'assets/cutting/{svg.name}', 'placements_csv': f'assets/cutting/{group}_placements.csv'})

(DATA/'site-data.json').write_text(json.dumps({'modules': modules, 'bomRows': bom_rows, 'cutSummary': summary, 'layouts': layouts}, ensure_ascii=False), encoding='utf-8')

(SITE/'.nojekyll').write_text('')
(SITE/'styles.css').write_text('''
:root{--bg:#f2f0ea;--paper:#fffdf8;--ink:#1d1d1b;--muted:#6b685f;--line:#d6d1c5;--accent:#7f5a3a;--accent2:#405d49}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(180deg,#f5f3ed 0,#ece7db 100%);color:var(--ink)}
header{padding:24px 28px;border-bottom:1px solid var(--line);background:rgba(255,253,248,.92);position:sticky;top:0;backdrop-filter:blur(8px);z-index:10}
h1{margin:0 0 8px;font-size:28px}header p{margin:0;color:var(--muted)}nav{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.tabbtn{border:1px solid var(--line);background:#fff;padding:10px 14px;cursor:pointer}.tabbtn.active{background:var(--ink);color:#fff;border-color:var(--ink)}
main{padding:24px;max-width:1440px;margin:0 auto}.tab{display:none}.tab.active{display:block}.grid{display:grid;grid-template-columns:280px 1fr;gap:20px}.side{background:var(--paper);border:1px solid var(--line);padding:14px;align-self:start;position:sticky;top:120px}.side button{width:100%;text-align:left;padding:10px 12px;margin:0 0 8px;border:1px solid var(--line);background:#fff;cursor:pointer}.side button.active{background:#f3ebe2;border-color:var(--accent)}
.panel{background:var(--paper);border:1px solid var(--line);padding:18px}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}.shot{background:#fff;border:1px solid var(--line);padding:10px}.shot img{width:100%;display:block}.meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}.chip{padding:5px 9px;background:#efe8dd;border:1px solid var(--line);font-size:12px}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px}.toolbar input,.toolbar select{padding:10px 12px;border:1px solid var(--line);background:#fff}.tablewrap{overflow:auto;border:1px solid var(--line);background:#fff}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}th{position:sticky;top:0;background:#f8f4ec}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-bottom:18px}.card{background:var(--paper);border:1px solid var(--line);padding:14px}.layout{background:var(--paper);border:1px solid var(--line);padding:18px;margin-bottom:18px}.layout img{width:100%;display:block;border:1px solid var(--line);background:#fff}.small{font-size:12px;color:var(--muted)}a{color:var(--accent2)}
@media (max-width:980px){.grid{grid-template-columns:1fr}.side{position:static}}
''', encoding='utf-8')
(SITE/'app.js').write_text('''
const $ = (s, el=document) => el.querySelector(s);
const $$ = (s, el=document) => [...el.querySelectorAll(s)];
let DATA;
async function load(){ DATA = await fetch('data/site-data.json').then(r=>r.json()); initTabs(); renderViews(); renderCuts(); renderLayouts(); }
function initTabs(){ $$('.tabbtn').forEach(b=>b.onclick=()=>{ $$('.tabbtn').forEach(x=>x.classList.remove('active')); $$('.tab').forEach(x=>x.classList.remove('active')); b.classList.add('active'); $('#'+b.dataset.tab).classList.add('active'); }); }
function renderViews(){ const side=$('#view-list'), detail=$('#view-detail'); let current=DATA.modules[0]?.code; side.innerHTML=''; DATA.modules.forEach(m=>{ const b=document.createElement('button'); b.textContent=`${m.code} · ${m.title}`; if(m.code===current)b.classList.add('active'); b.onclick=()=>{current=m.code; renderCurrent();}; side.appendChild(b); }); function renderCurrent(){ $$('#view-list button').forEach(b=>b.classList.toggle('active', b.textContent.startsWith(current+' ' )||b.textContent.startsWith(current+'·')||b.textContent.startsWith(current+' ·'))); const m=DATA.modules.find(x=>x.code===current); detail.innerHTML=`<div class="meta"><span class="chip">${m.kind}</span><span class="chip">${m.code}</span></div><h2>${m.title}</h2><div class="gallery">${Object.entries(m.views).map(([k,v])=>`<div class="shot"><div class="small">${k}</div><a href="${v}" target="_blank"><img src="${v}" alt="${m.code} ${k}"></a></div>`).join('')}</div>`; }
 renderCurrent(); }
function renderCuts(){ const rows=DATA.bomRows; const tbody=$('#cuts-body'); const q=$('#filter-q'), mod=$('#filter-module'), cat=$('#filter-category');
 const modules=['Todos',...new Set(rows.map(r=>r.module))]; const cats=['Todas',...new Set(rows.map(r=>r.categoria))]; mod.innerHTML=modules.map(v=>`<option>${v}</option>`).join(''); cat.innerHTML=cats.map(v=>`<option>${v}</option>`).join(''); const totals=$('#cut-cards'); const byModule={}; rows.forEach(r=>{byModule[r.module]=(byModule[r.module]||0)+Number(r.cantidad||0)}); totals.innerHTML=Object.entries(byModule).sort().map(([k,v])=>`<div class="card"><strong>${k}</strong><div>${v} piezas</div></div>`).join('');
 function draw(){ const term=q.value.toLowerCase().trim(); const mv=mod.value, cv=cat.value; const filtered=rows.filter(r=>(!term||Object.values(r).join(' ').toLowerCase().includes(term))&&(mv==='Todos'||r.module===mv)&&(cv==='Todas'||r.categoria===cv)); tbody.innerHTML=filtered.map(r=>`<tr><td>${r.module}</td><td>${r.codigo}</td><td>${r.categoria}</td><td>${r.pieza}</td><td>${r.cantidad}</td><td>${r.largo_mm}</td><td>${r.ancho_mm}</td><td>${r.espesor_mm}</td><td>${r.cantos||''}</td></tr>`).join(''); $('#cuts-count').textContent=`${filtered.length} filas`; }
 [q,mod,cat].forEach(el=>el.oninput=draw); draw(); }
function renderLayouts(){ $('#layout-summary').innerHTML=DATA.cutSummary.map(r=>`<div class="card"><strong>${r.group}</strong><div>${r.boards_used} placas</div><div>${r.utilization_pct}% uso</div><div class="small">${r.board_usable_w_mm} x ${r.board_usable_h_mm} util</div></div>`).join(''); $('#layouts').innerHTML=DATA.layouts.map(l=>`<section class="layout"><h3>${l.group}</h3><p class="small"><a href="${l.placements_csv}" target="_blank">placements.csv</a></p><img src="${l.svg}" alt="${l.group}"></section>`).join(''); }
load();
''', encoding='utf-8')
(SITE/'index.html').write_text('''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CADs Cocina</title><link rel="stylesheet" href="styles.css"></head><body><header><h1>CADs Cocina</h1><p>Modelos, vistas, lista de cortes y layouts de placas.</p><nav><button class="tabbtn active" data-tab="views">Vistas</button><button class="tabbtn" data-tab="cuts">Lista de cortes</button><button class="tabbtn" data-tab="layouts-tab">Placas</button><a class="tabbtn" href="assets/COCINA_manual.pdf" target="_blank">Manual PDF</a></nav></header><main><section id="views" class="tab active"><div class="grid"><aside id="view-list" class="side"></aside><section id="view-detail" class="panel"></section></div></section><section id="cuts" class="tab"><div id="cut-cards" class="cards"></div><div class="toolbar"><input id="filter-q" placeholder="Buscar pieza, modulo o canto"><select id="filter-module"></select><select id="filter-category"></select><span id="cuts-count" class="small"></span></div><div class="tablewrap"><table><thead><tr><th>Modulo</th><th>Codigo</th><th>Categoria</th><th>Pieza</th><th>Cant</th><th>Largo</th><th>Ancho</th><th>Espesor</th><th>Cantos</th></tr></thead><tbody id="cuts-body"></tbody></table></div></section><section id="layouts-tab" class="tab"><div id="layout-summary" class="cards"></div><div id="layouts"></div></section></main><script src="app.js"></script></body></html>''', encoding='utf-8')

#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
ASSETS = SITE / "assets"
IMG = ASSETS / "screenshots"
CUT = ASSETS / "cutting"
MODELS = ASSETS / "models"
DATA = SITE / "data"

MODULE_META = {
    "ENS": {"title": "Ensamble cocina principal", "kind": "ensamble"},
    "ENSI": {"title": "Ensamble isla", "kind": "ensamble"},
    "H": {"title": "Columna horno + micro", "kind": "modulo"},
    "AA": {"title": "Alacena izquierda", "kind": "modulo"},
    "AB": {"title": "Alacena derecha + AC", "kind": "modulo"},
    "L": {"title": "Armario lavarropas", "kind": "modulo"},
    "BA": {"title": "Bajo mesada izquierdo", "kind": "modulo"},
    "BB": {"title": "Bajo mesada derecho", "kind": "modulo"},
    "F": {"title": "Heladera + modular", "kind": "modulo"},
    "I": {"title": "Bajo mesada isla", "kind": "modulo"},
    "M": {"title": "Mesada", "kind": "modulo"},
}

for p in [SITE, ASSETS, IMG, CUT, MODELS, DATA]:
    p.mkdir(parents=True, exist_ok=True)

for shot in (ROOT / "screenshots").glob("*.png"):
    shutil.copy2(shot, IMG / shot.name)
for asset in (ROOT / "outputs" / "cutting").glob("*"):
    if asset.suffix.lower() in {".svg", ".csv"}:
        shutil.copy2(asset, CUT / asset.name)
for mesh in (ROOT / "outputs" / "web_models").glob("*.stl"):
    shutil.copy2(mesh, MODELS / mesh.name)
for fname in ["COCINA_manual.pdf", "COCINA_manual.html"]:
    src = ROOT / "manuals" / "out" / fname
    if src.exists():
        shutil.copy2(src, ASSETS / fname)

modules = []
for code, meta in MODULE_META.items():
    views = {}
    for v in ["iso", "front", "left", "right", "rear", "top", "bottom"]:
        f = IMG / f"{code}_{v}.png"
        if f.exists():
            views[v] = f"assets/screenshots/{f.name}"
    model_path = MODELS / f"{code}.stl"
    modules.append(
        {
            "code": code,
            **meta,
            "views": views,
            "model3d": f"assets/models/{code}.stl" if model_path.exists() else None,
        }
    )
modules.sort(key=lambda x: (0 if x["kind"] == "ensamble" else 1, x["code"]))

bom_rows = []
for path in sorted((ROOT / "bom").glob("*_bom.csv")):
    module = path.stem.replace("_bom", "")
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("codigo") == "TOTAL":
                continue
            r["module"] = module
            bom_rows.append(r)

summary = []
sp = ROOT / "outputs" / "cutting" / "summary.csv"
if sp.exists():
    with sp.open(encoding="utf-8", newline="") as f:
        summary = list(csv.DictReader(f))
layouts = []
for svg in sorted(CUT.glob("*_layout.svg")):
    group = svg.name.replace("_layout.svg", "")
    layouts.append(
        {
            "group": group,
            "svg": f"assets/cutting/{svg.name}",
            "placements_csv": f"assets/cutting/{group}_placements.csv",
        }
    )

(DATA / "site-data.json").write_text(
    json.dumps(
        {
            "modules": modules,
            "bomRows": bom_rows,
            "cutSummary": summary,
            "layouts": layouts,
        },
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

(SITE / ".nojekyll").write_text("")
(SITE / "styles.css").write_text(
    """
:root{--bg:#f2f0ea;--paper:#fffdf8;--ink:#1d1d1b;--muted:#6b685f;--line:#d6d1c5;--accent:#7f5a3a;--accent2:#405d49}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(180deg,#f5f3ed 0,#ece7db 100%);color:var(--ink)}
header{padding:24px 28px;border-bottom:1px solid var(--line);background:rgba(255,253,248,.92);position:sticky;top:0;backdrop-filter:blur(8px);z-index:10}
h1{margin:0 0 8px;font-size:28px}header p{margin:0;color:var(--muted)}nav{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.tabbtn{border:1px solid var(--line);background:#fff;padding:10px 14px;cursor:pointer}.tabbtn.active{background:var(--ink);color:#fff;border-color:var(--ink)}
main{padding:24px;max-width:1440px;margin:0 auto}.tab{display:none}.tab.active{display:block}.grid{display:grid;grid-template-columns:280px 1fr;gap:20px}.side{background:var(--paper);border:1px solid var(--line);padding:14px;align-self:start;position:sticky;top:120px}.side button{width:100%;text-align:left;padding:10px 12px;margin:0 0 8px;border:1px solid var(--line);background:#fff;cursor:pointer}.side button.active{background:#f3ebe2;border-color:var(--accent)}
.panel{background:var(--paper);border:1px solid var(--line);padding:18px}.viewer{background:#fbfaf6;border:1px solid var(--line);padding:12px;margin-bottom:16px}.viewer-head{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:10px}.viewer-actions{display:flex;gap:8px;flex-wrap:wrap}.viewer-actions button{padding:8px 10px;border:1px solid var(--line);background:#fff;cursor:pointer}.viewer canvas{width:100%;height:480px;display:block;background:linear-gradient(180deg,#fcfbf7 0,#f0ece3 100%);border:1px solid var(--line)}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}.shot{background:#fff;border:1px solid var(--line);padding:10px}.shot img{width:100%;display:block}.meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}.chip{padding:5px 9px;background:#efe8dd;border:1px solid var(--line);font-size:12px}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px}.toolbar input,.toolbar select{padding:10px 12px;border:1px solid var(--line);background:#fff}.tablewrap{overflow:auto;border:1px solid var(--line);background:#fff}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}th{position:sticky;top:0;background:#f8f4ec}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-bottom:18px}.card{background:var(--paper);border:1px solid var(--line);padding:14px}.layout{background:var(--paper);border:1px solid var(--line);padding:18px;margin-bottom:18px}.layout img{width:100%;display:block;border:1px solid var(--line);background:#fff}.small{font-size:12px;color:var(--muted)}a{color:var(--accent2)}
@media (max-width:980px){.grid{grid-template-columns:1fr}.side{position:static}}
""",
    encoding="utf-8",
)
(SITE / "app.js").write_text(
    """
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const $ = (s, el=document) => el.querySelector(s);
const $$ = (s, el=document) => [...el.querySelectorAll(s)];
let DATA;
let teardownViewer = null;
async function load(){ DATA = await fetch('data/site-data.json').then(r=>r.json()); initTabs(); renderViews(); renderCuts(); renderLayouts(); }
function initTabs(){ $$('.tabbtn').forEach(b=>b.onclick=()=>{ $$('.tabbtn').forEach(x=>x.classList.remove('active')); $$('.tab').forEach(x=>x.classList.remove('active')); b.classList.add('active'); $('#'+b.dataset.tab).classList.add('active'); }); }
function renderViews(){ const side=$('#view-list'), detail=$('#view-detail'); let current=DATA.modules[0]?.code; side.innerHTML=''; DATA.modules.forEach(m=>{ const b=document.createElement('button'); b.textContent=`${m.code} · ${m.title}`; if(m.code===current)b.classList.add('active'); b.onclick=()=>{current=m.code; renderCurrent();}; side.appendChild(b); }); function renderCurrent(){ $$('#view-list button').forEach(b=>b.classList.toggle('active', b.textContent.startsWith(current+' ' )||b.textContent.startsWith(current+'·')||b.textContent.startsWith(current+' ·'))); const m=DATA.modules.find(x=>x.code===current); const viewer = m.model3d ? `<section class="viewer"><div class="viewer-head"><strong>Modelo 3D</strong><div class="viewer-actions"><button id="viewer-reset" type="button">Reset</button><button id="viewer-wire" type="button">Wireframe</button><a href="${m.model3d}" target="_blank">STL</a></div></div><canvas id="model-canvas"></canvas><div class="small">Orbitar: arrastrar. Zoom: rueda. Pan: botón derecho.</div></section>` : ''; detail.innerHTML=`<div class="meta"><span class="chip">${m.kind}</span><span class="chip">${m.code}</span></div><h2>${m.title}</h2>${viewer}<div class="gallery">${Object.entries(m.views).map(([k,v])=>`<div class="shot"><div class="small">${k}</div><a href="${v}" target="_blank"><img src="${v}" alt="${m.code} ${k}"></a></div>`).join('')}</div>`; if(teardownViewer){ teardownViewer(); teardownViewer = null; } if(m.model3d){ teardownViewer = setupViewer('#model-canvas', m.model3d); } }
 renderCurrent(); }
function renderCuts(){ const rows=DATA.bomRows; const tbody=$('#cuts-body'); const q=$('#filter-q'), mod=$('#filter-module'), cat=$('#filter-category');
 const modules=['Todos',...new Set(rows.map(r=>r.module))]; const cats=['Todas',...new Set(rows.map(r=>r.categoria))]; mod.innerHTML=modules.map(v=>`<option>${v}</option>`).join(''); cat.innerHTML=cats.map(v=>`<option>${v}</option>`).join(''); const totals=$('#cut-cards'); const byModule={}; rows.forEach(r=>{byModule[r.module]=(byModule[r.module]||0)+Number(r.cantidad||0)}); totals.innerHTML=Object.entries(byModule).sort().map(([k,v])=>`<div class="card"><strong>${k}</strong><div>${v} piezas</div></div>`).join('');
 function draw(){ const term=q.value.toLowerCase().trim(); const mv=mod.value, cv=cat.value; const filtered=rows.filter(r=>(!term||Object.values(r).join(' ').toLowerCase().includes(term))&&(mv==='Todos'||r.module===mv)&&(cv==='Todas'||r.categoria===cv)); tbody.innerHTML=filtered.map(r=>`<tr><td>${r.module}</td><td>${r.codigo}</td><td>${r.categoria}</td><td>${r.pieza}</td><td>${r.cantidad}</td><td>${r.largo_mm}</td><td>${r.ancho_mm}</td><td>${r.espesor_mm}</td><td>${r.cantos||''}</td></tr>`).join(''); $('#cuts-count').textContent=`${filtered.length} filas`; }
 [q,mod,cat].forEach(el=>el.oninput=draw); draw(); }
function renderLayouts(){ $('#layout-summary').innerHTML=DATA.cutSummary.map(r=>`<div class="card"><strong>${r.group}</strong><div>${r.boards_used} placas</div><div>${r.utilization_pct}% uso</div><div class="small">${r.board_usable_w_mm} x ${r.board_usable_h_mm} util</div></div>`).join(''); $('#layouts').innerHTML=DATA.layouts.map(l=>`<section class="layout"><h3>${l.group}</h3><p class="small"><a href="${l.placements_csv}" target="_blank">placements.csv</a></p><img src="${l.svg}" alt="${l.group}"></section>`).join(''); }
function setupViewer(selector, url){
 const canvas = $(selector);
 const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
 const scene = new THREE.Scene();
 scene.background = new THREE.Color(0xf7f4ed);
 const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 10000);
 camera.up.set(0, 0, 1);
 const controls = new OrbitControls(camera, canvas);
 controls.enableDamping = true;
 controls.screenSpacePanning = false;
 controls.target.set(0, 0, 0);
 scene.add(new THREE.HemisphereLight(0xffffff, 0xb7ae9d, 1.7));
 const dir1 = new THREE.DirectionalLight(0xffffff, 1.2); dir1.position.set(1, 2, 3); scene.add(dir1);
 const dir2 = new THREE.DirectionalLight(0xffffff, 0.7); dir2.position.set(-2, 1, -1); scene.add(dir2);
 const grid = new THREE.GridHelper(4000, 40, 0xcabda9, 0xe3ddd1);
 grid.rotation.x = Math.PI / 2;
 scene.add(grid);
 let mesh = null;
 let wire = false;
 let fitState = null;
 const material = new THREE.MeshStandardMaterial({color:0xd7d3ca, metalness:0.0, roughness:0.92});
 const loader = new STLLoader();
 loader.load(url, geometry => {
   geometry.computeVertexNormals();
   geometry.computeBoundingBox();
   const box0 = geometry.boundingBox;
   const cx = (box0.min.x + box0.max.x) / 2;
   const cy = (box0.min.y + box0.max.y) / 2;
   geometry.translate(-cx, -cy, -box0.min.z);
   mesh = new THREE.Mesh(geometry, material);
   scene.add(mesh);
   const box = new THREE.Box3().setFromObject(mesh);
   const size = box.getSize(new THREE.Vector3());
   const center = box.getCenter(new THREE.Vector3());
   const maxDim = Math.max(size.x, size.y, size.z) || 1;
   fitState = {
     position: new THREE.Vector3(center.x + maxDim * 1.35, center.y - maxDim * 1.45, center.z + maxDim * 0.95),
     target: center.clone(),
   };
   camera.position.copy(fitState.position);
   camera.near = maxDim / 100;
   camera.far = maxDim * 20;
   camera.updateProjectionMatrix();
   controls.target.copy(fitState.target);
   controls.update();
 }, undefined, err => {
   console.error('No se pudo cargar STL', err);
 });
 function resize(){
   const rect = canvas.getBoundingClientRect();
   renderer.setSize(rect.width, rect.height, false);
   camera.aspect = rect.width / Math.max(rect.height, 1);
   camera.updateProjectionMatrix();
 }
 resize();
 window.addEventListener('resize', resize);
 let raf = 0;
 function tick(){
   controls.update();
   renderer.render(scene, camera);
   raf = requestAnimationFrame(tick);
 }
 tick();
 const resetBtn = $('#viewer-reset');
 const wireBtn = $('#viewer-wire');
 if(resetBtn) resetBtn.onclick = () => {
   if(!mesh || !fitState) return;
   camera.position.copy(fitState.position);
   controls.target.copy(fitState.target);
   controls.update();
 };
 if(wireBtn) wireBtn.onclick = () => {
   wire = !wire;
   material.wireframe = wire;
 };
 return () => {
   cancelAnimationFrame(raf);
   window.removeEventListener('resize', resize);
   controls.dispose();
   renderer.dispose();
   if(mesh){
     mesh.geometry.dispose();
   }
 };
}
load();
""",
    encoding="utf-8",
)
(SITE / "index.html").write_text(
    """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CADs Cocina</title><link rel="stylesheet" href="styles.css"><script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.165.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.165.0/examples/jsm/"}}</script></head><body><header><h1>CADs Cocina</h1><p>Modelos, vistas, lista de cortes y layouts de placas.</p><nav><button class="tabbtn active" data-tab="views">Vistas</button><button class="tabbtn" data-tab="cuts">Lista de cortes</button><button class="tabbtn" data-tab="layouts-tab">Placas</button><a class="tabbtn" href="assets/COCINA_manual.pdf" target="_blank">Manual PDF</a></nav></header><main><section id="views" class="tab active"><div class="grid"><aside id="view-list" class="side"></aside><section id="view-detail" class="panel"></section></div></section><section id="cuts" class="tab"><div id="cut-cards" class="cards"></div><div class="toolbar"><input id="filter-q" placeholder="Buscar pieza, modulo o canto"><select id="filter-module"></select><select id="filter-category"></select><span id="cuts-count" class="small"></span></div><div class="tablewrap"><table><thead><tr><th>Modulo</th><th>Codigo</th><th>Categoria</th><th>Pieza</th><th>Cant</th><th>Largo</th><th>Ancho</th><th>Espesor</th><th>Cantos</th></tr></thead><tbody id="cuts-body"></tbody></table></div></section><section id="layouts-tab" class="tab"><div id="layout-summary" class="cards"></div><div id="layouts"></div></section></main><script type="module" src="app.js"></script></body></html>""",
    encoding="utf-8",
)

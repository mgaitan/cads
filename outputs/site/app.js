
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
function renderLayouts(){ $('#layout-summary').innerHTML=DATA.cutSummary.map(r=>`<div class="card"><strong>${r.group}</strong><div>${r.boards_used} placas</div><div>${r.utilization_pct}% uso</div><div class="small">${r.board_usable_w_mm} x ${r.board_usable_h_mm} util</div></div>`).join(''); $('#layouts').innerHTML=DATA.layouts.map(l=>`<section class="layout"><h3>${l.group}</h3><p class="small"><a href="${l.placements_csv}" target="_blank">placements.csv</a></p>${l.svgs.map((s,i)=>`<figure><img src="${s}" alt="${l.group} hoja ${i+1}"><figcaption class="small">Hoja ${i+1}</figcaption></figure>`).join('')}</section>`).join(''); }
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

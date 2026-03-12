#!/usr/bin/env python3
"""Genera manual unico de cocina (MD/HTML/PDF)."""
from __future__ import annotations

import csv
import os
import shutil
import subprocess
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'manuals' / 'out'

ENSEMBLES = [
    ('ENS', 'Ensamble cocina principal'),
    ('ENSI', 'Ensamble isla'),
]
MODULES = [
    ('H', 'Columna horno + micro', 'Melamina blanca'),
    ('AA', 'Alacena izquierda', 'Melamina blanca'),
    ('AB', 'Alacena derecha + cajon AC', 'AB blanco / AC simil paraiso'),
    ('L', 'Frente armario lavarropas', 'Melamina blanca'),
    ('BA', 'Bajo mesada izquierdo', 'Melamina blanca'),
    ('BB', 'Bajo mesada derecho', 'Melamina blanca'),
    ('F', 'Mueble heladera + modular', 'Paraiso + blanco'),
    ('I', 'Bajo mesada isla', 'Melamina blanca'),
    ('M', 'Mesada principal', 'Piedra gris mara'),
]


def relpath(from_file: Path, target: Path) -> str:
    return os.path.relpath(target, from_file.parent)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def load_text(path: Path) -> str:
    if not path.exists():
        return '_Sin notas cargadas._'
    return path.read_text(encoding='utf-8').strip()


def img(md_path: Path, rel_target: Path, caption: str, width: str = '48%') -> str:
    if not rel_target.exists():
        return ''
    src = relpath(md_path, rel_target)
    return f'<figure style="display:inline-block; width:{width}; margin:0 1% 10px 0;"><img src="{src}" style="width:100%; border:1px solid #ccc;" /><figcaption style="font-size:8.5pt">{caption}</figcaption></figure>'


def table(headers: list[str], rows: list[list[str]]) -> str:
    sep = ['---'] * len(headers)
    out = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(sep) + ' |']
    for r in rows:
        out.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    return '\n'.join(out)


def bom_paths() -> list[Path]:
    return sorted((ROOT / 'bom').glob('*_bom.csv'))


def module_bom_rows(code: str) -> list[dict[str, str]]:
    path = ROOT / 'bom' / f'{code}_bom.csv'
    if not path.exists():
        return []
    rows = load_csv(path)
    return [r for r in rows if r.get('codigo') != 'TOTAL']


def consolidated_rows() -> list[list[str]]:
    acc: dict[tuple[str, str, str, str, str, str], dict[str, object]] = {}
    for path in bom_paths():
        code = path.stem.replace('_bom', '')
        for r in module_bom_rows(code):
            key = (
                r.get('categoria', ''),
                r.get('pieza', ''),
                r.get('largo_mm', ''),
                r.get('ancho_mm', ''),
                r.get('espesor_mm', ''),
                r.get('cantos', ''),
            )
            if key not in acc:
                acc[key] = {'cant': 0, 'mods': set(), 'ml': 0.0, 'bis': 0}
            acc[key]['cant'] += int(float(r.get('cantidad', '0') or 0))
            acc[key]['mods'].add(code)
            acc[key]['ml'] += float(r.get('ml_gola', '0') or 0)
            acc[key]['bis'] += int(float(r.get('bisagras_cazoleta', '0') or 0))
    rows = []
    for (cat, pieza, l, a, e, cantos), v in sorted(acc.items(), key=lambda x: (x[0][0], x[0][1])):
        rows.append([cat, pieza, v['cant'], l, a, e, cantos, ','.join(sorted(v['mods'])), f"{v['ml']:.3f}" if v['ml'] else '', v['bis'] if v['bis'] else ''])
    return rows


def ensemble_section(md_path: Path, code: str, title: str) -> str:
    shots = ROOT / 'screenshots'
    views = ''.join([
        img(md_path, shots / f'{code}_iso.png', f'{code} Iso', '48%'),
        img(md_path, shots / f'{code}_front.png', f'{code} Frente', '48%'),
        img(md_path, shots / f'{code}_left.png', f'{code} Lateral', '48%'),
        img(md_path, shots / f'{code}_right.png', f'{code} Lateral opuesto', '48%'),
        img(md_path, shots / f'{code}_rear.png', f'{code} Posterior', '48%'),
        img(md_path, shots / f'{code}_top.png', f'{code} Superior', '48%'),
    ])
    return f"""
## {code} - {title}
{views}
"""


def module_section(md_path: Path, code: str, name: str, finish: str) -> str:
    headers = ['Codigo', 'Categoria', 'Pieza', 'Cant', 'Largo', 'Ancho', 'Espesor', 'Cantos', 'ML gola', 'Bisagras']
    rows = []
    for r in module_bom_rows(code):
        rows.append([
            r.get('codigo', ''), r.get('categoria', ''), r.get('pieza', ''), r.get('cantidad', ''),
            r.get('largo_mm', ''), r.get('ancho_mm', ''), r.get('espesor_mm', ''), r.get('cantos', ''),
            r.get('ml_gola', ''), r.get('bisagras_cazoleta', ''),
        ])
    instr = load_text(ROOT / 'docs' / 'instrucciones' / f'{code}_instrucciones.md')
    shots = ROOT / 'screenshots'
    views = ''.join([
        img(md_path, shots / f'{code}_iso.png', f'{code} Iso'),
        img(md_path, shots / f'{code}_front.png', f'{code} Frente'),
        img(md_path, shots / f'{code}_left.png', f'{code} Lateral'),
    ])
    return f"""
## Modulo {code} - {name}
**Terminacion:** {finish}

{views}

### Despiece {code}
{table(headers, rows) if rows else '_Sin BOM._'}

### Notas de armado {code}
{instr}
"""


def cut_plan_section(md_path: Path) -> str:
    path = ROOT / 'outputs' / 'cutting' / 'summary.csv'
    if not path.exists():
        return '## 4. Plan de corte\n_No hay resultados. Ejecutar `make optimize-cuts`._\n'
    rows = load_csv(path)
    headers = ['Grupo', 'Piezas', 'Placas', 'Placa util (mm)', 'Kerf', 'Margen', 'Aprovechamiento', 'Descarte']
    table_rows = []
    fig_rows = []
    out_cut = ROOT / 'outputs' / 'cutting'
    for r in rows:
        group = r.get('group', '')
        table_rows.append([
            group, r.get('pieces', ''), r.get('boards_used', ''),
            f"{r.get('board_usable_w_mm', '')} x {r.get('board_usable_h_mm', '')}",
            r.get('kerf_mm', ''), r.get('margin_mm', ''), f"{r.get('utilization_pct', '')}%", f"{r.get('waste_pct', '')}%",
        ])
        svg = out_cut / f'{group}_layout.svg'
        if svg.exists():
            fig_rows.append(img(md_path, svg, f'Layout {group}', '96%'))
    blocks = []
    for i in range(0, len(fig_rows), 1):
        chunk = fig_rows[i]
        if i < len(fig_rows) - 1:
            chunk += '<div style="page-break-after: always;"></div>'
        blocks.append(chunk)
    return f"""
## 4. Plan de corte
{table(headers, table_rows)}

### Layouts por grupo
{''.join(blocks) if blocks else '_Sin SVGs._'}
"""


def build_markdown() -> str:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / 'COCINA_manual.md'
    total_headers = ['Categoria', 'Pieza', 'Cant total', 'Largo', 'Ancho', 'Espesor', 'Cantos', 'Modulos', 'ML gola', 'Bisagras']
    total_rows = consolidated_rows()
    ensambles = '\n'.join(ensemble_section(md_path, code, title) for code, title in ENSEMBLES)
    modules = '\n'.join(module_section(md_path, c, n, t) for c, n, t in MODULES)
    cut_section = cut_plan_section(md_path)
    return f'''<style>
@page {{ size: A4; margin: 7mm; }}
body {{ font-family: Arial, Helvetica, sans-serif; font-size: 9.6pt; line-height: 1.18; }}
h1, h2, h3 {{ margin-top: 0.45em; margin-bottom: 0.30em; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.8pt; }}
th, td {{ border: 1px solid #777; padding: 2px 4px; vertical-align: top; }}
</style>

# Manual Constructivo Integral - Cocina

## 1. Ensambles generales
{ensambles}

## 2. Lista unica total de partes
{table(total_headers, total_rows)}

## 3. Modulos
{modules}

{cut_section}
'''


def run_pandoc(md_path: Path, out_path: Path, to_format: str, extra: list[str] | None = None):
    cmd = ['pandoc', str(md_path), '-o', str(out_path)]
    if to_format:
        cmd.extend(['-t', to_format])
    if extra:
        cmd.extend(extra)
    subprocess.run(cmd, check=True)


def first_available(cmds: list[str]) -> str | None:
    for c in cmds:
        if shutil.which(c):
            return c
    return None


def run_chrome_pdf(html_path: Path, out_pdf: Path):
    chrome = first_available(['google-chrome', 'chromium', 'chromium-browser'])
    if not chrome:
        raise RuntimeError('No se encontro Chrome/Chromium para exportar PDF.')
    file_url = f"file://{urllib.parse.quote(str(html_path))}"
    cmd = [chrome, '--headless=new', '--disable-gpu', '--no-margins', '--no-pdf-header-footer', '--print-to-pdf-no-header', f'--print-to-pdf={out_pdf}', file_url]
    subprocess.run(cmd, check=True)


def main():
    md_path = OUT_DIR / 'COCINA_manual.md'
    html_path = OUT_DIR / 'COCINA_manual.html'
    pdf_path = OUT_DIR / 'COCINA_manual.pdf'
    md_path.write_text(build_markdown(), encoding='utf-8')
    print(f'[ok] Markdown: {md_path}')
    run_pandoc(md_path, html_path, 'html5')
    print(f'[ok] HTML: {html_path}')
    pdf_engine = first_available(['wkhtmltopdf', 'weasyprint', 'xelatex', 'lualatex', 'pdflatex', 'tectonic'])
    if pdf_engine:
        run_pandoc(md_path, pdf_path, '', ['--pdf-engine', pdf_engine])
        print(f'[ok] PDF: {pdf_path} (engine: {pdf_engine})')
        return
    run_chrome_pdf(html_path, pdf_path)
    print(f'[ok] PDF: {pdf_path} (engine: chrome-headless)')


if __name__ == '__main__':
    main()

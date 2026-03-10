#!/usr/bin/env python3
"""Genera manual constructivo (MD/HTML/PDF) a partir de un archivo TOML."""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


def relpath(from_file: Path, target: Path) -> str:
    return os.path.relpath(target, from_file.parent)


def read_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_bom(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_instructions(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def markdown_table(rows: list[dict[str, str]]) -> str:
    header = [
        "Código",
        "Categoría",
        "Pieza",
        "Cant.",
        "Largo (mm)",
        "Ancho (mm)",
        "Espesor (mm)",
        "Cantos",
    ]
    lines = [
        "| " + " | ".join(header) + " |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            "| {codigo} | {categoria} | {pieza} | {cantidad} | {largo_mm} | {ancho_mm} | {espesor_mm} | {cantos} |".format(
                **r
            )
        )
    return "\n".join(lines)


def build_markdown(cfg: dict, cfg_path: Path) -> str:
    mid = cfg["id"]
    nombre = cfg["nombre"]
    terminacion = cfg["terminacion"]
    espesor = cfg["espesor_mm"]

    bom_path = ROOT / cfg["bom_csv"]
    instr_path = ROOT / cfg["instrucciones_md"]
    out_md = ROOT / cfg["salidas"]["md"]
    screenshots = cfg["vistas"]
    screenshots_dir = ROOT / cfg["screenshots_dir"]

    bom = load_bom(bom_path)
    instrucciones = load_instructions(instr_path)

    def img_tag(key: str, caption: str) -> str:
        p = screenshots_dir / screenshots[key]
        src = relpath(out_md, p)
        return f'<figure style="display:inline-block; width:48%; margin:0 1% 12px 0;"><img src="{src}" style="width:100%; border:1px solid #ccc;" /><figcaption style="font-size:11px">{caption}</figcaption></figure>'

    table = markdown_table(bom)

    return f"""<style>
@page {{
  size: A4;
  margin: 8mm;
}}
body {{
  font-family: Arial, Helvetica, sans-serif;
  font-size: 12pt;
  line-height: 1.25;
}}
h1, h2 {{
  margin-top: 0.5em;
  margin-bottom: 0.35em;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 11pt;
}}
th, td {{
  border: 1px solid #777;
  padding: 3px 5px;
}}
</style>

# Manual Constructivo - Mueble {mid}

**Módulo:** {nombre}
**Código:** {mid}
**Terminación:** {terminacion}
**Espesor estándar:** {espesor} mm

## Vistas del Mueble
{img_tag("iso", "Isométrica")}
{img_tag("front", "Frente")}
{img_tag("rear", "Posterior")}
{img_tag("left", "Lateral Izquierdo")}
{img_tag("right", "Lateral Derecho")}
{img_tag("top", "Superior")}
{img_tag("bottom", "Inferior")}

## Detalle de Cortes
{table}

## Instrucciones de Ensamblado
{instrucciones}
"""


def run_pandoc(
    md_path: Path, out_path: Path, to_format: str, extra: list[str] | None = None
):
    cmd = ["pandoc", str(md_path), "-o", str(out_path)]
    if to_format:
        cmd.extend(["-t", to_format])
    if extra:
        cmd.extend(extra)
    subprocess.run(cmd, check=True)


def run_chrome_pdf(html_path: Path, out_pdf: Path):
    chrome = first_available(["google-chrome", "chromium", "chromium-browser"])
    if not chrome:
        raise RuntimeError("No se encontró Chrome/Chromium para exportar PDF.")

    # Chrome headless requiere URL de archivo para resolver rutas relativas.
    file_url = f"file://{urllib.parse.quote(str(html_path))}"
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-margins",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={out_pdf}",
        file_url,
    ]
    subprocess.run(cmd, check=True)


def first_available(cmds: list[str]) -> str | None:
    for c in cmds:
        if shutil.which(c):
            return c
    return None


def main():
    if len(sys.argv) < 2:
        print("Uso: manuals/generate_manual.py manuals/muebles/H.toml")
        sys.exit(1)

    cfg_path = Path(sys.argv[1]).resolve()
    cfg = read_toml(cfg_path)

    out_md = ROOT / cfg["salidas"]["md"]
    out_html = ROOT / cfg["salidas"]["html"]
    out_pdf = ROOT / cfg["salidas"]["pdf"]
    out_md.parent.mkdir(parents=True, exist_ok=True)

    md = build_markdown(cfg, cfg_path)
    out_md.write_text(md, encoding="utf-8")
    print(f"[ok] Markdown: {out_md}")

    run_pandoc(out_md, out_html, "html5")
    print(f"[ok] HTML: {out_html}")

    pdf_engine = first_available(
        ["wkhtmltopdf", "weasyprint", "xelatex", "lualatex", "pdflatex", "tectonic"]
    )
    if pdf_engine:
        extra = ["--pdf-engine", pdf_engine]
        if pdf_engine in {"xelatex", "lualatex", "pdflatex", "tectonic"}:
            extra.extend(["-V", "geometry:margin=1.5cm"])
        run_pandoc(out_md, out_pdf, "", extra=extra)
        print(f"[ok] PDF: {out_pdf} (engine: {pdf_engine})")
        return

    try:
        run_chrome_pdf(out_html, out_pdf)
        print(f"[ok] PDF: {out_pdf} (engine: chrome-headless)")
    except Exception:
        print("[warn] No hay engine PDF instalado. Se generó MD+HTML.")
        print(
            "[hint] Ubuntu: sudo apt-get update && sudo apt-get install -y texlive-xetex"
        )


if __name__ == "__main__":
    main()

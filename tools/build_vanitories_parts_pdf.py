#!/usr/bin/env python3
"""Genera una lista de piezas A4 para los vanitories actuales."""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent.parent
SOURCES = [
    ("Vanitory reforma 770 mm", ROOT / "outputs/supplier/vanitory_reforma_770_supplier.tsv"),
    ("Vanitory reforma 830 mm", ROOT / "outputs/supplier/vanitory_reforma_830_supplier.tsv"),
]
OUTPUT = ROOT / "outputs/manuals/VANITORIES_lista_piezas.pdf"


def material_name(value: str) -> str:
    return {
        "white melamine": "Melamina blanca",
        "drawer bottom 5mm": "Fondo cajon 5 mm",
        "black stone": "Piedra negra",
    }.get(value, value)


def edge_flags(row: dict[str, str]) -> str:
    return " ".join(row[key] for key in ("canto_izq", "canto_der", "canto_sup", "canto_inf"))


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def table_for(rows: list[dict[str, str]], cell: ParagraphStyle) -> Table:
    values = [["Codigo", "Pieza", "Material", "Medidas (mm)", "Cantos\nI D S I", "Bisagras"]]
    for row in rows:
        hinges = ""
        if row["cazoleta_cantidad"] not in ("", "0"):
            hinges = f'{row["cazoleta_cantidad"]} x {row["cazoleta_diametro_mm"]} mm ({row["bisagra_lado"]})'
        values.append([
            Paragraph(row["codigo"], cell),
            Paragraph(row["pieza"], cell),
            Paragraph(material_name(row["material"]), cell),
            Paragraph(f'{row["largo_mm"]} x {row["ancho_mm"]} x {row["espesor_mm"]}', cell),
            Paragraph(edge_flags(row), cell),
            Paragraph(hinges, cell),
        ])

    table = Table(values, colWidths=[32 * mm, 80 * mm, 33 * mm, 33 * mm, 22 * mm, 48 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24455d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("LEADING", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#aebbc4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#edf3f6")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#17364c"))
    subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#456071"))
    cell = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=7, leading=8.5)
    story = []
    for index, (name, source) in enumerate(SOURCES):
        rows = load_rows(source)
        story.extend([
            Paragraph(name, title),
            Spacer(1, 3 * mm),
            Paragraph(f"Lista unitaria de corte. {len(rows)} piezas. Cantos: I=izq, D=der, S=sup, I=inf.", subtitle),
            Spacer(1, 6 * mm),
            table_for(rows, cell),
        ])
        if index != len(SOURCES) - 1:
            story.append(PageBreak())

    SimpleDocTemplate(str(OUTPUT), pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm, title="Lista de piezas vanitories").build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()

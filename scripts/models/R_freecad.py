#!/usr/bin/env python3
"""Genera mueble R (rinconera bajo mesada) en FreeCAD.

Salida:
  - models/fcstd/R.FCStd
  - models/step/R.step
  - bom/R_bom.csv
"""

import csv
import os
import sys
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(globals().get("__file__", Path.cwd())).resolve()
if ROOT.is_file():
    ROOT = ROOT.parents[2]
else:
    ROOT = Path.cwd()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cads.freecad_gola import (
    GOLA_VISIBLE_H,
    J_GOLA_D,
    J_GOLA_TOTAL_H,
    make_j_gola,
)

GUI_AVAILABLE = False
Gui = None
if not os.environ.get("FREECAD_NO_GUI"):
    try:
        import FreeCADGui as Gui

        Gui.showMainWindow()
        GUI_AVAILABLE = True
    except Exception:
        Gui = None

TH = 18.0
BACK_TH = 6.0
WIDTH = 800.0
DEPTH = 450.0
CAB_H = 870.0
TOE_H = 80.0
COUNTER_TH = 30.0
TOP_OVERHANG = 20.0
LEG_W = 40.0
LEG_D = 40.0
LEG_INSET = 30.0
TOP_REAR_D = 100.0
CENTER_GAP = 2.0
OVERLAY = TH / 2.0
BOTTOM_LIGHT = 4.0
SHELF_SETBACK = 2.0

Z_BOTTOM = TOE_H
Z_BOTTOM_TOP = Z_BOTTOM + TH
Z_TOP = CAB_H
SIDE_H = Z_TOP - Z_BOTTOM
W_INT = WIDTH - 2.0 * TH
D_INT = DEPTH - BACK_TH

DOOR_Y = -TH
DOOR_Z = Z_BOTTOM + BOTTOM_LIGHT
DOOR_W = (WIDTH - 2.0 * OVERLAY - CENTER_GAP) / 2.0
DOOR1_X = OVERLAY
DOOR2_X = DOOR1_X + DOOR_W + CENTER_GAP
GOLA_Z = Z_TOP - J_GOLA_TOTAL_H
DOOR_H = (GOLA_Z + GOLA_VISIBLE_H) - DOOR_Z
SHELF_Z = Z_BOTTOM_TOP + (DOOR_H - TH) / 2.0
COUNTER_X = 0.0
COUNTER_Y = -(TH + TOP_OVERHANG)
COUNTER_W = WIDTH + TOP_OVERHANG
COUNTER_D = DEPTH + TH + TOP_OVERHANG
COUNTER_NOTCH_W = TOP_OVERHANG
COUNTER_NOTCH_D = 60.0


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_bom_metadata(parts):
    rows = []
    total_gola_ml = 0.0
    total_bisagras = 0

    for p in parts:
        codigo, categoria, pieza, cantidad, largo, ancho, espesor, cantos = p
        ml_gola = 0.0
        bisagras = 0

        if categoria == "Herraje" and "Gola" in str(pieza):
            ml_gola = (float(cantidad) * float(largo)) / 1000.0
            total_gola_ml += ml_gola

        if categoria == "Frente" and "Puerta" in str(pieza):
            alto_ref = max(float(largo), float(ancho))
            por_puerta = 3 if alto_ref >= 900.0 else 2
            bisagras = int(cantidad) * por_puerta
            total_bisagras += bisagras

        rows.append(list(p) + [f"{ml_gola:.3f}" if ml_gola else "", bisagras or ""])

    rows.append(
        [
            "TOTAL",
            "Resumen",
            "Totales_Herrajes",
            "",
            "",
            "",
            "",
            "",
            f"{total_gola_ml:.3f}",
            total_bisagras,
        ]
    )
    return rows


def ensure_visible(doc):
    for obj in doc.Objects:
        vo = getattr(obj, "ViewObject", None)
        if vo is not None:
            try:
                vo.Visibility = True
            except Exception:
                pass


def add_counter(doc):
    obj = doc.addObject("Part::Feature", "R11_Mesada")
    slab = Part.makeBox(
        COUNTER_W, COUNTER_D, COUNTER_TH, App.Vector(COUNTER_X, COUNTER_Y, Z_TOP)
    )
    notch = Part.makeBox(
        COUNTER_NOTCH_W,
        COUNTER_NOTCH_D,
        COUNTER_TH + 2.0,
        App.Vector(WIDTH, DEPTH - COUNTER_NOTCH_D, Z_TOP - 1.0),
    )
    obj.Shape = slab.cut(notch)
    return obj


def main():
    script_path = globals().get("__file__")
    if script_path:
        root = Path(script_path).resolve().parents[2]
    else:
        root = Path(os.getcwd())

    out_fcstd_dir = root / "models" / "fcstd"
    out_step_dir = root / "models" / "step"
    out_bom_dir = root / "bom"
    out_fcstd_dir.mkdir(parents=True, exist_ok=True)
    out_step_dir.mkdir(parents=True, exist_ok=True)
    out_bom_dir.mkdir(parents=True, exist_ok=True)

    doc = App.newDocument("RinconeraR")
    parts = []

    add_box(doc, "R1_Lateral_Izq", 0, 0, Z_BOTTOM, TH, DEPTH, SIDE_H)
    parts.append(("R1", "Casco", "Lateral_Izq", 1, SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "R2_Lateral_Der", WIDTH - TH, 0, Z_BOTTOM, TH, DEPTH, SIDE_H)
    parts.append(("R2", "Casco", "Lateral_Der", 1, SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "R3_Piso", 0, 0, Z_BOTTOM, WIDTH, DEPTH, TH)
    parts.append(("R3", "Casco", "Piso", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "R4_Fondo_6mm", TH, DEPTH - BACK_TH, Z_BOTTOM, W_INT, BACK_TH, SIDE_H)
    parts.append(("R4", "Fondo", "Fondo_6mm", 1, W_INT, SIDE_H, BACK_TH, "Sin canto"))

    add_box(
        doc,
        "R5_Travesano_Sup_Trasero",
        TH,
        DEPTH - TOP_REAR_D,
        Z_TOP - TH,
        W_INT,
        TOP_REAR_D,
        TH,
    )
    parts.append(
        ("R5", "Casco", "Travesano_Sup_Trasero", 1, W_INT, TOP_REAR_D, TH, "Sin canto")
    )

    add_box(
        doc,
        "R6_Estante_Regulable",
        TH + SHELF_SETBACK,
        0,
        SHELF_Z,
        W_INT - 2.0 * SHELF_SETBACK,
        D_INT - SHELF_SETBACK,
        TH,
    )
    parts.append(
        (
            "R6",
            "Interior",
            "Estante_Regulable",
            1,
            W_INT - 2.0 * SHELF_SETBACK,
            D_INT - SHELF_SETBACK,
            TH,
            "Canto frente",
        )
    )

    make_j_gola(doc, "R7_Gola_J_Superior", 0, 0, GOLA_Z, WIDTH)
    parts.append(
        (
            "R7",
            "Herraje",
            "Gola_J_Superior",
            1,
            WIDTH,
            J_GOLA_TOTAL_H,
            J_GOLA_D,
            "Aluminio",
        )
    )

    add_box(doc, "R8_Puerta_Izq", DOOR1_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("R8", "Frente", "Puerta_Izq", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "R9_Puerta_Der", DOOR2_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("R9", "Frente", "Puerta_Der", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    leg_pos = [
        (LEG_INSET, LEG_INSET),
        (WIDTH - LEG_INSET - LEG_W, LEG_INSET),
        (LEG_INSET, DEPTH - LEG_INSET - LEG_D),
        (WIDTH - LEG_INSET - LEG_W, DEPTH - LEG_INSET - LEG_D),
    ]
    for i, (lx, ly) in enumerate(leg_pos, start=1):
        add_box(doc, f"R10_Pata_{i}", lx, ly, 0.0, LEG_W, LEG_D, TOE_H)
    parts.append(("R10", "Herraje", "Pata_80", 4, LEG_W, LEG_D, TOE_H, "PVC/Aluminio"))

    add_counter(doc)
    parts.append(
        ("R11", "Mesada", "Mesada", 1, COUNTER_W, COUNTER_D, COUNTER_TH, "Piedra")
    )

    doc.recompute()

    if GUI_AVAILABLE:
        ensure_visible(doc)

    fcstd_path = out_fcstd_dir / "R.FCStd"
    step_path = out_step_dir / "R.step"
    bom_path = out_bom_dir / "R_bom.csv"

    doc.saveAs(str(fcstd_path))
    Part.export([o for o in doc.Objects if hasattr(o, "Shape")], str(step_path))

    rows = add_bom_metadata(parts)
    with open(bom_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "codigo",
                "categoria",
                "pieza",
                "cantidad",
                "largo_mm",
                "ancho_mm",
                "espesor_mm",
                "cantos",
                "ml_gola",
                "bisagras_cazoleta",
            ]
        )
        w.writerows(rows)

    print("Modelo generado:")
    print("-", fcstd_path)
    print("-", step_path)
    print("-", bom_path)
    print("\nResumen de cotas clave (mm):")
    print(f"- Ancho exterior: {WIDTH}")
    print(f"- Profundidad exterior: {DEPTH}")
    print(f"- Altura final con mesada: {CAB_H + COUNTER_TH}")
    print(f"- Mesada: {COUNTER_W} x {COUNTER_D}")
    print(f"- Puertas: {DOOR_W} x {DOOR_H}")
    print(f"- Hueco visible de dedos: {GOLA_VISIBLE_H}")


if __name__ == "__main__":
    main()

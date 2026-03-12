#!/usr/bin/env python3
"""Genera mueble AB (con AC integrado) en FreeCAD.

Uso:
  freecad -c scripts/models/AB_freecad.py

Salida:
  - models/fcstd/AB.FCStd
  - models/step/AB.step
  - bom/AB_bom.csv
"""

import csv
import os
from pathlib import Path

import FreeCAD as App
import Part

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
TH_AC = 18.0
BACK_TH = 3.0
AC_BACK_TH = 18.0

# Ancho restante total: 2930 - 672 - 1050 = 1208
WIDTH = 1355.0
DEPTH = 320.0

# AC (cajon paraiso inferior)
AC_H = 309.0
AC_SIDE_H = AC_H - 2 * TH_AC
AC_INT_W = WIDTH - 2 * TH_AC
AC_INNER_W = WIDTH - 4 * TH_AC
AC_INNER_H = AC_H - 2 * TH_AC

# AB (alacena superior blanca)
AB_H = 491.0
AB_SIDE_H = AB_H - 2 * TH
GOLA_J_H = 25.0
GOLA_J_D = 20.0

# AB: 3 puertas iguales, equidistantes
CENTER_GAP = 2.0
OUTER_OVERLAY = TH / 2.0  # 9 mm

AB_INT_W = WIDTH - 2 * TH
AB_INT_H = AB_SIDE_H
AB_INT_D = DEPTH - BACK_TH

DOOR_H = AB_H - TH
DOOR_W = (WIDTH - 2 * OUTER_OVERLAY - 2 * CENTER_GAP) / 3.0
DOOR1_X = OUTER_OVERLAY
DOOR2_X = DOOR1_X + DOOR_W + CENTER_GAP
DOOR3_X = DOOR2_X + DOOR_W + CENTER_GAP
DOOR_Y = -TH
DOOR_Z = AC_H + OUTER_OVERLAY
GOLA_Z = AC_H


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

    doc = App.newDocument("AlacenaAB")
    parts = []

    # --- AC: cajon inferior (paraiso doble 18 mm + fondo 18 mm) ---
    add_box(doc, "AC1_Lateral_Izq", 0, 0, TH_AC, TH_AC, DEPTH, AC_SIDE_H)
    parts.append(
        (
            "AC1",
            "AC_Paraiso",
            "AC_Lateral_Izq",
            1,
            AC_SIDE_H,
            DEPTH,
            TH_AC,
            "Crudo (enchapar en obra)",
        )
    )

    add_box(doc, "AC2_Lateral_Der", WIDTH - TH_AC, 0, TH_AC, TH_AC, DEPTH, AC_SIDE_H)
    parts.append(
        (
            "AC2",
            "AC_Paraiso",
            "AC_Lateral_Der",
            1,
            AC_SIDE_H,
            DEPTH,
            TH_AC,
            "Crudo (enchapar en obra)",
        )
    )

    add_box(doc, "AC3_Piso", 0, 0, 0, WIDTH, DEPTH, TH_AC)
    parts.append(
        ("AC3", "AC_Paraiso", "AC_Piso", 1, WIDTH, DEPTH, TH_AC, "Crudo (enchapar en obra)")
    )

    add_box(doc, "AC4_Tapa", 0, 0, AC_H - TH_AC, WIDTH, DEPTH, TH_AC)
    parts.append(
        ("AC4", "AC_Paraiso", "AC_Tapa", 1, WIDTH, DEPTH, TH_AC, "Crudo (enchapar en obra)")
    )

    add_box(doc, "AC6_Lateral_Izq_Interior", TH_AC, 0, TH_AC, TH_AC, DEPTH, AC_SIDE_H)
    parts.append(
        (
            "AC6",
            "AC_Paraiso",
            "AC_Lateral_Izq_Interior",
            1,
            AC_SIDE_H,
            DEPTH,
            TH_AC,
            "Crudo (enchapar en obra)",
        )
    )

    add_box(doc, "AC7_Lateral_Der_Interior", WIDTH - 2 * TH_AC, 0, TH_AC, TH_AC, DEPTH, AC_SIDE_H)
    parts.append(
        (
            "AC7",
            "AC_Paraiso",
            "AC_Lateral_Der_Interior",
            1,
            AC_SIDE_H,
            DEPTH,
            TH_AC,
            "Crudo (enchapar en obra)",
        )
    )

    add_box(doc, "AC8_Piso_Interior", 2 * TH_AC, 0, TH_AC, AC_INNER_W, DEPTH, TH_AC)
    parts.append(
        ("AC8", "AC_Paraiso", "AC_Piso_Interior", 1, AC_INNER_W, DEPTH, TH_AC, "Crudo (enchapar en obra)")
    )

    add_box(doc, "AC9_Tapa_Interior", 2 * TH_AC, 0, AC_H - 2 * TH_AC, AC_INNER_W, DEPTH, TH_AC)
    parts.append(
        ("AC9", "AC_Paraiso", "AC_Tapa_Interior", 1, AC_INNER_W, DEPTH, TH_AC, "Crudo (enchapar en obra)")
    )

    # Fondo AC en paraiso 18 mm (entre laterales y entre piso/tapa)
    add_box(
        doc,
        "AC5_Fondo_18mm",
        2 * TH_AC,
        DEPTH - AC_BACK_TH,
        TH_AC,
        AC_INNER_W,
        AC_BACK_TH,
        AC_SIDE_H,
    )
    parts.append(
        (
            "AC5",
            "AC_Paraiso",
            "AC_Fondo_18mm",
            1,
            AC_INNER_W,
            AC_SIDE_H,
            AC_BACK_TH,
            "Crudo (enchapar en obra)",
        )
    )

    # --- AB: alacena superior (sin estantes, sin divisores internos) ---
    z_ab = AC_H

    add_box(doc, "AB1_Lateral_Izq", 0, 0, z_ab + TH, TH, DEPTH, AB_SIDE_H)
    parts.append(
        ("AB1", "AB_Blanco", "AB_Lateral_Izq", 1, AB_SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AB2_Lateral_Der", WIDTH - TH, 0, z_ab + TH, TH, DEPTH, AB_SIDE_H)
    parts.append(
        ("AB2", "AB_Blanco", "AB_Lateral_Der", 1, AB_SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AB3_Piso", 0, 0, z_ab, WIDTH, DEPTH, TH)
    parts.append(("AB3", "AB_Blanco", "AB_Piso", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB4_Tapa", 0, 0, z_ab + AB_H - TH, WIDTH, DEPTH, TH)
    parts.append(("AB4", "AB_Blanco", "AB_Tapa", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB5_Fondo_3mm", TH, AB_INT_D, z_ab + TH, AB_INT_W, BACK_TH, AB_INT_H)
    parts.append(
        (
            "AB5",
            "AB_Blanco",
            "AB_Fondo_3mm",
            1,
            AB_INT_W,
            AB_INT_H,
            BACK_TH,
            "Sin canto",
        )
    )

    # Puertas AB (3 iguales)
    add_box(doc, "AB6_Puerta_1", DOOR1_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB6", "Frente", "AB_Puerta_1", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "AB7_Puerta_2", DOOR2_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB7", "Frente", "AB_Puerta_2", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "AB8_Puerta_3", DOOR3_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB8", "Frente", "AB_Puerta_3", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    # Perfil gola J inferior (debajo de puertas)
    add_box(doc, "AB9_Gola_J_Inferior", 0, -GOLA_J_D, GOLA_Z, WIDTH, GOLA_J_D, GOLA_J_H)
    parts.append(
        ("AB9", "Herraje", "Gola_J_Inferior", 1, WIDTH, GOLA_J_H, GOLA_J_D, "Aluminio")
    )

    doc.recompute()

    if GUI_AVAILABLE:
        for obj in doc.Objects:
            vo = getattr(obj, "ViewObject", None)
            if vo is not None:
                try:
                    vo.Visibility = True
                    if "Fondo" in obj.Name:
                        vo.Visibility = False
                except Exception:
                    pass

    fcstd_path = out_fcstd_dir / "AB.FCStd"
    step_path = out_step_dir / "AB.step"
    bom_path = out_bom_dir / "AB_bom.csv"

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
        for row in rows:
            w.writerow(row)

    print("Modelo generado:")
    print("-", fcstd_path)
    print("-", step_path)
    print("-", bom_path)
    print("\nResumen de cotas clave (mm):")
    print(f"- Ancho exterior total AB+AC: {WIDTH}")
    print(f"- Profundidad exterior: {DEPTH}")
    print(f"- AC (paraiso) alto: {AC_H}")
    print(f"- AB (blanco) alto: {AB_H}")
    print(f"- Altura total AB+AC: {AC_H + AB_H}")
    print(f"- AB puertas (3 iguales): {DOOR_W} x {DOOR_H}")


if __name__ == "__main__":
    main()

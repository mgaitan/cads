#!/usr/bin/env python3
"""Genera alacena superior A (AA) en FreeCAD.

Uso:
  freecad -c alacena_AA_freecad.py

Salida:
  - alacena_AA.FCStd
  - alacena_AA.step
  - alacena_AA_bom.csv
"""

import csv
import os

import FreeCAD as App
import Part

GUI_AVAILABLE = False
try:
    import FreeCADGui as Gui

    Gui.showMainWindow()
    GUI_AVAILABLE = True
except Exception:
    Gui = None

# Parametros principales (mm)
TH = 18.0
BACK_TH = 3.0
WIDTH = 1050.0
DEPTH = 320.0
HEIGHT = 680.0  # Colgado a 1620 mm para llegar a techo 2300 mm.

DOOR_GAP_CENTER = 2.0
DOOR_OVERLAP = TH / 2.0
DUCT_D = 160.0
DUCT_R = DUCT_D / 2.0
DUCT_REAR_CLR = 20.0

W_INT = WIDTH - 2 * TH
D_INT = DEPTH - BACK_TH
SIDE_H = HEIGHT - 2 * TH
MID_TH = TH
BAY_W = (W_INT - MID_TH) / 2.0

# Posiciones Z
Z_BOTTOM = 0.0
Z_TOP = HEIGHT - TH
Z_INNER0 = TH

# Centro de ducto en el modulo derecho
DUCT_CX = TH + BAY_W + MID_TH + BAY_W / 2.0
DUCT_CY = D_INT - DUCT_REAR_CLR - DUCT_R

# Puertas
DOOR_H = HEIGHT - TH  # solape 9 mm arriba/abajo
DOOR_W = (WIDTH - TH - DOOR_GAP_CENTER) / 2.0  # con luz central 2 mm
LEFT_DOOR_X = DOOR_OVERLAP
RIGHT_DOOR_X = LEFT_DOOR_X + DOOR_W + DOOR_GAP_CENTER
DOOR_Z = DOOR_OVERLAP
DOOR_Y = -TH


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_box_with_round_hole(doc, name, x, y, z, dx, dy, dz, cx, cy, r):
    box = Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
    cyl = Part.makeCylinder(
        r, dz + 2.0, App.Vector(cx, cy, z - 1.0), App.Vector(0, 0, 1)
    )
    shape = box.cut(cyl)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def main():
    script_path = globals().get("__file__")
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()

    doc = App.newDocument("AlacenaAA")
    parts = []

    # Casco con piso/techo pasantes
    add_box(doc, "AA1_Lateral_Izq", 0, 0, Z_INNER0, TH, DEPTH, SIDE_H)
    parts.append(
        ("AA1", "Lateral", "Lateral_Izq", 1, SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AA2_Lateral_Der", WIDTH - TH, 0, Z_INNER0, TH, DEPTH, SIDE_H)
    parts.append(
        ("AA2", "Lateral", "Lateral_Der", 1, SIDE_H, DEPTH, TH, "Canto frente")
    )

    # Piso y techo con calado ducto 160 mm
    add_box_with_round_hole(
        doc,
        "AA3_Piso_Casco",
        0,
        0,
        Z_BOTTOM,
        WIDTH,
        DEPTH,
        TH,
        DUCT_CX,
        DUCT_CY,
        DUCT_R,
    )
    parts.append(
        (
            "AA3",
            "Horizontal",
            "Piso_Casco_Calado160",
            1,
            WIDTH,
            DEPTH,
            TH,
            "Canto frente",
        )
    )

    add_box_with_round_hole(
        doc,
        "AA4_Tapa_Casco",
        0,
        0,
        Z_TOP,
        WIDTH,
        DEPTH,
        TH,
        DUCT_CX,
        DUCT_CY,
        DUCT_R,
    )
    parts.append(
        (
            "AA4",
            "Horizontal",
            "Tapa_Casco_Calado160",
            1,
            WIDTH,
            DEPTH,
            TH,
            "Canto frente",
        )
    )

    # Divisor vertical central
    add_box(doc, "AA5_Divisor_Central", TH + BAY_W, 0, Z_INNER0, MID_TH, D_INT, SIDE_H)
    parts.append(
        ("AA5", "Vertical", "Divisor_Central", 1, SIDE_H, D_INT, TH, "Canto frente")
    )

    # Estante solo lado derecho, a media altura, con calado 160
    estante_z = Z_INNER0 + (SIDE_H - TH) / 2.0
    add_box_with_round_hole(
        doc,
        "AA6_Estante_Der_Calado160",
        TH + BAY_W + MID_TH,
        0,
        estante_z,
        BAY_W,
        D_INT,
        TH,
        DUCT_CX,
        DUCT_CY,
        DUCT_R,
    )
    parts.append(
        (
            "AA6",
            "Horizontal",
            "Estante_Derecho_Calado160",
            1,
            BAY_W,
            D_INT,
            TH,
            "Canto frente",
        )
    )

    # Fondo 3 mm (oculto para capturas)
    add_box(doc, "AA7_Fondo_3mm", TH, D_INT, Z_INNER0, W_INT, BACK_TH, SIDE_H)
    parts.append(("AA7", "Fondo", "Fondo_3mm", 1, W_INT, SIDE_H, BACK_TH, "Sin canto"))

    # Dos puertas iguales
    add_box(doc, "AA8_Puerta_Izq", LEFT_DOOR_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(
        ("AA8", "Frente", "Puerta_Izquierda", 1, DOOR_W, DOOR_H, TH, "4 cantos")
    )

    add_box(doc, "AA9_Puerta_Der", RIGHT_DOOR_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AA9", "Frente", "Puerta_Derecha", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

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

    fcstd_path = os.path.join(here, "alacena_AA.FCStd")
    step_path = os.path.join(here, "alacena_AA.step")
    bom_path = os.path.join(here, "alacena_AA_bom.csv")

    doc.saveAs(fcstd_path)
    Part.export([o for o in doc.Objects if hasattr(o, "Shape")], step_path)

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
            ]
        )
        for row in parts:
            w.writerow(row)

    print("Modelo generado:")
    print("-", fcstd_path)
    print("-", step_path)
    print("-", bom_path)
    print("\nResumen de cotas clave (mm):")
    print(f"- Ancho exterior: {WIDTH}")
    print(f"- Profundidad exterior: {DEPTH}")
    print(f"- Alto mueble: {HEIGHT}")
    print(f"- Ancho util por lado: {BAY_W}")
    print(f"- Puertas (cada una): {DOOR_W} x {DOOR_H}")
    print(
        f"- Calado ducto: diametro {DUCT_D}, lado derecho, centro X={DUCT_CX}, Y={DUCT_CY} (20 mm desde fondo)"
    )
    print("- Altura recomendada de colocacion: base a 1650 mm (mesada 900, techo 2300)")


if __name__ == "__main__":
    main()

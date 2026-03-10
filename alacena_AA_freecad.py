#!/usr/bin/env python3
"""Genera alacena superior A (AA) en FreeCAD."""

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

TH = 18.0
BACK_TH = 3.0
WIDTH = 1050.0
DEPTH = 320.0
HEIGHT = 710.0

DUCT_D = 160.0
DUCT_R = DUCT_D / 2.0
DUCT_REAR_CLR = 20.0

CONN_D = 35.0
CONN_R = CONN_D / 2.0
CONN_SPACING = 80.0

W_INT = WIDTH - 2 * TH
D_INT = DEPTH - BACK_TH
SIDE_H = HEIGHT - 2 * TH

Z_BOTTOM = 0.0
Z_TOP = HEIGHT - TH
Z_INNER0 = TH

# Lado izquierdo (calefon) y derecho (extractor)
X_LEFT_ZONE = TH + W_INT * 0.25
X_RIGHT_ZONE = TH + W_INT * 0.75
Y_DUCT_TOP = D_INT - DUCT_REAR_CLR - DUCT_R
Y_DUCT_FLOOR = 90.0
Y_CONN = 55.0

# Dos frentes verticales
FRONT_H = HEIGHT - TH
FRONT_W = (WIDTH - TH - 2.0) / 2.0
LEFT_FRONT_X = TH / 2.0
RIGHT_FRONT_X = LEFT_FRONT_X + FRONT_W + 2.0
FRONT_Y = -TH
FRONT_Z = TH / 2.0


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_box_with_round_holes(doc, name, x, y, z, dx, dy, dz, holes):
    shape = Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
    for cx, cy, r in holes:
        cyl = Part.makeCylinder(
            r, dz + 2.0, App.Vector(cx, cy, z - 1.0), App.Vector(0, 0, 1)
        )
        shape = shape.cut(cyl)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def main():
    script_path = globals().get("__file__")
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()

    doc = App.newDocument("AlacenaAA")
    parts = []

    add_box(doc, "AA1_Lateral_Izq", 0, 0, Z_INNER0, TH, DEPTH, SIDE_H)
    parts.append(
        ("AA1", "Lateral", "Lateral_Izq", 1, SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AA2_Lateral_Der", WIDTH - TH, 0, Z_INNER0, TH, DEPTH, SIDE_H)
    parts.append(
        ("AA2", "Lateral", "Lateral_Der", 1, SIDE_H, DEPTH, TH, "Canto frente")
    )

    # Piso: 3 pasantes 35 (calefon) + 1 pasante 160 (extractor der)
    floor_holes = [
        (X_RIGHT_ZONE, Y_DUCT_FLOOR, DUCT_R),
        (X_LEFT_ZONE - CONN_SPACING, Y_CONN, CONN_R),
        (X_LEFT_ZONE, Y_CONN, CONN_R),
        (X_LEFT_ZONE + CONN_SPACING, Y_CONN, CONN_R),
    ]
    add_box_with_round_holes(
        doc, "AA3_Piso_Casco", 0, 0, Z_BOTTOM, WIDTH, DEPTH, TH, floor_holes
    )
    parts.append(
        ("AA3", "Horizontal", "Piso_Casco_Calados", 1, WIDTH, DEPTH, TH, "Canto frente")
    )

    # Techo: solo pasante 160 derecho
    top_holes = [(X_RIGHT_ZONE, Y_DUCT_TOP, DUCT_R)]
    add_box_with_round_holes(
        doc, "AA4_Tapa_Casco", 0, 0, Z_TOP, WIDTH, DEPTH, TH, top_holes
    )
    parts.append(
        (
            "AA4",
            "Horizontal",
            "Tapa_Casco_Calado_Der160",
            1,
            WIDTH,
            DEPTH,
            TH,
            "Canto frente",
        )
    )

    add_box(doc, "AA5_Travesano_Sup", TH, 0, Z_TOP - 60.0, W_INT, TH, 60.0)
    parts.append(("AA5", "Interior", "Travesano_Sup", 1, W_INT, 60.0, TH, "Sin canto"))

    add_box(doc, "AA6_Travesano_Inf", TH, 0, Z_INNER0, W_INT, TH, 60.0)
    parts.append(("AA6", "Interior", "Travesano_Inf", 1, W_INT, 60.0, TH, "Sin canto"))

    add_box(doc, "AA7_Fondo_3mm", TH, D_INT, Z_INNER0, W_INT, BACK_TH, SIDE_H)
    parts.append(("AA7", "Fondo", "Fondo_3mm", 1, W_INT, SIDE_H, BACK_TH, "Sin canto"))

    # Frentes verticales
    add_box(doc, "AA8_Frente_Izq", LEFT_FRONT_X, FRONT_Y, FRONT_Z, FRONT_W, TH, FRONT_H)
    parts.append(
        ("AA8", "Frente", "Frente_Izquierdo", 1, FRONT_W, FRONT_H, TH, "4 cantos")
    )

    add_box(
        doc, "AA9_Frente_Der", RIGHT_FRONT_X, FRONT_Y, FRONT_Z, FRONT_W, TH, FRONT_H
    )
    parts.append(
        ("AA9", "Frente", "Frente_Derecho", 1, FRONT_W, FRONT_H, TH, "4 cantos")
    )

    # Liston fijo 90 mm para completar visual hacia linea AC (se monta por debajo del piso)
    add_box(doc, "AA10_Liston_Fijo_90", TH / 2.0, FRONT_Y, -90.0, WIDTH - TH, TH, 90.0)
    parts.append(
        ("AA10", "Frente", "Liston_Fijo_90", 1, WIDTH - TH, 90.0, TH, "4 cantos")
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


if __name__ == "__main__":
    main()

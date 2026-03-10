#!/usr/bin/env python3
"""Genera conjunto derecho de alacena: AB + AC en FreeCAD.

Uso:
  freecad -c alacena_AB_freecad.py

Salida:
  - alacena_AB.FCStd
  - alacena_AB.step
  - alacena_AB_bom.csv
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

TH = 18.0
TH_AC = 25.4
BACK_TH = 3.0

# Ancho restante total: 2930 - 636 - 1050 = 1244
WIDTH = 1244.0
DEPTH = 320.0

# AC (cajon paraiso inferior)
AC_H = 300.0
AC_SIDE_H = AC_H - 2 * TH_AC

# AB (alacena superior blanca)
AB_H = 350.0
AB_SIDE_H = AB_H - 2 * TH

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


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def main():
    script_path = globals().get("__file__")
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()

    doc = App.newDocument("AlacenaAB")
    parts = []

    # --- AC: cajon inferior (melamina paraiso 25.4 mm) ---
    add_box(doc, "AC1_Lateral_Izq", 0, 0, TH_AC, TH_AC, DEPTH, AC_SIDE_H)
    parts.append(("AC1", "AC_Paraiso", "AC_Lateral_Izq", 1, AC_SIDE_H, DEPTH, TH_AC, "Canto frente"))

    add_box(doc, "AC2_Lateral_Der", WIDTH - TH_AC, 0, TH_AC, TH_AC, DEPTH, AC_SIDE_H)
    parts.append(("AC2", "AC_Paraiso", "AC_Lateral_Der", 1, AC_SIDE_H, DEPTH, TH_AC, "Canto frente"))

    add_box(doc, "AC3_Piso", 0, 0, 0, WIDTH, DEPTH, TH_AC)
    parts.append(("AC3", "AC_Paraiso", "AC_Piso", 1, WIDTH, DEPTH, TH_AC, "Canto frente"))

    add_box(doc, "AC4_Tapa", 0, 0, AC_H - TH_AC, WIDTH, DEPTH, TH_AC)
    parts.append(("AC4", "AC_Paraiso", "AC_Tapa", 1, WIDTH, DEPTH, TH_AC, "Canto frente"))

    # --- AB: alacena superior (sin estantes, sin divisores internos) ---
    z_ab = AC_H

    add_box(doc, "AB1_Lateral_Izq", 0, 0, z_ab + TH, TH, DEPTH, AB_SIDE_H)
    parts.append(("AB1", "AB_Blanco", "AB_Lateral_Izq", 1, AB_SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB2_Lateral_Der", WIDTH - TH, 0, z_ab + TH, TH, DEPTH, AB_SIDE_H)
    parts.append(("AB2", "AB_Blanco", "AB_Lateral_Der", 1, AB_SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB3_Piso", 0, 0, z_ab, WIDTH, DEPTH, TH)
    parts.append(("AB3", "AB_Blanco", "AB_Piso", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB4_Tapa", 0, 0, z_ab + AB_H - TH, WIDTH, DEPTH, TH)
    parts.append(("AB4", "AB_Blanco", "AB_Tapa", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB5_Fondo_3mm", TH, AB_INT_D, z_ab + TH, AB_INT_W, BACK_TH, AB_INT_H)
    parts.append(("AB5", "AB_Blanco", "AB_Fondo_3mm", 1, AB_INT_W, AB_INT_H, BACK_TH, "Sin canto"))

    # Puertas AB (3 iguales)
    add_box(doc, "AB6_Puerta_1", DOOR1_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB6", "Frente", "AB_Puerta_1", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "AB7_Puerta_2", DOOR2_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB7", "Frente", "AB_Puerta_2", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "AB8_Puerta_3", DOOR3_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB8", "Frente", "AB_Puerta_3", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

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

    fcstd_path = os.path.join(here, "alacena_AB.FCStd")
    step_path = os.path.join(here, "alacena_AB.step")
    bom_path = os.path.join(here, "alacena_AB_bom.csv")

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
    print(f"- Ancho exterior total AB+AC: {WIDTH}")
    print(f"- Profundidad exterior: {DEPTH}")
    print(f"- AC (paraiso) alto: {AC_H}")
    print(f"- AB (blanco) alto: {AB_H}")
    print(f"- Altura total AB+AC: {AC_H + AB_H}")
    print(f"- AB puertas (3 iguales): {DOOR_W} x {DOOR_H}")


if __name__ == "__main__":
    main()

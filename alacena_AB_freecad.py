#!/usr/bin/env python3
"""Genera conjunto derecho de alacena: A2 + A3 (AB) en FreeCAD.

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
BACK_TH = 3.0

# Ancho restante total: 2930 - 636 - 1050 = 1244
WIDTH = 1244.0
DEPTH = 320.0

# A3 (cajon paraiso inferior)
A3_H = 300.0
A3_SIDE_H = A3_H - 2 * TH

# A2 (alacena superior blanca)
A2_H = 350.0
A2_SIDE_H = A2_H - 2 * TH

# A2: 3 puertas iguales, equidistantes
CENTER_GAP = 2.0
OUTER_OVERLAY = TH / 2.0  # 9 mm

A2_INT_W = WIDTH - 2 * TH
A2_INT_H = A2_SIDE_H
A2_INT_D = DEPTH - BACK_TH

# Puertas A2 (3 iguales)
DOOR_H = A2_H - TH
DOOR_W = (WIDTH - 2 * OUTER_OVERLAY - 2 * CENTER_GAP) / 3.0
DOOR1_X = OUTER_OVERLAY
DOOR2_X = DOOR1_X + DOOR_W + CENTER_GAP
DOOR3_X = DOOR2_X + DOOR_W + CENTER_GAP
DOOR_Y = -TH
DOOR_Z = A3_H + OUTER_OVERLAY


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

    # --- A3: cajon inferior (melamina paraiso 18 mm) ---
    # Piso/techo pasantes; laterales entre ambos.
    add_box(doc, "AB1_A3_Lateral_Izq", 0, 0, TH, TH, DEPTH, A3_SIDE_H)
    parts.append(
        ("AB1", "A3_Paraiso", "A3_Lateral_Izq", 1, A3_SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AB2_A3_Lateral_Der", WIDTH - TH, 0, TH, TH, DEPTH, A3_SIDE_H)
    parts.append(
        ("AB2", "A3_Paraiso", "A3_Lateral_Der", 1, A3_SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AB3_A3_Piso", 0, 0, 0, WIDTH, DEPTH, TH)
    parts.append(("AB3", "A3_Paraiso", "A3_Piso", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB4_A3_Tapa", 0, 0, A3_H - TH, WIDTH, DEPTH, TH)
    parts.append(("AB4", "A3_Paraiso", "A3_Tapa", 1, WIDTH, DEPTH, TH, "Canto frente"))

    # --- A2: alacena superior (sin estantes) ---
    z2 = A3_H

    add_box(doc, "AB5_A2_Lateral_Izq", 0, 0, z2 + TH, TH, DEPTH, A2_SIDE_H)
    parts.append(
        ("AB5", "A2_Blanco", "A2_Lateral_Izq", 1, A2_SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AB6_A2_Lateral_Der", WIDTH - TH, 0, z2 + TH, TH, DEPTH, A2_SIDE_H)
    parts.append(
        ("AB6", "A2_Blanco", "A2_Lateral_Der", 1, A2_SIDE_H, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "AB7_A2_Piso", 0, 0, z2, WIDTH, DEPTH, TH)
    parts.append(("AB7", "A2_Blanco", "A2_Piso", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB8_A2_Tapa", 0, 0, z2 + A2_H - TH, WIDTH, DEPTH, TH)
    parts.append(("AB8", "A2_Blanco", "A2_Tapa", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(doc, "AB9_A2_Fondo_3mm", TH, A2_INT_D, z2 + TH, A2_INT_W, BACK_TH, A2_INT_H)
    parts.append(
        (
            "AB9",
            "A2_Blanco",
            "A2_Fondo_3mm",
            1,
            A2_INT_W,
            A2_INT_H,
            BACK_TH,
            "Sin canto",
        )
    )

    # Puertas A2 (3 iguales)
    add_box(doc, "AB10_A2_Puerta_1", DOOR1_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB10", "Frente", "A2_Puerta_1", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "AB11_A2_Puerta_2", DOOR2_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB11", "Frente", "A2_Puerta_2", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "AB12_A2_Puerta_3", DOOR3_X, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("AB12", "Frente", "A2_Puerta_3", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

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
    print(f"- Ancho exterior total AB: {WIDTH}")
    print(f"- Profundidad exterior: {DEPTH}")
    print(f"- A3 (paraiso) alto: {A3_H}")
    print(f"- A2 (blanco) alto: {A2_H}")
    print(f"- Altura total AB: {A3_H + A2_H}")
    print(f"- A2 puertas (3 iguales): {DOOR_W} x {DOOR_H}")
    print("- Referencia de montaje: piso A3 coincide con piso de A1")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Genera una columna para horno + microondas en FreeCAD.

Uso:
  freecad -c columna_horno_micro_freecad.py

Salida:
  - columna_horno_micro.FCStd
  - columna_horno_micro.step
  - columna_horno_micro_bom.csv
"""

import csv
import os

import FreeCAD as App
import Part

# Parametros principales (mm)
TH = 18.0
WIDTH_INT = 600.0
DEPTH = 600.0
HEIGHT_TOTAL = 2300.0
LEG_H = 80.0

OVEN_Z_START = 800.0
OVEN_OPENING_VISIBLE_H = 600.0
OVEN_EXTRA_INTERNAL_H = 30.0  # juego interno oculto por regrueso frontal
OVEN_OPENING_W = 600.0

MICRO_OPENING_H = 400.0
SEPARATOR_FRONT_H = 30.0  # faja frontal visible entre horno y micro

W = WIDTH_INT + 2 * TH
CARCASS_H = HEIGHT_TOTAL - LEG_H
X_INT0 = TH
X_INT1 = X_INT0 + WIDTH_INT

# Cotas derivadas en Z (desde piso)
Z_BOTTOM_PANEL = LEG_H
Z_TOP_PANEL = HEIGHT_TOTAL - TH

Z_OVEN_BASE = OVEN_Z_START
Z_OVEN_VISIBLE_TOP = Z_OVEN_BASE + OVEN_OPENING_VISIBLE_H
Z_OVEN_INTERNAL_TOP = Z_OVEN_VISIBLE_TOP + OVEN_EXTRA_INTERNAL_H

Z_MICRO_BASE = Z_OVEN_INTERNAL_TOP
Z_MICRO_TOP = Z_MICRO_BASE + MICRO_OPENING_H

# Compartimento inferior (bajo horno)
LOWER_CLEAR_H = Z_OVEN_BASE - Z_BOTTOM_PANEL
LOWER_MID_SHELF_Z = Z_BOTTOM_PANEL + (LOWER_CLEAR_H - TH) / 2.0

# Compartimento superior (sobre micro)
TOP_CLEAR_H = Z_TOP_PANEL - Z_MICRO_TOP

# Puertas (frente aplicado, holgura 2 mm perimetral)
DOOR_GAP = 2.0
DOOR_W = W - 2 * DOOR_GAP
LOWER_DOOR_H = (Z_OVEN_BASE - Z_BOTTOM_PANEL) - 2 * DOOR_GAP
UPPER_DOOR_H = (HEIGHT_TOTAL - Z_MICRO_TOP) - 2 * DOOR_GAP
DOOR_DEPTH = TH


def add_part(doc, name, x, y, z, dx, dy, dz):
    box = Part.makeBox(dx, dy, dz)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = box
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def main():
    script_path = globals().get("__file__")
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()
    doc = App.newDocument("ColumnaHornoMicro")

    parts = []

    # Codigos de despiece: H1..H11
    # Laterales
    add_part(doc, "H1_Lateral_Izq", 0, 0, LEG_H, TH, DEPTH, CARCASS_H)
    parts.append(
        (
            "H1",
            "Lateral",
            "Lateral_Izq",
            1,
            CARCASS_H,
            DEPTH,
            TH,
            "Cantos frente+arriba+abajo",
        )
    )

    add_part(doc, "H2_Lateral_Der", W - TH, 0, LEG_H, TH, DEPTH, CARCASS_H)
    parts.append(
        (
            "H2",
            "Lateral",
            "Lateral_Der",
            1,
            CARCASS_H,
            DEPTH,
            TH,
            "Cantos frente+arriba+abajo",
        )
    )

    # Tapa inferior y superior pasantes (debajo/encima de laterales)
    # Esto permite atornillar desde abajo/arriba y ocultar fijaciones.
    add_part(doc, "H3_Piso_Casco", 0, 0, Z_BOTTOM_PANEL, W, DEPTH, TH)
    parts.append(("H3", "Horizontal", "Piso_Casco", 1, W, DEPTH, TH, "Canto frente"))

    add_part(doc, "H4_Tapa_Casco", 0, 0, Z_TOP_PANEL, W, DEPTH, TH)
    parts.append(("H4", "Horizontal", "Tapa_Casco", 1, W, DEPTH, TH, "Canto frente"))

    # Divisiones horizontales
    add_part(doc, "H5_Piso_Horno", X_INT0, 0, Z_OVEN_BASE, WIDTH_INT, DEPTH, TH)
    parts.append(
        ("H5", "Horizontal", "Piso_Horno", 1, WIDTH_INT, DEPTH, TH, "Canto frente")
    )

    add_part(doc, "H6_Piso_Micro", X_INT0, 0, Z_MICRO_BASE, WIDTH_INT, DEPTH, TH)
    parts.append(
        ("H6", "Horizontal", "Piso_Micro", 1, WIDTH_INT, DEPTH, TH, "Canto frente")
    )

    add_part(doc, "H7_Tapa_Micro", X_INT0, 0, Z_MICRO_TOP, WIDTH_INT, DEPTH, TH)
    parts.append(
        ("H7", "Horizontal", "Tapa_Micro", 1, WIDTH_INT, DEPTH, TH, "Canto frente")
    )

    # Estante inferior intermedio
    add_part(
        doc, "H8_Estante_Inferior", X_INT0, 0, LOWER_MID_SHELF_Z, WIDTH_INT, DEPTH, TH
    )
    parts.append(
        (
            "H8",
            "Horizontal",
            "Estante_Inferior",
            1,
            WIDTH_INT,
            DEPTH,
            TH,
            "Canto frente",
        )
    )

    # Regrueso/faja frontal entre horno y micro (tapa el juego superior del horno)
    add_part(
        doc,
        "H9_Faja_Frontal_30",
        X_INT0,
        0,
        Z_OVEN_VISIBLE_TOP,
        WIDTH_INT,
        TH,
        SEPARATOR_FRONT_H,
    )
    parts.append(
        (
            "H9",
            "Frente",
            "Faja_Frontal_30",
            1,
            WIDTH_INT,
            SEPARATOR_FRONT_H,
            TH,
            "Cantos vistos",
        )
    )

    # Puertas (referencia de frente aplicado)
    add_part(
        doc,
        "H10_Puerta_Inferior",
        DOOR_GAP,
        -DOOR_DEPTH,
        Z_BOTTOM_PANEL + DOOR_GAP,
        DOOR_W,
        DOOR_DEPTH,
        LOWER_DOOR_H,
    )
    parts.append(
        ("H10", "Frente", "Puerta_Inferior", 1, DOOR_W, LOWER_DOOR_H, TH, "4 cantos")
    )

    add_part(
        doc,
        "H11_Puerta_Superior",
        DOOR_GAP,
        -DOOR_DEPTH,
        Z_MICRO_TOP + DOOR_GAP,
        DOOR_W,
        DOOR_DEPTH,
        UPPER_DOOR_H,
    )
    parts.append(
        ("H11", "Frente", "Puerta_Superior", 1, DOOR_W, UPPER_DOOR_H, TH, "4 cantos")
    )

    doc.recompute()

    # Exportes
    fcstd_path = os.path.join(here, "columna_horno_micro.FCStd")
    step_path = os.path.join(here, "columna_horno_micro.step")
    bom_path = os.path.join(here, "columna_horno_micro_bom.csv")

    doc.saveAs(fcstd_path)

    objs = [o for o in doc.Objects if hasattr(o, "Shape")]
    Part.export(objs, step_path)

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
    print(f"- Ancho exterior: {W}")
    print(f"- Profundidad exterior: {DEPTH}")
    print(f"- Altura total: {HEIGHT_TOTAL}")
    print(
        f"- Hueco horno visible: {OVEN_OPENING_W} x {OVEN_OPENING_VISIBLE_H}, inicia en Z={OVEN_Z_START}"
    )
    print(
        f"- Hueco horno interno: {OVEN_OPENING_W} x {OVEN_OPENING_VISIBLE_H + OVEN_EXTRA_INTERNAL_H}"
    )
    print(
        f"- Hueco micro: {OVEN_OPENING_W} x {MICRO_OPENING_H}, inicia en Z={Z_MICRO_BASE}"
    )
    print(f"- Faja frontal entre huecos: {SEPARATOR_FRONT_H}")
    print(f"- Compartimento superior util: {TOP_CLEAR_H}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Genera bajo mesada BA en FreeCAD.

Salida:
  - bajo_BA.FCStd
  - bajo_BA.step
  - bajo_BA_bom.csv
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
DRAWER_BOTTOM_TH = 6.0

WIDTH = 903.0
DEPTH = 600.0
CAB_H = 870.0
TOE_H = 80.0
COUNTER_TH = 30.0

TOP_FRONT_H = 130.0
TOP_SUPPORT_D = 200.0
SLIDE_CLR = 12.5
DRAWER_DEPTH = 500.0
GOLA_H = 25.0
GOLA_D = 20.0
LEG_W = 40.0
LEG_D = 40.0
LEG_INSET = 30.0

# Luces/frentes para continuidad visual con BB
GRID_GAP = 4.0
CENTER_GAP = GRID_GAP
OUTER_OVERLAY_L = TH / 2.0
SEAM_INSET_R = GRID_GAP / 2.0  # deja 4 mm de luz total con BB (2 + 2)
ROW_GAP = GRID_GAP

# Cotas en Z
Z_BOTTOM = TOE_H
Z_BOTTOM_TOP = Z_BOTTOM + TH
Z_TOP = CAB_H
Z_TOP_SUPPORT = Z_TOP - TH
SIDE_H = Z_TOP_SUPPORT - Z_BOTTOM_TOP

# Plataforma separadora top row
Z_TOPROW_SHELF = Z_TOP - TOP_FRONT_H - TH

W_INT = WIDTH - 2 * TH
D_INT = DEPTH - BACK_TH

# Unico frente falso superior bajo anafe (ancho completo de BA, misma grilla que frentes inferiores).
TOP_FALSE_X = OUTER_OVERLAY_L
TOP_FALSE_W = WIDTH - OUTER_OVERLAY_L - SEAM_INSET_R
TOP_FRONT_Z = Z_TOP_SUPPORT - TOP_FRONT_H

# Filas inferiores (2 frentes grandes de todo el ancho, continuidad con BB)
# Se deja luz inferior igual al GRID_GAP para completar el efecto de grilla.
ROW3_Z = Z_BOTTOM + ROW_GAP
TOTAL_FACE_H = Z_TOP_SUPPORT - ROW3_Z
MID_BOT_H = (TOTAL_FACE_H - TOP_FRONT_H - 2.0 * ROW_GAP) / 2.0
ROW2_Z = ROW3_Z + MID_BOT_H + ROW_GAP
ROW1_Z = ROW2_Z + MID_BOT_H + ROW_GAP

# Estante interior BA (mitad del hueco inferior)
LOWER_SHELF_Z = Z_BOTTOM_TOP + (ROW2_Z - Z_BOTTOM_TOP - TH) / 2.0
MID_LINE_Z = ROW2_Z


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_drawer(doc, prefix, x, y, z, outer_w, depth, box_h, parts, code_base):
    side_t = TH
    front_back_w = outer_w - 2 * side_t

    add_box(doc, f"{prefix}_Lateral_Izq", x, y, z, side_t, depth, box_h)
    add_box(
        doc, f"{prefix}_Lateral_Der", x + outer_w - side_t, y, z, side_t, depth, box_h
    )
    add_box(doc, f"{prefix}_Frente_Caja", x + side_t, y, z, front_back_w, side_t, box_h)
    add_box(
        doc,
        f"{prefix}_Trasera_Caja",
        x + side_t,
        y + depth - side_t,
        z,
        front_back_w,
        side_t,
        box_h,
    )
    add_box(
        doc,
        f"{prefix}_Fondo_6mm",
        x,
        y,
        z - DRAWER_BOTTOM_TH,
        outer_w,
        depth,
        DRAWER_BOTTOM_TH,
    )

    parts.extend(
        [
            (
                f"{code_base}a",
                "Cajon",
                f"{prefix}_Lateral",
                2,
                depth,
                box_h,
                side_t,
                "Sin canto",
            ),
            (
                f"{code_base}b",
                "Cajon",
                f"{prefix}_Frente_Trasera",
                2,
                front_back_w,
                box_h,
                side_t,
                "Sin canto",
            ),
            (
                f"{code_base}c",
                "Cajon",
                f"{prefix}_Fondo_6mm",
                1,
                outer_w,
                depth,
                DRAWER_BOTTOM_TH,
                "Fondo clavado pasante",
            ),
        ]
    )


def main():
    script_path = globals().get("__file__")
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()
    doc = App.newDocument("BajoBA")
    parts = []

    # Casco
    add_box(doc, "BA1_Lateral_Izq", 0, 0, Z_BOTTOM_TOP, TH, DEPTH, SIDE_H)
    parts.append(("BA1", "Casco", "Lateral_Izq", 1, SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "BA2_Lateral_Der", WIDTH - TH, 0, Z_BOTTOM_TOP, TH, DEPTH, SIDE_H)
    parts.append(("BA2", "Casco", "Lateral_Der", 1, SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "BA3_Piso_Pasante", 0, 0, Z_BOTTOM, WIDTH, DEPTH, TH)
    parts.append(("BA3", "Casco", "Piso_Pasante", 1, WIDTH, DEPTH, TH, "Canto frente"))

    # Patas 80 mm
    leg_pos = [
        (LEG_INSET, LEG_INSET),
        (WIDTH - LEG_INSET - LEG_W, LEG_INSET),
        (LEG_INSET, DEPTH - LEG_INSET - LEG_D),
        (WIDTH - LEG_INSET - LEG_W, DEPTH - LEG_INSET - LEG_D),
    ]
    for i, (lx, ly) in enumerate(leg_pos, start=1):
        add_box(doc, f"BA3L_Pata_{i}", lx, ly, 0.0, LEG_W, LEG_D, TOE_H)
    parts.append(("BA3L", "Herraje", "Pata_80", 4, LEG_W, LEG_D, TOE_H, "PVC/Aluminio"))

    # Fondo 3 mm (oculto)
    add_box(
        doc, "BA4_Fondo_3mm", TH, DEPTH - BACK_TH, Z_BOTTOM_TOP, W_INT, BACK_TH, SIDE_H
    )
    parts.append(("BA4", "Casco", "Fondo_3mm", 1, W_INT, SIDE_H, BACK_TH, "Sin canto"))

    # Soportes superiores (frente y fondo, 200 mm profundidad)
    add_box(
        doc,
        "BA5_Soporte_Superior_Frente",
        0,
        0,
        Z_TOP_SUPPORT,
        WIDTH,
        TOP_SUPPORT_D,
        TH,
    )
    parts.append(
        (
            "BA5",
            "Casco",
            "Soporte_Sup_Frente",
            1,
            WIDTH,
            TOP_SUPPORT_D,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "BA6_Soporte_Superior_Fondo",
        0,
        DEPTH - TOP_SUPPORT_D,
        Z_TOP_SUPPORT,
        WIDTH,
        TOP_SUPPORT_D,
        TH,
    )
    parts.append(
        ("BA6", "Casco", "Soporte_Sup_Fondo", 1, WIDTH, TOP_SUPPORT_D, TH, "Sin canto")
    )

    # Repisa separadora de fila superior
    add_box(doc, "BA7_Repisa_Separadora", TH, 0, Z_TOPROW_SHELF, W_INT, DEPTH, TH)
    parts.append(
        ("BA7", "Casco", "Repisa_Separadora", 1, W_INT, DEPTH, TH, "Canto frente")
    )

    # Estante interior inferior (todo el ancho)
    add_box(doc, "BA8_Estante_Inferior", TH, 0, LOWER_SHELF_Z, W_INT, DEPTH, TH)
    parts.append(
        ("BA8", "Interior", "Estante_Inferior", 1, W_INT, DEPTH, TH, "Canto frente")
    )

    # Unico frente superior falso bajo anafe
    add_box(
        doc,
        "BA9_Frente_Falso_Sup",
        TOP_FALSE_X,
        -TH,
        TOP_FRONT_Z,
        TOP_FALSE_W,
        TH,
        TOP_FRONT_H,
    )
    parts.append(
        (
            "BA9",
            "Frente",
            "Frente_Falso_Sup",
            1,
            TOP_FALSE_W,
            TOP_FRONT_H,
            TH,
            "4 cantos",
        )
    )

    # Dos frentes grandes de ancho completo (medio e inferior)
    add_box(
        doc,
        "BA10_Frente_Mid",
        OUTER_OVERLAY_L,
        -TH,
        ROW2_Z,
        WIDTH - OUTER_OVERLAY_L - SEAM_INSET_R,
        TH,
        MID_BOT_H,
    )
    parts.append(
        (
            "BA10",
            "Frente",
            "Frente_Mid_Ancho_Completo",
            1,
            WIDTH - OUTER_OVERLAY_L - SEAM_INSET_R,
            MID_BOT_H,
            TH,
            "4 cantos",
        )
    )

    add_box(
        doc,
        "BA11_Frente_Bot",
        OUTER_OVERLAY_L,
        -TH,
        ROW3_Z,
        WIDTH - OUTER_OVERLAY_L - SEAM_INSET_R,
        TH,
        MID_BOT_H,
    )
    parts.append(
        (
            "BA11",
            "Frente",
            "Frente_Bot_Ancho_Completo",
            1,
            WIDTH - OUTER_OVERLAY_L - SEAM_INSET_R,
            MID_BOT_H,
            TH,
            "4 cantos",
        )
    )

    # Perfiles gola
    add_box(
        doc,
        "BA12_Gola_C_Superior",
        0,
        -GOLA_D,
        ROW1_Z - ROW_GAP,
        WIDTH,
        GOLA_D,
        GOLA_H,
    )
    parts.append(
        ("BA12", "Herraje", "Gola_C_Superior", 1, WIDTH, GOLA_H, GOLA_D, "Aluminio")
    )

    add_box(doc, "BA13_Gola_J_Media", 0, -GOLA_D, MID_LINE_Z, WIDTH, GOLA_D, GOLA_H)
    parts.append(
        ("BA13", "Herraje", "Gola_J_Media", 1, WIDTH, GOLA_H, GOLA_D, "Aluminio")
    )

    doc.recompute()

    if GUI_AVAILABLE:
        for obj in doc.Objects:
            vo = getattr(obj, "ViewObject", None)
            if vo is not None:
                try:
                    vo.Visibility = True
                    if "Fondo_3mm" in obj.Name:
                        vo.Visibility = False
                except Exception:
                    pass

    fcstd = os.path.join(here, "bajo_BA.FCStd")
    step = os.path.join(here, "bajo_BA.step")
    bom = os.path.join(here, "bajo_BA_bom.csv")

    doc.saveAs(fcstd)
    Part.export([o for o in doc.Objects if hasattr(o, "Shape")], step)

    with open(bom, "w", newline="", encoding="utf-8") as f:
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
        for r in parts:
            w.writerow(r)

    print("Modelo generado:")
    print("-", fcstd)
    print("-", step)
    print("-", bom)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Genera bajo mesada BB en FreeCAD.

Salida:
  - bajo_BB.FCStd
  - bajo_BB.step
  - bajo_BB_bom.csv
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

WIDTH = 1355.0
DEPTH = 600.0
CAB_H = 870.0
TOE_H = 80.0

TOP_FRONT_H = 130.0
TOP_SUPPORT_D = 200.0
SLIDE_CLR = 12.5
DRAWER_DEPTH = 500.0
OPEN_DRAWER_OFFSET = 0.0  # frente enrasado para verificar grilla
GOLA_H = 25.0
GOLA_D = 20.0
LEG_W = 40.0
LEG_D = 40.0
LEG_INSET = 30.0

# Luces/frentes para continuidad visual con BA
GRID_GAP = 4.0
CENTER_GAP = GRID_GAP
SEAM_INSET_L = GRID_GAP / 2.0  # deja 4 mm de luz total con BA (2 + 2)
OUTER_OVERLAY_R = TH / 2.0
ROW_GAP = GRID_GAP

Z_BOTTOM = TOE_H
Z_BOTTOM_TOP = Z_BOTTOM + TH
Z_TOP = CAB_H
Z_TOP_SUPPORT = Z_TOP - TH
SIDE_H = Z_TOP_SUPPORT - Z_BOTTOM_TOP

# Fajas/frentes (3 filas), apoyando en canto inferior del soporte superior.
# Se deja luz inferior igual al GRID_GAP para completar el efecto de grilla.
ROW3_Z = Z_BOTTOM + ROW_GAP
TOTAL_FACE_H = Z_TOP_SUPPORT - ROW3_Z
MID_BOT_H = (TOTAL_FACE_H - TOP_FRONT_H - 2.0 * ROW_GAP) / 2.0
ROW2_Z = ROW3_Z + MID_BOT_H + ROW_GAP
ROW1_Z = ROW2_Z + MID_BOT_H + ROW_GAP

W_INT = WIDTH - 2 * TH
D_INT = DEPTH - BACK_TH
COL_INT_W = (W_INT - TH) / 2.0
FRONT_W = (WIDTH - SEAM_INSET_L - OUTER_OVERLAY_R - CENTER_GAP) / 2.0

# Caja cajon por columna
DRAWER_OUT_W = COL_INT_W - 2 * SLIDE_CLR
LEFT_COL_X = TH
RIGHT_COL_X = TH + COL_INT_W + TH

TOP_BOX_H = 80.0
LOW_BOX_H = 180.0


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
    doc = App.newDocument("BajoBB")
    parts = []

    # Casco
    add_box(doc, "BB1_Lateral_Izq", 0, 0, Z_BOTTOM_TOP, TH, DEPTH, SIDE_H)
    parts.append(("BB1", "Casco", "Lateral_Izq", 1, SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "BB2_Lateral_Der", WIDTH - TH, 0, Z_BOTTOM_TOP, TH, DEPTH, SIDE_H)
    parts.append(("BB2", "Casco", "Lateral_Der", 1, SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "BB3_Piso_Pasante", 0, 0, Z_BOTTOM, WIDTH, DEPTH, TH)
    parts.append(("BB3", "Casco", "Piso_Pasante", 1, WIDTH, DEPTH, TH, "Canto frente"))

    # Patas 80 mm
    leg_pos = [
        (LEG_INSET, LEG_INSET),
        (WIDTH - LEG_INSET - LEG_W, LEG_INSET),
        (LEG_INSET, DEPTH - LEG_INSET - LEG_D),
        (WIDTH - LEG_INSET - LEG_W, DEPTH - LEG_INSET - LEG_D),
    ]
    for i, (lx, ly) in enumerate(leg_pos, start=1):
        add_box(doc, f"BB3L_Pata_{i}", lx, ly, 0.0, LEG_W, LEG_D, TOE_H)
    parts.append(("BB3L", "Herraje", "Pata_80", 4, LEG_W, LEG_D, TOE_H, "PVC/Aluminio"))

    add_box(
        doc, "BB4_Fondo_3mm", TH, DEPTH - BACK_TH, Z_BOTTOM_TOP, W_INT, BACK_TH, SIDE_H
    )
    parts.append(("BB4", "Casco", "Fondo_3mm", 1, W_INT, SIDE_H, BACK_TH, "Sin canto"))

    add_box(
        doc,
        "BB5_Soporte_Superior_Frente",
        0,
        0,
        Z_TOP_SUPPORT,
        WIDTH,
        TOP_SUPPORT_D,
        TH,
    )
    parts.append(
        (
            "BB5",
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
        "BB6_Soporte_Superior_Fondo",
        0,
        DEPTH - TOP_SUPPORT_D,
        Z_TOP_SUPPORT,
        WIDTH,
        TOP_SUPPORT_D,
        TH,
    )
    parts.append(
        ("BB6", "Casco", "Soporte_Sup_Fondo", 1, WIDTH, TOP_SUPPORT_D, TH, "Sin canto")
    )

    # Division central para dos columnas de cajones
    add_box(
        doc,
        "BB7_Divisor_Central",
        TH + COL_INT_W,
        TH,
        Z_BOTTOM_TOP,
        TH,
        D_INT - TH,
        SIDE_H,
    )
    parts.append(
        ("BB7", "Interior", "Divisor_Central", 1, SIDE_H, D_INT - TH, TH, "Sin canto")
    )

    # Frentes (2 columnas x 3 filas = 6 cajones)
    x_l = SEAM_INSET_L
    x_r = x_l + FRONT_W + CENTER_GAP

    add_box(doc, "BB8_Frente_Top_Izq", x_l, -TH, ROW1_Z, FRONT_W, TH, TOP_FRONT_H)
    add_box(doc, "BB9_Frente_Top_Der", x_r, -TH, ROW1_Z, FRONT_W, TH, TOP_FRONT_H)
    parts.append(
        ("BB8", "Frente", "Frente_Top", 2, FRONT_W, TOP_FRONT_H, TH, "4 cantos")
    )

    add_box(doc, "BB10_Frente_Mid_Izq", x_l, -TH, ROW2_Z, FRONT_W, TH, MID_BOT_H)
    add_box(doc, "BB11_Frente_Mid_Der", x_r, -TH, ROW2_Z, FRONT_W, TH, MID_BOT_H)
    parts.append(
        ("BB10", "Frente", "Frente_Mid", 2, FRONT_W, MID_BOT_H, TH, "4 cantos")
    )

    add_box(doc, "BB12_Frente_Bot_Izq", x_l, -TH, ROW3_Z, FRONT_W, TH, MID_BOT_H)
    add_box(doc, "BB13_Frente_Bot_Der", x_r, -TH, ROW3_Z, FRONT_W, TH, MID_BOT_H)
    parts.append(
        ("BB12", "Frente", "Frente_Bot", 2, FRONT_W, MID_BOT_H, TH, "4 cantos")
    )

    # Cajas de cajones (6 unidades)
    y_draw = TH
    add_drawer(
        doc,
        "BB14_Caja_Top_Izq",
        LEFT_COL_X + SLIDE_CLR,
        y_draw,
        ROW1_Z + TH,
        DRAWER_OUT_W,
        DRAWER_DEPTH,
        TOP_BOX_H,
        parts,
        "BB14",
    )
    add_drawer(
        doc,
        "BB15_Caja_Top_Der",
        RIGHT_COL_X + SLIDE_CLR,
        y_draw,
        ROW1_Z + TH,
        DRAWER_OUT_W,
        DRAWER_DEPTH,
        TOP_BOX_H,
        parts,
        "BB15",
    )

    add_drawer(
        doc,
        "BB16_Caja_Mid_Izq",
        LEFT_COL_X + SLIDE_CLR,
        y_draw,
        ROW2_Z + TH,
        DRAWER_OUT_W,
        DRAWER_DEPTH,
        LOW_BOX_H,
        parts,
        "BB16",
    )
    add_drawer(
        doc,
        "BB17_Caja_Mid_Der",
        RIGHT_COL_X + SLIDE_CLR,
        y_draw,
        ROW2_Z + TH,
        DRAWER_OUT_W,
        DRAWER_DEPTH,
        LOW_BOX_H,
        parts,
        "BB17",
    )

    add_drawer(
        doc,
        "BB18_Caja_Bot_Izq",
        LEFT_COL_X + SLIDE_CLR,
        y_draw,
        ROW3_Z + TH,
        DRAWER_OUT_W,
        DRAWER_DEPTH,
        LOW_BOX_H,
        parts,
        "BB18",
    )
    add_drawer(
        doc,
        "BB19_Caja_Bot_Der",
        RIGHT_COL_X + SLIDE_CLR,
        y_draw,
        ROW3_Z + TH,
        DRAWER_OUT_W,
        DRAWER_DEPTH,
        LOW_BOX_H,
        parts,
        "BB19",
    )

    # Perfiles gola
    add_box(
        doc,
        "BB20_Gola_C_Superior",
        0,
        -GOLA_D,
        ROW1_Z - ROW_GAP,
        WIDTH,
        GOLA_D,
        GOLA_H,
    )
    parts.append(
        ("BB20", "Herraje", "Gola_C_Superior", 1, WIDTH, GOLA_H, GOLA_D, "Aluminio")
    )

    add_box(doc, "BB21_Gola_J_Media", 0, -GOLA_D, ROW2_Z, WIDTH, GOLA_D, GOLA_H)
    parts.append(
        ("BB21", "Herraje", "Gola_J_Media", 1, WIDTH, GOLA_H, GOLA_D, "Aluminio")
    )

    # Visual: dejar un cajon apenas abierto (fila media izquierda).
    for obj in doc.Objects:
        if obj.Name == "BB10_Frente_Mid_Izq" or obj.Name.startswith(
            "BB16_Caja_Mid_Izq_"
        ):
            obj.Placement.Base.y -= OPEN_DRAWER_OFFSET

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

    fcstd = os.path.join(here, "bajo_BB.FCStd")
    step = os.path.join(here, "bajo_BB.step")
    bom = os.path.join(here, "bajo_BB_bom.csv")

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

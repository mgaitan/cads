#!/usr/bin/env python3
"""Genera mueble F (Fridge + modular posterior) en FreeCAD."""

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
MIN_STRIP = 50.0
WIDTH = 780.0
DEPTH_TOTAL = 950.0
DEPTH_MOD = 300.0
BODY_HEIGHT = 2260.0
TOP_DRAWER_FLOATING_W = 1540.0 + 820.0
TOP_DRAWER_TOTAL_W = WIDTH + TOP_DRAWER_FLOATING_W
TOP_DRAWER_D = 300.0
TOP_DRAWER_H = 140.0
HEIGHT_TOTAL = BODY_HEIGHT + TOP_DRAWER_H
TOE_H = 80.0
SIDE_TOP_RISE = 70.0

FRIDGE_ROOF_Z = 1800.0
CENTER_GAP = 2.0
SIDE_FRAME_VISIBLE = 20.0
DOOR_LIGHT_BOTTOM = 4.0
DOOR_OVERLAP_TOP = 9.0

VISIBLE_SETBACK_X = 8.0
VISIBLE_SETBACK_Y = 20.0

VENT_W = 300.0
VENT_H = 80.0
VENT_Z = 200.0

LEG_W = 40.0
LEG_D = 40.0
LEG_INSET = 30.0

W_INT = WIDTH - 2 * TH
W_INT_REGR = WIDTH - 4 * TH
SIDE_H = BODY_HEIGHT - TOE_H
SIDE_PANEL_H = SIDE_H + (TOP_DRAWER_H - 3.0 * TH - 4.0)
LEFT_SIDE_PANEL_H = HEIGHT_TOTAL - TOE_H
Z_BOTTOM = TOE_H
Z_TOP = BODY_HEIGHT
Z_SIDE = TOE_H
MOD_BACK_Y = DEPTH_MOD - TH
FRIDGE_DEPTH = DEPTH_TOTAL - DEPTH_MOD
MOD_INT_D = DEPTH_MOD - TH
MOD_X = 2.0 * TH
MOD_X_VIS = MOD_X + VISIBLE_SETBACK_X
W_VIS = W_INT_REGR - 2.0 * VISIBLE_SETBACK_X

DOOR_W = (WIDTH - 2.0 * SIDE_FRAME_VISIBLE - CENTER_GAP) / 2.0
DOOR_X1 = SIDE_FRAME_VISIBLE
DOOR_X2 = DOOR_X1 + DOOR_W + CENTER_GAP
DOOR_Y = -TH
DOOR_Z = Z_BOTTOM + DOOR_LIGHT_BOTTOM

# Grilla vertical: dividir altura util del casco en 5.
# 2/5 hasta el estante fijo F9 y 3/5 en el tramo superior.
GRID = (Z_TOP - Z_BOTTOM) / 5.0
SHELF_Z_1 = Z_BOTTOM + 1.0 * GRID
SHELF_Z_2 = Z_BOTTOM + 2.0 * GRID  # fijo F9

# Reparto visual uniforme de los 3 huecos superiores hasta el piso del cajon superior.
Z_LOWER = SHELF_Z_2 + 2.0 * TH  # cara superior de F20
Z_UPPER = Z_TOP
OPEN_UP = (Z_UPPER - Z_LOWER - 4.0 * TH) / 3.0
SHELF_Z_3 = Z_LOWER + OPEN_UP + TH
SHELF_Z_4 = SHELF_Z_3 + OPEN_UP + 2.0 * TH

# Las puertas inferiores deben superponer sobre F9
DOOR_H = (SHELF_Z_2 + DOOR_OVERLAP_TOP) - DOOR_Z

REGRUESO_LONG_H = SIDE_H - TH  # llega hasta apoyar bajo el cajon superior
REGRUESO_LONG_Z = Z_SIDE + TH


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_box_with_rect_cut(doc, name, x, y, z, dx, dy, dz, cut):
    shape = Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
    cx, cy, cz, cdx, cdy, cdz = cut
    cut_box = Part.makeBox(cdx, cdy, cdz, App.Vector(cx, cy, cz))
    shape = shape.cut(cut_box)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def add_box_with_rect_cuts(doc, name, x, y, z, dx, dy, dz, cuts):
    shape = Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
    for cx, cy, cz, cdx, cdy, cdz in cuts:
        cut_box = Part.makeBox(cdx, cdy, cdz, App.Vector(cx, cy, cz))
        shape = shape.cut(cut_box)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def add_box_with_cyl_cuts(doc, name, x, y, z, dx, dy, dz, holes):
    shape = Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
    for hx, hy, hz, radius, height in holes:
        cyl = Part.makeCylinder(radius, height, App.Vector(hx, hy, hz))
        shape = shape.cut(cyl)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
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

    doc = App.newDocument("FridgeF")
    parts = []

    vent_y = (DEPTH_TOTAL - VENT_W) / 2.0
    side_top_notch = (-1.0, 0.0, BODY_HEIGHT, TH + 2.0, DEPTH_MOD, SIDE_TOP_RISE)
    vent_cut = (-1.0, vent_y, VENT_Z, TH + 2.0, VENT_W, VENT_H)
    add_box_with_rect_cut(
        doc,
        "F1_Lateral_Izq",
        0,
        0,
        Z_SIDE,
        TH,
        DEPTH_TOTAL,
        LEFT_SIDE_PANEL_H,
        vent_cut,
    )
    parts.append(
        (
            "F1",
            "Casco",
            "Lateral_Izq",
            1,
            LEFT_SIDE_PANEL_H,
            DEPTH_TOTAL,
            TH,
            "Crudo (cinta 36mm en obra)",
        )
    )

    add_box_with_rect_cuts(
        doc,
        "F2_Lateral_Der",
        WIDTH - TH,
        0,
        Z_SIDE,
        TH,
        DEPTH_TOTAL,
        SIDE_PANEL_H,
        [
            (
                WIDTH - TH - 1.0,
                0.0,
                BODY_HEIGHT,
                TH + 2.0,
                DEPTH_MOD,
                (Z_SIDE + SIDE_PANEL_H) - BODY_HEIGHT,
            )
        ],
    )
    parts.append(
        (
            "F2",
            "Casco",
            "Lateral_Der",
            1,
            SIDE_PANEL_H,
            DEPTH_TOTAL,
            TH,
            "Crudo (cinta 36mm en obra)",
        )
    )

    add_box(doc, "F3_Piso_Modular", TH, 0, Z_BOTTOM, W_INT, DEPTH_MOD, TH)
    parts.append(
        ("F3", "Casco", "Piso_Modular", 1, W_INT, DEPTH_MOD, TH, "Canto frente")
    )

    leg_pos = [
        (0.0, LEG_INSET),
        (WIDTH - LEG_W, LEG_INSET),
        ((WIDTH - LEG_W) / 2.0, MOD_BACK_Y - LEG_D / 2.0),
        (0.0, DEPTH_TOTAL - LEG_INSET - LEG_D),
        (WIDTH - LEG_W, DEPTH_TOTAL - LEG_INSET - LEG_D),
    ]
    for i, (lx, ly) in enumerate(leg_pos, start=1):
        add_box(doc, f"F3L_Pata_{i}", lx, ly, 0.0, LEG_W, LEG_D, TOE_H)
    parts.append(("F3L", "Herraje", "Pata_80", 5, LEG_W, LEG_D, TOE_H, "PVC/Aluminio"))

    add_box(doc, "F5_Panel_Divisor_Prof", TH, MOD_BACK_Y, Z_SIDE, W_INT, TH, SIDE_H)
    parts.append(
        ("F5", "Division", "Panel_Divisor_Prof", 1, W_INT, SIDE_H, TH, "Sin canto")
    )

    # Regruesos largos continuos en laterales interiores (menos 36 mm de largo)
    add_box(
        doc,
        "F14_Regrueso_Vis_Izq",
        TH,
        0,
        REGRUESO_LONG_Z,
        TH,
        MOD_INT_D,
        REGRUESO_LONG_H,
    )
    parts.append(
        (
            "F14",
            "Regrueso",
            "Regrueso_Vis_Izq",
            1,
            REGRUESO_LONG_H,
            MOD_INT_D,
            TH,
            "Crudo (cinta 36mm en obra)",
        )
    )

    add_box(
        doc,
        "F15_Regrueso_Vis_Der",
        WIDTH - 2.0 * TH,
        0,
        REGRUESO_LONG_Z,
        TH,
        MOD_INT_D,
        REGRUESO_LONG_H,
    )
    parts.append(
        (
            "F15",
            "Regrueso",
            "Regrueso_Vis_Der",
            1,
            REGRUESO_LONG_H,
            MOD_INT_D,
            TH,
            "Crudo (cinta 36mm en obra)",
        )
    )

    add_box(
        doc,
        "F6_Techo_Heladera_1800",
        TH,
        DEPTH_MOD,
        FRIDGE_ROOF_Z,
        W_INT,
        FRIDGE_DEPTH,
        TH,
    )
    parts.append(
        (
            "F6",
            "Horizontal",
            "Techo_Heladera_1800",
            1,
            W_INT,
            FRIDGE_DEPTH,
            TH,
            "Canto frente",
        )
    )

    # Estante bajo movil (unico)
    add_box(doc, "F7_Estante_Bajo_Reg", MOD_X, 0, SHELF_Z_1, W_INT_REGR, MOD_INT_D, TH)
    parts.append(
        (
            "F7",
            "Estante_Regulable",
            "Estante_Bajo",
            1,
            W_INT_REGR,
            MOD_INT_D,
            TH,
            "Canto frente",
        )
    )

    # Estante fijo por adentro (no pasante)
    add_box(
        doc,
        "F9_Estante_Fijo_Interior",
        MOD_X,
        0,
        SHELF_Z_2 + TH,
        W_INT_REGR,
        MOD_INT_D,
        TH,
    )
    parts.append(
        (
            "F9",
            "Horizontal",
            "Estante_Fijo_Interior",
            1,
            W_INT_REGR,
            MOD_INT_D,
            TH,
            "Canto frente",
        )
    )

    # Engroses de marco superior/inferior del sector visible
    add_box(
        doc,
        "F20_Regrueso_Sobre_F9",
        MOD_X,
        0,
        SHELF_Z_2,
        W_INT_REGR,
        MIN_STRIP,
        TH,
    )
    parts.append(
        (
            "F20",
            "Regrueso",
            "Regrueso_Sobre_F9",
            1,
            W_INT_REGR,
            MIN_STRIP,
            TH,
            "Canto frente",
        )
    )

    # Estantes moviles superiores (visibles) + regrueso frontal
    add_box(
        doc,
        "F10_Estante_Sup_Reg_1",
        MOD_X_VIS,
        VISIBLE_SETBACK_Y,
        SHELF_Z_3,
        W_VIS,
        MOD_INT_D - VISIBLE_SETBACK_Y,
        TH,
    )
    parts.append(
        (
            "F10",
            "Estante_Regulable",
            "Estante_Sup_1",
            1,
            W_VIS,
            MOD_INT_D - VISIBLE_SETBACK_Y,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "F16_Regrueso_Front_Estante_Sup_1",
        MOD_X_VIS,
        VISIBLE_SETBACK_Y,
        SHELF_Z_3 - TH,
        W_VIS,
        MIN_STRIP,
        TH,
    )
    parts.append(
        (
            "F16",
            "Regrueso",
            "Regrueso_Front_Estante_Sup_1",
            1,
            W_VIS,
            MIN_STRIP,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "F11_Estante_Sup_Reg_2",
        MOD_X_VIS,
        VISIBLE_SETBACK_Y,
        SHELF_Z_4,
        W_VIS,
        MOD_INT_D - VISIBLE_SETBACK_Y,
        TH,
    )
    parts.append(
        (
            "F11",
            "Estante_Regulable",
            "Estante_Sup_2",
            1,
            W_VIS,
            MOD_INT_D - VISIBLE_SETBACK_Y,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "F17_Regrueso_Front_Estante_Sup_2",
        MOD_X_VIS,
        VISIBLE_SETBACK_Y,
        SHELF_Z_4 - TH,
        W_VIS,
        MIN_STRIP,
        TH,
    )
    parts.append(
        (
            "F17",
            "Regrueso",
            "Regrueso_Front_Estante_Sup_2",
            1,
            W_VIS,
            MIN_STRIP,
            TH,
            "Canto frente",
        )
    )

    add_box(doc, "F12_Puerta_Mod_Izq", DOOR_X1, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("F12", "Frente", "Puerta_Mod_Izq", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    add_box(doc, "F13_Puerta_Mod_Der", DOOR_X2, DOOR_Y, DOOR_Z, DOOR_W, TH, DOOR_H)
    parts.append(("F13", "Frente", "Puerta_Mod_Der", 1, DOOR_W, DOOR_H, TH, "4 cantos"))

    # Cajon superior corrido (en L invertida), toma el techo del sector modular y continua sobre isla.
    top_z0 = BODY_HEIGHT
    inner_top_w = TOP_DRAWER_TOTAL_W - 2.0 * TH
    inner_top_d = TOP_DRAWER_D - 2.0 * TH

    add_box(
        doc,
        "F23_Cajon_Sup_Lateral_Der",
        TOP_DRAWER_TOTAL_W - 2.0 * TH,
        TH,
        top_z0 + TH,
        TH,
        TOP_DRAWER_D - 2.0 * TH,
        TOP_DRAWER_H - TH,
    )
    parts.append(
        (
            "F23",
            "Cajon_Sup",
            "Lateral_Der",
            1,
            TOP_DRAWER_H - TH,
            TOP_DRAWER_D - 2.0 * TH,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "F24_Cajon_Sup_Trasera",
        TH,
        TOP_DRAWER_D - TH,
        top_z0,
        TOP_DRAWER_TOTAL_W - 2.0 * TH,
        TH,
        TOP_DRAWER_H - 3.0 * TH - 4.0,
    )
    parts.append(
        (
            "F24",
            "Cajon_Sup",
            "Trasera",
            1,
            TOP_DRAWER_TOTAL_W - 2.0 * TH,
            TOP_DRAWER_H - 3.0 * TH - 4.0,
            TH,
            "Sin canto",
        )
    )

    floating_start_x = WIDTH
    # Los spots mantienen su posicion absoluta respecto del origen historico del tramo flotante.
    floating_step = 1540.0 / 4.0
    spot_centers_x = [
        floating_start_x + floating_step,
        floating_start_x + 2.0 * floating_step,
        floating_start_x + 3.0 * floating_step,
    ]
    spot_center_y = TOP_DRAWER_D / 2.0
    spot_holes = [
        (cx, spot_center_y, top_z0 - 1.0, 30.0, TH + 2.0) for cx in spot_centers_x
    ]
    add_box_with_cyl_cuts(
        doc,
        "F25_Cajon_Sup_Piso",
        TH,
        TH,
        top_z0,
        inner_top_w,
        inner_top_d,
        TH,
        spot_holes,
    )
    parts.append(
        (
            "F25",
            "Cajon_Sup",
            "Piso_Interior_3xØ60",
            1,
            inner_top_w,
            inner_top_d,
            TH,
            "Sin canto",
        )
    )

    add_box(
        doc,
        "F26_Cajon_Sup_Frente",
        TH,
        0,
        top_z0,
        TOP_DRAWER_TOTAL_W - 2.0 * TH,
        TH,
        TOP_DRAWER_H,
    )
    parts.append(
        (
            "F26",
            "Frente",
            "Frente_Cajon_Superior",
            1,
            TOP_DRAWER_TOTAL_W - 2.0 * TH,
            TOP_DRAWER_H,
            TH,
            "4 cantos",
        )
    )

    doc.recompute()

    if GUI_AVAILABLE:
        for obj in doc.Objects:
            vo = getattr(obj, "ViewObject", None)
            if vo is not None:
                try:
                    vo.Visibility = True
                except Exception:
                    pass

    fcstd = out_fcstd_dir / "F.FCStd"
    step = out_step_dir / "F.step"
    bom = out_bom_dir / "F_bom.csv"

    doc.saveAs(str(fcstd))
    Part.export([o for o in doc.Objects if hasattr(o, "Shape")], str(step))

    rows = add_bom_metadata(parts)
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
                "ml_gola",
                "bisagras_cazoleta",
            ]
        )
        for row in rows:
            w.writerow(row)

    print("Modelo generado:")
    print("-", fcstd)
    print("-", step)
    print("-", bom)
    print("\nResumen de cotas clave (mm):")
    print(f"- Ancho: {WIDTH}")
    print(f"- Profundidad total: {DEPTH_TOTAL}")
    print(f"- Profundidad modulo: {DEPTH_MOD}")
    print(f"- Altura cuerpo: {BODY_HEIGHT}")
    print(f"- Cajon superior: {TOP_DRAWER_TOTAL_W} x {TOP_DRAWER_D} x {TOP_DRAWER_H}")
    print(f"- Altura total: {HEIGHT_TOTAL}")
    print(f"- Grilla (1/5): {GRID}")
    print(f"- Puertas modular: {DOOR_W} x {DOOR_H}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Genera mueble I (bajo mesada isla con nicho lavavajillas) en FreeCAD.

Salida:
  - models/fcstd/I.FCStd
  - models/step/I.step
  - bom/I_bom.csv
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
BACK_TH = 6.0
DRAWER_BOTTOM_TH = 6.0

WIDTH = 1540.0
DEPTH = 600.0
CAB_H = 870.0
TOE_H = 80.0
COUNTER_TH = 30.0

# Modulos: izquierda cajones, centro lavavajillas, derecha puerta.
OPEN_DW = 455.0
OPEN_LEFT = 430.0
OPEN_RIGHT = WIDTH - 4.0 * TH - OPEN_DW - OPEN_LEFT  # 583.0
LEFT_NICHE_W = 290.0

TOP_SUPPORT_D = 100.0
DRAWER_DEPTH = 210.0
SLIDE_CLR = 12.5

GOLA_H = 25.0
GOLA_D = 20.0
LEG_W = 40.0
LEG_D = 40.0
LEG_Y_FRONT = 30.0
LEG_Y_BACK = DEPTH - 30.0 - LEG_D

# Frentes
SIDE_LIGHT = 5.0
CENTER_GAP = 4.0
ROW_GAP = 4.0

# Mesada con bacha
TOP_OVERHANG = 30.0
COUNTER_D = DEPTH + TH + TOP_OVERHANG
COUNTER_Y = -(TH + TOP_OVERHANG)
# Bacha de apoyo 560x420 (solapa 15 mm por lado): calado 530x390.
SINK_W = 530.0
SINK_D = 390.0
SINK_RIGHT_MARGIN = 50.0
SINK_CENTER_Y = 300.0

# Nicho trasero izquierdo (detras de cajones)
LEFT_REAR_NICHE_D = 350.0
LEFT_FRONT_BLOCK_D = 311.0
DRAWER_DEPTH = LEFT_FRONT_BLOCK_D - 2.0 * TH

# Cava integrada en el nicho (simil paraiso), orientada perpendicular a cajones.
V_CLR = 2.0
V_FACE_W = LEFT_NICHE_W - V_CLR
V_DX = 330.0
V_COLS = 2
V_ROWS = 3
V_CELL = (V_FACE_W - (V_COLS + 1.0) * TH) / V_COLS
V_H = (V_ROWS + 1.0) * TH + V_ROWS * V_CELL

# Cotas Z
Z_BOTTOM = TOE_H
Z_BOTTOM_TOP = Z_BOTTOM + TH
Z_TOP = CAB_H
Z_TOP_SUPPORT = Z_TOP - TH
SIDE_H = Z_TOP - Z_BOTTOM_TOP
DIV_H = Z_TOP_SUPPORT - Z_BOTTOM_TOP
TOP_GOLA_Z = Z_TOP_SUPPORT - GOLA_H

# Tabiques en X
X_P1 = TH + OPEN_LEFT
X_P2 = X_P1 + TH + OPEN_DW

# Frentes por columna (con grilla 5/4/5)
FRONT_L_W = OPEN_LEFT + TH
FRONT_L_X = SIDE_LIGHT
# Puertas centro/derecha de igual ancho.
FRONT_CR_W = (WIDTH - SIDE_LIGHT - (FRONT_L_X + FRONT_L_W) - 2.0 * CENTER_GAP) / 2.0
FRONT_C_W = FRONT_CR_W
FRONT_R_W = FRONT_CR_W
FRONT_C_X = FRONT_L_X + FRONT_L_W + CENTER_GAP
FRONT_R_X = FRONT_C_X + FRONT_C_W + CENTER_GAP

# Parante adicional hacia la derecha en la union de puertas C/R.
EXTRA_STILE_W = (OPEN_RIGHT + TH) - FRONT_CR_W  # 64 mm con cotas actuales
EXTRA_STILE_X = X_P2 + TH

# 3 cajones iguales a izquierda:
#  - top abre con gola J superior
#  - medio y abajo con gola C entre ambos
DRAWER_FRONT_H = (TOP_GOLA_Z - ROW_GAP - (Z_BOTTOM + ROW_GAP) - GOLA_H - ROW_GAP) / 3.0
ROW3_Z = Z_BOTTOM + ROW_GAP  # cajon inferior
GOLA_C_Z = ROW3_Z + DRAWER_FRONT_H
ROW2_Z = GOLA_C_Z + GOLA_H  # cajon medio
ROW1_Z = ROW2_Z + DRAWER_FRONT_H + ROW_GAP  # cajon superior
DOOR_Z = ROW3_Z
DOOR_H = ROW1_Z + DRAWER_FRONT_H - DOOR_Z

# Calado de bacha: dejar al menos 50 mm a la derecha y mover hacia fondo.
SINK_X = WIDTH - SINK_RIGHT_MARGIN - SINK_W
SINK_CENTER_X = SINK_X + SINK_W / 2.0
SINK_Y = SINK_CENTER_Y - SINK_D / 2.0


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_drawer(doc, prefix, x, y, z, outer_w, depth, box_h, parts, code_base):
    side_t = TH
    front_back_w = outer_w - 2.0 * side_t

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


def add_counter_with_sink(doc):
    slab = Part.makeBox(WIDTH, COUNTER_D, COUNTER_TH, App.Vector(0, COUNTER_Y, Z_TOP))
    sink = Part.makeBox(
        SINK_W, SINK_D, COUNTER_TH + 2.0, App.Vector(SINK_X, SINK_Y, Z_TOP - 1.0)
    )
    obj = doc.addObject("Part::Feature", "I20_Mesada_Calado_Bacha")
    obj.Shape = slab.cut(sink)
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

    doc = App.newDocument("BajoIslaI")
    parts = []

    # Casco
    add_box(
        doc, "I1_Lateral_Izq_Frente", 0, 0, Z_BOTTOM_TOP, TH, LEFT_FRONT_BLOCK_D, SIDE_H
    )
    parts.append(
        (
            "I1",
            "Casco",
            "Lateral_Izq_Frente",
            1,
            SIDE_H,
            LEFT_FRONT_BLOCK_D,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "I1B_Lateral_Izq_Trasero",
        0,
        DEPTH - TH,
        Z_BOTTOM_TOP,
        OPEN_LEFT + TH,
        TH,
        SIDE_H,
    )
    parts.append(
        (
            "I1B",
            "Casco",
            "Fondo_Modulo_Izq",
            1,
            SIDE_H,
            OPEN_LEFT + TH,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "I1C_Fondo_Cajonera",
        0,
        LEFT_FRONT_BLOCK_D - TH,
        Z_BOTTOM_TOP,
        OPEN_LEFT + TH,
        TH,
        SIDE_H,
    )
    parts.append(
        (
            "I1C",
            "Casco",
            "Fondo_Cajonera",
            1,
            SIDE_H,
            OPEN_LEFT + TH,
            TH,
            "Canto frente",
        )
    )

    add_box(doc, "I2_Lateral_Der", WIDTH - TH, 0, Z_BOTTOM_TOP, TH, DEPTH, SIDE_H)
    parts.append(("I2", "Casco", "Lateral_Der", 1, SIDE_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "I3_Division_1", X_P1, 0, Z_BOTTOM_TOP, TH, DEPTH, DIV_H)
    parts.append(("I3", "Division", "Divisor_1", 1, DIV_H, DEPTH, TH, "Canto frente"))

    add_box(doc, "I4_Division_2", X_P2, 0, Z_BOTTOM_TOP, TH, DEPTH, DIV_H)
    parts.append(("I4", "Division", "Divisor_2", 1, DIV_H, DEPTH, TH, "Canto frente"))

    add_box(
        doc,
        "I4B_Parante_Union_CR",
        X_P2 + TH,
        0,
        Z_BOTTOM_TOP - TH,
        60.0,
        TH,
        SIDE_H,
    )
    parts.append(
        (
            "I4B",
            "Division",
            "Parante_Union_CR",
            1,
            SIDE_H,
            TH,
            60.0,
            "Canto frente",
        )
    )

    # Pisos pasantes por modulo (sin piso en lavavajillas)
    add_box(doc, "I5_Piso_Izq", 0, 0, Z_BOTTOM, OPEN_LEFT + 2.0 * TH, DEPTH, TH)
    parts.append(
        ("I5", "Casco", "Piso_Izq", 1, OPEN_LEFT + 2.0 * TH, DEPTH, TH, "Canto frente")
    )

    add_box(doc, "I6_Piso_Der", X_P2, 0, Z_BOTTOM, OPEN_RIGHT + 2.0 * TH, DEPTH, TH)
    parts.append(
        ("I6", "Casco", "Piso_Der", 1, OPEN_RIGHT + 2.0 * TH, DEPTH, TH, "Canto frente")
    )

    # Cava integrada (codigo V) dentro del nicho trasero izquierdo.
    v_x = TH
    v_y = DEPTH - V_FACE_W
    v_z = Z_BOTTOM_TOP
    v_inner_w = V_FACE_W - 2.0 * TH
    v_inner_h = V_H - 2.0 * TH

    add_box(doc, "V1_Cava_Lateral_Izq", v_x, v_y, v_z, V_DX, TH, V_H)
    add_box(
        doc, "V2_Cava_Lateral_Der", v_x, v_y + V_FACE_W - 2.0 * TH, v_z, V_DX, TH, V_H
    )
    add_box(
        doc, "V3_Cava_Base", v_x + TH, v_y + TH, v_z, V_DX - 2.0 * TH, v_inner_w, TH
    )
    add_box(
        doc,
        "V4_Cava_Tapa",
        v_x + TH,
        v_y + TH,
        v_z + V_H - TH,
        V_DX - 2.0 * TH,
        v_inner_w,
        TH,
    )

    y_div = v_y + TH + V_CELL
    add_box(doc, "V5_Cava_Divisor_Vert", v_x, y_div, v_z + TH, V_DX, TH, v_inner_h)

    for i in range(1, V_ROWS):
        z_h = v_z + TH + i * V_CELL + (i - 1) * TH
        add_box(
            doc,
            f"V{5 + i}_Cava_Divisor_Hor_{i}",
            v_x + TH,
            v_y + TH,
            z_h,
            V_DX - 2.0 * TH,
            v_inner_w,
            TH,
        )

    parts.extend(
        [
            ("V1", "Cava_Paraiso", "Lateral_Izq", 1, V_H, V_DX, TH, "Canto frente"),
            ("V2", "Cava_Paraiso", "Lateral_Der", 1, V_H, V_DX, TH, "Canto frente"),
            (
                "V3",
                "Cava_Paraiso",
                "Base",
                1,
                V_DX - 2.0 * TH,
                v_inner_w,
                TH,
                "Canto frente",
            ),
            (
                "V4",
                "Cava_Paraiso",
                "Tapa",
                1,
                V_DX - 2.0 * TH,
                v_inner_w,
                TH,
                "Canto frente",
            ),
            (
                "V5",
                "Cava_Paraiso",
                "Divisor_Vert",
                1,
                v_inner_h,
                V_DX,
                TH,
                "Canto frente",
            ),
            (
                "V6",
                "Cava_Paraiso",
                "Divisor_Hor",
                V_ROWS - 1,
                V_DX - 2.0 * TH,
                v_inner_w,
                TH,
                "Canto frente",
            ),
        ]
    )

    # Soportes superiores
    add_box(
        doc,
        "I9_Soporte_Sup_Frente",
        TH,
        0,
        Z_TOP_SUPPORT,
        WIDTH - 2.0 * TH,
        TOP_SUPPORT_D,
        TH,
    )
    parts.append(
        (
            "I9",
            "Casco",
            "Soporte_Sup_Frente",
            1,
            WIDTH - 2.0 * TH,
            TOP_SUPPORT_D,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "I10_Soporte_Sup_Fondo",
        X_P1,
        DEPTH - TOP_SUPPORT_D,
        Z_TOP_SUPPORT,
        WIDTH - X_P1 - TH,
        TOP_SUPPORT_D,
        TH,
    )
    parts.append(
        (
            "I10",
            "Casco",
            "Soporte_Sup_Fondo",
            1,
            WIDTH - X_P1 - TH,
            TOP_SUPPORT_D,
            TH,
            "Sin canto",
        )
    )

    # Patas: 8 unidades
    leg_x = [30.0, X_P1 - 50.0, X_P2 + 10.0, WIDTH - 30.0 - LEG_W]
    for i, lx in enumerate(leg_x, start=1):
        add_box(doc, f"I11_Pata_Front_{i}", lx, LEG_Y_FRONT, 0.0, LEG_W, LEG_D, TOE_H)
        add_box(doc, f"I11_Pata_Back_{i}", lx, LEG_Y_BACK, 0.0, LEG_W, LEG_D, TOE_H)
    parts.append(("I11", "Herraje", "Pata_80", 8, LEG_W, LEG_D, TOE_H, "PVC/Aluminio"))

    # Golas
    add_box(doc, "I12_Gola_J_Superior", 0, -GOLA_D, TOP_GOLA_Z, WIDTH, GOLA_D, GOLA_H)
    parts.append(
        ("I12", "Herraje", "Gola_J_Superior", 1, WIDTH, GOLA_H, GOLA_D, "Aluminio")
    )

    add_box(
        doc,
        "I13_Gola_C_Cajon_Medio_Bajo",
        FRONT_L_X,
        -GOLA_D,
        GOLA_C_Z,
        FRONT_L_W,
        GOLA_D,
        GOLA_H,
    )
    parts.append(
        ("I13", "Herraje", "Gola_C_Izq", 1, FRONT_L_W, GOLA_H, GOLA_D, "Aluminio")
    )

    # Frentes
    add_box(
        doc,
        "I14_Frente_Cajon_Sup_Izq",
        FRONT_L_X,
        -TH,
        ROW1_Z,
        FRONT_L_W,
        TH,
        DRAWER_FRONT_H,
    )
    parts.append(
        (
            "I14",
            "Frente",
            "Frente_Cajon_Sup_Izq",
            1,
            FRONT_L_W,
            DRAWER_FRONT_H,
            TH,
            "4 cantos",
        )
    )

    add_box(
        doc,
        "I15_Frente_Cajon_Med_Izq",
        FRONT_L_X,
        -TH,
        ROW2_Z,
        FRONT_L_W,
        TH,
        DRAWER_FRONT_H,
    )
    parts.append(
        (
            "I15",
            "Frente",
            "Frente_Cajon_Med_Izq",
            1,
            FRONT_L_W,
            DRAWER_FRONT_H,
            TH,
            "4 cantos",
        )
    )

    add_box(
        doc,
        "I16_Frente_Cajon_Inf_Izq",
        FRONT_L_X,
        -TH,
        ROW3_Z,
        FRONT_L_W,
        TH,
        DRAWER_FRONT_H,
    )
    parts.append(
        (
            "I16",
            "Frente",
            "Frente_Cajon_Inf_Izq",
            1,
            FRONT_L_W,
            DRAWER_FRONT_H,
            TH,
            "4 cantos",
        )
    )

    add_box(
        doc, "I17_Frente_Lavavajillas", FRONT_C_X, -TH, DOOR_Z, FRONT_C_W, TH, DOOR_H
    )
    parts.append(
        ("I17", "Frente", "Frente_Lavavajillas", 1, FRONT_C_W, DOOR_H, TH, "4 cantos")
    )

    add_box(doc, "I18_Puerta_Der", FRONT_R_X, -TH, DOOR_Z, FRONT_R_W, TH, DOOR_H)
    parts.append(("I18", "Frente", "Puerta_Der", 1, FRONT_R_W, DOOR_H, TH, "4 cantos"))

    # Cajones internos izquierda (3 iguales)
    drawer_outer_w = OPEN_LEFT - 2.0 * SLIDE_CLR
    drawer_x = TH + SLIDE_CLR
    drawer_y = 0
    box_h = 170.0
    add_drawer(
        doc,
        "I19_Cajon_Sup",
        drawer_x,
        drawer_y,
        ROW1_Z + 20.0,
        drawer_outer_w,
        DRAWER_DEPTH,
        box_h,
        parts,
        "I19",
    )
    add_drawer(
        doc,
        "I20_Cajon_Med",
        drawer_x,
        drawer_y,
        ROW2_Z + 20.0,
        drawer_outer_w,
        DRAWER_DEPTH,
        box_h,
        parts,
        "I20",
    )
    add_drawer(
        doc,
        "I21_Cajon_Inf",
        drawer_x,
        drawer_y,
        ROW3_Z + 20.0,
        drawer_outer_w,
        DRAWER_DEPTH,
        box_h,
        parts,
        "I21",
    )

    # Mesada superior con bacha
    counter = add_counter_with_sink(doc)
    parts.append(
        (
            "I22",
            "Mesada",
            f"Mesada_Calado_Bacha_{int(SINK_W)}x{int(SINK_D)}",
            1,
            WIDTH,
            COUNTER_D,
            COUNTER_TH,
            "Pulido perimetral segun proveedor",
        )
    )

    doc.recompute()

    fcstd = out_fcstd_dir / "I.FCStd"
    step = out_step_dir / "I.step"
    bom = out_bom_dir / "I_bom.csv"
    doc.saveAs(str(fcstd))
    Part.export(
        [o for o in doc.Objects if hasattr(o, "Shape") and not o.Shape.isNull()],
        str(step),
    )

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
        w.writerows(rows)

    print("Modelo generado:")
    print("-", fcstd)
    print("-", step)
    print("-", bom)
    print("\nResumen de frente:")
    print(f"- Modulo izq (3 cajones): {FRONT_L_W} mm")
    print(f"- Nicho lavavajillas (luz): {OPEN_DW} mm")
    print(f"- Modulo der (puerta): {FRONT_R_W} mm")
    print(f"- Parante union C/R: {EXTRA_STILE_W} mm")
    print(f"- Altura frentes cajon: {DRAWER_FRONT_H:.3f} mm")
    print(f"- Altura puerta der / frente lavavajillas: {DOOR_H:.3f} mm")
    print(f"- Nicho izquierdo (ancho): {LEFT_NICHE_W} mm")
    print(f"- Nicho trasero izquierdo: {LEFT_REAR_NICHE_D} mm profundidad")
    print(f"- Cava integrada (V): {V_DX:.1f}x{V_FACE_W:.1f}x{V_H:.1f} mm (XxYxZ)")
    print(f"- Hueco cava: {V_CELL:.1f} x {V_CELL:.1f} mm")


if __name__ == "__main__":
    main()

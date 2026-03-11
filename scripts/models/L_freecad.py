#!/usr/bin/env python3
"""Genera mueble L (frente armario lavarropas/escobero) en FreeCAD.

Version simplificada:
- 2 hojas frontales simetricas (tirador comun, sin gola),
- sin piso,
- parante interior a la derecha hasta linea de puertas superiores,
- estante corrido de todo el ancho en la base del modulo superior,
- 4 parantes exteriores (2 frente + 2 fondo) de 150 mm de profundidad.

Salida:
  - models/fcstd/L.FCStd
  - models/step/L.step
  - bom/L_bom.csv
"""

import csv
import os
from pathlib import Path

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

WIDTH = 890.0
DEPTH = 760.0
HEIGHT_TOTAL = 2300.0
TOE_H = 80.0
POST_D = 150.0
LEG_W = 40.0
LEG_D = 40.0
LEG_INSET = 30.0
GOLA_H = 25.0
GOLA_D = 20.0

# Distribucion interior
WASHER_CLEAR_W = 630.0
WASHER_CLEAR_H = 880.0
DIV_X = WIDTH - 2.0 * TH - WASHER_CLEAR_W
W_LEFT_CLEAR = DIV_X - TH
W_RIGHT_CLEAR = WIDTH - TH - (DIV_X + TH)
WASHER_SHELF_Z = TOE_H + WASHER_CLEAR_H
REGRUESO_H = 60.0

# Frentes: 2 hojas inferiores + 2 hojas superiores (linea AB en Z=1809)
OVERLAY = TH / 2.0
CENTER_GAP = 2.0
DOOR_Y = -TH
DOOR_W = (WIDTH - 2.0 * OVERLAY - CENTER_GAP) / 2.0
DOOR1_X = OVERLAY
DOOR2_X = DOOR1_X + DOOR_W + CENTER_GAP

AB_GOLA_Z = 1809.0

LOWER_DOOR_Z = TOE_H + OVERLAY
LOWER_DOOR_H = (AB_GOLA_Z + OVERLAY) - LOWER_DOOR_Z

UPPER_DOOR_Z = AB_GOLA_Z + OVERLAY
UPPER_DOOR_H = (HEIGHT_TOTAL - TH + OVERLAY) - UPPER_DOOR_Z

INNER_DIV_H = AB_GOLA_Z - TOE_H


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

    doc = App.newDocument("ArmarioL")
    parts = []

    side_h = HEIGHT_TOTAL - TOE_H - TH

    # Parantes exteriores (frente)
    add_box(doc, "L1_Parante_Front_Izq", 0, 0, TOE_H, TH, POST_D, side_h)
    parts.append(
        ("L1", "Casco", "Parante_Front_Izq", 1, side_h, POST_D, TH, "Canto frente")
    )

    add_box(doc, "L2_Parante_Front_Der", WIDTH - TH, 0, TOE_H, TH, POST_D, side_h)
    parts.append(
        ("L2", "Casco", "Parante_Front_Der", 1, side_h, POST_D, TH, "Canto frente")
    )

    # Parantes exteriores (fondo) para sostener tapa en 4 apoyos
    add_box(doc, "L15_Parante_Rear_Izq", 0, DEPTH - POST_D, TOE_H, TH, POST_D, side_h)
    parts.append(
        ("L15", "Casco", "Parante_Rear_Izq", 1, side_h, POST_D, TH, "Sin canto")
    )

    add_box(
        doc,
        "L16_Parante_Rear_Der",
        WIDTH - TH,
        DEPTH - POST_D,
        TOE_H,
        TH,
        POST_D,
        side_h,
    )
    parts.append(
        ("L16", "Casco", "Parante_Rear_Der", 1, side_h, POST_D, TH, "Sin canto")
    )

    # Patas 80 mm (referencia de zocalo inferior)
    leg_pos = [
        (LEG_INSET, LEG_INSET),
        (WIDTH - LEG_INSET - LEG_W, LEG_INSET),
        (LEG_INSET, DEPTH - LEG_INSET - LEG_D),
        (WIDTH - LEG_INSET - LEG_W, DEPTH - LEG_INSET - LEG_D),
    ]
    for i, (lx, ly) in enumerate(leg_pos, start=1):
        add_box(doc, f"L17_Pata_{i}", lx, ly, 0.0, LEG_W, LEG_D, TOE_H)
    parts.append(("L17", "Herraje", "Pata_80", 4, LEG_W, LEG_D, TOE_H, "PVC/Aluminio"))

    # Sin piso: solo tapa y fondo
    add_box(doc, "L3_Tapa_Casco", 0, 0, HEIGHT_TOTAL - TH, WIDTH, DEPTH, TH)
    parts.append(("L3", "Casco", "Tapa_Casco", 1, WIDTH, DEPTH, TH, "Canto frente"))

    add_box(
        doc, "L4_Fondo_3mm", TH, DEPTH - BACK_TH, TOE_H, WIDTH - 2 * TH, BACK_TH, side_h
    )
    parts.append(
        ("L4", "Fondo", "Fondo_3mm", 1, WIDTH - 2 * TH, side_h, BACK_TH, "Sin canto")
    )

    # Parante interior derecho (solo hasta inicio de modulo superior)
    add_box(doc, "L5_Parante_Interior", DIV_X, 0, TOE_H, TH, DEPTH, INNER_DIV_H)
    parts.append(
        (
            "L5",
            "Division",
            "Parante_Interior",
            1,
            INNER_DIV_H,
            DEPTH,
            TH,
            "Canto frente",
        )
    )

    # Techo lavarropas (lado derecho)
    add_box(
        doc,
        "L6_Techo_Lavarropas_Der",
        DIV_X + TH,
        0,
        WASHER_SHELF_Z,
        W_RIGHT_CLEAR,
        DEPTH,
        TH,
    )
    parts.append(
        (
            "L6",
            "Horizontal",
            "Techo_Lavarropas_Der",
            1,
            W_RIGHT_CLEAR,
            DEPTH,
            TH,
            "Canto frente",
        )
    )

    add_box(
        doc,
        "L7_Regrueso_Techo_Lav",
        DIV_X + TH,
        0,
        WASHER_SHELF_Z - REGRUESO_H,
        W_RIGHT_CLEAR,
        TH,
        REGRUESO_H,
    )
    parts.append(
        (
            "L7",
            "Refuerzo",
            "Regrueso_Techo_Lav",
            1,
            W_RIGHT_CLEAR,
            REGRUESO_H,
            TH,
            "Cantos vistos",
        )
    )

    # Piso del modulo superior (ancho completo)
    add_box(doc, "L13_Piso_Modulo_Superior", 0, 0, AB_GOLA_Z, WIDTH, DEPTH, TH)
    parts.append(
        (
            "L13",
            "Horizontal",
            "Piso_Modulo_Superior",
            1,
            WIDTH,
            DEPTH,
            TH,
            "Canto frente",
        )
    )

    # Dos hojas inferiores
    add_box(
        doc,
        "L8_Puerta_Inf_Izq",
        DOOR1_X,
        DOOR_Y,
        LOWER_DOOR_Z,
        DOOR_W,
        TH,
        LOWER_DOOR_H,
    )
    parts.append(
        ("L8", "Frente", "Puerta_Inf_Izq", 1, DOOR_W, LOWER_DOOR_H, TH, "4 cantos")
    )

    add_box(
        doc,
        "L9_Puerta_Inf_Der",
        DOOR2_X,
        DOOR_Y,
        LOWER_DOOR_Z,
        DOOR_W,
        TH,
        LOWER_DOOR_H,
    )
    parts.append(
        ("L9", "Frente", "Puerta_Inf_Der", 1, DOOR_W, LOWER_DOOR_H, TH, "4 cantos")
    )

    # Dos hojas superiores (puertitas)
    add_box(
        doc,
        "L10_Puerta_Sup_Izq",
        DOOR1_X,
        DOOR_Y,
        UPPER_DOOR_Z,
        DOOR_W,
        TH,
        UPPER_DOOR_H,
    )
    parts.append(
        ("L10", "Frente", "Puerta_Sup_Izq", 1, DOOR_W, UPPER_DOOR_H, TH, "4 cantos")
    )

    add_box(
        doc,
        "L11_Puerta_Sup_Der",
        DOOR2_X,
        DOOR_Y,
        UPPER_DOOR_Z,
        DOOR_W,
        TH,
        UPPER_DOOR_H,
    )
    parts.append(
        ("L11", "Frente", "Puerta_Sup_Der", 1, DOOR_W, UPPER_DOOR_H, TH, "4 cantos")
    )

    # Gola C horizontal bajo puertas superiores (sirve tambien para abrir inferiores)
    add_box(doc, "L12_Gola_C_Media", 0, -GOLA_D, AB_GOLA_Z, WIDTH, GOLA_D, GOLA_H)
    parts.append(
        ("L12", "Herraje", "Gola_C_Media", 1, WIDTH, GOLA_H, GOLA_D, "Aluminio")
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

    fcstd = out_fcstd_dir / "L.FCStd"
    step = out_step_dir / "L.step"
    bom = out_bom_dir / "L_bom.csv"

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
    print(f"- Profundidad: {DEPTH}")
    print(f"- Altura total: {HEIGHT_TOTAL}")
    print(f"- Vano escobero izq (interno): {W_LEFT_CLEAR}")
    print(f"- Vano lavarropas der (libre): {W_RIGHT_CLEAR} x {WASHER_CLEAR_H}")
    print(f"- Linea de corte frentes (gola AB): Z={AB_GOLA_Z}")


if __name__ == "__main__":
    main()

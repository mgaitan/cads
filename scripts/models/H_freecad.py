#!/usr/bin/env python3
"""Genera mueble H (columna horno + microondas) en FreeCAD.

Uso:
  freecad -c scripts/models/H_freecad.py

Salida:
  - models/fcstd/H.FCStd
  - models/step/H.step
  - bom/H_bom.csv
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

# Parametros principales (mm)
TH = 18.0
BACK_TH = 3.0
WIDTH_INT = 636.0
DEPTH = 600.0
HEIGHT_TOTAL = 2300.0
LEG_H = 80.0

OVEN_Z_START = 768.0
OVEN_OPENING_VISIBLE_H = 599.0
OVEN_OPENING_W = 600.0

MICRO_OPENING_H = 420.0
MICRO_SHIFT_UP = 0.0
FASCIA_H = 50.0  # altura de cada faja frontal
# Juego interno oculto por faja central (ajustado para alinear lineas de gola en ensamble)
OVEN_EXTRA_INTERNAL_H = 13.0
GOLA_H = 25.0
GOLA_D = 20.0
AB_GOLA_Z = 1809.0
LEG_W = 40.0
LEG_D = 40.0
LEG_INSET = 30.0

W = WIDTH_INT + 2 * TH
CARCASS_H = HEIGHT_TOTAL - LEG_H - 2 * TH
X_INT0 = TH
X_INT1 = X_INT0 + WIDTH_INT
INNER_DEPTH = DEPTH - TH

# Cotas derivadas en Z (desde piso)
Z_BOTTOM_PANEL = LEG_H
Z_TOP_PANEL = HEIGHT_TOTAL - TH
Z_SIDE_START = Z_BOTTOM_PANEL + TH

Z_OVEN_BASE = OVEN_Z_START
Z_OVEN_VISIBLE_TOP = Z_OVEN_BASE + OVEN_OPENING_VISIBLE_H
Z_OVEN_INTERNAL_TOP = Z_OVEN_VISIBLE_TOP + OVEN_EXTRA_INTERNAL_H
Z_OVEN_FASCIA_BOTTOM = Z_OVEN_BASE - FASCIA_H
Z_OVEN_SHELF_BOTTOM = Z_OVEN_BASE - TH

Z_MICRO_BASE = Z_OVEN_INTERNAL_TOP + MICRO_SHIFT_UP
Z_MICRO_TOP = AB_GOLA_Z
MICRO_OPENING_H = Z_MICRO_TOP - Z_MICRO_BASE
Z_MICRO_SHELF_BOTTOM = Z_MICRO_BASE - TH
Z_MICRO_TOP_FASCIA_BOTTOM = Z_MICRO_TOP - FASCIA_H

# Regrueso vertical frontal para apoyo de frente de horno/micro
LISTON_W = TH
LISTON_D = 60.0
LISTON_Z0 = Z_OVEN_BASE
LISTON_H = OVEN_OPENING_VISIBLE_H
# Extension para que el liston llegue justo a la cara inferior de H6
# (manteniendo un calado frontal donde encastra H9).
LISTON_EXT = max(0.0, (OVEN_EXTRA_INTERNAL_H + MICRO_SHIFT_UP - TH))
LISTON_H_TOTAL = LISTON_H + LISTON_EXT

# Compartimento inferior (bajo horno)
LOWER_CLEAR_H = Z_OVEN_FASCIA_BOTTOM - Z_BOTTOM_PANEL
LOWER_MID_SHELF_Z = Z_BOTTOM_PANEL + (LOWER_CLEAR_H - TH) / 2.0

# Compartimento superior (sobre micro)
TOP_CLEAR_H = Z_TOP_PANEL - Z_MICRO_TOP
# Puertas (frente aplicado, holgura 2 mm perimetral)
# Puertas centradas sobre cantos de 18 mm:
# solape 9 mm por lado (TH/2) en ancho y alto.
DOOR_OVERLAP = TH / 2.0
DOOR_W = W - TH  # 672 - 18 = 654
DOOR_X = DOOR_OVERLAP

# H10 ajustado a grilla de bajos (sin solape vertical):
# arranca en Z_BOTTOM_PANEL y termina en la cara inferior de H12.
LOWER_OPEN_Z0 = Z_BOTTOM_PANEL + TH
LOWER_DOOR_Z = Z_BOTTOM_PANEL
LOWER_DOOR_TOP = Z_OVEN_FASCIA_BOTTOM
LOWER_DOOR_H = LOWER_DOOR_TOP - LOWER_DOOR_Z

UPPER_DOOR_Z = AB_GOLA_Z + DOOR_OVERLAP
UPPER_DOOR_H = (Z_TOP_PANEL + DOOR_OVERLAP) - UPPER_DOOR_Z

DOOR_DEPTH = TH


def add_part(doc, name, x, y, z, dx, dy, dz):
    box = Part.makeBox(dx, dy, dz)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = box
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_liston_calado(doc, name, x, y, z):
    """Liston vertical con extension superior y calado frontal para encastre de H9."""
    shape = Part.makeBox(LISTON_W, LISTON_D, LISTON_H_TOTAL, App.Vector(x, y, z))
    if LISTON_EXT > 0.0:
        notch = Part.makeBox(
            LISTON_W,
            TH,
            LISTON_EXT,
            App.Vector(x, y, z + LISTON_H),
        )
        shape = shape.cut(notch)

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
    doc = App.newDocument("ColumnaHornoMicro")

    parts = []

    # Codigos de despiece: H1..H18
    # Laterales
    add_part(doc, "H1_Lateral_Izq", 0, 0, Z_SIDE_START, TH, DEPTH, CARCASS_H)
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

    add_part(doc, "H2_Lateral_Der", W - TH, 0, Z_SIDE_START, TH, DEPTH, CARCASS_H)
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

    # Patas 80 mm
    legs = [
        (LEG_INSET, LEG_INSET),
        (W - LEG_INSET - LEG_W, LEG_INSET),
        (LEG_INSET, DEPTH - LEG_INSET - LEG_D),
        (W - LEG_INSET - LEG_W, DEPTH - LEG_INSET - LEG_D),
    ]
    for i, (lx, ly) in enumerate(legs, start=1):
        add_part(doc, f"H3L_Pata_{i}", lx, ly, 0.0, LEG_W, LEG_D, LEG_H)
    parts.append(("H3L", "Herraje", "Pata_80", 4, LEG_W, LEG_D, LEG_H, "PVC/Aluminio"))

    add_part(doc, "H4_Tapa_Casco", 0, 0, Z_TOP_PANEL, W, DEPTH, TH)
    parts.append(("H4", "Horizontal", "Tapa_Casco", 1, W, DEPTH, TH, "Canto frente"))

    # Fondo (oculto para no interferir en capturas, pero incluido en despiece)
    add_part(
        doc,
        "H14_Fondo_3mm",
        X_INT0,
        DEPTH - BACK_TH,
        Z_SIDE_START,
        WIDTH_INT,
        BACK_TH,
        CARCASS_H,
    )
    parts.append(
        ("H14", "Fondo", "Fondo_3mm", 1, WIDTH_INT, CARCASS_H, BACK_TH, "Sin canto")
    )

    # Regruesos verticales frontales para apoyo del frente de horno/micro
    add_liston_calado(doc, "H15_Liston_Vert_Izq", X_INT0, 0, LISTON_Z0)
    parts.append(
        (
            "H15",
            "Regrueso",
            "Liston_Vert_Izq",
            1,
            LISTON_H_TOTAL,
            LISTON_D,
            LISTON_W,
            "Canto frente",
        )
    )

    add_liston_calado(doc, "H16_Liston_Vert_Der", X_INT1 - LISTON_W, 0, LISTON_Z0)
    parts.append(
        (
            "H16",
            "Regrueso",
            "Liston_Vert_Der",
            1,
            LISTON_H_TOTAL,
            LISTON_D,
            LISTON_W,
            "Canto frente",
        )
    )

    # Divisiones horizontales
    add_part(
        doc,
        "H5_Piso_Horno",
        X_INT0,
        TH,
        Z_OVEN_SHELF_BOTTOM,
        WIDTH_INT,
        INNER_DEPTH,
        TH,
    )
    parts.append(
        (
            "H5",
            "Horizontal",
            "Piso_Horno",
            1,
            WIDTH_INT,
            INNER_DEPTH,
            TH,
            "Canto frente",
        )
    )

    add_part(
        doc,
        "H6_Piso_Micro",
        X_INT0,
        TH,
        Z_MICRO_SHELF_BOTTOM,
        WIDTH_INT,
        INNER_DEPTH,
        TH,
    )
    parts.append(
        (
            "H6",
            "Horizontal",
            "Piso_Micro",
            1,
            WIDTH_INT,
            INNER_DEPTH,
            TH,
            "Canto frente",
        )
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
        "H9_Faja_Frontal_50",
        X_INT0,
        0,
        Z_OVEN_VISIBLE_TOP,
        WIDTH_INT,
        TH,
        FASCIA_H,
    )
    parts.append(
        (
            "H9",
            "Frente",
            "Faja_Frontal_50",
            1,
            WIDTH_INT,
            FASCIA_H,
            TH,
            "Cantos vistos",
        )
    )

    # Faja frontal inferior del horno (reduce alto visible de la puerta inferior)
    add_part(
        doc,
        "H12_Faja_Frontal_Inferior_50",
        X_INT0,
        0,
        Z_OVEN_FASCIA_BOTTOM,
        WIDTH_INT,
        TH,
        FASCIA_H,
    )
    parts.append(
        (
            "H12",
            "Frente",
            "Faja_Frontal_Inferior_50",
            1,
            WIDTH_INT,
            FASCIA_H,
            TH,
            "Cantos vistos",
        )
    )

    # Faja frontal superior del micro (techo del hueco micro)
    add_part(
        doc,
        "H13_Faja_Frontal_Superior_Micro_50",
        X_INT0,
        0,
        Z_MICRO_TOP_FASCIA_BOTTOM,
        WIDTH_INT,
        TH,
        FASCIA_H,
    )
    parts.append(
        (
            "H13",
            "Frente",
            "Faja_Frontal_Superior_Micro_50",
            1,
            WIDTH_INT,
            FASCIA_H,
            TH,
            "Cantos vistos",
        )
    )

    # Perfil gola C de continuidad con bajo mesada (sobre puerta inferior)
    add_part(
        doc,
        "H17_Gola_C_Continuidad",
        0,
        -GOLA_D,
        Z_OVEN_FASCIA_BOTTOM,
        W,
        GOLA_D,
        GOLA_H,
    )
    parts.append(
        ("H17", "Herraje", "Gola_C_Continuidad", 1, W, GOLA_H, GOLA_D, "Aluminio")
    )

    # Perfil gola J bajo puerta superior
    add_part(
        doc,
        "H18_Gola_J_Sup",
        0,
        -GOLA_D,
        AB_GOLA_Z,
        W,
        GOLA_D,
        GOLA_H,
    )
    parts.append(("H18", "Herraje", "Gola_J_Sup", 1, W, GOLA_H, GOLA_D, "Aluminio"))

    # Puertas (referencia de frente aplicado)
    add_part(
        doc,
        "H10_Puerta_Inferior",
        DOOR_X,
        -DOOR_DEPTH,
        LOWER_DOOR_Z,
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
        DOOR_X,
        -DOOR_DEPTH,
        UPPER_DOOR_Z,
        DOOR_W,
        DOOR_DEPTH,
        UPPER_DOOR_H,
    )
    parts.append(
        ("H11", "Frente", "Puerta_Superior", 1, DOOR_W, UPPER_DOOR_H, TH, "4 cantos")
    )

    doc.recompute()

    # En algunos entornos, los objetos quedan ocultos al guardar desde CLI.
    # Si hay GUI, forzamos visibilidad para que se persista en GuiDocument.xml.
    if GUI_AVAILABLE:
        for obj in doc.Objects:
            vo = getattr(obj, "ViewObject", None)
            if vo is not None:
                try:
                    vo.Visibility = True
                    if obj.Name.endswith("_Fondo_3mm"):
                        vo.Visibility = False
                except Exception:
                    pass

    # Exportes
    fcstd_path = out_fcstd_dir / "H.FCStd"
    step_path = out_step_dir / "H.step"
    bom_path = out_bom_dir / "H_bom.csv"

    doc.saveAs(str(fcstd_path))

    objs = [o for o in doc.Objects if hasattr(o, "Shape")]
    Part.export(objs, str(step_path))

    rows = add_bom_metadata(parts)
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
                "ml_gola",
                "bisagras_cazoleta",
            ]
        )
        for row in rows:
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
    print(f"- Faja frontal entre huecos: {FASCIA_H}")
    print(f"- Compartimento superior util: {TOP_CLEAR_H}")


if __name__ == "__main__":
    main()

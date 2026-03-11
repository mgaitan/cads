#!/usr/bin/env python3
"""Genera mueble AA en FreeCAD."""

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
WIDTH = 903.0
DEPTH = 320.0
HEIGHT = 710.0
EXTRACTOR_W = 590.0
EXTRACTOR_D = 470.0
EXTRACTOR_H = 90.0

DUCT_D = 160.0
DUCT_R = DUCT_D / 2.0
DUCT_REAR_CLR = 20.0
GOLA_J_H = 25.0
GOLA_J_D = 20.0

CONN_D = 35.0
CONN_R = CONN_D / 2.0
CONN_SPACING = 80.0

W_INT = WIDTH - 2 * TH
D_INT = DEPTH - BACK_TH
SIDE_H = HEIGHT - 2 * TH

Z_BOTTOM = 0.0
Z_TOP = HEIGHT - TH
Z_INNER0 = TH

# Lado izquierdo (calefon) y eje extractor/anafe a derecha
X_LEFT_ZONE = TH + W_INT * 0.25
# El extractor va alineado al borde derecho de AA en ensamble; su centro define el eje.
X_RIGHT_ZONE = WIDTH - EXTRACTOR_W / 2.0
Y_DUCT_TOP = D_INT - DUCT_REAR_CLR - DUCT_R
Y_DUCT_FLOOR = Y_DUCT_TOP
Y_CONN = D_INT - 55.0

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


def add_extractor(doc, name, x, y, z, w, d, h, bevel_d=120.0, bevel_h=40.0):
    body = Part.makeBox(w, d, h, App.Vector(x, y, z))
    tri = Part.makePolygon(
        [
            # Bisel frontal superior: baja desde la tapa hacia atras.
            App.Vector(x, y, z + h),
            App.Vector(x, y + bevel_d, z + h),
            App.Vector(x, y, z + h - bevel_h),
            App.Vector(x, y, z + h),
        ]
    )
    tri_face = Part.Face(tri)
    tri_prism = tri_face.extrude(App.Vector(w, 0, 0))
    shape = body.cut(tri_prism)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def add_bom_metadata(parts):
    rows = []
    total_gola_ml = 0.0
    total_bisagras = 0
    door_tokens = ("Puerta", "Frente_Izquierdo", "Frente_Derecho")

    for p in parts:
        codigo, categoria, pieza, cantidad, largo, ancho, espesor, cantos = p
        ml_gola = 0.0
        bisagras = 0

        if categoria == "Herraje" and "Gola" in str(pieza):
            ml_gola = (float(cantidad) * float(largo)) / 1000.0
            total_gola_ml += ml_gola

        if categoria == "Frente" and any(t in str(pieza) for t in door_tokens):
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

    # Techo: pasante izq alineado con agujero central de piso (calefon),
    # y pasante der alineado con extractor/anafe.
    top_holes = [(X_LEFT_ZONE, Y_DUCT_TOP, DUCT_R), (X_RIGHT_ZONE, Y_DUCT_TOP, DUCT_R)]
    add_box_with_round_holes(
        doc, "AA4_Tapa_Casco", 0, 0, Z_TOP, WIDTH, DEPTH, TH, top_holes
    )
    parts.append(
        (
            "AA4",
            "Horizontal",
            "Tapa_Casco_Calados_IzqDer160",
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

    # Perfil gola J bajo puertas (tirador inferior continuo)
    add_box(
        doc, "AA12_Gola_J_Inferior", 0, -GOLA_J_D, Z_BOTTOM, WIDTH, GOLA_J_D, GOLA_J_H
    )
    parts.append(
        ("AA12", "Herraje", "Gola_J_Inferior", 1, WIDTH, GOLA_J_H, GOLA_J_D, "Aluminio")
    )

    # Liston fijo 90 mm para completar visual hacia linea AC (se monta por debajo del piso)
    add_box(doc, "AA10_Liston_Fijo_90", TH / 2.0, FRONT_Y, -90.0, WIDTH - TH, TH, 90.0)
    parts.append(
        ("AA10", "Frente", "Liston_Fijo_90", 1, WIDTH - TH, 90.0, TH, "4 cantos")
    )

    # Extractor de referencia (solo visual en este modulo)
    ex_x = X_RIGHT_ZONE - EXTRACTOR_W / 2.0
    ex_y = DEPTH - EXTRACTOR_D
    ex_z = -EXTRACTOR_H
    add_extractor(
        doc,
        "AA11_Extractor_Ref",
        ex_x,
        ex_y,
        ex_z,
        EXTRACTOR_W,
        EXTRACTOR_D,
        EXTRACTOR_H,
    )
    parts.append(
        (
            "AA11",
            "Referencia",
            "Extractor_590x470x90",
            1,
            EXTRACTOR_W,
            EXTRACTOR_D,
            EXTRACTOR_H,
            "No fabricar",
        )
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

    fcstd_path = out_fcstd_dir / "AA.FCStd"
    step_path = out_step_dir / "AA.step"
    bom_path = out_bom_dir / "AA_bom.csv"

    doc.saveAs(str(fcstd_path))
    Part.export([o for o in doc.Objects if hasattr(o, "Shape")], str(step_path))

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


if __name__ == "__main__":
    main()

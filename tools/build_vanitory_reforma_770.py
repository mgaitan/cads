"""Build the 770 mm bathroom vanity model in FreeCAD.

Run inside FreeCAD's Python environment, or paste/execute through the FreeCAD MCP.
The generated FCStd is the source of truth and supplier TSVs are exported from
the same part definitions.
"""

from __future__ import annotations

import csv
import os
import re
import unicodedata
from pathlib import Path

import FreeCAD as App


ROOT = str(Path(__file__).resolve().parent.parent)
SUPPLIER_DIR = os.path.join(ROOT, "outputs", "supplier")

PREFIX = "vanitory_reforma_770"
DOC_NAME = PREFIX
MODEL_PATH = os.path.join(ROOT, "models", f"{PREFIX}.FCStd")

W = 770
# Overall furniture depth includes the 18 mm fronts. The carcass ends at y=D.
D = 500
LEG_H = 120
STONE_T = 20
BASIN_TOP_H = 1000
BASIN_H = 140
COUNTERTOP_TOP_H = BASIN_TOP_H - BASIN_H
STONE_Z = COUNTERTOP_TOP_H - STONE_T
CARCASS_H = STONE_Z - LEG_H
T = 18
DRAWER_BOTTOM_T = 5

BODY_Z = LEG_H
BODY_TOP_Z = BODY_Z + CARCASS_H

INNER_W = W - 2 * T
SIDE_H = CARCASS_H - T
RAIL_H = T
RAIL_D = 100

DRAWER_FRONT_H = 180
SIDE_REVEAL = 3
GAP = 4
DRAWER_FRONT_Z = BODY_TOP_Z - RAIL_H - DRAWER_FRONT_H
DOOR_TOP_Z = DRAWER_FRONT_Z - GAP
DOOR_BOTTOM_Z = BODY_Z + 8
DOOR_H = DOOR_TOP_Z - DOOR_BOTTOM_Z

CENTER_SERVICE_GAP = 80
DRAWER_BOX_DEPTH = 300
SLIDE_CLEARANCE = 13
CENTER_GAP_LEFT_X = (W - CENTER_SERVICE_GAP) / 2
CENTER_GAP_RIGHT_X = CENTER_GAP_LEFT_X + CENTER_SERVICE_GAP
CENTER_SUPPORT_D = D
CENTER_SUPPORT_H = DRAWER_FRONT_H
CENTER_SUPPORT_Y = 0
CENTER_SUPPORT_Z = BODY_TOP_Z - RAIL_H - CENTER_SUPPORT_H
LEFT_CENTER_SUPPORT_X = CENTER_GAP_LEFT_X - T
RIGHT_CENTER_SUPPORT_X = CENTER_GAP_RIGHT_X
LEFT_DRAWER_X = T + SLIDE_CLEARANCE
RIGHT_DRAWER_X = RIGHT_CENTER_SUPPORT_X + T + SLIDE_CLEARANCE
DRAWER_BOX_W = LEFT_CENTER_SUPPORT_X - SLIDE_CLEARANCE - LEFT_DRAWER_X
DRAWER_BOX_H = 140
DRAWER_BOX_Y = 0
DRAWER_BOX_Z = DRAWER_FRONT_Z + 24

SHELF_Z = BODY_Z + T + 230
SHELF_W = INNER_W
SHELF_D = D - 30

# The stone is flush with the carcass at both sides; only its front edge overhangs.
STONE_SIDE_OVERHANG = 0
STONE_FRONT_OVERHANG = T + 15
COUNTERTOP_W = W + 2 * STONE_SIDE_OVERHANG
COUNTERTOP_D = D + STONE_FRONT_OVERHANG
ZOCALO_H = 120
BASIN_W = 480
BASIN_D = 360
BASIN_Y = 70
HANDLE_LEN = 46
HANDLE_W = 18
HANDLE_PROJ = 10
HANDLE_FROM_TOP = 28
HANDLE_FROM_MEETING = 28
DOOR_HANDLE_FROM_TOP = 90


def recalc() -> None:
    global DOC_NAME, MODEL_PATH
    global COUNTERTOP_TOP_H, STONE_Z, CARCASS_H, BODY_Z, BODY_TOP_Z
    global INNER_W, SIDE_H, DRAWER_FRONT_Z, DOOR_TOP_Z, DOOR_BOTTOM_Z, DOOR_H
    global CENTER_GAP_LEFT_X, CENTER_GAP_RIGHT_X, CENTER_SUPPORT_D
    global CENTER_SUPPORT_Z, LEFT_CENTER_SUPPORT_X, RIGHT_CENTER_SUPPORT_X
    global LEFT_DRAWER_X, RIGHT_DRAWER_X, DRAWER_BOX_W, DRAWER_BOX_Z
    global SHELF_Z, SHELF_W, SHELF_D, COUNTERTOP_W, COUNTERTOP_D

    DOC_NAME = PREFIX
    MODEL_PATH = os.path.join(ROOT, "models", f"{PREFIX}.FCStd")
    COUNTERTOP_TOP_H = BASIN_TOP_H - BASIN_H
    STONE_Z = COUNTERTOP_TOP_H - STONE_T
    CARCASS_H = STONE_Z - LEG_H
    BODY_Z = LEG_H
    BODY_TOP_Z = BODY_Z + CARCASS_H
    INNER_W = W - 2 * T
    SIDE_H = CARCASS_H - T
    DRAWER_FRONT_Z = BODY_TOP_Z - RAIL_H - DRAWER_FRONT_H
    DOOR_TOP_Z = DRAWER_FRONT_Z - GAP
    DOOR_BOTTOM_Z = BODY_Z + 8
    DOOR_H = DOOR_TOP_Z - DOOR_BOTTOM_Z
    CENTER_GAP_LEFT_X = (W - CENTER_SERVICE_GAP) / 2
    CENTER_GAP_RIGHT_X = CENTER_GAP_LEFT_X + CENTER_SERVICE_GAP
    CENTER_SUPPORT_D = D
    CENTER_SUPPORT_Z = BODY_TOP_Z - RAIL_H - CENTER_SUPPORT_H
    LEFT_CENTER_SUPPORT_X = CENTER_GAP_LEFT_X - T
    RIGHT_CENTER_SUPPORT_X = CENTER_GAP_RIGHT_X
    LEFT_DRAWER_X = T + SLIDE_CLEARANCE
    RIGHT_DRAWER_X = RIGHT_CENTER_SUPPORT_X + T + SLIDE_CLEARANCE
    DRAWER_BOX_W = LEFT_CENTER_SUPPORT_X - SLIDE_CLEARANCE - LEFT_DRAWER_X
    DRAWER_BOX_Z = DRAWER_FRONT_Z + 24
    SHELF_Z = BODY_Z + T + 230
    SHELF_W = INNER_W
    SHELF_D = D - 30
    COUNTERTOP_W = W + 2 * STONE_SIDE_OVERHANG
    COUNTERTOP_D = D + STONE_FRONT_OVERHANG


def ensure_dirs() -> None:
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    os.makedirs(SUPPLIER_DIR, exist_ok=True)


def new_doc():
    try:
        old = App.getDocument(DOC_NAME)
    except Exception:
        old = None
    if old:
        App.closeDocument(DOC_NAME)
    return App.newDocument(DOC_NAME)


def set_prop(obj, name, value):
    if not hasattr(obj, name):
        if isinstance(value, bool):
            obj.addProperty("App::PropertyBool", name, "BOM")
        elif isinstance(value, int):
            obj.addProperty("App::PropertyInteger", name, "BOM")
        elif isinstance(value, float):
            obj.addProperty("App::PropertyFloat", name, "BOM")
        else:
            obj.addProperty("App::PropertyString", name, "BOM")
    setattr(obj, name, value)


SLUG_WORDS = {
    "base": "base",
    "inferior": "inf",
    "pasante": "pas",
    "lateral": "lat",
    "izquierdo": "izq",
    "izquierda": "izq",
    "derecho": "der",
    "derecha": "der",
    "sobre": "",
    "riel": "riel",
    "superior": "sup",
    "frontal": "front",
    "trasero": "tras",
    "soporte": "sop",
    "piedra": "piedra",
    "estante": "est",
    "regulable": "reg",
    "completo": "comp",
    "faja": "faja",
    "central": "cent",
    "corredera": "corr",
    "frente": "fte",
    "cajon": "caj",
    "puerta": "pta",
    "trasfrente": "trasfte",
    "contrafrente": "ctrfte",
    "fondo": "fondo",
    "zocalo": "zoc",
    "mesada": "mes",
}


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text).strip("_").lower())


def short_slug(text: str) -> str:
    parts = []
    for word in slug(text).split("_"):
        mapped = SLUG_WORDS.get(word, word[:6])
        if mapped:
            parts.append(mapped)
    return "_".join(parts[:4])


def code_prefix() -> str:
    if PREFIX.endswith("_770"):
        return "VS"
    if PREFIX.endswith("_830"):
        return "VC"
    return "V"


def part_number(code: str) -> str:
    return re.sub(r"^[A-Za-z]+", "", code).lower()


def part_code(code: str, piece: str) -> str:
    return f"{code_prefix()}_{part_number(code)}_{short_slug(piece)}"


def add_box(doc, code, piece, category, material, size, pos, color, bom):
    full_code = part_code(code, piece)
    obj = doc.addObject("Part::Box", full_code)
    obj.Label = f"{full_code} {piece}"
    obj.Length = float(size[0])
    obj.Width = float(size[1])
    obj.Height = float(size[2])
    obj.Placement.Base = App.Vector(float(pos[0]), float(pos[1]), float(pos[2]))
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = int(bom.pop("transparency", 0))

    cut_dims = sorted([float(size[0]), float(size[1]), float(size[2])], reverse=True)
    defaults = {
        "bom_include": True,
        "bom_codigo": full_code,
        "bom_pieza": piece,
        "bom_categoria": category,
        "bom_material": material,
        "bom_largo_mm": int(round(cut_dims[0])),
        "bom_ancho_mm": int(round(cut_dims[1])),
        "bom_espesor_mm": int(round(cut_dims[2])),
        "bom_canto_izq": 0,
        "bom_canto_der": 0,
        "bom_canto_sup": 0,
        "bom_canto_inf": 0,
        "bom_cantos": "",
        "bom_bisagra_codo": "",
        "bom_luz_bisagra_mm": "",
        "bom_bisagra_lado": "",
        "bom_cazoleta_diametro_mm": 0,
        "bom_cazoleta_cantidad": 0,
        "bom_cazoleta_posiciones": "",
    }
    defaults.update(bom)
    for key, value in defaults.items():
        set_prop(obj, key, value)
    return obj


def edge_front():
    return {
        "bom_canto_izq": 1,
        "bom_cantos": "front edge",
    }


def edge_all():
    return {
        "bom_canto_izq": 1,
        "bom_canto_der": 1,
        "bom_canto_sup": 1,
        "bom_canto_inf": 1,
        "bom_cantos": "todos los cantos visibles",
    }


def edge_top():
    return {
        "bom_canto_sup": 1,
        "bom_cantos": "canto superior visible al abrir el cajon",
    }


def no_bom():
    return {
        "bom_include": False,
    }


def build():
    recalc()
    ensure_dirs()
    doc = new_doc()
    mel = (0.88, 0.88, 0.84, 1.0)
    front = (0.72, 0.78, 0.82, 1.0)
    drawer = (0.82, 0.78, 0.70, 1.0)
    stone = (0.08, 0.08, 0.08, 1.0)
    handle = (0.01, 0.01, 0.01, 1.0)
    glass = (0.25, 0.55, 0.95, 0.35)

    add_box(doc, "VR01", "Base inferior pasante", "Carcass", "white melamine", (W, D, T), (0, 0, BODY_Z), mel, edge_front())
    add_box(doc, "VR02", "Lateral izquierdo sobre base", "Carcass", "white melamine", (T, D, SIDE_H), (0, 0, BODY_Z + T), mel, edge_front())
    add_box(doc, "VR03", "Lateral derecho sobre base", "Carcass", "white melamine", (T, D, SIDE_H), (W - T, 0, BODY_Z + T), mel, edge_front())
    add_box(doc, "VR04", "Riel superior frontal soporte piedra", "Carcass", "white melamine", (INNER_W, RAIL_D, RAIL_H), (T, 0, BODY_TOP_Z - RAIL_H), mel, edge_front())
    add_box(doc, "VR05", "Riel superior trasero soporte piedra", "Carcass", "white melamine", (INNER_W, RAIL_D, RAIL_H), (T, D - RAIL_D, BODY_TOP_Z - RAIL_H), mel, {"bom_cantos": "oculto, sin canto visible"})
    add_box(doc, "VR06", "Estante regulable completo", "Adjustable_Shelf", "white melamine", (SHELF_W, SHELF_D, T), (T, 15, SHELF_Z), mel, {**edge_front(), "bom_cantos": "front edge; estante regulable con soportes/perforaciones laterales"})
    add_box(doc, "VR17", "Faja central izquierda soporte corredera", "Carcass", "white melamine", (T, CENTER_SUPPORT_D, CENTER_SUPPORT_H), (LEFT_CENTER_SUPPORT_X, CENTER_SUPPORT_Y, CENTER_SUPPORT_Z), mel, {"bom_cantos": "soporte interior de corredera, atornillable desde arriba"})
    add_box(doc, "VR18", "Faja central derecha soporte corredera", "Carcass", "white melamine", (T, CENTER_SUPPORT_D, CENTER_SUPPORT_H), (RIGHT_CENTER_SUPPORT_X, CENTER_SUPPORT_Y, CENTER_SUPPORT_Z), mel, {"bom_cantos": "soporte interior de corredera, atornillable desde arriba"})

    front_w = (W - 2 * SIDE_REVEAL - GAP) / 2
    left_front_x = SIDE_REVEAL
    right_front_x = SIDE_REVEAL + front_w + GAP
    add_box(doc, "VR07", "Frente cajon izquierdo", "Front", "white melamine", (front_w, T, DRAWER_FRONT_H), (left_front_x, -T, DRAWER_FRONT_Z), front, edge_all())
    add_box(doc, "VR08", "Frente cajon derecho", "Front", "white melamine", (front_w, T, DRAWER_FRONT_H), (right_front_x, -T, DRAWER_FRONT_Z), front, edge_all())

    door_w = front_w
    hinge_left = {
        **edge_all(),
        "bom_bisagra_codo": 0,
        "bom_luz_bisagra_mm": 3,
        "bom_bisagra_lado": "left",
        "bom_cazoleta_diametro_mm": 35,
        "bom_cazoleta_cantidad": 2,
        "bom_cazoleta_posiciones": "left side; codo 0; 3mm reveal; centers 90mm from bottom/top; x center 22mm from hinge edge",
    }
    hinge_right = {
        **edge_all(),
        "bom_bisagra_codo": 0,
        "bom_luz_bisagra_mm": 3,
        "bom_bisagra_lado": "right",
        "bom_cazoleta_diametro_mm": 35,
        "bom_cazoleta_cantidad": 2,
        "bom_cazoleta_posiciones": "right side; codo 0; 3mm reveal; centers 90mm from bottom/top; x center 22mm from hinge edge",
    }
    add_box(doc, "VR09", "Puerta inferior izquierda", "Front", "white melamine", (door_w, T, DOOR_H), (left_front_x, -T, DOOR_BOTTOM_Z), front, hinge_left)
    add_box(doc, "VR10", "Puerta inferior derecha", "Front", "white melamine", (door_w, T, DOOR_H), (right_front_x, -T, DOOR_BOTTOM_Z), front, hinge_right)

    add_box(doc, "H01", "Tirador negro 46mm horizontal cajon izquierdo", "Hardware", "black handle 46mm", (HANDLE_LEN, HANDLE_PROJ, HANDLE_W), (left_front_x + (front_w - HANDLE_LEN) / 2, -T - HANDLE_PROJ, DRAWER_FRONT_Z + DRAWER_FRONT_H - HANDLE_FROM_TOP - HANDLE_W), handle, no_bom())
    add_box(doc, "H02", "Tirador negro 46mm horizontal cajon derecho", "Hardware", "black handle 46mm", (HANDLE_LEN, HANDLE_PROJ, HANDLE_W), (right_front_x + (front_w - HANDLE_LEN) / 2, -T - HANDLE_PROJ, DRAWER_FRONT_Z + DRAWER_FRONT_H - HANDLE_FROM_TOP - HANDLE_W), handle, no_bom())
    add_box(doc, "H03", "Tirador negro 46mm vertical puerta izquierda", "Hardware", "black handle 46mm", (HANDLE_W, HANDLE_PROJ, HANDLE_LEN), (left_front_x + door_w - HANDLE_FROM_MEETING - HANDLE_W, -T - HANDLE_PROJ, DOOR_TOP_Z - DOOR_HANDLE_FROM_TOP - HANDLE_LEN), handle, no_bom())
    add_box(doc, "H04", "Tirador negro 46mm vertical puerta derecha", "Hardware", "black handle 46mm", (HANDLE_W, HANDLE_PROJ, HANDLE_LEN), (right_front_x + HANDLE_FROM_MEETING, -T - HANDLE_PROJ, DOOR_TOP_Z - DOOR_HANDLE_FROM_TOP - HANDLE_LEN), handle, no_bom())

    for prefix, x, side in (("VR11", LEFT_DRAWER_X, "izquierdo"), ("VR12", RIGHT_DRAWER_X, "derecho")):
        add_box(doc, f"{prefix}A", f"Lateral izquierdo cajon {side}", "Drawer", "white melamine", (T, DRAWER_BOX_DEPTH, DRAWER_BOX_H), (x, DRAWER_BOX_Y, DRAWER_BOX_Z), drawer, edge_top())
        add_box(doc, f"{prefix}B", f"Lateral derecho cajon {side}", "Drawer", "white melamine", (T, DRAWER_BOX_DEPTH, DRAWER_BOX_H), (x + DRAWER_BOX_W - T, DRAWER_BOX_Y, DRAWER_BOX_Z), drawer, edge_top())
        add_box(doc, f"{prefix}C", f"Trasfrente cajon {side}", "Drawer", "white melamine", (DRAWER_BOX_W, T, DRAWER_BOX_H), (x, DRAWER_BOX_Y, DRAWER_BOX_Z), drawer, edge_top())
        add_box(doc, f"{prefix}D", f"Contrafrente cajon {side}", "Drawer", "white melamine", (DRAWER_BOX_W, T, DRAWER_BOX_H), (x, DRAWER_BOX_Y + DRAWER_BOX_DEPTH - T, DRAWER_BOX_Z), drawer, edge_top())
        add_box(doc, f"{prefix}E", f"Fondo cajon {side}", "Drawer", "drawer bottom 5mm", (DRAWER_BOX_W, DRAWER_BOX_DEPTH, DRAWER_BOTTOM_T), (x, DRAWER_BOX_Y, DRAWER_BOX_Z - DRAWER_BOTTOM_T), drawer, {"bom_material": "drawer bottom 5mm", "bom_espesor_mm": DRAWER_BOTTOM_T, "bom_cantos": "sin canto visible"})

    add_box(doc, "VR15", "Zocalo mesada piedra trasero", "Plinth", "black stone", (COUNTERTOP_W, STONE_T, ZOCALO_H), (-STONE_SIDE_OVERHANG, D - STONE_T, COUNTERTOP_TOP_H), stone, {"bom_material": "black stone", "bom_espesor_mm": STONE_T, "bom_cantos": "alzada trasera sobre mesada"})

    add_box(doc, "VR16", "Piedra superior", "Countertop", "black stone", (COUNTERTOP_W, COUNTERTOP_D, STONE_T), (-STONE_SIDE_OVERHANG, -STONE_FRONT_OVERHANG, STONE_Z), stone, {"bom_material": "black stone", "bom_espesor_mm": STONE_T, "bom_cantos": "vuela 15mm por delante de los frentes; verificar plantilla en obra"})
    add_box(doc, "REF01", "Bacha de apoyar centrada referencia", "Reference", "ceramic basin", (BASIN_W, BASIN_D, BASIN_H), ((W - BASIN_W) / 2, BASIN_Y, COUNTERTOP_TOP_H), glass, {"bom_include": False, "transparency": 65})
    add_box(doc, "REF02", "Canal sanitario cajones 80mm", "Reference", "clearance", (CENTER_SERVICE_GAP, DRAWER_BOX_DEPTH, DRAWER_BOX_H + 20), ((W - CENTER_SERVICE_GAP) / 2, DRAWER_BOX_Y, DRAWER_BOX_Z - 10), glass, {"bom_include": False, "transparency": 80})

    doc.recompute()
    doc.saveAs(MODEL_PATH)
    export_tsv(doc)
    return doc


TSV_HEADERS = [
    "codigo",
    "pieza",
    "categoria",
    "material",
    "largo_mm",
    "ancho_mm",
    "espesor_mm",
    "canto_izq",
    "canto_der",
    "canto_sup",
    "canto_inf",
    "cantos",
    "bisagra_codo",
    "luz_bisagra_mm",
    "bisagra_lado",
    "cazoleta_diametro_mm",
    "cazoleta_cantidad",
    "cazoleta_posiciones",
]


def prop(obj, name, default=""):
    return getattr(obj, name, default)


def bom_rows(doc):
    rows = []
    for obj in doc.Objects:
        if not bool(prop(obj, "bom_include", False)):
            continue
        rows.append({
            "codigo": prop(obj, "bom_codigo"),
            "pieza": prop(obj, "bom_pieza"),
            "categoria": prop(obj, "bom_categoria"),
            "material": prop(obj, "bom_material"),
            "largo_mm": int(round(prop(obj, "bom_largo_mm", 0))),
            "ancho_mm": int(round(prop(obj, "bom_ancho_mm", 0))),
            "espesor_mm": int(round(prop(obj, "bom_espesor_mm", 0))),
            "canto_izq": prop(obj, "bom_canto_izq", 0),
            "canto_der": prop(obj, "bom_canto_der", 0),
            "canto_sup": prop(obj, "bom_canto_sup", 0),
            "canto_inf": prop(obj, "bom_canto_inf", 0),
            "cantos": prop(obj, "bom_cantos"),
            "bisagra_codo": prop(obj, "bom_bisagra_codo"),
            "luz_bisagra_mm": prop(obj, "bom_luz_bisagra_mm"),
            "bisagra_lado": prop(obj, "bom_bisagra_lado"),
            "cazoleta_diametro_mm": prop(obj, "bom_cazoleta_diametro_mm", 0),
            "cazoleta_cantidad": prop(obj, "bom_cazoleta_cantidad", 0),
            "cazoleta_posiciones": prop(obj, "bom_cazoleta_posiciones"),
        })
    return rows


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_HEADERS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_optimizer_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        for row in rows:
            writer.writerow([
                row["codigo"],
                1,
                row["largo_mm"],
                row["ancho_mm"],
                "YES",
            ])


def export_tsv(doc):
    rows = bom_rows(doc)
    write_rows(os.path.join(SUPPLIER_DIR, f"{PREFIX}_supplier.tsv"), rows)
    groups = {
        "white_melamine_18mm": lambda r: r["material"] == "white melamine" and r["espesor_mm"] == 18,
        "drawer_bottom_5mm": lambda r: r["material"] == "drawer bottom 5mm" and r["espesor_mm"] == 5,
        "black_stone_20mm": lambda r: r["material"] == "black stone" and r["espesor_mm"] == 20,
    }
    for suffix, predicate in groups.items():
        write_rows(
            os.path.join(SUPPLIER_DIR, f"{PREFIX}_{suffix}.tsv"),
            [row for row in rows if predicate(row)],
        )
    write_optimizer_rows(
        os.path.join(SUPPLIER_DIR, f"{PREFIX}_white_18mm.tsv"),
        [row for row in rows if groups["white_melamine_18mm"](row)],
    )
    write_optimizer_rows(
        os.path.join(SUPPLIER_DIR, f"{PREFIX}_drawer_bottom_5mm.tsv"),
        [row for row in rows if groups["drawer_bottom_5mm"](row)],
    )


if __name__ == "__main__":
    build()

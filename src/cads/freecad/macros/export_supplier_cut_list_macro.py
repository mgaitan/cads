#!/usr/bin/env python3
"""Exporta TSV de importacion para proveedor desde documentos FreeCAD abiertos.

Cada fila, sin encabezado, usa exactamente este orden:
pieza, cantidad, largo_mm, ancho_mm, girar, canto_izq, canto_der,
canto_sup, canto_inf.

Se genera un archivo por combinacion de material y espesor. Ejecutar dentro de
FreeCAD GUI con los FCStd que se quieran exportar abiertos.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import FreeCAD as App

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(globals().get("OUT_DIR", ROOT / "outputs" / "supplier"))

# None exporta todos los documentos abiertos. Usar, por ejemplo,
# MODULES = ["AA", "AB"] antes de ejecutar para limitar la exportacion.
MODULES = globals().get("MODULES", None)
OUTPUT_PREFIX = globals().get("OUTPUT_PREFIX", None)

CATEGORY_RULES = [
    ("Gola", "Herraje"),
    ("Pata", "Herraje"),
    ("Mesada", "Mesada"),
    ("Alzada", "Mesada"),
    ("Barra", "Mesada"),
    ("Cajon_", "Cajon"),
    ("Frente_Caja", "Cajon"),
    ("Trasera_Caja", "Cajon"),
    ("Soporte", "Casco"),
    ("Piso", "Casco"),
    ("Lateral", "Casco"),
    ("Division", "Division"),
    ("Divisor", "Division"),
    ("Parante", "Division"),
    ("Fondo", "Fondo"),
    ("Estante", "Estante_Regulable"),
    ("Regrueso", "Regrueso"),
    ("Puerta", "Frente"),
    ("Frente", "Frente"),
]


def read_prop(obj, name, default=None):
    try:
        if hasattr(obj, "PropertiesList") and name in obj.PropertiesList:
            value = getattr(obj, name)
            return value if value not in ("", None) else default
    except Exception:
        pass
    return default


def prop_is_true(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no")
    return bool(value)


def ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^A-Z0-9]+", "_", normalized.upper()).strip("_")


def compact_piece_slug(piece: str) -> str:
    """Produce un identificador breve sin articulos ni preposiciones."""
    ignored = {"A", "AL", "CON", "DE", "DEL", "EL", "EN", "LA", "LOS", "PARA", "SOBRE", "Y"}
    words = [word for word in ascii_slug(piece).split("_") if word not in ignored]
    return "_".join(words) or "PIEZA"


def compact_code(value: str) -> str:
    """Conserva el prefijo y correlativo, sin separadores internos."""
    code = ascii_slug(value)
    match = re.match(r"([A-Z]+)_?(\d+)([A-Z]?)(?:_|$)", code)
    if match:
        return "".join(match.groups(default=""))
    return code.split("_", 1)[0]


def infer_category(name: str) -> str:
    for needle, category in CATEGORY_RULES:
        if needle in name:
            return category
    return "Casco"


def bbox_dims(obj) -> tuple[float, float, float]:
    bb = obj.Shape.BoundBox
    return tuple(sorted([float(bb.XLength), float(bb.YLength), float(bb.ZLength)], reverse=True))


def detect_module(doc) -> str:
    try:
        return Path(doc.FileName).stem.upper()
    except Exception:
        return doc.Name.upper()


def panel_axes(obj) -> tuple[float, float]:
    bb = obj.Shape.BoundBox
    dims = sorted([float(bb.XLength), float(bb.YLength), float(bb.ZLength)])
    return dims[2], dims[1]


def pair_choice(obj) -> int:
    if prop_is_true(read_prop(obj, "bom_canto_der", False)) or prop_is_true(
        read_prop(obj, "bom_canto_inf", False)
    ):
        return 1
    return 0


def is_vertical_front_piece(name: str) -> bool:
    return any(
        keyword in name
        for keyword in ("Lateral", "Parante", "Divisor", "Division", "Liston_Vert")
    )


def supplier_edge_flags(obj, name: str, export_largo: int) -> list[int]:
    raw = [
        int(prop_is_true(read_prop(obj, "bom_canto_izq", False))),
        int(prop_is_true(read_prop(obj, "bom_canto_der", False))),
        int(prop_is_true(read_prop(obj, "bom_canto_sup", False))),
        int(prop_is_true(read_prop(obj, "bom_canto_inf", False))),
    ]
    if sum(raw) in (0, 4):
        return raw

    canto = str(read_prop(obj, "bom_cantos", "")).strip().lower()
    choice = pair_choice(obj)
    panel_largo, _panel_ancho = panel_axes(obj)
    if canto == "canto frente":
        edge_len = float(obj.Shape.BoundBox.ZLength) if is_vertical_front_piece(name) else float(obj.Shape.BoundBox.XLength)
    elif canto in ("canto sup", "canto inf"):
        edge_len = panel_largo
    else:
        return raw

    if int(round(edge_len)) == export_largo:
        return [1, 0, 0, 0] if choice == 0 else [0, 1, 0, 0]
    return [0, 0, 1, 0] if choice == 0 else [0, 0, 0, 1]


def material_key(material: str, espesor: int) -> str:
    return f"{ascii_slug(material).lower() or 'sin_material'}_{espesor}mm"


def iter_rows(doc):
    for obj in doc.Objects:
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue
        if not prop_is_true(read_prop(obj, "bom_include", True)):
            continue

        object_name = str(getattr(obj, "Name", ""))
        largo, ancho, espesor = bbox_dims(obj)
        piece = str(read_prop(obj, "bom_pieza", object_name))
        category = str(read_prop(obj, "bom_categoria", infer_category(object_name)))
        if category in ("Herraje", "Resumen"):
            continue

        export_largo = int(round(float(read_prop(obj, "bom_largo_mm", largo))))
        export_ancho = int(round(float(read_prop(obj, "bom_ancho_mm", ancho))))
        export_espesor = int(round(float(read_prop(obj, "bom_espesor_mm", espesor))))
        if min(export_largo, export_ancho) < 50:
            raise RuntimeError(f"Pieza menor a 50 mm: {object_name}")

        code = compact_code(str(read_prop(obj, "bom_codigo", object_name)))
        if not code:
            raise RuntimeError(f"Falta bom_codigo en {object_name}")
        name = f"{code}_{compact_piece_slug(piece)}"
        flags = supplier_edge_flags(obj, object_name, export_largo)
        material = str(read_prop(obj, "bom_material", "sin material")).strip()

        yield material_key(material, export_espesor), [
            name,
            "1",
            str(export_largo),
            str(export_ancho),
            "SI",
            *(str(flag) for flag in flags),
        ]


def output_prefix(documents) -> str:
    if OUTPUT_PREFIX:
        return ascii_slug(str(OUTPUT_PREFIX)).lower()
    modules = sorted(detect_module(doc) for doc in documents)
    return "_".join(modules).lower()


def main():
    if App.ActiveDocument is None:
        raise RuntimeError("No hay documentos abiertos en FreeCAD.")

    selected = {str(module).upper() for module in MODULES} if MODULES else None
    documents = [
        doc
        for doc in App.listDocuments().values()
        if selected is None or detect_module(doc) in selected
    ]
    if not documents:
        raise RuntimeError("No hay documentos abiertos que coincidan con MODULES.")

    groups = defaultdict(list)
    for doc in documents:
        for material, row in iter_rows(doc):
            groups[material].append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prefix = output_prefix(documents)
    for material, rows in sorted(groups.items()):
        path = OUT_DIR / f"{prefix}_{material}.tsv"
        rows.sort(key=lambda row: row[0])
        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle, delimiter="\t", lineterminator="\n").writerows(rows)
        print(f"saved {path} ({len(rows)} piezas)")


if globals().get("RUN_MACRO", True):
    main()

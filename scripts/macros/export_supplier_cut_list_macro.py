#!/usr/bin/env python3
"""Macro para exportar lista unitaria de corte para proveedor.

Uso dentro de FreeCAD GUI:
- Abrir uno o mas documentos FCStd.
- Ajustar MODULES / MATERIAL_GROUP si hace falta.
- Ejecutar la macro.

Salida TSV:
- Nombre de la pieza
- Cantidad
- Largo (mm)
- Ancho (mm)
- Rotacion
- Canto izq
- Canto der
- Canto sup
- Canto inf
"""

from __future__ import annotations

import csv
from pathlib import Path

import FreeCAD as App

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs" / "supplier"

# Configuracion rapida de la macro.
MODULES = globals().get("MODULES", ["BA", "BB", "H"])
MATERIAL_GROUP = globals().get("MATERIAL_GROUP", "blanco_18mm")
OUTPUT_PATH = Path(
    globals().get(
        "OUTPUT_PATH",
        str(OUT_DIR / f"{'_'.join(MODULES)}_{MATERIAL_GROUP}.tsv"),
    )
)

CATEGORY_RULES = [
    ("AC_", "AC_Paraiso"),
    ("F_", "F_Paraiso"),
    ("R13_", "R_Paraiso"),
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


def infer_category(name: str) -> str:
    for needle, category in CATEGORY_RULES:
        if needle in name:
            return category
    return "Casco"


def infer_material_group(category: str, piece: str, espesor: float) -> str:
    key = f"{category} {piece}"
    if category in ("AC_Paraiso", "F_Paraiso", "R_Paraiso") or "Paraiso" in key:
        return "paraiso_18mm"
    if abs(espesor - 3.0) <= 0.6:
        return "fondo_3mm"
    if abs(espesor - 6.0) <= 0.6:
        return "fondo_6mm"
    return "blanco_18mm"


def bbox_dims(obj) -> tuple[float, float, float]:
    bb = obj.Shape.BoundBox
    dims = sorted(
        [float(bb.XLength), float(bb.YLength), float(bb.ZLength)],
        reverse=True,
    )
    return dims[0], dims[1], dims[2]


def allowed_prefixes(module: str) -> tuple[str, ...]:
    if module == "AB":
        return ("AB", "AC")
    return (module,)


def detect_module(doc) -> str:
    try:
        stem = Path(doc.FileName).stem
    except Exception:
        stem = doc.Name
    stem = stem.upper()
    return "I" if stem == "ALT-02" else stem


def iter_rows(doc, module: str):
    prefixes = allowed_prefixes(module)
    for obj in doc.Objects:
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue
        name = str(getattr(obj, "Name", ""))
        if "_" not in name:
            continue
        code, piece_name = name.split("_", 1)
        if not any(code.startswith(prefix) for prefix in prefixes):
            continue
        if piece_name.endswith("_Preview"):
            continue
        if not prop_is_true(read_prop(obj, "bom_include", True)):
            continue

        largo, ancho, espesor = bbox_dims(obj)
        piece_name = str(read_prop(obj, "bom_pieza", piece_name))
        category = str(read_prop(obj, "bom_categoria", infer_category(name)))
        material = str(read_prop(obj, "bom_material", "")).strip().lower()
        if material in ("piedra gris mara", "piedra", "mesada", "granito"):
            continue
        group = infer_material_group(category, piece_name, espesor)
        if group != MATERIAL_GROUP:
            continue
        if category in ("Herraje", "Mesada", "Resumen"):
            continue

        yield [
            name,
            "1",
            str(int(round(float(read_prop(obj, "bom_largo_mm", largo))))),
            str(int(round(float(read_prop(obj, "bom_ancho_mm", ancho))))),
            "SI",
            "1" if prop_is_true(read_prop(obj, "bom_canto_izq", False)) else "0",
            "1" if prop_is_true(read_prop(obj, "bom_canto_der", False)) else "0",
            "1" if prop_is_true(read_prop(obj, "bom_canto_sup", False)) else "0",
            "1" if prop_is_true(read_prop(obj, "bom_canto_inf", False)) else "0",
        ]


def main():
    if App.ActiveDocument is None:
        raise RuntimeError("No hay documentos abiertos en FreeCAD.")

    rows = []
    for doc in App.listDocuments().values():
        module = detect_module(doc)
        if module not in MODULES:
            continue
        rows.extend(iter_rows(doc, module))

    rows.sort(key=lambda row: row[0])
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(rows)

    print(f"saved {OUTPUT_PATH}")
    for row in rows:
        print("\t".join(row))


if globals().get("RUN_MACRO", True):
    main()

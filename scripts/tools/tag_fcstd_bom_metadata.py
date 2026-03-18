#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FCSTD_DIR = ROOT / "models" / "fcstd"
BOM_DIR = ROOT / "bom"

MODULE_TO_FCSTD = {
    "AA": FCSTD_DIR / "AA.FCStd",
    "AB": FCSTD_DIR / "AB.FCStd",
    "BA": FCSTD_DIR / "BA.FCStd",
    "BB": FCSTD_DIR / "BB.FCStd",
    "H": FCSTD_DIR / "H.FCStd",
    "L": FCSTD_DIR / "L.FCStd",
    "F": FCSTD_DIR / "F.FCStd",
    "R": FCSTD_DIR / "R.FCStd",
    "I": FCSTD_DIR / "variants" / "I" / "alt-02.FCStd",
}

TARGET_MODULES = ["AA", "AB", "BA", "BB", "H", "L", "F", "R", "I"]


def load_bom_rows(module: str) -> dict[str, list[dict[str, str]]]:
    path = BOM_DIR / f"{module}_bom.csv"
    rows_by_code: dict[str, list[dict[str, str]]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            code = (row.get("codigo") or "").strip()
            if not code or code == "TOTAL":
                continue
            rows_by_code.setdefault(code, []).append(row)
    return rows_by_code


def infer_category(name: str) -> str:
    for needle, category in [
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
    ]:
        if needle in name:
            return category
    return "Casco"


def infer_cantos_from_name(name: str, category: str) -> str:
    if category in ("Herraje", "Mesada", "Resumen"):
        return "Sin canto"
    if "Puerta" in name or "Frente" in name:
        return "4 cantos"
    if any(
        token in name
        for token in (
            "Piso",
            "Tapa",
            "Techo",
            "Estante",
            "Soporte",
            "Lateral",
            "Division",
            "Divisor",
            "Parante",
        )
    ):
        return "Canto frente"
    if "Fondo" in name:
        return "Sin canto"
    if "Regrueso" in name or "Liston" in name:
        return "Sin canto"
    return "Sin canto"


def allowed_prefixes(module: str) -> tuple[str, ...]:
    if module == "AB":
        return ("AB", "AC")
    return (module,)


def choose_row(name: str, code: str, suffix: str, rows: list[dict[str, str]] | None):
    if not rows:
        return None

    normalized = suffix.lower()
    for row in rows:
        piece = (row.get("pieza") or "").lower()
        if piece and piece in normalized:
            return row
    return rows[0]


def cantos_flags(cantos: str) -> dict[str, bool]:
    text = (cantos or "").strip().lower()
    if text == "4 cantos":
        return {
            "bom_canto_izq": True,
            "bom_canto_der": True,
            "bom_canto_sup": True,
            "bom_canto_inf": True,
        }
    if text == "canto frente":
        return {
            "bom_canto_izq": False,
            "bom_canto_der": False,
            "bom_canto_sup": True,
            "bom_canto_inf": False,
        }
    return {
        "bom_canto_izq": False,
        "bom_canto_der": False,
        "bom_canto_sup": False,
        "bom_canto_inf": False,
    }


def build_metadata_payload() -> dict[str, dict[str, dict[str, object]]]:
    payload: dict[str, dict[str, dict[str, object]]] = {}
    for module in TARGET_MODULES:
        rows_by_code = load_bom_rows(module)
        payload[module] = {"__fcstd__": {"path": str(MODULE_TO_FCSTD[module])}}
        prefixes = allowed_prefixes(module)
        for code, rows in rows_by_code.items():
            if not any(code.startswith(prefix) for prefix in prefixes):
                continue
            payload[module][code] = {"rows": rows}
    return payload


PAYLOAD = build_metadata_payload()


FREECAD_TAGGER_CODE = f"""
from pathlib import Path
import FreeCAD as App

PAYLOAD = {PAYLOAD!r}


def ensure_prop(obj, type_name, prop_name):
    if prop_name not in getattr(obj, "PropertiesList", []):
        obj.addProperty(type_name, prop_name, "BOM", prop_name)


def infer_category(name):
    for needle, category in [
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
    ]:
        if needle in name:
            return category
    return "Casco"


def infer_cantos_from_name(name, category):
    if category in ("Herraje", "Mesada", "Resumen"):
        return "Sin canto"
    if "Puerta" in name or "Frente" in name:
        return "4 cantos"
    if any(token in name for token in ("Piso", "Tapa", "Techo", "Estante", "Soporte", "Lateral", "Division", "Divisor", "Parante")):
        return "Canto frente"
    if "Fondo" in name:
        return "Sin canto"
    if "Regrueso" in name or "Liston" in name:
        return "Sin canto"
    return "Sin canto"


def directional_cantos_flags(name, category, cantos):
    text = (cantos or "").strip().lower()
    base = dict(bom_canto_izq=False, bom_canto_der=False, bom_canto_sup=False, bom_canto_inf=False)
    if text == "4 cantos":
        return dict(bom_canto_izq=True, bom_canto_der=True, bom_canto_sup=True, bom_canto_inf=True)
    if text != "canto frente":
        return base

    vertical_tokens = ("Lateral", "Parante", "Division", "Divisor")
    horizontal_tokens = ("Piso", "Tapa", "Techo", "Estante", "Soporte")

    if any(token in name for token in vertical_tokens):
        if "Izq" in name:
            base["bom_canto_der"] = True
            return base
        if "Der" in name:
            base["bom_canto_izq"] = True
            return base
        base["bom_canto_izq"] = True
        return base

    if any(token in name for token in horizontal_tokens):
        base["bom_canto_inf"] = True
        return base

    return base


def choose_row(suffix, rows):
    normalized = suffix.lower()
    for row in rows or []:
        piece = (row.get("pieza") or "").lower()
        if piece and piece in normalized:
            return row
    return rows[0] if rows else None


def directional_cantos_flags(name, category, cantos):
    text = (cantos or "").strip().lower()
    base = dict(bom_canto_izq=False, bom_canto_der=False, bom_canto_sup=False, bom_canto_inf=False)
    if text == "4 cantos":
        return dict(bom_canto_izq=True, bom_canto_der=True, bom_canto_sup=True, bom_canto_inf=True)
    if text != "canto frente":
        return base

    vertical_tokens = ("Lateral", "Parante", "Division", "Divisor")
    horizontal_tokens = ("Piso", "Tapa", "Techo", "Estante", "Soporte")

    if any(token in name for token in vertical_tokens):
        if "Izq" in name:
            base["bom_canto_der"] = True
            return base
        if "Der" in name:
            base["bom_canto_izq"] = True
            return base
        base["bom_canto_izq"] = True
        return base

    if any(token in name for token in horizontal_tokens):
        base["bom_canto_inf"] = True
        return base

    return base


for module, module_payload in PAYLOAD.items():
    fcstd = Path(module_payload["__fcstd__"]["path"])
    doc = App.openDocument(str(fcstd))
    try:
        for obj in doc.Objects:
            if not hasattr(obj, "Shape") or obj.Shape.isNull():
                continue
            name = str(getattr(obj, "Name", ""))
            if "_" not in name:
                continue
            code, suffix = name.split("_", 1)

            ensure_prop(obj, "App::PropertyBool", "bom_include")
            obj.bom_include = True

            if suffix.endswith("_Preview"):
                obj.bom_include = False
                continue

            rows = module_payload.get(code, {{}}).get("rows", [])
            row = choose_row(suffix, rows)
            category = (row.get("categoria") if row else infer_category(name))
            cantos = infer_cantos_from_name(name, category)

            data = {{
                "bom_codigo": code,
                "bom_pieza": suffix,
                "bom_categoria": category,
                "bom_cantos": cantos,
            }}

            if row:
                for key in ("largo_mm", "ancho_mm", "espesor_mm", "bisagras_cazoleta"):
                    raw = (row.get(key) or "").strip()
                    if raw:
                        data[f"bom_{{key}}"] = float(raw)

            for prop_name, value in directional_cantos_flags(name, category, data["bom_cantos"]).items():
                ensure_prop(obj, "App::PropertyBool", prop_name)
                setattr(obj, prop_name, value)

            for prop_name, value in data.items():
                if isinstance(value, bool):
                    prop_type = "App::PropertyBool"
                elif isinstance(value, int):
                    prop_type = "App::PropertyInteger"
                elif isinstance(value, float):
                    prop_type = "App::PropertyFloat"
                else:
                    prop_type = "App::PropertyString"
                ensure_prop(obj, prop_type, prop_name)
                setattr(obj, prop_name, value)

        doc.recompute()
        doc.save()
        print(fcstd)
    finally:
        App.closeDocument(doc.Name)
"""

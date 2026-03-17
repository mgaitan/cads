#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FCSTD_DIR = ROOT / "models" / "fcstd"
STEP_DIR = ROOT / "models" / "step"
BOM_DIR = ROOT / "bom"

MODEL_CODES = [
    "ENS",
    "ENSI",
    "FULL",
    "H",
    "AA",
    "AB",
    "L",
    "BA",
    "BB",
    "F",
    "I",
    "R",
    "M",
]

BOM_MODULES = {"H", "AA", "AB", "L", "BA", "BB", "F", "I", "R", "M"}

FCSTD_OVERRIDES = {
    "I": FCSTD_DIR / "variants" / "I" / "alt-02.FCStd",
}

CATEGORY_RULES = [
    ("AC_", "AC_Paraiso"),
    ("AB_", "AB_Blanco"),
    ("AA_", "AA_Blanco"),
    ("BA_", "BA_Blanco"),
    ("BB_", "BB_Blanco"),
    ("L_", "L_Blanco"),
    ("H_", "H_Blanco"),
    ("R_", "R_Blanco"),
    ("Gola", "Herraje"),
    ("Pata", "Herraje"),
    ("Mesada", "Mesada"),
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

CANTOS_RULES = [
    ("Gola", "Aluminio"),
    ("Pata", "PVC/Aluminio"),
    ("Puerta", "4 cantos"),
    ("Frente", "4 cantos"),
    ("Fondo_3mm", "Sin canto"),
    ("Fondo_6mm", "Fondo clavado pasante"),
    ("Regrueso", "Crudo (cinta 36mm en obra)"),
    ("Estante", "Canto frente"),
    ("Soporte", "Canto frente"),
    ("Piso", "Canto frente"),
    ("Lateral", "Canto frente"),
    ("Division", "Canto frente"),
    ("Divisor", "Canto frente"),
    ("Parante", "Canto frente"),
]


def existing_bom_metadata() -> dict[str, dict[str, dict[str, object]]]:
    by_module: dict[str, dict[str, dict[str, object]]] = {}
    for path in sorted(BOM_DIR.glob("*_bom.csv")):
        module = path.stem.replace("_bom", "")
        rows: dict[str, dict[str, object]] = {}
        with path.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                code = (row.get("codigo") or "").strip()
                if not code or code == "TOTAL":
                    continue
                qty = int(float(row.get("cantidad", "0") or 0) or 1)
                ml_total = float(row.get("ml_gola", "0") or 0)
                hinges_total = int(float(row.get("bisagras_cazoleta", "0") or 0) or 0)
                rows[code] = {
                    "codigo": code,
                    "categoria": (row.get("categoria") or "").strip(),
                    "pieza": (row.get("pieza") or "").strip(),
                    "cantos": (row.get("cantos") or "").strip(),
                    "ml_per_unit": (ml_total / qty) if qty else 0.0,
                    "hinges_per_unit": (hinges_total / qty) if qty else 0.0,
                }
        by_module[module] = rows
    return by_module


def build_freecad_script(
    fcstd_map: dict[str, str],
    bom_modules: list[str],
    existing_meta: dict[str, dict[str, dict[str, object]]],
) -> str:
    return f"""import csv
from pathlib import Path

import FreeCAD as App
import Mesh
import Part

ROOT = Path({ROOT.as_posix()!r})
FCSTD_MAP = {fcstd_map!r}
BOM_MODULES = set({bom_modules!r})
EXISTING_META = {existing_meta!r}
CATEGORY_RULES = {CATEGORY_RULES!r}
CANTOS_RULES = {CANTOS_RULES!r}


def infer_category(piece: str) -> str:
    for needle, category in CATEGORY_RULES:
        if needle in piece:
            return category
    return "Casco"


def infer_cantos(piece: str) -> str:
    for needle, cantos in CANTOS_RULES:
        if needle in piece:
            return cantos
    return "Sin canto"


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


def bbox_dims(obj) -> tuple[float, float, float]:
    bb = obj.Shape.BoundBox
    dims = sorted([float(bb.XLength), float(bb.YLength), float(bb.ZLength)], reverse=True)
    return dims[0], dims[1], dims[2]


def allowed_prefixes(module: str) -> tuple[str, ...]:
    if module == "AB":
        return ("AB", "AC")
    return (module,)


def export_shape_objects(doc, module: str):
    out = []
    prefixes = allowed_prefixes(module)
    for obj in doc.Objects:
        try:
            if not hasattr(obj, "Shape") or obj.Shape.isNull():
                continue
            name = str(getattr(obj, "Name", ""))
            if module in ("ENS", "ENSI", "FULL"):
                out.append(obj)
                continue
            if "_" not in name:
                continue
            code = name.split("_", 1)[0]
            if any(code.startswith(prefix) for prefix in prefixes):
                out.append(obj)
        except Exception:
            pass
    return out


for module, fcstd_path in FCSTD_MAP.items():
    doc = App.openDocument(fcstd_path)
    objects = export_shape_objects(doc, module)

    step_path = ROOT / "models" / "step" / f"{{module}}.step"
    step_path.parent.mkdir(parents=True, exist_ok=True)
    Part.export(objects, str(step_path))

    if module in BOM_MODULES:
        module_meta = EXISTING_META.get(module, {{}})
        rows = []
        for obj in objects:
            name = str(getattr(obj, "Name", ""))
            if "_" not in name:
                continue
            obj_code, suffix = name.split("_", 1)
            meta = module_meta.get(obj_code, {{}})
            include_in_bom = prop_is_true(read_prop(obj, "bom_include", True))
            if suffix.endswith("_Preview") or not include_in_bom:
                continue
            largo, ancho, espesor = bbox_dims(obj)
            code = str(read_prop(obj, "bom_codigo", meta.get("codigo", obj_code)))
            piece = str(read_prop(obj, "bom_pieza", meta.get("pieza", suffix)))
            category = str(read_prop(obj, "bom_categoria", meta.get("categoria", infer_category(piece))))
            cantos = str(read_prop(obj, "bom_cantos", meta.get("cantos", infer_cantos(piece))))
            qty = int(read_prop(obj, "bom_cantidad", 1))
            largo = float(read_prop(obj, "bom_largo_mm", largo))
            ancho = float(read_prop(obj, "bom_ancho_mm", ancho))
            espesor = float(read_prop(obj, "bom_espesor_mm", espesor))
            ml_per_unit = float(read_prop(obj, "bom_ml_gola", meta.get("ml_per_unit", 0.0)) or 0.0)
            hinges_per_unit = float(read_prop(obj, "bom_bisagras_cazoleta", meta.get("hinges_per_unit", 0.0)) or 0.0)
            rows.append({{
                "codigo": code,
                "categoria": category,
                "pieza": piece,
                "cantidad": qty,
                "largo_mm": largo,
                "ancho_mm": ancho,
                "espesor_mm": espesor,
                "cantos": cantos,
                "ml_gola": ml_per_unit,
                "bisagras_cazoleta": hinges_per_unit,
            }})

        grouped = {{}}
        for row in rows:
            key = (
                row["codigo"],
                row["categoria"],
                row["pieza"],
                round(row["largo_mm"], 1),
                round(row["ancho_mm"], 1),
                round(row["espesor_mm"], 1),
                row["cantos"],
            )
            current = grouped.setdefault(
                key,
                {{"cantidad": 0, "ml_gola": 0.0, "bisagras_cazoleta": 0.0}},
            )
            current["cantidad"] += int(row["cantidad"])
            current["ml_gola"] += float(row["ml_gola"]) * int(row["cantidad"])
            current["bisagras_cazoleta"] += float(row["bisagras_cazoleta"]) * int(row["cantidad"])

        out_rows = []
        total_gola = 0.0
        total_hinges = 0
        for key, agg in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][2])):
            code, category, piece, largo, ancho, espesor, cantos = key
            ml_value = round(agg["ml_gola"], 3)
            hinges_value = int(round(agg["bisagras_cazoleta"]))
            total_gola += ml_value
            total_hinges += hinges_value
            out_rows.append({{
                "codigo": code,
                "categoria": category,
                "pieza": piece,
                "cantidad": str(agg["cantidad"]),
                "largo_mm": f"{{largo:.1f}}",
                "ancho_mm": f"{{ancho:.1f}}",
                "espesor_mm": f"{{espesor:.1f}}",
                "cantos": cantos,
                "ml_gola": f"{{ml_value:.3f}}" if ml_value else "",
                "bisagras_cazoleta": str(hinges_value) if hinges_value else "",
            }})

        bom_path = ROOT / "bom" / f"{{module}}_bom.csv"
        bom_path.parent.mkdir(parents=True, exist_ok=True)
        with bom_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
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
                ],
            )
            writer.writeheader()
            writer.writerows(out_rows)
            writer.writerow(
                {{
                    "codigo": "TOTAL",
                    "categoria": "Resumen",
                    "pieza": "Totales_Herrajes",
                    "cantidad": "",
                    "largo_mm": "",
                    "ancho_mm": "",
                    "espesor_mm": "",
                    "cantos": "",
                    "ml_gola": f"{{total_gola:.3f}}",
                    "bisagras_cazoleta": str(total_hinges),
                }}
            )
        print(bom_path.relative_to(ROOT))

    print(step_path.relative_to(ROOT))
    App.closeDocument(doc.Name)
"""


def run_freecad(script_text: str) -> int:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(script_text)
        tmp_path = Path(tmp.name)

    env = os.environ.copy()
    env.setdefault("APPIMAGE_EXTRACT_AND_RUN", "1")
    env.setdefault("FREECAD_NO_GUI", "1")

    try:
        proc = subprocess.run(
            ["freecad", "-c", str(tmp_path)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


def main() -> int:
    fcstd_map = {}
    for code in MODEL_CODES:
        path = FCSTD_OVERRIDES.get(code, FCSTD_DIR / f"{code}.FCStd")
        if path.exists():
            fcstd_map[code] = str(path.resolve())
    if not fcstd_map:
        print("No hay FCStd para exportar.", file=sys.stderr)
        return 1
    rc = run_freecad(
        build_freecad_script(
            fcstd_map=fcstd_map,
            bom_modules=sorted(BOM_MODULES),
            existing_meta=existing_bom_metadata(),
        )
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

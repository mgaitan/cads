#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "outputs" / "variants"

CATEGORY_RULES = [
    ("Gola", "Herraje"),
    ("Pata", "Herraje"),
    ("Mesada", "Mesada"),
    ("Cajon_", "Cajon"),
    ("Frente_Caja", "Cajon"),
    ("Trasera_Caja", "Cajon"),
    ("Fondo_Cajonera", "Casco"),
    ("Soporte", "Casco"),
    ("Piso", "Casco"),
    ("Lateral", "Casco"),
    ("Division", "Division"),
    ("Divisor", "Division"),
    ("Parante", "Division"),
    ("Fondo", "Fondo"),
    ("Estante", "Nicho"),
    ("Faja", "Nicho"),
    ("Nicho", "Nicho"),
    ("Pano", "Frente"),
    ("Paño", "Frente"),
    ("Puerta", "Frente"),
    ("Frente", "Frente"),
    ("Cajon", "Cajon"),
]

CANTOS_RULES = [
    ("Gola", "Aluminio"),
    ("Pata", "PVC/Aluminio"),
    ("Soporte_Sup_Frente", "Canto frente"),
    ("Frente_Cajon", "4 cantos"),
    ("Frente_Caja", "Sin canto"),
    ("Trasera_Caja", "Sin canto"),
    ("Cajon_", "Sin canto"),
    ("Pano", "4 cantos"),
    ("Paño", "4 cantos"),
    ("Puerta", "4 cantos"),
    ("Frente", "4 cantos"),
    ("Fondo_6mm", "Fondo clavado pasante"),
    ("Fondo_3mm", "Sin canto"),
    ("Fondo_Cajonera", "Canto frente"),
    ("Estante", "Canto frente"),
    ("Faja", "Canto frente"),
    ("Lateral", "Canto frente"),
    ("Division", "Canto frente"),
    ("Divisor", "Canto frente"),
    ("Parante", "Canto frente"),
    ("Piso", "Canto frente"),
    ("Soporte_Sup_Fondo", "Sin canto"),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Exporta bundle de variante desde FCStd.")
    p.add_argument("fcstd", type=Path, help="Ruta al archivo FCStd fuente.")
    p.add_argument("--module", required=True, help="Codigo de modulo, por ejemplo I.")
    p.add_argument(
        "--variant",
        required=True,
        help="Slug de variante, por ejemplo alt-01.",
    )
    p.add_argument(
        "--title",
        help="Titulo para web. Por defecto usa '<module> <variant>'.",
    )
    p.add_argument(
        "--out-root",
        type=Path,
        default=DEFAULT_OUT,
        help="Raiz de salida para variantes.",
    )
    return p.parse_args()


def build_freecad_script(
    fcstd_path: Path,
    module: str,
    variant: str,
    title: str,
    out_dir: Path,
) -> str:
    return f"""import csv
import json
from pathlib import Path

import FreeCAD as App
import Mesh
import Part

FCSTD = Path({fcstd_path.as_posix()!r})
MODULE = {module!r}
VARIANT = {variant!r}
TITLE = {title!r}
OUT_DIR = Path({out_dir.as_posix()!r})
OUT_DIR.mkdir(parents=True, exist_ok=True)


def infer_category(piece: str) -> str:
    rules = {CATEGORY_RULES!r}
    for needle, category in rules:
        if needle in piece:
            return category
    return "Referencia"


def infer_cantos(piece: str) -> str:
    rules = {CANTOS_RULES!r}
    for needle, cantos in rules:
        if needle in piece:
            return cantos
    return "Sin canto"


def infer_quantity(piece: str) -> int:
    if piece.startswith("Pata_"):
        return 1
    return 1


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


doc = App.openDocument(str(FCSTD))
rows = []
objects_for_export = []
for obj in doc.Objects:
    shape = getattr(obj, "Shape", None)
    if not shape or shape.isNull():
        continue
    name = str(getattr(obj, "Name", ""))
    if "_" not in name:
        continue
    code, piece = name.split("_", 1)
    if not code.startswith(MODULE):
        continue
    include_in_bom = prop_is_true(read_prop(obj, "bom_include", True))
    if not include_in_bom:
        objects_for_export.append(obj)
        continue
    largo, ancho, espesor = bbox_dims(obj)
    code = str(read_prop(obj, "bom_codigo", code))
    piece = str(read_prop(obj, "bom_pieza", piece))
    category = str(read_prop(obj, "bom_categoria", infer_category(piece)))
    cantos = str(read_prop(obj, "bom_cantos", infer_cantos(piece)))
    qty = int(read_prop(obj, "bom_cantidad", infer_quantity(piece)))
    largo = float(read_prop(obj, "bom_largo_mm", largo))
    ancho = float(read_prop(obj, "bom_ancho_mm", ancho))
    espesor = float(read_prop(obj, "bom_espesor_mm", espesor))
    ml_gola_value = read_prop(obj, "bom_ml_gola", None)
    hinges_value = read_prop(obj, "bom_bisagras_cazoleta", None)
    ml_gola = ""
    hinges = ""
    if ml_gola_value is not None:
        ml_gola = f"{{float(ml_gola_value):.3f}}"
    elif category == "Herraje" and "Gola" in piece:
        ml_gola = f"{{largo / 1000.0:.3f}}"
    if hinges_value is not None:
        hinges = str(int(hinges_value))
    elif category == "Frente" and "Puerta" in piece:
        hinges = "3" if max(largo, ancho) >= 900.0 else "2"
    rows.append({{
        "codigo": code,
        "categoria": category,
        "pieza": piece,
        "cantidad": str(qty),
        "largo_mm": f"{{largo:.1f}}",
        "ancho_mm": f"{{ancho:.1f}}",
        "espesor_mm": f"{{espesor:.1f}}",
        "cantos": cantos,
        "ml_gola": ml_gola,
        "bisagras_cazoleta": hinges,
    }})
    objects_for_export.append(obj)

grouped = {{}}
for row in rows:
    key = (
        row["codigo"],
        row["categoria"],
        row["pieza"],
        row["largo_mm"],
        row["ancho_mm"],
        row["espesor_mm"],
        row["cantos"],
    )
    current = grouped.setdefault(
        key,
        {{
            "cantidad": 0,
            "ml_gola": 0.0,
            "bisagras_cazoleta": 0,
        }},
    )
    current["cantidad"] += int(row["cantidad"])
    if row["ml_gola"]:
        current["ml_gola"] += float(row["ml_gola"])
    if row["bisagras_cazoleta"]:
        current["bisagras_cazoleta"] += int(row["bisagras_cazoleta"])

rows = []
for key, agg in grouped.items():
    codigo, categoria, pieza, largo, ancho, espesor, cantos = key
    rows.append(
        {{
            "codigo": codigo,
            "categoria": categoria,
            "pieza": pieza,
            "cantidad": str(agg["cantidad"]),
            "largo_mm": largo,
            "ancho_mm": ancho,
            "espesor_mm": espesor,
            "cantos": cantos,
            "ml_gola": f'{{agg["ml_gola"]:.3f}}' if agg["ml_gola"] else "",
            "bisagras_cazoleta": str(agg["bisagras_cazoleta"]) if agg["bisagras_cazoleta"] else "",
        }}
    )

rows.sort(key=lambda r: (r["codigo"], r["pieza"]))

total_gola = 0.0
total_hinges = 0
for row in rows:
    if row["ml_gola"]:
        total_gola += float(row["ml_gola"])
    if row["bisagras_cazoleta"]:
        total_hinges += int(row["bisagras_cazoleta"]) * int(row["cantidad"])

bom_path = OUT_DIR / f"{{MODULE}}_{{VARIANT}}_bom.csv"
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
    writer.writerows(rows)
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

step_path = OUT_DIR / f"{{MODULE}}_{{VARIANT}}.step"
stl_path = OUT_DIR / f"{{MODULE}}_{{VARIANT}}.stl"
Part.export(objects_for_export, str(step_path))
Mesh.export(objects_for_export, str(stl_path))

manifest = {{
    "module": MODULE,
    "variant": VARIANT,
    "title": TITLE,
    "fcstd": str(FCSTD.relative_to(Path({ROOT.as_posix()!r}))),
    "bom_csv": str(bom_path.relative_to(Path({ROOT.as_posix()!r}))),
    "step": str(step_path.relative_to(Path({ROOT.as_posix()!r}))),
    "stl": str(stl_path.relative_to(Path({ROOT.as_posix()!r}))),
    "object_count": len(objects_for_export),
}}
manifest_path = OUT_DIR / "manifest.json"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

print(manifest_path)
print(bom_path)
print(step_path)
print(stl_path)
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
    args = parse_args()
    fcstd = args.fcstd.resolve()
    if not fcstd.exists():
        print(f"No existe FCStd: {fcstd}", file=sys.stderr)
        return 1

    title = args.title or f"{args.module} {args.variant}"
    out_dir = args.out_root.resolve() / args.module / args.variant
    out_dir.mkdir(parents=True, exist_ok=True)

    rc = run_freecad(
        build_freecad_script(
            fcstd_path=fcstd,
            module=args.module,
            variant=args.variant,
            title=title,
            out_dir=out_dir,
        )
    )
    if rc != 0:
        return rc

    manifest = out_dir / "manifest.json"
    if not manifest.exists():
        print(f"No se genero manifest: {manifest}", file=sys.stderr)
        return 1
    print(manifest.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

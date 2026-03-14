#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Agrega metadata BOM al modulo I en FCStd.")
    p.add_argument("fcstd", type=Path, help="Ruta al FCStd a etiquetar.")
    return p.parse_args()


def build_script(fcstd: Path) -> str:
    metadata = {
        "I1_Lateral_Izq_Frente": {
            "bom_codigo": "I1",
            "bom_pieza": "Lateral_Izq_Frente",
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I1B_Lateral_Izq_Trasero": {
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I1C_Fondo_Cajonera": {
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I2_Lateral_Der": {
            "bom_codigo": "I2",
            "bom_pieza": "Lateral_Der",
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I3_Division_1": {
            "bom_codigo": "I3",
            "bom_pieza": "Divisor_1",
            "bom_categoria": "Division",
            "bom_cantos": "Canto frente",
        },
        "I4_Division_2": {
            "bom_codigo": "I4",
            "bom_pieza": "Divisor_2",
            "bom_categoria": "Division",
            "bom_cantos": "Canto frente",
        },
        "I5_Piso_Izq": {
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I6_Piso_Der": {
            "bom_codigo": "I6",
            "bom_pieza": "Piso_Der",
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I8_Estante_Regulable_Bacha": {
            "bom_codigo": "I8",
            "bom_pieza": "Estante_Regulable_Bacha",
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I8B_Piso_Removible_Lavavajillas": {
            "bom_codigo": "I8B",
            "bom_pieza": "Piso_Removible_Lavavajillas",
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I8C_Piso_Falso_Lavavajillas": {
            "bom_codigo": "I8C",
            "bom_pieza": "Piso_Falso_Lavavajillas",
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I8_Estante_Nicho_Regulable": {
            "bom_codigo": "I8",
            "bom_pieza": "Estante_Nicho_Regulable",
            "bom_categoria": "Nicho",
            "bom_cantos": "Canto frente",
        },
        "I8B_Faja_Superior_Nicho": {
            "bom_codigo": "I8B",
            "bom_pieza": "Faja_Superior_Nicho",
            "bom_categoria": "Nicho",
            "bom_cantos": "Canto frente",
        },
        "I8C_Faja_Frontal_Estante_Nicho": {
            "bom_codigo": "I8C",
            "bom_pieza": "Faja_Frontal_Estante_Nicho",
            "bom_categoria": "Nicho",
            "bom_cantos": "Canto frente",
        },
        "I9_Soporte_Sup_Frente": {
            "bom_categoria": "Casco",
            "bom_cantos": "Canto frente",
        },
        "I10_Soporte_Sup_Fondo": {
            "bom_categoria": "Casco",
            "bom_cantos": "Sin canto",
        },
        "I12_Gola_J_Superior": {
            "bom_codigo": "I12",
            "bom_pieza": "Gola_J_Superior",
            "bom_categoria": "Herraje",
            "bom_cantos": "Aluminio",
        },
        "I13_Gola_C_Cajon_Medio_Bajo": {
            "bom_codigo": "I13",
            "bom_pieza": "Gola_C_Izq",
            "bom_categoria": "Herraje",
            "bom_cantos": "Aluminio",
        },
        "I14_Frente_Cajon_Sup_Izq": {
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
        },
        "I15_Frente_Cajon_Med_Izq": {
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
        },
        "I16_Frente_Cajon_Inf_Izq": {
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
        },
        "I17_Frente_Lavavajillas": {
            "bom_codigo": "I17",
            "bom_pieza": "Frente_Lavavajillas",
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
        },
        "I17_Puerta_Lavavajillas": {
            "bom_codigo": "I17",
            "bom_pieza": "Puerta_Lavavajillas",
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
            "bom_bisagras_cazoleta": 2,
        },
        "I17_Puerta_Izq": {
            "bom_include": False,
        },
        "I18_Puerta_Der": {
            "bom_codigo": "I18",
            "bom_pieza": "Puerta_Der",
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
            "bom_bisagras_cazoleta": 2,
        },
        "I18_Puerta_Bacha_Izq": {
            "bom_codigo": "I18",
            "bom_pieza": "Puerta_Bacha_Izq",
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
            "bom_bisagras_cazoleta": 2,
        },
        "I18B_Puerta_Bacha_Der": {
            "bom_codigo": "I18B",
            "bom_pieza": "Puerta_Bacha_Der",
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
            "bom_bisagras_cazoleta": 2,
        },
        "I18B_Pano_Fijo_Der": {
            "bom_codigo": "I18B",
            "bom_pieza": "Pano_Fijo_Der",
            "bom_categoria": "Frente",
            "bom_cantos": "4 cantos",
        },
        "I20_Mesada_Calado_Bacha": {
            "bom_codigo": "I22",
            "bom_pieza": "Mesada_Calado_Bacha_536x396",
            "bom_categoria": "Mesada",
            "bom_cantos": "Pulido perimetral segun proveedor",
            "bom_largo_mm": 1580.0,
            "bom_ancho_mm": 688.0,
            "bom_espesor_mm": 30.0,
        },
    }

    drawer_groups = {
        "I19": "Sup",
        "I20": "Med",
        "I21": "Inf",
    }

    return f"""import FreeCAD as App
from pathlib import Path

FCSTD = Path({fcstd.as_posix()!r})

doc = App.openDocument(str(FCSTD))

metadata = {metadata!r}
drawer_groups = {drawer_groups!r}

def ensure_prop(obj, type_name, prop_name):
    if prop_name not in getattr(obj, "PropertiesList", []):
        obj.addProperty(type_name, prop_name, "BOM", prop_name)

for obj in doc.Objects:
    name = getattr(obj, "Name", "")
    if not hasattr(obj, "Shape") or obj.Shape.isNull():
        continue

    ensure_prop(obj, "App::PropertyBool", "bom_include")
    obj.bom_include = True

    if name.endswith("_Preview"):
        obj.bom_include = False
        continue

    if name in metadata:
        data = metadata[name]
    elif name.startswith("I11_Pata_"):
        code = "I11"
        piece = "Pata_80"
        data = {{
            "bom_codigo": code,
            "bom_pieza": piece,
            "bom_categoria": "Herraje",
            "bom_cantos": "PVC/Aluminio",
            "bom_largo_mm": 40.0,
            "bom_ancho_mm": 40.0,
            "bom_espesor_mm": 80.0,
        }}
    elif any(name.startswith(prefix + "_") for prefix in drawer_groups):
        code = name.split("_", 1)[0]
        group = drawer_groups[code]
        suffix = name[len(code) + 1 :]
        if suffix.endswith("_Fondo_6mm"):
            piece = f"{{code}}_Cajon_{{group}}_Fondo_6mm"
            category = "Cajon"
            cantos = "Fondo clavado pasante"
        elif suffix.endswith("_Frente_Caja"):
            piece = f"{{code}}_Cajon_{{group}}_Frente_Trasera"
            category = "Cajon"
            cantos = "Sin canto"
        elif suffix.endswith("_Trasera_Caja"):
            piece = f"{{code}}_Cajon_{{group}}_Frente_Trasera"
            category = "Cajon"
            cantos = "Sin canto"
        elif suffix.endswith("_Lateral_Izq") or suffix.endswith("_Lateral_Der"):
            piece = f"{{code}}_Cajon_{{group}}_Lateral"
            category = "Cajon"
            cantos = "Sin canto"
        else:
            piece = suffix
            category = "Cajon"
            cantos = "Sin canto"
        data = {{
            "bom_codigo": code,
            "bom_pieza": piece,
            "bom_categoria": category,
            "bom_cantos": cantos,
        }}
    else:
        continue

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
print(FCSTD)
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
    return run_freecad(build_script(fcstd))


if __name__ == "__main__":
    raise SystemExit(main())

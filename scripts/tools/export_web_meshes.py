#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STEP_DIR = ROOT / "models" / "step"
OUT_DIR = ROOT / "outputs" / "web_models"

MODEL_CODES = ["ENS", "ENSI", "H", "AA", "AB", "L", "BA", "BB", "F", "I", "M"]


def build_freecad_script(pairs: list[tuple[Path, Path]]) -> str:
    serialized = ",\n    ".join(
        f"({src.as_posix()!r}, {dst.as_posix()!r})" for src, dst in pairs
    )
    return f"""import FreeCAD as App
import Part
import Mesh

pairs = [
    {serialized}
]

for src, dst in pairs:
    doc = App.newDocument('web_mesh')
    shape = Part.read(src)
    obj = doc.addObject('Part::Feature', 'Model')
    obj.Shape = shape
    Mesh.export([obj], dst)
    App.closeDocument(doc.Name)
    print(dst)
"""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs: list[tuple[Path, Path]] = []
    for code in MODEL_CODES:
        src = STEP_DIR / f"{code}.step"
        if src.exists():
            pairs.append((src, OUT_DIR / f"{code}.stl"))

    if not pairs:
        print("No hay STEP para exportar.", file=sys.stderr)
        return 1

    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(build_freecad_script(pairs))
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

    missing = [
        dst.name for _, dst in pairs if not dst.exists() or dst.stat().st_size == 0
    ]
    if missing:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        print(f"Faltan STL generados: {', '.join(missing)}", file=sys.stderr)
        return proc.returncode or 1

    for _, dst in pairs:
        print(dst.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

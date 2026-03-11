#!/usr/bin/env python3
"""Arma ENSI (ensamble isla) con modulos I + F.

Salida:
  - models/fcstd/ENSI.FCStd
  - models/step/ENSI.step
"""

import os
from pathlib import Path

import FreeCAD as App
import Part


def add_step(doc, name, step_path, x=0.0, y=0.0, z=0.0):
    shape = Part.read(step_path)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def main():
    script_path = globals().get("__file__")
    if script_path:
        root = Path(script_path).resolve().parents[2]
    else:
        root = Path(os.getcwd())

    step_dir = root / "models" / "step"
    out_fcstd_dir = root / "models" / "fcstd"
    out_step_dir = root / "models" / "step"
    out_fcstd_dir.mkdir(parents=True, exist_ok=True)
    out_step_dir.mkdir(parents=True, exist_ok=True)

    # Vista de frente isla: I + F
    # I (1540) a la izquierda, F (780) a la derecha.
    x_i = 0.0
    x_f = 1540.0

    doc = App.newDocument("IslaEnsamble")
    objs = []
    objs.append(add_step(doc, "I_Bajo_Isla", str(step_dir / "I.step"), x_i, 0, 0))
    objs.append(add_step(doc, "F_Fridge_Modular", str(step_dir / "F.step"), x_f, 0, 0))

    doc.recompute()

    fcstd = out_fcstd_dir / "ENSI.FCStd"
    step = out_step_dir / "ENSI.step"
    doc.saveAs(str(fcstd))
    Part.export(objs, str(step))

    print("Ensamble isla generado:")
    print("-", fcstd)
    print("-", step)
    print("\nLayout frontal:")
    print("- I: x=0..1540")
    print("- F: x=1540..2320")


if __name__ == "__main__":
    main()

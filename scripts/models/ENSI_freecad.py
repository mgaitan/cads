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


def add_step(doc, name, step_path, x=0.0, y=0.0, z=0.0, rot_z=0.0):
    shape = Part.read(step_path)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.Placement = App.Placement(
        App.Vector(x, y, z), App.Rotation(App.Vector(0, 0, 1), rot_z)
    )
    return obj


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
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
    i_w = 1540.0
    f_w = 780.0
    f_d = 950.0
    i_d = 650.0
    wall_th = 150.0
    wall_h = 1080.0
    bar_th = 30.0
    bar_w = 370.0
    bar_len = i_w + 20.0

    doc = App.newDocument("IslaEnsamble")
    objs = []
    objs.append(add_step(doc, "I_Bajo_Isla", str(step_dir / "I.step"), x_i, 0, 0))
    # Rotado 180° y recolocado para conservar su huella en x=1540..2320 / y=0..950.
    objs.append(
        add_step(
            doc,
            "F_Fridge_Modular",
            str(step_dir / "F.step"),
            x_i + i_w + f_w,
            f_d,
            0,
            180.0,
        )
    )
    wall_y = i_d
    objs.append(add_box(doc, "ENSI_Muro_Fondo_Heladera", 0, wall_y, 0, i_w, wall_th, wall_h))
    objs.append(
        add_box(
            doc,
            "ENSI_Barra_Sobre_Muro",
            -20.0,
            wall_y - 50.0,
            wall_h,
            bar_len,
            bar_w,
            bar_th,
        )
    )

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
    print(f"- Muro: x=0..1540, y={wall_y:.0f}..{wall_y + wall_th:.0f}, h=1080")
    print(f"- Barra: x=-20..{bar_len - 20.0:.0f}, y={wall_y - 50.0:.0f}..{wall_y - 50.0 + bar_w:.0f}, esp=30")


if __name__ == "__main__":
    main()

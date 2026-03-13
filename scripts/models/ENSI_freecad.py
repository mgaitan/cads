#!/usr/bin/env python3
"""Arma ENSI (ensamble isla) con modulos R + I + F y apoyo de muros/barra."""

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

    r_w = 800.0
    r_d = 450.0
    r_wall_h = 1080.0
    r_wall_th = 150.0

    col_w = 210.0
    col_d = 210.0
    paso_w = 820.0

    i_w = 1540.0
    i_d = 650.0
    i_wall_th = 150.0
    i_wall_h = 1080.0

    f_w = 780.0
    f_d = 950.0

    bar_th = 30.0
    r_bar_d = 250.0
    i_bar_d = 370.0

    x_r = 0.0
    y_r = i_d - r_d
    x_col = x_r + r_w
    x_i = x_col + col_w + paso_w
    x_f_place = x_i + i_w + f_w  # para rotacion 180, deja huella x_i+i_w .. +f_w

    doc = App.newDocument("IslaEnsamble")
    objs = []

    objs.append(add_step(doc, "R_Rinconera", str(step_dir / "R.step"), x_r, y_r, 0))
    objs.append(add_step(doc, "I_Bajo_Isla", str(step_dir / "I.step"), x_i, 0, 0))
    objs.append(
        add_step(
            doc,
            "F_Fridge_Modular",
            str(step_dir / "F.step"),
            x_f_place,
            f_d,
            0,
            180.0,
        )
    )

    # Muro de fondo de R
    objs.append(
        add_box(doc, "ENSI_Muro_Fondo_R", x_r, i_d, 0, r_w, r_wall_th, r_wall_h)
    )
    objs.append(
        add_box(doc, "ENSI_Barra_R", x_r, i_d - 50.0, r_wall_h, r_w, r_bar_d, bar_th)
    )

    # Columna intermedia 250x250, con avance hacia el frente respecto de la linea del muro de I.
    objs.append(
        add_box(
            doc,
            "ENSI_Columna",
            x_col,
            i_d - col_d + i_wall_th,
            0,
            col_w,
            col_d,
            HEIGHT := 2400.0,
        )
    )

    # Muro de fondo de I
    objs.append(
        add_box(doc, "ENSI_Muro_Fondo_I", x_i, i_d, 0, i_w, i_wall_th, i_wall_h)
    )
    objs.append(
        add_box(
            doc,
            "ENSI_Barra_I",
            x_i - 20.0,
            i_d - 50.0,
            i_wall_h,
            i_w + 20.0,
            i_bar_d,
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
    print(f"- R: x={x_r:.0f}..{x_r + r_w:.0f}")
    print(f"- Columna: x={x_col:.0f}..{x_col + col_w:.0f}")
    print(f"- Paso libre: x={x_col + col_w:.0f}..{x_i:.0f}")
    print(f"- I: x={x_i:.0f}..{x_i + i_w:.0f}")
    print(f"- F: x={x_i + i_w:.0f}..{x_i + i_w + f_w:.0f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Arma FULL parcial: ENSI + muro ventana + ENS."""

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


def add_wall_with_window(doc, name, x, y, z, dx, dy, dz, win_y0, win_w, sill_z, win_h):
    wall = Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
    hole = Part.makeBox(
        dx + 2.0,
        win_w,
        win_h,
        App.Vector(x - 1.0, y + win_y0, sill_z),
    )
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = wall.cut(hole)
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

    # Convencion de planta:
    # - x=0 en lateral izquierdo de R
    # - se evita usar Y negativos
    # - el muro izquierdo crece en +Y, y ENSI se desplaza para tocarlo en su extremo superior
    ensi_wall_face_y = 650.0
    wall_th = 300.0
    wall_x = -wall_th
    wall_y = 0.0
    wall_len = 2820.0
    wall_h = 2400.0
    ensi_x = 0.0
    ensi_y = wall_len - ensi_wall_face_y

    win_offset = 560.0
    win_w = 1100.0
    win_h = 1200.0
    win_sill_z = 800.0

    doc = App.newDocument("CocinaFull")
    objs = []

    objs.append(
        add_step(
            doc, "FULL_ENSI", str(step_dir / "ENSI.step"), ensi_x, ensi_y, 0.0, 0.0
        )
    )
    # ENS rotado 180 para que L quede a la izquierda tocando el muro de ventana.
    # Se fija la cota del fondo de AA/AB a 2230 mm del fondo de I.
    ens_x = 3820.0
    ens_y = 1190.0
    objs.append(
        add_step(
            doc,
            "FULL_ENS",
            str(step_dir / "ENS.step"),
            ens_x,
            ens_y,
            0.0,
            180.0,
        )
    )
    objs.append(
        add_wall_with_window(
            doc,
            "FULL_Muro_Izquierdo",
            wall_x,
            wall_y,
            0.0,
            wall_th,
            wall_len,
            wall_h,
            win_offset,
            win_w,
            win_sill_z,
            win_h,
        )
    )

    mullion_w = 50.0
    objs.append(
        add_box(
            doc,
            "FULL_Ventana_Parteluz",
            wall_x + (wall_th - mullion_w) / 2.0,
            wall_y + win_offset + (win_w - mullion_w) / 2.0,
            win_sill_z,
            mullion_w,
            mullion_w,
            win_h,
        )
    )

    doc.recompute()

    fcstd = out_fcstd_dir / "FULL.FCStd"
    step = out_step_dir / "FULL.step"
    doc.saveAs(str(fcstd))
    Part.export(objs, str(step))

    print("FULL parcial generado:")
    print("-", fcstd)
    print("-", step)
    print(f"- ENSI en ({ensi_x:.0f}, {ensi_y:.0f})")
    print(f"- ENS rotado 180 en ({ens_x:.0f}, {ens_y:.0f})")
    print(
        f"- Muro izquierdo: x={wall_x:.0f}..{wall_x + wall_th:.0f}, y={wall_y:.0f}..{wall_y + wall_len:.0f}"
    )
    print(f"- Ventana desde y={win_offset:.0f}, ancho={win_w:.0f}")


if __name__ == "__main__":
    main()

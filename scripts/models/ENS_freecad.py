#!/usr/bin/env python3
"""Arma ENS (vista conjunta de todos los modulos en posicion).

Salida:
  - models/fcstd/ENS.FCStd
  - models/step/ENS.step
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


def add_box(doc, name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz)
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def add_extractor(doc, name, x, y, z, w, d, h, bevel_d=120.0, bevel_h=40.0):
    """Extractor simplificado con bisel frontal.

    Frente total h, con frente plano superior de (h - bevel_h) y bisel bevel_d x bevel_h.
    """
    body = Part.makeBox(w, d, h, App.Vector(x, y, z))
    # Prisma triangular a sustraer en el borde inferior frontal.
    tri = Part.makePolygon(
        [
            App.Vector(x, y, z),
            App.Vector(x, y + bevel_d, z),
            App.Vector(x, y, z + bevel_h),
            App.Vector(x, y, z),
        ]
    )
    tri_face = Part.Face(tri)
    tri_prism = tri_face.extrude(App.Vector(w, 0, 0))
    shape = body.cut(tri_prism)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
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

    # Layout en planta (mm):
    # BA [0..903], BB [903..2258], H [2258..2930], L [2930..3820]
    x_ba = 0.0
    x_bb = 903.0
    x_h = 2258.0
    x_l = 2930.0

    # Alacenas superiores a cota de colgado definida.
    # Van contra el fondo (pared): profundidad 320 sobre referencia de 600.
    y_upper = 600.0 - 320.0
    z_abac = 1500.0
    z_aa = 1590.0

    # Modulo L retranqueado respecto al frente de H.
    # Frente de L queda 390 mm por detras del frente de H.
    y_l = 390.0

    doc = App.newDocument("CocinaEnsamble")

    objs = []
    objs.append(add_step(doc, "BA_Bajo_Izq", str(step_dir / "BA.step"), x_ba, 0, 0))
    objs.append(add_step(doc, "BB_Bajo_Der", str(step_dir / "BB.step"), x_bb, 0, 0))
    objs.append(add_step(doc, "H_Columna", str(step_dir / "H.step"), x_h, 0, 0))
    objs.append(
        add_step(
            doc,
            "AA_Alacena_Izq",
            str(step_dir / "AA.step"),
            x_ba,
            y_upper,
            z_aa,
        )
    )
    objs.append(
        add_step(
            doc,
            "ABAC_Alacena_Der",
            str(step_dir / "AB.step"),
            x_bb,
            y_upper,
            z_abac,
        )
    )
    objs.append(add_step(doc, "M_Mesada", str(step_dir / "M.step"), 0, 0, 0))
    objs.append(
        add_step(doc, "L_Armario_Lavadero", str(step_dir / "L.step"), x_l, y_l, 0)
    )

    doc.recompute()

    fcstd = out_fcstd_dir / "ENS.FCStd"
    step = out_step_dir / "ENS.step"
    doc.saveAs(str(fcstd))
    Part.export(objs, str(step))

    print("Ensamble generado:")
    print("-", fcstd)
    print("-", step)


if __name__ == "__main__":
    main()

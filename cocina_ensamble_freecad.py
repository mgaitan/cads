#!/usr/bin/env python3
"""Arma una vista conjunta de todos los modulos en posicion.

Salida:
  - cocina_ensamble.FCStd
  - cocina_ensamble.step
"""

import os

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
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()

    # Layout en planta (mm):
    # BA [0..903], BB [903..2258], H [2258..2930]
    x_ba = 0.0
    x_bb = 903.0
    x_h = 2258.0

    # Alacenas superiores a cota de colgado definida.
    # Van contra el fondo (pared): profundidad 320 sobre referencia de 600.
    y_upper = 600.0 - 320.0
    z_abac = 1500.0
    z_aa = 1590.0

    # Extractor: ya esta incluido como referencia en el modulo AA.

    doc = App.newDocument("CocinaEnsamble")

    objs = []
    objs.append(
        add_step(doc, "BA_Bajo_Izq", os.path.join(here, "bajo_BA.step"), x_ba, 0, 0)
    )
    objs.append(
        add_step(doc, "BB_Bajo_Der", os.path.join(here, "bajo_BB.step"), x_bb, 0, 0)
    )
    objs.append(
        add_step(
            doc, "H_Columna", os.path.join(here, "columna_horno_micro.step"), x_h, 0, 0
        )
    )

    objs.append(
        add_step(
            doc,
            "AA_Alacena_Izq",
            os.path.join(here, "alacena_AA.step"),
            x_ba,
            y_upper,
            z_aa,
        )
    )
    objs.append(
        add_step(
            doc,
            "ABAC_Alacena_Der",
            os.path.join(here, "alacena_AB.step"),
            x_bb,
            y_upper,
            z_abac,
        )
    )

    objs.append(add_step(doc, "M_Mesada", os.path.join(here, "mesada.step"), 0, 0, 0))

    doc.recompute()

    fcstd = os.path.join(here, "cocina_ensamble.FCStd")
    step = os.path.join(here, "cocina_ensamble.step")
    doc.saveAs(fcstd)
    Part.export(objs, step)

    print("Ensamble generado:")
    print("-", fcstd)
    print("-", step)


if __name__ == "__main__":
    main()

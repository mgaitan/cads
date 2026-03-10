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


def main():
    script_path = globals().get("__file__")
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()

    # Layout en planta (mm):
    # BA [0..1050], BB [1050..2258], H [2258..2930]
    x_ba = 0.0
    x_bb = 1050.0
    x_h = 2258.0

    # Alacenas superiores a cota de colgado definida.
    # Van contra el fondo (pared): profundidad 320 sobre referencia de 600.
    y_upper = 600.0 - 320.0
    z_upper = 1620.0

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
            z_upper,
        )
    )
    objs.append(
        add_step(
            doc,
            "ABAC_Alacena_Der",
            os.path.join(here, "alacena_AB.step"),
            x_bb,
            y_upper,
            z_upper,
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

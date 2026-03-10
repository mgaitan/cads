#!/usr/bin/env python3
"""Genera piedra de mesada con hueco para anafe de apoyo.

Salida:
  - mesada.FCStd
  - mesada.step
  - mesada_bom.csv
"""

import csv
import os

import FreeCAD as App
import Part

# Parametros (mm)
WIDTH = 2294.0  # BA + BB
DEPTH = 648.0  # 600 de modulo + 18 de frente + 30 de vuelo extra
THICK = 30.0
Z_BASE = 870.0  # sobre cascos de bajo mesada
Y_FRONT = -48.0  # supera 30 mm el frente de cajones (frente a y=-18)

# Hueco anafe (con margen)
CUT_W = 600.0
CUT_D = 555.0
CUT_CENTER_X = 783.0  # alineado al eje ducto en AA/BA
# Mantener anafe hacia el fondo en la zona util del mueble (0..600 en Y).
CUT_CENTER_Y = 300.0

CUT_X = CUT_CENTER_X - CUT_W / 2.0
CUT_Y = CUT_CENTER_Y - CUT_D / 2.0


def main():
    script_path = globals().get("__file__")
    here = os.path.dirname(os.path.abspath(script_path)) if script_path else os.getcwd()

    doc = App.newDocument("Mesada")

    slab = Part.makeBox(WIDTH, DEPTH, THICK, App.Vector(0, Y_FRONT, Z_BASE))
    hole = Part.makeBox(
        CUT_W, CUT_D, THICK + 2.0, App.Vector(CUT_X, CUT_Y, Z_BASE - 1.0)
    )
    shape = slab.cut(hole)

    obj = doc.addObject("Part::Feature", "M1_Mesada_Gris_Mara")
    obj.Shape = shape
    doc.recompute()

    fcstd = os.path.join(here, "mesada.FCStd")
    step = os.path.join(here, "mesada.step")
    bom = os.path.join(here, "mesada_bom.csv")

    doc.saveAs(fcstd)
    Part.export([obj], step)

    with open(bom, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "codigo",
                "categoria",
                "pieza",
                "cantidad",
                "largo_mm",
                "ancho_mm",
                "espesor_mm",
                "cantos",
            ]
        )
        w.writerow(
            [
                "M1",
                "Mesada",
                f"Piedra_Gris_Mara_Calado_{int(CUT_W)}x{int(CUT_D)}",
                1,
                WIDTH,
                DEPTH,
                THICK,
                "Pulido perimetral segun proveedor",
            ]
        )

    print("Modelo generado:")
    print("-", fcstd)
    print("-", step)
    print("-", bom)
    print("\nCalado anafe:")
    print(f"- {CUT_W} x {CUT_D} mm")
    print(f"- centro en X={CUT_CENTER_X} mm, Y={CUT_CENTER_Y} mm")


if __name__ == "__main__":
    main()

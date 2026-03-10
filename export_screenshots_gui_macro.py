#!/usr/bin/env python3
"""Macro para ejecutar dentro de FreeCAD GUI.

Exporta:
- la vista actual como `horno_iso.png` (dejala manualmente como quieras),
- y luego `front`, `left`, `top`.
"""

import os

import FreeCAD as App
import FreeCADGui as Gui

OUT_DIR = "./screenshots"
WIDTH = 1920
HEIGHT = 1080
BG = "White"


def save(view, name):
    path = os.path.join(OUT_DIR, name)
    view.fitAll()
    view.saveImage(path, WIDTH, HEIGHT, BG)
    print("saved", path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    doc = App.ActiveDocument
    if doc is None:
        raise RuntimeError(
            "No hay documento activo. Abri columna_horno_micro.FCStd primero."
        )

    gdoc = Gui.ActiveDocument
    if gdoc is None:
        raise RuntimeError("No hay documento GUI activo.")

    view = gdoc.ActiveView

    # Asegura visibilidad de todas las piezas
    for obj in doc.Objects:
        vo = getattr(obj, "ViewObject", None)
        if vo is not None:
            vo.Visibility = True
            try:
                vo.DisplayMode = "Flat Lines"
            except Exception:
                pass

    # Oculta overlays
    if hasattr(view, "setAxisCross"):
        try:
            view.setAxisCross(False)
        except Exception:
            pass
    if hasattr(view, "setCornerCrossVisible"):
        try:
            view.setCornerCrossVisible(False)
        except Exception:
            pass

    # 1) iso = vista actual (ajustada por vos)
    save(view, "horno_iso.png")

    # 2) vistas ortogonales
    view.viewFront()
    save(view, "horno_front.png")

    view.viewLeft()
    save(view, "horno_left.png")

    view.viewTop()
    save(view, "horno_top.png")


main()

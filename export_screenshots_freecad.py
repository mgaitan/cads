#!/usr/bin/env python3
"""Exporta screenshots de un modelo FreeCAD en vistas estandar.

Uso recomendado:
  printf "exec(open('export_screenshots_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c
"""

import os

import FreeCAD as App
import FreeCADGui as Gui

MODEL_FILE = "columna_horno_micro.FCStd"
OUT_DIR = "screenshots"
WIDTH = 1920
HEIGHT = 1080
BG = "White"
ZOOM_STEPS = 0


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def shot(view, out_path):
    view.fitAll()
    # Ajuste para evitar objeto demasiado chico en el encuadre.
    for _ in range(ZOOM_STEPS):
        try:
            view.zoomIn()
        except Exception:
            break
    view.saveImage(out_path, WIDTH, HEIGHT, BG)
    print(f"- {out_path}")


def clean_view(view):
    # Limpia overlays molestos en captura (ejes/cross de esquina).
    for fn, arg in (
        ("setAxisCross", False),
        ("setCornerCrossVisible", False),
    ):
        if hasattr(view, fn):
            try:
                getattr(view, fn)(arg)
            except Exception:
                pass


def main():
    model_path = os.path.abspath(MODEL_FILE)
    out_dir = os.path.abspath(OUT_DIR)
    ensure_dir(out_dir)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No existe el modelo: {model_path}")

    # En algunos builds, `freecad -c` carga FreeCADGui pero sin GUI activa.
    if not getattr(App, "GuiUp", 0):
        try:
            Gui.showMainWindow()
        except Exception:
            pass

    if not getattr(App, "GuiUp", 0):
        raise RuntimeError(
            "FreeCAD esta en modo sin GUI (GuiUp=0). "
            "Para screenshots usa FreeCAD GUI + macro, o ejecuta con display virtual (xvfb)."
        )

    doc = App.openDocument(model_path)

    if not hasattr(Gui, "getDocument"):
        raise RuntimeError(
            "Este entorno no expone API de vista (Gui.getDocument). "
            "Ejecuta el script como macro dentro de FreeCAD GUI."
        )

    Gui.activateWorkbench("PartWorkbench")
    Gui_doc = Gui.getDocument(doc.Name)
    view = Gui_doc.ActiveView
    clean_view(view)
    if hasattr(view, "setCameraType"):
        try:
            view.setCameraType("Orthographic")
        except Exception:
            pass

    # En esta instalacion los objetos se abren ocultos via script.
    # Forzamos visibilidad para que la captura no salga en blanco.
    for obj in doc.Objects:
        vo = getattr(obj, "ViewObject", None)
        if vo is not None:
            vo.Visibility = True
            try:
                vo.DisplayMode = "Flat Lines"
            except Exception:
                pass

    # Vista isometrica
    if hasattr(view, "viewAxonometric"):
        view.viewAxonometric()
    else:
        view.viewIsometric()
    shot(view, os.path.join(out_dir, "horno_iso.png"))

    # Vista frontal
    view.viewFront()
    shot(view, os.path.join(out_dir, "horno_front.png"))

    # Vista lateral izquierda
    view.viewLeft()
    shot(view, os.path.join(out_dir, "horno_left.png"))

    # Vista superior
    view.viewTop()
    shot(view, os.path.join(out_dir, "horno_top.png"))

    App.closeDocument(doc.Name)
    print("Screenshots generados.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Macro para ejecutar dentro de FreeCAD GUI.

Exporta:
- la vista actual como `<prefijo>_iso.png` (dejala manualmente como quieras),
- vistas estandar via comandos Std_View*: front/rear/left/right/top/bottom.

Prefijo:
- Si `OUTPUT_PREFIX` esta definido, usa ese valor.
- Si no, lo deduce del nombre del archivo abierto:
  - `columna_horno_micro.FCStd` -> `horno`
  - `alacena_AA.FCStd` -> `aa`
  - `alacena_AB.FCStd` -> `ab`
"""

import os

import FreeCAD as App
import FreeCADGui as Gui

OUT_DIR = "/home/tin/lab/diseños_CAD/screenshots"
WIDTH = 1920
HEIGHT = 1080
BG = "White"
DOOR_TRANSPARENCY = 65  # 0 opaco, 100 transparente
OUTPUT_PREFIX = None  # ejemplo: "aa", "ab", "horno"


def detect_prefix(doc):
    if OUTPUT_PREFIX:
        return OUTPUT_PREFIX

    fn = ""
    try:
        fn = App.ActiveDocument.FileName
    except Exception:
        fn = ""

    base = os.path.splitext(os.path.basename(fn))[0].lower()
    if "horno" in base:
        return "horno"
    if "alacena_aa" in base:
        return "aa"
    if "alacena_ab" in base:
        return "ab"
    return base if base else "modelo"


def save(view, name):
    path = os.path.join(OUT_DIR, name)
    view.fitAll()
    view.saveImage(path, WIDTH, HEIGHT, BG)
    print("saved", path)


def set_std_view(command_name):
    # Usa los mismos comandos que la barra de vistas de FreeCAD.
    Gui.runCommand(command_name, 0)
    Gui.SendMsgToActiveView("ViewFit")
    Gui.updateGui()


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
    prefix = detect_prefix(doc)

    # Asegura visibilidad de piezas, excepto fondos (ocultos intencionalmente).
    for obj in doc.Objects:
        vo = getattr(obj, "ViewObject", None)
        if vo is not None:
            vo.Visibility = True
            if "Fondo" in obj.Name:
                vo.Visibility = False
            if "Puerta" in obj.Name:
                try:
                    vo.Transparency = DOOR_TRANSPARENCY
                except Exception:
                    pass
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
    save(view, f"{prefix}_iso.png")

    # 2) vistas estandar (mismo mecanismo que toolbar)
    std_views = [
        ("Std_ViewFront", f"{prefix}_front.png"),
        ("Std_ViewRear", f"{prefix}_rear.png"),
        ("Std_ViewLeft", f"{prefix}_left.png"),
        ("Std_ViewRight", f"{prefix}_right.png"),
        ("Std_ViewTop", f"{prefix}_top.png"),
        ("Std_ViewBottom", f"{prefix}_bottom.png"),
    ]
    for cmd, filename in std_views:
        set_std_view(cmd)
        save(view, filename)


main()

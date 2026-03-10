#!/usr/bin/env python3
"""Macro para ejecutar dentro de FreeCAD GUI.

Exporta:
- la vista actual como `<prefijo>_iso.png` (dejala manualmente como quieras),
- vistas estandar via comandos Std_View*: front/rear/left/right/top/bottom.

Prefijo:
- Si `OUTPUT_PREFIX` esta definido, usa ese valor.
- Si no, lo deduce del nombre del archivo abierto (prefijo de codigo):
  - `H.FCStd` -> `H`
  - `AA.FCStd` -> `AA`
  - `AB.FCStd` -> `AB`
  - `BA.FCStd` -> `BA`
  - `BB.FCStd` -> `BB`
  - `M.FCStd` -> `M`
  - `ENS.FCStd` -> `ENS`
"""

import os
from pathlib import Path

import FreeCAD as App
import FreeCADGui as Gui

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = str(ROOT / "screenshots")
WIDTH = 1920
HEIGHT = 1080
BG = "White"
DOOR_TRANSPARENCY = 65  # 0 opaco, 100 transparente
OUTPUT_PREFIX = None  # ejemplo: "AA", "AB", "H"
EXPORT_ALL_OPEN = True  # True: exporta todos los documentos abiertos


def detect_prefix(doc):
    if OUTPUT_PREFIX and not EXPORT_ALL_OPEN:
        return OUTPUT_PREFIX

    fn = ""
    try:
        fn = doc.FileName
    except Exception:
        fn = ""

    base = os.path.splitext(os.path.basename(fn))[0]
    mapped = {
        "h": "H",
        "aa": "AA",
        "ab": "AB",
        "ba": "BA",
        "bb": "BB",
        "m": "M",
        "ens": "ENS",
    }
    key = base.lower()
    return mapped.get(key, base.upper() if base else "MODEL")


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


def prepare_visuals(doc, view):
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


def activate_doc(doc_name):
    try:
        App.setActiveDocument(doc_name)
    except Exception:
        pass
    try:
        Gui.activateDocument(doc_name)
    except Exception:
        pass
    Gui.updateGui()


def export_doc(doc):
    activate_doc(doc.Name)
    gdoc = Gui.getDocument(doc.Name)
    if gdoc is None:
        return
    view = gdoc.ActiveView
    prefix = detect_prefix(doc)

    prepare_visuals(doc, view)

    # 1) iso = vista actual (la que tengas guardada en esa pestaña)
    save(view, f"{prefix}_iso.png")

    # 2) vistas estandar
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


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if App.ActiveDocument is None:
        raise RuntimeError(
            "No hay documento activo. Abri un modelo (ej. H.FCStd) primero."
        )

    if Gui.ActiveDocument is None:
        raise RuntimeError("No hay documento GUI activo.")

    if EXPORT_ALL_OPEN:
        docs = list(App.listDocuments().values())
        for doc in docs:
            export_doc(doc)
    else:
        export_doc(App.ActiveDocument)


main()

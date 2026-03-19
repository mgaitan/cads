#!/usr/bin/env python3
"""Macro para ejecutar dentro de FreeCAD GUI.

Exporta en `outputs/screenshots/<modulo>/`:
- `iso.png`
- `front.png`
- `rear.png`
- `left.png`
- `right.png`
- `top.png`
- `bottom.png`

Prefijo:
- Si `OUTPUT_PREFIX` esta definido, usa ese valor.
- Si no, lo deduce del nombre del archivo abierto (prefijo de codigo):
  - `H.FCStd` -> `H`
  - `AA.FCStd` -> `AA`
  - `AB.FCStd` -> `AB`
  - `BA.FCStd` -> `BA`
  - `BB.FCStd` -> `BB`
  - `F.FCStd` -> `F`
  - `L.FCStd` -> `L`
  - `M.FCStd` -> `M`
  - `ENS.FCStd` -> `ENS`
"""

import os
import time
from pathlib import Path

import FreeCAD as App
import FreeCADGui as Gui

ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "outputs" / "screenshots"
WIDTH = 1920
HEIGHT = 1080
BG = "White"
DOOR_TRANSPARENCY = 65  # 0 opaco, 100 transparente
OUTPUT_PREFIX = None  # ejemplo: "AA", "AB", "H"
EXPORT_ALL_OPEN = True  # True: exporta todos los documentos abiertos
FORCE_STANDARD_ISO = True  # True: fuerza Std_ViewIsometric para *_iso


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
        "f": "F",
        "l": "L",
        "m": "M",
        "ens": "ENS",
    }
    key = base.lower()
    return mapped.get(key, base.upper() if base else "MODEL")


def save(view, out_dir, name):
    path = os.path.join(out_dir, name)
    view.fitAll()
    view.saveImage(path, WIDTH, HEIGHT, BG)
    print("saved", path)


def set_std_view(command_name):
    # Usa los mismos comandos que la barra de vistas de FreeCAD.
    Gui.runCommand(command_name, 0)
    Gui.SendMsgToActiveView("ViewFit")
    Gui.updateGui()
    time.sleep(0.12)


def prepare_visuals(doc, view):
    for obj in doc.Objects:
        vo = getattr(obj, "ViewObject", None)
        if vo is not None:
            vo.Visibility = True
            name = obj.Name
            is_panel_back = (
                name.startswith("H14_")
                or name.startswith("AB5_")
                or name.startswith("AA")
                and "Fondo" in name
                or name.startswith("BA")
                and "Fondo" in name
                or name.startswith("BB")
                and "Fondo" in name
                or name.startswith("I")
                and "Fondo_6mm" in name
                or name.startswith("L")
                and "Fondo" in name
                or name.startswith("F")
                and "Fondo" in name
            )
            if is_panel_back:
                vo.Visibility = False
            if "Puerta" in name:
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
    out_dir = OUT_ROOT / prefix
    out_dir.mkdir(parents=True, exist_ok=True)

    prepare_visuals(doc, view)

    # 1) iso
    if FORCE_STANDARD_ISO:
        set_std_view("Std_ViewIsometric")
    save(view, str(out_dir), "iso.png")

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
        save(view, str(out_dir), filename.replace(f"{prefix}_", ""))


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

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

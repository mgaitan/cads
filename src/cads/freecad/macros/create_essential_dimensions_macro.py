#!/usr/bin/env python3
"""Crea cotas maestras para el documento activo en FreeCAD GUI.

Agrega ancho, profundidad y altura totales en el grupo Cotas_Esenciales.
Las cotas se ven en cualquier vista, incluida la perspectiva. Para ocultarlas o
mostrarlas, seleccionar el grupo en el arbol de FreeCAD y presionar Espacio.
"""

from __future__ import annotations

import Draft
import FreeCAD as App
import FreeCADGui as Gui

GROUP_NAME = "Cotas_Esenciales"
OFFSET_MM = 140
TEXT_SIZE_MM = 18
ARROW_SIZE_MM = 12


def set_if_present(target, name, value):
    try:
        setattr(target, name, value)
    except Exception:
        pass


def model_bound_box(doc):
    boxes = []
    for obj in doc.Objects:
        if getattr(obj, "cotas_esenciales", False):
            continue
        shape = getattr(obj, "Shape", None)
        if shape is not None and not shape.isNull():
            boxes.append(shape.BoundBox)
    if not boxes:
        raise RuntimeError("El documento no tiene geometria para acotar.")

    return (
        min(box.XMin for box in boxes),
        max(box.XMax for box in boxes),
        min(box.YMin for box in boxes),
        max(box.YMax for box in boxes),
        min(box.ZMin for box in boxes),
        max(box.ZMax for box in boxes),
    )


def group_for(doc):
    group = doc.getObject(GROUP_NAME)
    if group is None:
        group = doc.addObject("App::DocumentObjectGroup", GROUP_NAME)
        group.Label = "Cotas esenciales"
    return group


def remove_previous(doc):
    for obj in list(doc.Objects):
        if getattr(obj, "cotas_esenciales", False):
            doc.removeObject(obj.Name)


def style(dimension):
    view = dimension.ViewObject
    set_if_present(view, "LineColor", (0.15, 0.45, 0.20))
    set_if_present(view, "TextColor", (0.15, 0.45, 0.20))
    set_if_present(view, "LineWidth", 2.0)
    set_if_present(view, "FontSize", TEXT_SIZE_MM)
    set_if_present(view, "ArrowSize", ARROW_SIZE_MM)


def make_dimension(group, label, start, end, line_point):
    dimension = Draft.make_dimension(start, end, line_point)
    dimension.Label = label
    dimension.addProperty("App::PropertyBool", "cotas_esenciales", "Cotas")
    dimension.cotas_esenciales = True
    group.addObject(dimension)
    style(dimension)
    return dimension


def main():
    doc = App.ActiveDocument
    if doc is None:
        raise RuntimeError("Abri y activa un modelo FCStd antes de ejecutar la macro.")
    if Gui.ActiveDocument is None:
        raise RuntimeError("Esta macro necesita ejecutarse desde FreeCAD GUI.")

    remove_previous(doc)
    doc.recompute()
    xmin, xmax, ymin, ymax, zmin, zmax = model_bound_box(doc)
    offset = OFFSET_MM
    group = group_for(doc)

    make_dimension(
        group,
        "Ancho total",
        App.Vector(xmin, ymin, zmin),
        App.Vector(xmax, ymin, zmin),
        App.Vector(xmin, ymin - offset, zmin),
    )
    make_dimension(
        group,
        "Profundidad total",
        App.Vector(xmin, ymin, zmin),
        App.Vector(xmin, ymax, zmin),
        App.Vector(xmin - offset, ymin, zmin),
    )
    make_dimension(
        group,
        "Altura total",
        App.Vector(xmin, ymin, zmin),
        App.Vector(xmin, ymin, zmax),
        App.Vector(xmin - offset, ymin - offset, zmin),
    )
    doc.recompute()
    Gui.activeDocument().activeView().fitAll()
    print("Cotas esenciales actualizadas. Selecciona Cotas esenciales y usa Espacio para mostrarlas u ocultarlas.")


main()

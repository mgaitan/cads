from __future__ import annotations

import FreeCAD as App
import Part

GOLA_SETBACK = 26.0
GOLA_VISIBLE_H = 26.0
J_GOLA_TOTAL_H = 48.0
J_GOLA_D = 24.4
C_GOLA_TOTAL_H = 72.8
C_GOLA_D = 26.0
GOLA_TH = 2.0


def add_compound(doc, name, shapes):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeCompound(shapes)
    return obj


def make_j_gola(doc, name, x, y, z, length):
    y0 = y
    shapes = [
        Part.makeBox(
            length, GOLA_TH, J_GOLA_TOTAL_H, App.Vector(x, y0 + J_GOLA_D - GOLA_TH, z)
        ),
        Part.makeBox(length, J_GOLA_D, GOLA_TH, App.Vector(x, y0, z)),
        Part.makeBox(length, GOLA_TH, 6.0, App.Vector(x, y0, z)),
        Part.makeBox(length, 6.0, GOLA_TH, App.Vector(x, y0 + J_GOLA_D - 6.0, z + GOLA_TH)),
    ]
    return add_compound(doc, name, shapes)


def make_j_gola_inverted(doc, name, x, y, z, length):
    y0 = y
    shapes = [
        Part.makeBox(
            length, GOLA_TH, J_GOLA_TOTAL_H, App.Vector(x, y0 + J_GOLA_D - GOLA_TH, z)
        ),
        Part.makeBox(
            length,
            J_GOLA_D,
            GOLA_TH,
            App.Vector(x, y0, z + J_GOLA_TOTAL_H - GOLA_TH),
        ),
        Part.makeBox(length, GOLA_TH, 6.0, App.Vector(x, y0, z + J_GOLA_TOTAL_H - 6.0)),
        Part.makeBox(
            length,
            6.0,
            GOLA_TH,
            App.Vector(x, y0 + J_GOLA_D - 6.0, z + J_GOLA_TOTAL_H - GOLA_TH - 6.0),
        ),
    ]
    return add_compound(doc, name, shapes)


def make_c_gola(doc, name, x, y, z, length):
    y0 = y
    lip_h = 10.0
    shapes = [
        Part.makeBox(
            length, GOLA_TH, C_GOLA_TOTAL_H, App.Vector(x, y0 + C_GOLA_D - GOLA_TH, z)
        ),
        Part.makeBox(length, C_GOLA_D, GOLA_TH, App.Vector(x, y0, z)),
        Part.makeBox(length, C_GOLA_D, GOLA_TH, App.Vector(x, y0, z + C_GOLA_TOTAL_H - GOLA_TH)),
        Part.makeBox(length, GOLA_TH, lip_h, App.Vector(x, y0, z + GOLA_TH)),
        Part.makeBox(length, GOLA_TH, lip_h, App.Vector(x, y0, z + C_GOLA_TOTAL_H - GOLA_TH - lip_h)),
    ]
    return add_compound(doc, name, shapes)

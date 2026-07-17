"""Build the 830 x 410 mm variant of the bathroom vanity in FreeCAD."""

from __future__ import annotations

import importlib.util
from pathlib import Path


BASE_PATH = Path(__file__).resolve().with_name("build_vanitory_reforma_770.py")
SPEC = importlib.util.spec_from_file_location("vanitory_reforma_base", BASE_PATH)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.PREFIX = "vanitory_reforma_830"
base.W = 820
# Overall furniture depth includes the 18 mm fronts. The carcass is 407 mm.
base.D = 407
base.BASIN_Y = base.D - base.STONE_T - base.BASIN_D
base.recalc()

build = base.build


if __name__ == "__main__":
    build()

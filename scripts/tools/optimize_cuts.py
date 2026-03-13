#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "ortools>=9.10",
# ]
# ///
"""Optimizacion de corte de placas desde BOM usando OR-Tools CP-SAT.

Uso:
  uv run scripts/tools/optimize_cuts.py
  uv run scripts/tools/optimize_cuts.py --board 2820x1830 --kerf 3 --margin 10

Salida:
  - outputs/cutting/summary.csv
  - outputs/cutting/<grupo>_placements.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[2]
BOM_DIR = ROOT / "bom"
OUT_DIR = ROOT / "outputs" / "cutting"

SKIP_CATEGORIES = {"Herraje", "Referencia", "Mesada", "Resumen"}
VALID_THICKNESS = (3.0, 6.0, 18.0, 25.4)


@dataclass(frozen=True)
class PieceType:
    module: str
    code: str
    category: str
    name: str
    qty: int
    w: int
    h: int
    t: float
    material: str
    cantos: str


@dataclass(frozen=True)
class PieceInstance:
    uid: str
    module: str
    code: str
    name: str
    w: int
    h: int
    w_eff: int
    h_eff: int
    t: float
    group: str
    cantos: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Optimizacion de cortes de placas.")
    p.add_argument(
        "--board",
        default="2820x1830",
        help="Tamano placa bruto en mm: ANCHOxALTO (default: 2820x1830)",
    )
    p.add_argument(
        "--kerf",
        type=int,
        default=3,
        help="Ancho de corte sierra en mm (default: 3).",
    )
    p.add_argument(
        "--margin",
        type=int,
        default=10,
        help="Margen perimetral util por placa en mm (default: 10).",
    )
    p.add_argument(
        "--time-limit",
        type=float,
        default=10.0,
        help="Limite de tiempo por intento CP-SAT en segundos (default: 10).",
    )
    p.add_argument(
        "--max-extra-boards",
        type=int,
        default=6,
        help="Cantidad maxima de placas extra sobre el lower-bound a explorar con CP-SAT (default: 6).",
    )
    p.add_argument(
        "--svg",
        action="store_true",
        help="Genera un SVG por grupo con el layout de cortes.",
    )
    return p.parse_args()


def parse_board_size(text: str) -> tuple[int, int]:
    m = re.match(r"^\s*(\d+)\s*[xX]\s*(\d+)\s*$", text)
    if not m:
        raise ValueError(f"Formato invalido para --board: {text}")
    a, b = int(m.group(1)), int(m.group(2))
    return a, b


def infer_material(category: str, name: str, t: float) -> str:
    key = f"{category} {name}".lower()
    if "paraiso" in key:
        return "paraiso"
    if t <= 6.5:
        return "fondo"
    return "blanco"


def parse_float(text: str) -> float:
    try:
        return float(str(text).strip().replace(",", "."))
    except Exception:
        return 0.0


def is_valid_thickness(t: float) -> bool:
    return any(abs(t - v) <= 0.6 for v in VALID_THICKNESS)


def load_piece_types() -> list[PieceType]:
    out: list[PieceType] = []
    for bom_path in sorted(BOM_DIR.glob("*_bom.csv")):
        module = bom_path.stem.replace("_bom", "")
        with bom_path.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                code = (r.get("codigo") or "").strip()
                category = (r.get("categoria") or "").strip()
                if not code or code == "TOTAL" or category in SKIP_CATEGORIES:
                    continue
                qty = int(parse_float(r.get("cantidad", "0")))
                if qty <= 0:
                    continue
                w = int(round(parse_float(r.get("largo_mm", "0"))))
                h = int(round(parse_float(r.get("ancho_mm", "0"))))
                t = parse_float(r.get("espesor_mm", "0"))
                if w <= 0 or h <= 0 or t <= 0:
                    continue
                if not is_valid_thickness(t):
                    continue
                name = (r.get("pieza") or "").strip()
                cantos = (r.get("cantos") or "").strip()
                material = infer_material(category, name, t)
                out.append(
                    PieceType(
                        module=module,
                        code=code,
                        category=category,
                        name=name,
                        qty=qty,
                        w=w,
                        h=h,
                        t=t,
                        material=material,
                        cantos=cantos,
                    )
                )
    return out


def expand_instances(
    types: Iterable[PieceType], kerf: int, margin: int, board_w: int, board_h: int
) -> list[PieceInstance]:
    usable_w = board_w - 2 * margin
    usable_h = board_h - 2 * margin
    items: list[PieceInstance] = []
    for p in types:
        w_eff = p.w + kerf
        h_eff = p.h + kerf
        fits = (w_eff <= usable_w and h_eff <= usable_h) or (
            h_eff <= usable_w and w_eff <= usable_h
        )
        if not fits:
            raise RuntimeError(
                f"Pieza no entra en placa ({board_w}x{board_h} con margen {margin}): "
                f"{p.module}:{p.code} {p.w}x{p.h}x{p.t}"
            )
        group = f"{p.material}_{p.t:g}mm"
        for i in range(p.qty):
            items.append(
                PieceInstance(
                    uid=f"{p.module}_{p.code}_{i + 1}",
                    module=p.module,
                    code=p.code,
                    name=p.name,
                    w=p.w,
                    h=p.h,
                    w_eff=w_eff,
                    h_eff=h_eff,
                    t=p.t,
                    group=group,
                    cantos=p.cantos,
                )
            )
    return items


def solve_group(
    items: list[PieceInstance],
    board_w: int,
    board_h: int,
    time_limit: float,
    max_extra_boards: int,
) -> tuple[int, list[dict[str, object]]]:
    n = len(items)
    board_area = board_w * board_h
    total_area = sum(i.w_eff * i.h_eff for i in items)
    lb = max(1, math.ceil(total_area / board_area))

    max_boards = min(n, lb + max(0, max_extra_boards))
    for boards in range(lb, max_boards + 1):
        model = cp_model.CpModel()
        used = [model.NewBoolVar(f"used_{b}") for b in range(boards)]
        x, y, wv, hv, pres, rot = {}, {}, {}, {}, {}, {}
        x_int_by_b = [[] for _ in range(boards)]
        y_int_by_b = [[] for _ in range(boards)]

        for i, it in enumerate(items):
            assigns = []
            for b in range(boards):
                p = model.NewBoolVar(f"p_{i}_{b}")
                r = model.NewBoolVar(f"r_{i}_{b}")
                w_var = model.NewIntVar(
                    min(it.w_eff, it.h_eff), max(it.w_eff, it.h_eff), f"w_{i}_{b}"
                )
                h_var = model.NewIntVar(
                    min(it.w_eff, it.h_eff), max(it.w_eff, it.h_eff), f"h_{i}_{b}"
                )
                model.AddAllowedAssignments(
                    [r, w_var, h_var],
                    [[0, it.w_eff, it.h_eff], [1, it.h_eff, it.w_eff]],
                )
                xs = model.NewIntVar(0, board_w, f"x_{i}_{b}")
                ys = model.NewIntVar(0, board_h, f"y_{i}_{b}")
                xe = model.NewIntVar(0, board_w, f"xe_{i}_{b}")
                ye = model.NewIntVar(0, board_h, f"ye_{i}_{b}")
                xi = model.NewOptionalIntervalVar(xs, w_var, xe, p, f"xi_{i}_{b}")
                yi = model.NewOptionalIntervalVar(ys, h_var, ye, p, f"yi_{i}_{b}")
                model.Add(xe <= board_w).OnlyEnforceIf(p)
                model.Add(ye <= board_h).OnlyEnforceIf(p)
                model.AddImplication(p, used[b])

                x[i, b], y[i, b] = xs, ys
                wv[i, b], hv[i, b] = w_var, h_var
                pres[i, b], rot[i, b] = p, r
                x_int_by_b[b].append(xi)
                y_int_by_b[b].append(yi)
                assigns.append(p)

            model.Add(sum(assigns) == 1)

        for b in range(boards):
            model.AddNoOverlap2D(x_int_by_b[b], y_int_by_b[b])
            if b > 0:
                model.AddImplication(used[b], used[b - 1])

        model.Minimize(sum(used))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            continue

        placements: list[dict[str, object]] = []
        for i, it in enumerate(items):
            for b in range(boards):
                if solver.Value(pres[i, b]) == 1:
                    placements.append(
                        {
                            "board_idx": b + 1,
                            "uid": it.uid,
                            "module": it.module,
                            "code": it.code,
                            "name": it.name,
                            "x_mm": solver.Value(x[i, b]),
                            "y_mm": solver.Value(y[i, b]),
                            "cut_w_mm": solver.Value(wv[i, b]),
                            "cut_h_mm": solver.Value(hv[i, b]),
                            "part_w_mm": it.w,
                            "part_h_mm": it.h,
                            "rotated": solver.Value(rot[i, b]),
                            "cantos": it.cantos,
                        }
                    )
                    break
        return boards, placements

    return greedy_shelf_pack(items, board_w, board_h)


def greedy_shelf_pack(
    items: list[PieceInstance], board_w: int, board_h: int
) -> tuple[int, list[dict[str, object]]]:
    sorted_items = sorted(items, key=lambda i: i.w_eff * i.h_eff, reverse=True)
    boards: list[list[dict[str, int]]] = []  # shelves per board: y,h,x
    placements: list[dict[str, object]] = []

    def try_place_in_board(
        bidx: int, it: PieceInstance, w: int, h: int, rotated: int
    ) -> bool:
        shelves = boards[bidx]
        for s in shelves:
            if h <= s["h"] and s["x"] + w <= board_w:
                px, py = s["x"], s["y"]
                s["x"] += w
                placements.append(
                    {
                        "board_idx": bidx + 1,
                        "uid": it.uid,
                        "module": it.module,
                        "code": it.code,
                        "name": it.name,
                        "x_mm": px,
                        "y_mm": py,
                        "cut_w_mm": w,
                        "cut_h_mm": h,
                        "part_w_mm": it.w,
                        "part_h_mm": it.h,
                        "rotated": rotated,
                        "cantos": it.cantos,
                    }
                )
                return True

        y_top = shelves[-1]["y"] + shelves[-1]["h"] if shelves else 0
        if y_top + h <= board_h:
            shelves.append({"y": y_top, "h": h, "x": w})
            placements.append(
                {
                    "board_idx": bidx + 1,
                    "uid": it.uid,
                    "module": it.module,
                    "code": it.code,
                    "name": it.name,
                    "x_mm": 0,
                    "y_mm": y_top,
                    "cut_w_mm": w,
                    "cut_h_mm": h,
                    "part_w_mm": it.w,
                    "part_h_mm": it.h,
                    "rotated": rotated,
                    "cantos": it.cantos,
                }
            )
            return True
        return False

    for it in sorted_items:
        options = [(it.w_eff, it.h_eff, 0)]
        if it.w_eff != it.h_eff:
            options.append((it.h_eff, it.w_eff, 1))
        # probar primero la orientacion mas baja (shelf packing)
        options.sort(key=lambda t: (t[1], t[0]))

        placed = False
        for w, h, r in options:
            for b in range(len(boards)):
                if try_place_in_board(b, it, w, h, r):
                    placed = True
                    break
            if placed:
                break

        if not placed:
            boards.append([])
            w, h, r = options[0]
            ok = try_place_in_board(len(boards) - 1, it, w, h, r)
            if not ok:
                raise RuntimeError(
                    f"No se pudo ubicar pieza {it.uid} en fallback greedy."
                )

    return len(boards), placements


def write_csv(path: Path, rows: list[dict[str, object]]):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_group_svgs(
    out_dir: Path,
    group: str,
    placements: list[dict[str, object]],
    board_w: int,
    board_h: int,
):
    if not placements:
        return
    scale = 0.35
    pad = 40
    boards = max(int(p["board_idx"]) for p in placements)
    boards_per_page = 2
    cols = 1
    rows = min(boards_per_page, boards)
    cell_w = int(board_w * scale) + pad * 2
    cell_h = int(board_h * scale) + pad * 2 + 24
    svg_w = cols * cell_w
    svg_h = rows * cell_h

    colors = [
        "#d9e8fb",
        "#fce8d6",
        "#d9f2e6",
        "#f5d9fb",
        "#fde2e2",
        "#fff3cd",
    ]

    def board_origin(local_idx: int) -> tuple[int, int]:
        i = local_idx
        c = i % cols
        r = i // cols
        return c * cell_w + pad, r * cell_h + pad + 18

    total_pages = math.ceil(boards / boards_per_page)
    for page_idx in range(total_pages):
        board_start = page_idx * boards_per_page + 1
        board_end = min(boards, board_start + boards_per_page - 1)
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
            f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="#ffffff"/>',
            f'<text x="12" y="20" font-size="14" font-family="Arial">Layout de corte - {group} - hoja {page_idx + 1}/{total_pages}</text>',
        ]

        for local_idx, b in enumerate(range(board_start, board_end + 1)):
            ox, oy = board_origin(local_idx)
            bw = board_w * scale
            bh = board_h * scale
            lines.append(
                f'<rect x="{ox}" y="{oy}" width="{bw:.1f}" height="{bh:.1f}" fill="#f8f9fa" stroke="#333" stroke-width="1.2"/>'
            )
            lines.append(
                f'<text x="{ox}" y="{oy - 6}" font-size="11" font-family="Arial">Placa {b}</text>'
            )

        for idx, p in enumerate(placements):
            b = int(p["board_idx"])
            if not (board_start <= b <= board_end):
                continue
            ox, oy = board_origin(b - board_start)
            x = ox + float(p["x_mm"]) * scale
            y = oy + float(p["y_mm"]) * scale
            w = float(p["cut_w_mm"]) * scale
            h = float(p["cut_h_mm"]) * scale
            color = colors[idx % len(colors)]
            label = f"{p['code']} ({int(p['part_w_mm'])}x{int(p['part_h_mm'])})"
            cantos = str(p.get("cantos", "")).strip()
            if cantos:
                label = f"{label} - {cantos}"
            lines.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}" stroke="#555" stroke-width="0.8"/>'
            )
            if w > 46 and h > 18:
                lines.append(
                    f'<text x="{x + 3:.1f}" y="{y + 13:.1f}" font-size="9" font-family="Arial">{label}</text>'
                )

        lines.append("</svg>")
        path = out_dir / f"{group}_layout_p{page_idx + 1:02d}.svg"
        path.write_text("\n".join(lines), encoding="utf-8")


def main():
    args = parse_args()
    board_w_raw, board_h_raw = parse_board_size(args.board)
    # permitimos rotar placa base segun convenga
    board_w = max(board_w_raw, board_h_raw) - 2 * args.margin
    board_h = min(board_w_raw, board_h_raw) - 2 * args.margin

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in OUT_DIR.glob("*_placements.csv"):
        stale.unlink(missing_ok=True)
    for stale in OUT_DIR.glob("*_layout*.svg"):
        stale.unlink(missing_ok=True)

    types = load_piece_types()
    items = expand_instances(types, args.kerf, args.margin, board_w_raw, board_h_raw)

    by_group: dict[str, list[PieceInstance]] = {}
    for it in items:
        by_group.setdefault(it.group, []).append(it)

    summary_rows: list[dict[str, object]] = []
    for group, group_items in sorted(by_group.items()):
        boards, placements = solve_group(
            group_items,
            board_w=board_w,
            board_h=board_h,
            time_limit=args.time_limit,
            max_extra_boards=args.max_extra_boards,
        )
        placements.sort(key=lambda r: (r["board_idx"], r["y_mm"], r["x_mm"]))
        write_csv(OUT_DIR / f"{group}_placements.csv", placements)
        if args.svg:
            write_group_svgs(
                OUT_DIR,
                group=group,
                placements=placements,
                board_w=board_w,
                board_h=board_h,
            )

        part_area = sum(it.w_eff * it.h_eff for it in group_items)
        board_area_total = boards * board_w * board_h
        waste = (
            max(0.0, 1.0 - (part_area / board_area_total)) if board_area_total else 0.0
        )
        summary_rows.append(
            {
                "group": group,
                "pieces": len(group_items),
                "boards_used": boards,
                "board_usable_w_mm": board_w,
                "board_usable_h_mm": board_h,
                "kerf_mm": args.kerf,
                "margin_mm": args.margin,
                "utilization_pct": f"{(1.0 - waste) * 100:.2f}",
                "waste_pct": f"{waste * 100:.2f}",
            }
        )

    write_csv(OUT_DIR / "summary.csv", summary_rows)
    print(f"[ok] generado: {OUT_DIR / 'summary.csv'}")
    for r in summary_rows:
        print(
            f"- {r['group']}: piezas={r['pieces']}, placas={r['boards_used']}, "
            f"uso={r['utilization_pct']}%, descarte={r['waste_pct']}%"
        )


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path

from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "outputs" / "cutting"


@dataclass(frozen=True)
class PieceInstance:
    uid: str
    source: str
    module: str
    code: str
    name: str
    w: int
    h: int
    w_eff: int
    h_eff: int
    rotate: bool
    group: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Optimiza cortes desde TSV de proveedor.")
    p.add_argument(
        "input",
        help="TSV de proveedor a optimizar.",
    )
    p.add_argument(
        "--board",
        default="2750x1830",
        help="Tamano placa bruto en mm: ANCHOxALTO (default: 2750x1830).",
    )
    p.add_argument("--kerf", type=int, default=3, help="Ancho de corte en mm.")
    p.add_argument(
        "--margin", type=int, default=10, help="Margen perimetral util en mm."
    )
    p.add_argument(
        "--time-limit",
        type=float,
        default=10.0,
        help="Limite de tiempo por intento CP-SAT en segundos.",
    )
    p.add_argument(
        "--max-extra-boards",
        type=int,
        default=20,
        help="Placas extra a explorar por encima del lower-bound.",
    )
    p.add_argument("--svg", action="store_true", help="Genera layouts SVG.")
    return p.parse_args()


def parse_board_size(text: str) -> tuple[int, int]:
    m = re.match(r"^\s*(\d+)\s*[xX]\s*(\d+)\s*$", text)
    if not m:
        raise ValueError(f"Formato invalido para --board: {text}")
    return int(m.group(1)), int(m.group(2))


def infer_group(path: Path) -> str:
    stem = path.stem
    for suffix in ("blanco_18mm", "fondo_3mm", "fondo_6mm", "paraiso_18mm"):
        if stem.endswith(suffix):
            return suffix
    raise ValueError(f"No pude inferir grupo de material desde {path.name}")


def infer_module_and_code(name: str) -> tuple[str, str]:
    code = name.split("_", 1)[0]
    module = re.match(r"^[A-Z]+", code)
    return (module.group(0) if module else code, code)


def input_path(raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if not path.is_absolute() else path


def load_instances(
    path: Path, board_w: int, board_h: int, kerf: int, margin: int
) -> list[PieceInstance]:
    usable_w = board_w - 2 * margin
    usable_h = board_h - 2 * margin
    items: list[PieceInstance] = []
    group = infer_group(path)
    with path.open("r", encoding="utf-8", newline="") as f:
        for row_num, row in enumerate(csv.reader(f, delimiter="\t"), start=1):
            if len(row) < 5:
                continue
            name, qty_s, largo_s, ancho_s, rot_s = row[:5]
            qty = int(qty_s or "0")
            largo = int(round(float(largo_s)))
            ancho = int(round(float(ancho_s)))
            rotate = rot_s.strip().upper() == "SI"
            if qty <= 0:
                continue
            if min(largo, ancho) < 50:
                raise RuntimeError(
                    f"Pieza menor a 50 mm: {name} ({largo}x{ancho}) en {path.name}"
                )
            w_eff = largo + kerf
            h_eff = ancho + kerf
            fits = (w_eff <= usable_w and h_eff <= usable_h) or (
                rotate and h_eff <= usable_w and w_eff <= usable_h
            )
            if not fits:
                raise RuntimeError(
                    f"Pieza no entra en placa {board_w}x{board_h}: {name} {largo}x{ancho} ({path.name})"
                )
            module, code = infer_module_and_code(name)
            for i in range(qty):
                items.append(
                    PieceInstance(
                        uid=f"{path.stem}_{row_num}_{i + 1}",
                        source=path.name,
                        module=module,
                        code=code,
                        name=name,
                        w=largo,
                        h=ancho,
                        w_eff=w_eff,
                        h_eff=h_eff,
                        rotate=rotate,
                        group=group,
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
                if it.rotate:
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
                else:
                    r = model.NewConstant(0)
                    w_var = model.NewConstant(it.w_eff)
                    h_var = model.NewConstant(it.h_eff)
                xs = model.NewIntVar(0, board_w, f"x_{i}_{b}")
                ys = model.NewIntVar(0, board_h, f"y_{i}_{b}")
                xe = model.NewIntVar(0, board_w, f"xe_{i}_{b}")
                ye = model.NewIntVar(0, board_h, f"ye_{i}_{b}")
                xi = model.NewOptionalIntervalVar(xs, w_var, xe, p, f"xi_{i}_{b}")
                yi = model.NewOptionalIntervalVar(ys, h_var, ye, p, f"yi_{i}_{b}")
                model.Add(xe <= board_w).OnlyEnforceIf(p)
                model.Add(ye <= board_h).OnlyEnforceIf(p)
                model.AddImplication(p, used[b])
                x[i, b], y[i, b], wv[i, b], hv[i, b], pres[i, b], rot[i, b] = (
                    xs,
                    ys,
                    w_var,
                    h_var,
                    p,
                    r,
                )
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
                if solver.Value(pres[i, b]):
                    placements.append(
                        {
                            "uid": it.uid,
                            "source": it.source,
                            "module": it.module,
                            "code": it.code,
                            "name": it.name,
                            "board": b + 1,
                            "x": solver.Value(x[i, b]),
                            "y": solver.Value(y[i, b]),
                            "w": solver.Value(wv[i, b]) - 3,
                            "h": solver.Value(hv[i, b]) - 3,
                            "rotated": bool(solver.Value(rot[i, b]))
                            if it.rotate
                            else False,
                        }
                    )
        return boards, placements
    raise RuntimeError("No se encontro solucion de nesting.")


def write_placements(group: str, placements: list[dict[str, object]]) -> None:
    path = OUT_DIR / f"{group}_placements.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "uid",
                "source",
                "module",
                "code",
                "name",
                "board",
                "x",
                "y",
                "w",
                "h",
                "rotated",
            ],
        )
        writer.writeheader()
        writer.writerows(placements)


def write_summary(rows: list[dict[str, object]]) -> None:
    path = OUT_DIR / "summary.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "group",
                "boards_used",
                "pieces",
                "utilization_pct",
                "board_usable_w_mm",
                "board_usable_h_mm",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_svg(
    group: str, placements: list[dict[str, object]], board_w: int, board_h: int
) -> None:
    boards = sorted({int(p["board"]) for p in placements})
    scale = min(980 / board_w, 633.5 / board_h)
    palette = [
        "#d9e8fb",
        "#fce8d6",
        "#d9f2e6",
        "#f5d9fb",
        "#fde2e2",
        "#fff3cd",
        "#e2f0cb",
        "#dbeafe",
    ]
    per_page = 2
    pages = math.ceil(len(boards) / per_page)

    for page in range(pages):
        page_boards = boards[page * per_page : (page + 1) * per_page]
        svg = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1059" height="1474" viewBox="0 0 1059 1474">',
            '<rect x="0" y="0" width="1059" height="1474" fill="#ffffff"/>',
            f'<text x="12" y="20" font-size="14" font-family="Arial">Layout de corte - {group} - hoja {page + 1}/{pages}</text>',
        ]
        for slot, board in enumerate(page_boards):
            ox = 40
            oy = 58 + slot * 737
            svg.append(
                f'<rect x="{ox}" y="{oy}" width="{board_w * scale}" height="{board_h * scale}" fill="#f8f9fa" stroke="#333" stroke-width="1.2"/>'
            )
            svg.append(
                f'<text x="{ox}" y="{oy - 6}" font-size="11" font-family="Arial">Placa {board}</text>'
            )
            for idx, p in enumerate(
                [p for p in placements if int(p["board"]) == board]
            ):
                x = ox + float(p["x"]) * scale
                y = oy + float(p["y"]) * scale
                w = float(p["w"]) * scale
                h = float(p["h"]) * scale
                fill = palette[idx % len(palette)]
                label = f"{p['code']} ({p['w']}x{p['h']})"
                svg.append(
                    f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#555" stroke-width="0.8"/>'
                )
                svg.append(
                    f'<text x="{x + 3}" y="{y + 13}" font-size="9" font-family="Arial">{label}</text>'
                )
        svg.append("</svg>")
        (OUT_DIR / f"{group}_layout_p{page + 1:02d}.svg").write_text(
            "\n".join(svg), encoding="utf-8"
        )


def main() -> int:
    args = parse_args()
    board_w, board_h = parse_board_size(args.board)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = input_path(args.input)
    items = load_instances(path, board_w, board_h, args.kerf, args.margin)
    if not items:
        raise SystemExit(f"No hay piezas en {path}.")

    summary_rows: list[dict[str, object]] = []
    usable_w = board_w - 2 * args.margin
    usable_h = board_h - 2 * args.margin
    board_area = usable_w * usable_h
    group = items[0].group
    boards_used, placements = solve_group(
        items, usable_w, usable_h, args.time_limit, args.max_extra_boards
    )
    write_placements(group, placements)
    if args.svg:
        write_svg(group, placements, usable_w, usable_h)
    total_piece_area = sum(it.w * it.h for it in items)
    utilization = round(100 * total_piece_area / (boards_used * board_area), 2)
    summary_rows.append(
        {
            "group": group,
            "boards_used": boards_used,
            "pieces": len(items),
            "utilization_pct": utilization,
            "board_usable_w_mm": usable_w,
            "board_usable_h_mm": usable_h,
        }
    )
    write_summary(summary_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

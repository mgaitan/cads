from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = ROOT / "outputs"
SITE = OUTPUTS / "site"


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree_files(src_dir: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(src_dir.iterdir()):
        if src.is_file():
            shutil.copy2(src, dst_dir / src.name)


def sync_screenshots() -> None:
    src_root = OUTPUTS / "screenshots"
    dst_root = SITE / "assets" / "screenshots"
    reset_dir(dst_root)
    for module_dir in sorted(src_root.iterdir()):
        if not module_dir.is_dir():
            continue
        module = module_dir.name
        for shot in sorted(module_dir.glob("*.png")):
            copy_file(shot, dst_root / f"{module}_{shot.name}")


def main() -> int:
    assets = SITE / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    manual = OUTPUTS / "manuals" / "COCINA.pdf"
    if manual.exists():
        copy_file(manual, assets / "COCINA_manual.pdf")

    copy_tree_files(OUTPUTS / "web_models", assets / "models")
    copy_tree_files(OUTPUTS / "cutting", assets / "cutting")
    sync_screenshots()
    print(f"refreshed {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

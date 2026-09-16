#!/usr/bin/env python3
"""驗證及整理 W03 notebooks（課程維護工具）。

notebook 本身是唯一內容來源；此工具不再從內嵌的舊文字重建檔案，避免覆寫
已更新的學生版與教師版。

用法：
    python scripts/_build_notebooks.py
    python scripts/_build_notebooks.py --clear-outputs
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = (
    ROOT / "notebooks" / "W03" / "00_w03_setup.ipynb",
    ROOT / "notebooks" / "W03" / "01_debug_challenge.ipynb",
    ROOT / "teacher" / "W03" / "01_debug_challenge_ANSWER.ipynb",
)

REQUIRED_TEXT = {
    "00_w03_setup.ipynb": (
        "檢查點 0",
        "set_seed(42)",
        "run_all(ROOT)",
        "defacing",
    ),
    "01_debug_challenge.ipynb": (
        "版本、路徑、隨機",
        "修補後驗收",
        "SUB",
    ),
    "01_debug_challenge_ANSWER.ipynb": (
        "17 分鐘",
        "requirements.txt",
        "修補後驗收",
    ),
}


def source_text(cell: dict[str, Any]) -> str:
    """將 notebook cell source 正規化為字串。"""
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def parse_code(source: str, label: str) -> None:
    """剝除行首 notebook magic 後檢查 Python 語法。"""
    lines = []
    for line in source.splitlines():
        if line.lstrip().startswith(("!", "%")):
            lines.append("pass  # notebook magic")
        else:
            lines.append(line)
    ast.parse("\n".join(lines), filename=label)


def validate(path: Path, clear_outputs: bool = False) -> bool:
    """驗證單一 notebook；必要時清除輸出，回傳檔案是否被修改。"""
    if not path.is_file():
        raise FileNotFoundError(f"找不到 notebook：{path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("nbformat") != 4 or not isinstance(data.get("cells"), list):
        raise ValueError(f"{path.name} 不是有效的 notebook v4")

    all_text = []
    changed = False
    for index, cell in enumerate(data["cells"]):
        cell_type = cell.get("cell_type")
        if cell_type not in {"code", "markdown", "raw"}:
            raise ValueError(f"{path.name} cell {index} 類型不支援：{cell_type}")
        text = source_text(cell)
        all_text.append(text)
        if cell_type == "code":
            parse_code(text, f"{path.name}:cell{index}")
            if clear_outputs:
                if cell.get("outputs"):
                    cell["outputs"] = []
                    changed = True
                if cell.get("execution_count") is not None:
                    cell["execution_count"] = None
                    changed = True

    joined = "\n".join(all_text)
    missing = [marker for marker in REQUIRED_TEXT[path.name] if marker not in joined]
    if missing:
        raise ValueError(f"{path.name} 缺少必要內容：{missing}")

    if changed:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="驗證 W03 notebooks")
    parser.add_argument(
        "--clear-outputs",
        action="store_true",
        help="驗證後清除所有執行輸出與 execution count",
    )
    args = parser.parse_args()

    for path in NOTEBOOKS:
        changed = validate(path, clear_outputs=args.clear_outputs)
        action = "已驗證並清除輸出" if changed else "驗證通過"
        print(f"✓ {action}：{path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""建立 W03 約定的六層研究專案資料夾。

用法：
    python scripts/make_project_structure.py
    python scripts/make_project_structure.py ./my_project
    python scripts/make_project_structure.py --colab --name radiomics_course

預設在目前目錄建立 ``radiomics_course/``，並複製一份不覆寫既有內容的
``docs/README.md`` 三行樣板。
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.paths import ensure_project, get_root, show_tree  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent.parent / "docs" / "00_README樣板.md"


def main() -> None:
    ap = argparse.ArgumentParser(description="建立六層專案資料夾")
    ap.add_argument(
        "root",
        nargs="?",
        type=Path,
        help="專案根目錄；省略時建立目前目錄下的 --name 資料夾",
    )
    ap.add_argument("--colab", action="store_true", help="在 Colab 上掛載 Drive 並建在 MyDrive 底下")
    ap.add_argument("--name", default="radiomics_course", help="專案資料夾名稱")
    ap.add_argument(
        "--force-readme",
        action="store_true",
        help="以三行樣板覆寫既有 docs/README.md",
    )
    args = ap.parse_args()

    if args.colab and args.root is not None:
        ap.error("--colab 與 root 路徑不能同時使用")

    if args.colab:
        root = get_root(project=args.name)
    elif args.root is not None:
        root = args.root.expanduser().resolve()
    else:
        root = (Path.cwd() / args.name).resolve()

    ensure_project(root)

    readme = Path(root) / "docs" / "README.md"
    if TEMPLATE.exists() and (args.force_readme or not readme.exists()):
        readme.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"已放入 README 樣板：{readme}")
    elif readme.exists():
        print(f"保留既有 README：{readme}")

    show_tree(root)
    print()
    print("六層都建好了。接下來：")
    print("  1. 打開 docs/README.md，填寫環境、資料位置與執行順序")
    print("  2. data/raw/ 當成唯讀，永不修改")
    print("  3. 檔名不用中文與空白；病人一律用 SUB001 這種代號")


if __name__ == "__main__":
    main()

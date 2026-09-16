"""
路徑管理｜W03 檢查點 2 與檢查點 6

一條規矩：**notebook 裡不准出現完整的絕對路徑**。
所有路徑都用 ROOT 組合出來，這樣同一本 notebook 在你的 Drive、
在同學的 Drive、在你自己的筆電上都跑得動。

用法：
    from src.paths import get_root, ensure_project
    ROOT = get_root()                 # Colab 會自動掛載 Drive
    ensure_project(ROOT)              # 建立六層資料夾
    df.to_csv(ROOT / "results" / "20260917_features.csv", index=False)

"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

#: 本課程統一的六層專案結構（W03 第 35 頁）
PROJECT_DIRS: tuple[str, ...] = (
    "data/raw",        # 去識別化後的原始影像 · 組內 · 唯讀，永不修改
    "data/processed",  # 前處理後的中間檔 · 組內 · 可重建，不必備份
    "notebooks",       # 編號的分析 notebook · 可公開 · 不得含病人資料輸出
    "src",             # 共用函式與模組 · 可公開 · 貼第三次就搬進來
    "results",         # 特徵矩陣、模型結果、圖 · 視情況 · 檔名帶日期與參數
    "docs",            # README、環境說明、決策紀錄 · 可公開
)

DEFAULT_PROJECT_NAME = "radiomics_course"


def in_colab() -> bool:
    """是否跑在 Google Colab 上。"""
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def mount_drive(mountpoint: str = "/content/drive") -> Path:
    """在 Colab 掛載 Google Drive；已掛載則直接回傳路徑。

    授權時請選檢查點 0 決定的那一個帳號 —— 選錯之後權限會很麻煩。
    """
    if not in_colab():
        raise RuntimeError("mount_drive() 只能在 Colab 上用。本機請直接指定 root=。")
    mp = Path(mountpoint)
    if not (mp / "MyDrive").exists():
        from google.colab import drive
        drive.mount(mountpoint)
    return mp / "MyDrive"


def get_root(project: str = DEFAULT_PROJECT_NAME,
             root: str | os.PathLike | None = None,
             create: bool = True) -> Path:
    """回傳專案根目錄 ROOT。

    * 在 Colab：掛載 Drive，回傳 ``MyDrive/<project>``
    * 在本機  ：回傳目前工作目錄下的 ``<project>``（或你給的 root）

    不要把回傳值展開成字串貼進 notebook —— 那就等於把路徑寫死了。
    """
    if root is not None:
        base = Path(root).expanduser()
    elif in_colab():
        base = mount_drive() / project
    else:
        base = Path.cwd() / project

    if create:
        base.mkdir(parents=True, exist_ok=True)
    return base


def ensure_project(root: str | os.PathLike,
                   dirs: Iterable[str] = PROJECT_DIRS,
                   gitkeep: bool = True) -> Path:
    """在 ROOT 底下建立六層資料夾，並放一份 .gitkeep。"""
    base = Path(root)
    for d in dirs:
        target = base / d
        target.mkdir(parents=True, exist_ok=True)
        if gitkeep:
            keep = target / ".gitkeep"
            if not keep.exists():
                keep.touch()
    return base


def show_tree(root: str | os.PathLike, dirs: Iterable[str] = PROJECT_DIRS) -> None:
    """把建好的結構印出來，讓學生在螢幕上對照。"""
    base = Path(root)
    print(base)
    for d in dirs:
        exists = (base / d).is_dir()
        print(f"  {'✓' if exists else '✗'}  {d}/")


def stamped(name: str, date: str | None = None, ext: str = ".csv") -> str:
    """依課程命名約定產生結果檔名：``YYYYMMDD_<name><ext>``。

    >>> stamped("features_bin25", date="20260917")
    '20260917_features_bin25.csv'

    命名約定（W03 第 34 頁）：
      · 檔名只用英數字與底線，不用中文、空白、括號
      · 日期用 YYYYMMDD，排序就是時間順序
      · notebook 用 `編號_動作_對象`，如 01_preprocess_ct.ipynb
      · 結果檔帶日期與參數，不要每次覆寫同一個 result.csv
      · 病人一律用代號 SUB001，絕不使用病歷號或姓名
    """
    import datetime

    if not re.fullmatch(r"[A-Za-z0-9_]+", name):
        raise ValueError("name 只能包含英文字母、數字與底線")
    if not re.fullmatch(r"\.[A-Za-z0-9]+", ext):
        raise ValueError("ext 必須是形如 '.csv' 的英數副檔名")

    d = date or datetime.date.today().strftime("%Y%m%d")
    if not re.fullmatch(r"\d{8}", d):
        raise ValueError("date 必須使用 YYYYMMDD")
    return f"{d}_{name}{ext}"


if __name__ == "__main__":
    r = get_root(root="./_demo_project")
    ensure_project(r)
    show_tree(r)
    print(stamped("features_bin25"))

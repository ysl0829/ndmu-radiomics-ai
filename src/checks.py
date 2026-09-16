"""
六個檢查點的自動檢核｜W03

下課前把這支跑一次。能自動驗的就自動驗，不能自動驗的（配對、Gemini、Cursor）
會列成「手動確認」，請你自己看著螢幕回答。

用法：
    from src.checks import run_all
    run_all(ROOT)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from .paths import PROJECT_DIRS, in_colab

Result = Tuple[str, str, str]  # (狀態, 名稱, 說明)

OK, NO, MANUAL = "通過", "未過", "手動"


def check_gpu() -> Result:
    """檢查點 1：GPU 啟用，而且用指令驗過，不是只看設定畫面。"""
    if shutil.which("nvidia-smi") is None:
        return (NO, "檢查點 1　GPU",
                "找不到 nvidia-smi。執行階段 → 變更執行階段類型 → 硬體加速器選 GPU。"
                "（註：今天所有練習 CPU 都跑得動，分不到 GPU 不影響進度）")
    try:
        out = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=20)
        if out.returncode != 0 or not out.stdout.strip():
            return (NO, "檢查點 1　GPU", "nvidia-smi 沒有輸出。")
    except Exception as exc:  # pragma: no cover
        return (NO, "檢查點 1　GPU", f"nvidia-smi 執行失敗：{exc}")

    detail = "第一層通過（機器上有卡）"
    try:
        import torch
        if torch.cuda.is_available():
            detail = f"第一、二層都通過（框架看得到：{torch.cuda.get_device_name(0)}）"
        else:
            return (NO, "檢查點 1　GPU",
                    "nvidia-smi 有輸出，但 torch.cuda.is_available() 回 False —— "
                    "這是投影片上的狀況 A。不要升級 Colab 預裝的深度學習套件，重開執行階段再試。")
    except ImportError:
        detail += "（未安裝 torch，第二層略過）"
    return (OK, "檢查點 1　GPU", detail)


def check_root(root: Optional[str | os.PathLike]) -> Result:
    """檢查點 2：Drive 掛載成功，路徑用 ROOT 變數組合，沒有寫死。"""
    if root is None:
        return (NO, "檢查點 2　ROOT", "還沒有 ROOT 變數。先跑 get_root()。")
    base = Path(root)
    if not base.is_dir():
        return (NO, "檢查點 2　ROOT", f"{base} 不存在。")
    probe = base / ".w03_write_test"
    try:
        probe.write_text("ok", encoding="utf-8")
        got = probe.read_text(encoding="utf-8")
        probe.unlink()
    except Exception as exc:
        return (NO, "檢查點 2　ROOT", f"權限測試失敗：{exc}")
    if got != "ok":
        return (NO, "檢查點 2　ROOT", "寫得進去但讀不回來。")
    if in_colab() and str(base).startswith("/content") and "/drive/" not in str(base):
        return (NO, "檢查點 2　ROOT",
                f"ROOT 指到 {base} —— /content 底下的東西斷線會消失。請改指到 Drive。")
    return (OK, "檢查點 2　ROOT", f"{base}（寫入、讀回都成功）")


def check_pair() -> Result:
    """檢查點 3：與夥伴配對完成，兩人的螢幕都跑得動。"""
    return (MANUAL, "檢查點 3　配對",
            "兩台電腦都跑得出 nvidia-smi、都掛上各自的 Drive、"
            "兩份 notebook 都有 ROOT 變數；而且你能不看筆記把流程講一遍。")


def check_repro(
    root: Optional[str | os.PathLike] = None,
    seed_expected: int = 42,
) -> Result:
    """檢查點 4：版本鎖定、種子設定、環境紀錄三格齊全。"""
    missing: List[str] = []
    if os.environ.get("PYTHONHASHSEED") != str(seed_expected):
        missing.append("還沒呼叫 set_seed()")
    try:
        import numpy  # noqa: F401
    except ImportError:
        missing.append("numpy 沒裝起來")

    env_path: Optional[Path] = None
    if root is not None:
        result_dir = Path(root) / "results"
        reports = sorted(result_dir.glob("*_env.json")) if result_dir.is_dir() else []
        if not reports:
            missing.append("results/ 裡沒有 YYYYMMDD_env.json")
        else:
            env_path = reports[-1]
            try:
                report = json.loads(env_path.read_text(encoding="utf-8"))
                required = {"timestamp", "python", "gpu", "seed", "packages"}
                absent = sorted(required.difference(report))
                if absent:
                    missing.append(f"{env_path.name} 缺少欄位：{', '.join(absent)}")
                if str(report.get("seed")) != str(seed_expected):
                    missing.append(f"{env_path.name} 記錄的種子不是 {seed_expected}")
            except (OSError, json.JSONDecodeError) as exc:
                missing.append(f"環境紀錄無法讀取：{exc}")

    if missing:
        return (NO, "檢查點 4　可重現", "；".join(missing))
    report_detail = f"，環境紀錄：{env_path.name}" if env_path else ""
    return (OK, "檢查點 4　可重現",
            f"set_seed({seed_expected}) 已呼叫{report_detail}。"
            "別忘了 sklearn 的 random_state 要另外填。")


def check_tools() -> Result:
    """檢查點 5：Gemini 校準過、Cursor 開得了專案資料夾。"""
    return (MANUAL, "檢查點 5　工具",
            "Gemini 已登入並做過一次校準提問；Cursor 開的是『資料夾』不是單一檔案"
            "（裝不了就改走純 Colab 路線，這也算通過）。"
            "紅線：不得把可識別的病人資料貼進任何線上 AI 工具。")


def check_structure(root: Optional[str | os.PathLike]) -> Result:
    """檢查點 6：命名與資料夾結構符合約定。"""
    if root is None:
        return (NO, "檢查點 6　結構", "還沒有 ROOT 變數。")
    base = Path(root)
    missing = [d for d in PROJECT_DIRS if not (base / d).is_dir()]
    if missing:
        return (NO, "檢查點 6　結構", "缺少：" + "、".join(missing))
    return (OK, "檢查點 6　結構",
            "六層都在。檔名不用中文與空白、日期用 YYYYMMDD、病人一律用 SUB 代號。")


def run_all(root: Optional[str | os.PathLike] = None, seed_expected: int = 42) -> List[Result]:
    """依序跑六個檢查點，印出結果表，並回傳結果清單。"""
    results = [
        check_gpu(),
        check_root(root),
        check_pair(),
        check_repro(root, seed_expected),
        check_tools(),
        check_structure(root),
    ]
    width = max(len(name) for _, name, _ in results)
    print("W03　六個檢查點")
    print("═" * 76)
    for status, name, detail in results:
        mark = {OK: "✓", NO: "✗", MANUAL: "?"}[status]
        print(f" {mark} [{status}] {name:<{width}}  {detail}")
    print("═" * 76)
    failed = [n for s, n, _ in results if s == NO]
    manual = [n for s, n, _ in results if s == MANUAL]
    if failed:
        print(f"還沒過：{'、'.join(failed)} —— 手舉著不要放，我過去看。")
    else:
        print("可自動檢核的項目全部通過。")
    if manual:
        print(f"請自己確認：{'、'.join(manual)}")
    return results

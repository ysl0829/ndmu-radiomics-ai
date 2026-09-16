"""
可重現性工具｜W03 檢查點 4

這個模組只做兩件事：
  1. set_seed()     — 一次設好所有該設的種子
  2. env_report()   — 把「這次是在什麼環境跑的」記下來

為什麼重要：W18 專題驗收的方式是「我拿你的檔案、照你的說明跑一次，
看能不能得到你報告裡的數字」。沒有這兩件事，那件事做不到。

用法（Colab / 本機都一樣）：
    from src.repro import set_seed, env_report, RANDOM_STATE
    set_seed(42)
    env_report(save_to="results/env_20260917.json")

"""

from __future__ import annotations

import datetime
import json
import os
import platform
import random
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SEED_DEFAULT: int = 42

#: 傳給 sklearn 的 random_state 用這一個常數，不要各處手打數字。
#: set_seed() 管不到 sklearn 的函式層級隨機性 —— 這是全班最常漏的一項。
RANDOM_STATE: int = SEED_DEFAULT

_KEY_PACKAGES = [
    "numpy", "pandas", "scipy", "sklearn", "matplotlib",
    "SimpleITK", "radiomics", "pydicom", "nibabel", "skimage", "torch",
]


def set_seed(seed: int = SEED_DEFAULT, deterministic: bool = False) -> int:
    """設定所有會影響結果的亂數來源。

    涵蓋三個位置：
      位置一  Python 內建 random      —— shuffle、sample 吃這個
      位置二  NumPy                   —— 多數科學運算的底層亂數來源
      位置三  深度學習框架（若已安裝）  —— 含 GPU 端，與 CPU 端是分開的

    注意 set_seed() **管不到** sklearn 的函式層級參數。
    看到 `random_state=` 就填 `RANDOM_STATE`，一個都不要漏：
        train_test_split(X, y, random_state=RANDOM_STATE)
        RandomForestClassifier(random_state=RANDOM_STATE)
        StratifiedKFold(shuffle=True, random_state=RANDOM_STATE)

    Parameters
    ----------
    seed : int
        種子值。整個專案用同一個，不要每個 notebook 換一個。
    deterministic : bool
        True 時額外要求 GPU 運算走確定性路徑（會變慢）。
        只有在「同一台機器上重跑必須位元級相同」時才需要。

    Returns
    -------
    int
        實際設定的種子值。
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)

    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass

    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
            torch.use_deterministic_algorithms(True, warn_only=True)
    except ImportError:
        pass

    return seed


def gpu_name() -> str:
    """回傳 GPU 型號字串；沒有 GPU 或指令不存在時回傳 'CPU only'。"""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15,
        )
        name = out.stdout.strip().splitlines()
        if out.returncode == 0 and name:
            return name[0].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "CPU only"


def package_versions() -> Dict[str, str]:
    """回傳本課程關鍵套件的版本；沒裝的不列入。"""
    versions: Dict[str, str] = {}
    for name in _KEY_PACKAGES:
        try:
            mod = __import__(name)
        except Exception:
            continue
        v = getattr(mod, "__version__", None)
        if v is None and name == "SimpleITK":
            v = mod.Version_VersionString()
        versions[name] = str(v) if v is not None else "unknown"
    return versions


def env_report(save_to: Optional[str | Path] = None, echo: bool = True) -> Dict[str, Any]:
    """收集並（預設）印出環境紀錄。

    半年後審稿人問「訓練用什麼硬體」、或你的數字跟同學對不起來時，
    要靠這一份紀錄回答。存成 JSON 跟結果放在一起。
    """
    report: Dict[str, Any] = {
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "gpu": gpu_name(),
        "seed": os.environ.get("PYTHONHASHSEED", "(未設定)"),
        "packages": package_versions(),
    }

    if echo:
        print("環境紀錄")
        print("─" * 52)
        print(f"  時間      {report['timestamp']}")
        print(f"  Python    {report['python']}")
        print(f"  執行檔    {report['python_executable']}")
        print(f"  平台      {report['platform']}")
        print(f"  GPU       {report['gpu']}")
        print(f"  種子      {report['seed']}")
        print("  套件版本")
        for k, v in report["packages"].items():
            print(f"    {k:<12} {v}")
        print("─" * 52)

    if save_to is not None:
        path = Path(save_to)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        if echo:
            print(f"已寫入 {path}")

    return report


if __name__ == "__main__":
    set_seed()
    env_report()

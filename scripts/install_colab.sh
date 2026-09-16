#!/usr/bin/env bash
# Colab／Linux 一鍵安裝
#
# 在 Colab 的儲存格裡這樣用：
#   !bash ndmu-radiomics-ai/scripts/install_colab.sh
#
# 可用環境變數 PYTHON_BIN 指定 Python，例如 PYTHON_BIN=python3.12。
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"

if (($#)); then
  echo "此腳本不接受參數：W03–W18 統一安裝 requirements.txt" >&2
  exit 2
fi

echo "[1/4] 安裝 W03–W18 共用環境（不變更 Colab 預裝的 torch）"
"${PYTHON_BIN}" -m pip install -q -r "${REPO_DIR}/requirements.txt"

echo "[2/4] 檢查套件相依性"
"${PYTHON_BIN}" -m pip check

echo "[3/4] 驗證關鍵套件匯入"
"${PYTHON_BIN}" - <<'PY'
import importlib

mods = [
    "numpy", "pandas", "sklearn", "matplotlib",
    "SimpleITK", "pydicom", "nibabel", "radiomics",
]

bad = []
for m in mods:
    try:
        mod = importlib.import_module(m)
        v = getattr(mod, "__version__", None) or getattr(mod, "Version_VersionString", lambda: "?")()
        print(f"  ✓ {m:<12} {v}")
    except Exception as exc:
        bad.append(m)
        print(f"  ✗ {m:<12} {exc}")
if bad:
    raise SystemExit(f"匯入失敗：{bad}。請保留完整錯誤訊息，不要直接升級預裝框架。")
PY

echo "[4/4] 顯示環境紀錄"
PYTHONPATH="${REPO_DIR}${PYTHONPATH:+:${PYTHONPATH}}" \
  "${PYTHON_BIN}" "${REPO_DIR}/src/repro.py"

echo
echo "完成。若 Colab 要求重新啟動執行階段，請重啟後從安裝格重新執行。"

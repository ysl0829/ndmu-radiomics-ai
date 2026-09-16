# <你的專案名稱>

> 本週必做：把下面三行填掉。**三行就好，不要寫成正式文件。**
> 判準只有一個：把這個資料夾丟給同學，他不問你任何問題就跑得起來。

**環境怎麼裝**：<例：Colab；`pip install -r requirements.txt`；不動 Colab 預裝的 torch>

**資料放哪**：<例：去識別化資料在 `data/raw/`，代號為 SUB001–SUB120；真實資料與對照表不進 Git>

**程式什麼順序跑**：<例：`notebooks/01_preprocess_ct.ipynb` → `02_extract_features.ipynb` → `03_model.ipynb`>

---

以下是選填的，**W18 驗收前**再補就好：

- 種子：`set_seed(42)`，sklearn 的 `random_state` 一律用 `RANDOM_STATE`
- 環境紀錄：`results/YYYYMMDD_env.json`
- 已知限制：<例：只有單中心資料；異常個案 11 例>
- AI 使用與驗證：<例：使用 Cursor 協助重構；已以固定測試資料比對修改前後輸出>

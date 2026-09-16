# W03 Notebook 使用說明

本資料夾是「人工智慧於醫學影像組學的分析與應用（3010040）」第 3 週的課堂實作材料，依據
`W03_AI研究環境建置_v3.pptx` 更新。主題是建立可攜、可重建、可重現的 AI 研究環境。

本週的核心判準：

> 把專案交給同學，對方不問任何問題就能執行，而且能得到相同數字。

## 檔案與建議順序

1. `00_w03_setup.ipynb`：先完成研究環境建置與六個檢查點。
2. `01_debug_challenge.ipynb`：再用故意有缺陷的流程練習找出可重現性問題。

兩份 notebook 都可以在 Google Colab 開啟。課堂主流程也會使用 Google Drive、Gemini 與
Cursor；其中只有 Colab 負責執行程式，Gemini 與 Cursor 的項目需要人工確認。

---

## `00_w03_setup.ipynb`

### 用途

這是 W03 的主要實作 notebook。學生會從零確認 Colab、GPU、Google Drive、套件版本、隨機種子、
環境紀錄與專案結構，最後執行自動檢核。

### 學習成果

完成後，學生應能：

- 說明 GPU、runtime、mount、package version、random seed、reproducible、tensor 與
  de-identification。
- 用 `nvidia-smi` 與 PyTorch 驗證 GPU，而不是只相信介面設定。
- 掛載 Google Drive，使用單一 `ROOT` 變數組合路徑。
- 知道 `/content`、已安裝套件與記憶體內變數可能在 runtime 中斷後消失。
- 使用鎖定版本的 `requirements.txt` 重建環境。
- 呼叫 `set_seed(42)`，並在 scikit-learn 函式中設定 `random_state`。
- 儲存 Python、套件、GPU、種子與執行時間等環境紀錄。
- 建立課程統一的六層專案結構。
- 說明去識別化的三個必要檢查與頭部影像去臉風險。
- 完成 Gemini 校準與 Cursor 專案資料夾確認。

### 內容流程

#### 檢查點 0：出發前確認

確認電源、網路、固定使用的 Google 帳號、notebook 名稱與配對夥伴。此段也提供術語卡及工作坊規則。

#### 環境安裝

第一個程式區塊會：

1. 讀取 `COURSE_REPO`。
2. 尚未下載時執行 `git clone`。
3. 依 `requirements.txt` 安裝課程套件。
4. 把 repo 加入 Python 模組搜尋路徑。
5. 用清楚訊息提示網址、網路或套件安裝問題。

實際課程 GitHub URL：

```python
https://github.com/ysl0829/ndmu-radiomics-ai.git
```

若安裝後 Colab 要求重新啟動 runtime，請重新啟動並從安裝區塊開始執行。
不要自行升級 Colab 預裝的 PyTorch。

#### 檢查點 1：GPU

- 第一層：`nvidia-smi` 確認虛擬機有實體 GPU。
- 第二層：`torch.cuda.is_available()` 確認框架能使用 GPU。
- 第三層：提供張量運算範例作為進階驗證。

免費 Colab 分不到 GPU 不代表操作錯誤；本週其他練習仍可用 CPU 完成。

#### 檢查點 2：Drive 與 `ROOT`

`get_root()` 在 Colab 會掛載 Drive，在本機則建立本機專案根目錄。接著以實際寫入、讀回與刪除測試
確認權限。後續路徑都應由 `ROOT / "子資料夾" / "檔名"` 組合，不得貼入個人的絕對路徑。

#### 檢查點 3：配對實作

兩人輪流擔任駕駛與領航員，在兩台電腦上完成 GPU、Drive 與 `ROOT` 流程。這一項無法自動判定，
必須由學生互相示範與口頭說明。

#### 檢查點 4：可重現性

- `set_seed(42)` 同時處理 Python、NumPy 與可用的深度學習框架。
- `RANDOM_STATE` 用於 `train_test_split`、交叉驗證、隨機森林及其他 scikit-learn 隨機操作。
- `env_report()` 將環境資訊存入 `results/`，檔名由 `stamped()` 加上日期。
- 隨堂檢核用兩題確認學生理解 runtime 暫存性與鎖定版本的重要性。

#### 檢查點 5：Gemini 與 Cursor

- Gemini：登入、提出真實研究問題，再用已知答案校準可靠度。
- Cursor：開啟整個專案資料夾，確認左側能看到專案樹。
- 共通原則：AI 輸出必須由研究者驗證，不得輸入可識別的病人資料。

#### 檢查點 6：結構、命名與去識別化

`ensure_project(ROOT)` 建立：

```text
data/raw/
data/processed/
notebooks/
src/
results/
docs/
```

`show_tree(ROOT)` 顯示各資料夾是否存在，`stamped()` 產生
`YYYYMMDD_分析內容_參數.csv` 形式的結果檔名。

去識別化至少包括：

1. 批次移除 DICOM 標頭中的身分資訊。
2. 檢查燒錄在影像像素上的文字。
3. 將代號與真實身分對照表分開保存。

頭部 3D 影像可能重建臉部，公開前還須評估 defacing。

#### 最後檢核與作業

`run_all(ROOT)` 自動檢查 GPU、`ROOT`、種子與六層結構，並列出配對、Gemini 和 Cursor 等人工確認項目。
notebook 最後也保留本週作業及 W04 預告。

### 執行產物

- Drive 或本機中的六層專案結構。
- `results/YYYYMMDD_env.json` 環境紀錄。
- 通過 `run_all(ROOT)` 的檢核結果。
- 完成後的 `w03_setup` notebook 連結。

---

## `01_debug_challenge.ipynb`

### 用途

這是一個 17 分鐘的主動學習活動。範例可以正常執行，但故意保留三類研究流程缺陷，讓學生理解
「不報錯」不等於「可交付」或「可重現」。

### 情境與資料

notebook 用 `make_classification()` 產生 120 例、30 個特徵的合成 CT radiomics 特徵表，病人只用
`SUB001` 形式的代號。流程包括：

1. 安裝 NumPy、pandas、Matplotlib 與 scikit-learn。
2. 設定輸出位置。
3. 建立合成資料與特徵名稱。
4. 分割訓練集和測試集。
5. 訓練 100 棵樹的隨機森林並計算測試 AUC。
6. 輸出 `result.csv` 與 `feature_importance.csv`。

本檔不含真實醫療資料，可以安全地公開與重跑。

### 活動流程

- 教師說明：2 分鐘。
- 個人檢視：5 分鐘。
- 配對比對：5 分鐘。
- 合作修補：4 分鐘。
- 全班回收：1 分鐘。

學生需記錄問題位置、可能後果，以及驗證修補有效的方法。完成後要重新啟動 runtime、從頭執行兩次，
比較 AUC，並交由另一組在不提問的情況下重跑。

### 學生可見提示

三類問題位於：

- 版本
- 路徑
- 隨機

提示只界定搜尋方向，不應把「加註解」或「改短變數名稱」誤認為可重現性修補。

<details>
<summary>教師參考：三項預期問題與修補方向</summary>

1. **版本未鎖定**：安裝指令未指定版本，不同日期或電腦可能安裝不同套件。修補時應改用課程
   `requirements.txt` 或明確的相容版本清單。
2. **輸出路徑寫死且位於 `/content`**：Colab runtime 回收後輸出會消失，也無法直接搬到本機。
   修補時應掛載 Drive 並以 `ROOT` 組合路徑；本機則由同一個路徑工具選擇專案根目錄。
3. **隨機性未固定**：雖然合成資料本身有種子，資料切分與隨機森林仍未設定 `random_state`，
   因而可能得到不同 AUC。修補時應呼叫 `set_seed(42)`，並把 `RANDOM_STATE` 傳給每個
   scikit-learn 隨機操作。

</details>

### 延伸觀察

固定輸出成 `result.csv` 會覆寫舊實驗。這不是原活動指定的三個答案之一，但正式研究應使用日期、
分析名稱與重要參數建立不覆寫的檔名。

---

## 建議授課操作

1. 課前確認課程 GitHub URL 已填入主 notebook，並測試 Colab 可以安裝 `requirements.txt`。
2. 先用 `00_w03_setup.ipynb` 完成檢查點 0–4。
3. 在檢查點 4 後發放 `01_debug_challenge.ipynb`，避免學生先看到教師解答。
4. 挑戰結束後再完成 Gemini、Cursor、專案結構與去識別化。
5. 下課前執行 `run_all(ROOT)`，人工確認無法自動檢查的項目。

## 常見問題

- **`YOUR-GITHUB-ACCOUNT` 尚未替換**：安裝區塊會停止並提示，需填入真正 repo URL。
- **`nvidia-smi` 找不到**：先確認 Colab runtime 的硬體加速器設定；無 GPU 時仍可完成其他活動。
- **PyTorch 看不到 GPU**：不要升級 Colab 預裝 PyTorch，重新啟動 runtime 後再測。
- **Drive 授權錯帳號**：重新掛載並選擇檢查點 0 決定的固定帳號。
- **重新啟動後 import 失敗**：runtime 已被重建，需從安裝區塊重新執行。
- **AUC 每次不同**：檢查資料切分與模型是否都設定相同 `random_state`。
- **本機沒有 PyTorch**：不影響本週 CPU 活動；GPU 第二層驗證只在有 PyTorch 時執行。

## 資料安全

- notebook、Git、Gemini、Cursor 或其他線上 AI 工具中不得放入可識別病人資訊。
- `data/raw/` 只能放已去識別化影像，並視研究治理規定限制分享。
- notebook 輸出也可能洩漏身分資訊；公開前必須清除表格、路徑、影像與 metadata 中的識別內容。
- 病人代號統一使用 `SUB001` 形式，不使用姓名或病歷號。

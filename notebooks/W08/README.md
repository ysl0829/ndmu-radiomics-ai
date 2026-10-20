# W08 上機

管線五層，課堂只跑前兩層。每加一層，回到紙上那三個數字比對。

檔案：
  pipeline_00.py    STEP 0 基準線 — 先跑它，把三個 GLCM 數字抄在紙的最上面一行
  pipeline_01.py    LAYER ① 重取樣到 1×1×1 mm，印出與基準線的逐項變化
  _common.py        兩支共用的合成影像、重取樣與 3D GLCM（只需要 numpy）
  00_resample_two_layers.ipynb   Colab harness：重取樣與確認 ROI 兩層

跑完之後，回答紙上這兩題（數字自己量，不要先問 AI）：
  · 三個 GLCM 特徵各變了多少？方向一不一樣？
  · ROI 體素數變多了，體積呢？這兩件事一樣嗎？

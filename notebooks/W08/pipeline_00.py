#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_00.py — 基準線：什麼前處理都沒做
醫學影像 AI 與 Radiomics 研究｜第 6→8 週｜2026/10/22

把印出來的三個 GLCM 數字抄在紙的最上面一行。
今天每加一層前處理，都回來跟這三個數字比。

執行：python pipeline_00.py      （只需要 numpy）
"""
from _common import phantom, report

def main():
    vol, msk, sp = phantom()
    report("STEP 0　基準線（原始非等向體素，無前處理）", vol, msk, sp)
    print("\n把對比度、同質性、能量這三個數字抄到紙上。")

if __name__ == "__main__":
    main()

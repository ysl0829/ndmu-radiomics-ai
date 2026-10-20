#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_01.py — 第 ① 層：重取樣成等向體素
醫學影像 AI 與 Radiomics 研究｜第 6→8 週｜2026/10/22

影像用線性內插、遮罩用最近鄰，重取樣到 1×1×1 mm。
跑完把新的三個數字寫在基準線下面，然後回答：
  · 三個特徵各變了多少？方向一樣嗎？
  · ROI 體素數變多了，體積呢？

執行：python pipeline_01.py      （只需要 numpy）
"""
from _common import phantom, resample, report, SPACING_TARGET

def main():
    vol, msk, sp = phantom()
    base = report("STEP 0　基準線（原始非等向體素）", vol, msk, sp)
    print()
    vol_r = resample(vol, sp, SPACING_TARGET, order=1)
    msk_r = (resample(msk.astype(float), sp, SPACING_TARGET, order=0) > 0.5).astype(int)
    new = report("LAYER ①　重取樣到 1×1×1 mm（影像線性／遮罩最近鄰）", vol_r, msk_r, SPACING_TARGET)

    print("\n--- 比對 ---")
    for k, label in [("contrast","GLCM 對比度"),("homogeneity","GLCM 同質性"),("energy","GLCM 能量")]:
        d = (new[k]-base[k])/base[k]*100
        print(f"  {label:<12} {base[k]:>10.4f} → {new[k]:>10.4f}   變化 {d:+7.1f}%")
    print(f"  {'ROI 體素數':<12} {base['n']:>10} → {new['n']:>10}   變化 {(new['n']-base['n'])/base['n']*100:+7.1f}%")
    print(f"  {'ROI 體積(mm³)':<12} {base['vol']:>10.1f} → {new['vol']:>10.1f}   變化 {(new['vol']-base['vol'])/base['vol']*100:+7.1f}%")
    print("\n體素數變多是因為格子變密，不是腫瘤變大。這兩件事要分清楚。")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""W08 共用：合成影像、重取樣、GLCM 三個數字。只用 numpy。"""
import numpy as np

SPACING_NATIVE = (0.976, 0.976, 3.0)   # x, y, z（mm）非等向
SPACING_TARGET = (1.0, 1.0, 1.0)
SEED = 20261022
BIN_WIDTH = 25


def phantom(spacing=SPACING_NATIVE, seed=SEED):
    """一例合成頭頸 CT：24×96×96（z,y,x），腫瘤標 1。"""
    rng = np.random.default_rng(seed)
    vol = rng.normal(-20, 28, size=(24, 96, 96))
    zz, yy, xx = np.ogrid[:24, :96, :96]
    core = ((zz-12)/4.0)**2 + ((yy-48)/13.0)**2 + ((xx-48)/15.0)**2 <= 1.0
    texture = 26*np.sin(xx/3.0) + 18*np.cos(yy/4.0) + 12*np.sin(zz/1.5)
    vol = np.where(core, 55 + texture + rng.normal(0, 7, vol.shape), vol)
    msk = core.astype(np.int16)
    return vol, msk, spacing


def resample(arr, spacing, target, order):
    """order=1 線性（影像）／order=0 最近鄰（遮罩）。純 numpy 實作。"""
    sz, sy, sx = spacing[2], spacing[1], spacing[0]
    tz, ty, tx = target[2], target[1], target[0]
    nz = max(1, int(round(arr.shape[0]*sz/tz)))
    ny = max(1, int(round(arr.shape[1]*sy/ty)))
    nx = max(1, int(round(arr.shape[2]*sx/tx)))
    gz = np.linspace(0, arr.shape[0]-1, nz)
    gy = np.linspace(0, arr.shape[1]-1, ny)
    gx = np.linspace(0, arr.shape[2]-1, nx)
    if order == 0:
        out = arr[np.round(gz).astype(int)][:, np.round(gy).astype(int)][:, :, np.round(gx).astype(int)]
        return out
    def lerp(a, g, axis):
        lo = np.floor(g).astype(int); hi = np.clip(lo+1, 0, a.shape[axis]-1); w = (g-lo)
        sl = [slice(None)]*a.ndim
        sl[axis] = lo; A = a[tuple(sl)]
        sl[axis] = hi; B = a[tuple(sl)]
        sh = [1]*a.ndim; sh[axis] = -1
        return A*(1-w.reshape(sh)) + B*w.reshape(sh)
    out = lerp(arr.astype(float), gz, 0)
    out = lerp(out, gy, 1)
    out = lerp(out, gx, 2)
    return out


def glcm3(vol, msk, bin_width=BIN_WIDTH):
    """3D GLCM：x／y／z 三個方向、距離 1，平均後回傳對比度、同質性、能量。

    z 方向是重點：體素非等向時，z 方向的鄰居在物理上離得比 x/y 遠很多，
    算出來的紋理會被「格子形狀」主導，而不是組織本身。
    """
    roi = msk > 0
    if roi.sum() < 8:
        return 0.0, 1.0, 1.0
    v = np.where(roi, vol, np.nan)
    lo = np.floor(np.nanmin(v) / bin_width) * bin_width
    d = np.floor((v - lo) / bin_width)
    ng = int(np.nanmax(d)) + 1
    P = np.zeros((ng, ng), dtype=float)
    for ax in (0, 1, 2):          # 0=z, 1=y, 2=x
        a = np.take(d, range(0, d.shape[ax] - 1), axis=ax)
        b = np.take(d, range(1, d.shape[ax]), axis=ax)
        ok = ~(np.isnan(a) | np.isnan(b))
        ai = a[ok].astype(int); bi = b[ok].astype(int)
        np.add.at(P, (ai, bi), 1); np.add.at(P, (bi, ai), 1)
    if P.sum() == 0:
        return 0.0, 1.0, 1.0
    P /= P.sum()
    i, j = np.mgrid[0:ng, 0:ng]
    return (float((P * (i - j) ** 2).sum()),
            float((P / (1.0 + (i - j) ** 2)).sum()),
            float((P ** 2).sum()))




def report(tag, vol, msk, spacing):
    n = int((msk > 0).sum())
    vmm = n*spacing[0]*spacing[1]*spacing[2]
    c, h, e = glcm3(vol, msk)
    print(f"=== {tag} ===")
    print(f"  體素間距      {spacing[0]:.3f} × {spacing[1]:.3f} × {spacing[2]:.3f} mm")
    print(f"  ROI 體素數    {n}")
    print(f"  ROI 體積      {vmm:.1f} mm³")
    print(f"  GLCM 對比度   {c:.4f}")
    print(f"  GLCM 同質性   {h:.4f}")
    print(f"  GLCM 能量     {e:.4f}")
    return dict(n=n, vol=vmm, contrast=c, homogeneity=h, energy=e)

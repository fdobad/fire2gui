#!/bin/env python3
#REPLENV: /home/fdo/pyenv/qgis
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import rasterio

def fmt(x):
    s = f"{x:.1f}"
    if s.endswith("0"):
        s = f"{x:.0f}"
    return rf"{s} \%" if plt.rcParams["text.usetex"] else f"{s} %"

delta = np.nextafter( np.float32(0.0), np.float32(1.0), dtype=np.float32)
def NormalizeData(data):
    return (data - np.min(data) - delta) / (np.max(data) - np.min(data) + delta)

e = rasterio.open('elevation.asc')
H,W = e.read(1).shape

e = rasterio.open('py.asc')

x = np.arange(W)
y = np.arange(H)
X, Y = np.meshgrid(x, y)
Z = -(X - W/2)**2 -(Y - H/2)**2

Z = NormalizeData(Z)
Z = np.float32(Z)
fig, ax = plt.subplots()
CS = ax.contour(X, Y, Z)
ax.clabel(CS, CS.levels, inline=True, fmt=fmt, fontsize=10)
plt.show()

plt.close('all')


Z.dtype
probMap = rasterio.open('py2.asc', mode='w', driver=e.driver, width=e.width, height=e.height, count=1, crs=e.crs, dtype=Z.dtype)

probMap.write(Z,1)
probMap.close()

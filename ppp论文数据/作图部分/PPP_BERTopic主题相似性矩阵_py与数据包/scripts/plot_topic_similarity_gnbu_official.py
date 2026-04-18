# -*- coding: utf-8 -*-
"""
基于修正版相似性矩阵，按 BERTopic / Plotly 官方 GnBu 冰蓝风格重绘热力图
输入：
- data/PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版.xlsx
输出：
- outputs/PPP_BERTopic主题相似性矩阵_官方GnBu冰蓝版.png
- outputs/PPP_BERTopic主题相似性矩阵_官方GnBu冰蓝版.svg
- outputs/PPP_BERTopic主题相似性矩阵_官方GnBu冰蓝版_标签对照.xlsx
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, leaves_list

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

xlsx_path = os.path.join(DATA, "PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版.xlsx")
sim_df = pd.read_excel(xlsx_path, sheet_name="相似性矩阵", index_col=0)

S = sim_df.values.astype(float)
D = np.clip(1.0 - S, 0.0, 1.0)
np.fill_diagonal(D, 0.0)

Z = linkage(squareform(D, checks=False), method="average", optimal_ordering=True)
order = leaves_list(Z)
S_ord = S[np.ix_(order, order)]
labels = [str(sim_df.index[i]) for i in order]

# Plotly / BERTopic 常用 GnBu 冰蓝色阶
gnbu_hex = [
    "#f7fcf0", "#e0f3db", "#ccebc5", "#a8ddb5",
    "#7bccc4", "#4eb3d3", "#2b8cbe", "#0868ac", "#084081"
]
cmap = LinearSegmentedColormap.from_list("plotly_gnbu_official", gnbu_hex, N=256)

fig, ax = plt.subplots(figsize=(11.5, 10))
im = ax.imshow(S_ord, cmap=cmap, vmin=0, vmax=1, aspect="auto")
ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=90, fontsize=8)
ax.set_yticklabels(labels, fontsize=8)
ax.set_title("BERTopic Topic Similarity Matrix (Official GnBu Ice-Blue Style)", fontsize=13)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Cosine similarity", fontsize=10)
ax.set_xticks(np.arange(-.5, len(labels), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
ax.grid(which="minor", color="white", linestyle="-", linewidth=0.35, alpha=0.35)
ax.tick_params(which="minor", bottom=False, left=False)
plt.tight_layout()

png_path = os.path.join(OUT, "PPP_BERTopic主题相似性矩阵_官方GnBu冰蓝版.png")
svg_path = os.path.join(OUT, "PPP_BERTopic主题相似性矩阵_官方GnBu冰蓝版.svg")
plt.savefig(png_path, dpi=300, bbox_inches="tight")
plt.savefig(svg_path, bbox_inches="tight")
plt.close(fig)

meta = pd.read_excel(xlsx_path, sheet_name="热力图标签对照")
meta_out = os.path.join(OUT, "PPP_BERTopic主题相似性矩阵_官方GnBu冰蓝版_标签对照.xlsx")
meta.to_excel(meta_out, index=False)
print("完成：", png_path)

import io
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

out_dir = Path(".")
zip_path = Path("/mnt/data/ppp论文数据(1).zip")

def read_csv_from_zip(zf: zipfile.ZipFile, path: str) -> pd.DataFrame:
    with zf.open(path) as f:
        return pd.read_csv(f)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#222222",
    "axes.linewidth": 0.8,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10.5,
    "ytick.labelsize": 10.5,
    "legend.fontsize": 10,
    "grid.color": "#D9D9D9",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.65,
    "font.family": "DejaVu Sans",
})

with zipfile.ZipFile(zip_path) as zf:
    prov = read_csv_from_zip(
        zf,
        "01_第3到第8部分_最终修正版/第4部分_文本变量构造/（4.1-4.4）文本变量构造与输出/PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv",
    )
    doc = read_csv_from_zip(
        zf,
        "01_第3到第8部分_最终修正版/第4部分_文本变量构造/（4.1-4.4）文本变量构造与输出/PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv",
    )

prov["year"] = prov["year"].astype(int)
doc["year"] = pd.to_numeric(doc["year"], errors="coerce")
doc = doc.dropna(subset=["year"]).copy()
doc["year"] = doc["year"].astype(int)

topic_cols = [c for c in prov.columns if c.startswith("topic_") and c.endswith("_share")]
X = prov[topic_cols].fillna(0.0).to_numpy()
X = X - X.mean(axis=0, keepdims=True)
U, S, VT = np.linalg.svd(X, full_matrices=False)
coords = U[:, :2] * S[:2]
prov_plot = prov.copy()
prov_plot["pc1"] = coords[:, 0]
prov_plot["pc2"] = coords[:, 1]

topic_ids = sorted(doc["topic"].dropna().astype(int).unique())
topic_center_map = {
    int(tid): (
        np.cos(i * 2 * np.pi / max(1, len(topic_ids))),
        np.sin(i * 2 * np.pi / max(1, len(topic_ids))),
    )
    for i, tid in enumerate(topic_ids)
}

doc_plot = doc[["province", "year", "topic", "char_len"]].copy()
doc_plot = doc_plot[doc_plot["topic"].notna()].copy()
doc_plot["topic"] = doc_plot["topic"].astype(int)

rng = np.random.default_rng(42)
doc_centers = np.array([topic_center_map.get(t, (0.0, 0.0)) for t in doc_plot["topic"]])
doc_plot["x"] = doc_centers[:, 0] + rng.normal(scale=0.12, size=len(doc_plot))
doc_plot["y"] = doc_centers[:, 1] + rng.normal(scale=0.12, size=len(doc_plot))

fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(
    doc_plot["x"],
    doc_plot["y"],
    s=np.clip(np.log1p(doc_plot["char_len"]) * 2.0, 7, 30),
    facecolors="none",
    edgecolors="#6F9FCB",
    linewidths=1.0,
    alpha=0.52,
    zorder=1
)
ax.scatter(
    doc_plot["x"],
    doc_plot["y"],
    s=np.clip(np.log1p(doc_plot["char_len"]) * 1.0, 5, 14),
    c="#BFD3E6",
    alpha=0.10,
    linewidths=0,
    zorder=1
)

sc = ax.scatter(
    prov_plot["pc1"],
    prov_plot["pc2"],
    c=prov_plot["year"],
    s=np.clip(prov_plot["doc_count"].fillna(1) * 3.2, 22, 130),
    edgecolors="#1F2933",
    linewidths=0.45,
    alpha=0.96,
    zorder=3
)

ax.set_xlabel("Text-structure axis 1")
ax.set_ylabel("Text-structure axis 2")
ax.set_title("Figure 3. Dual-layer topic embedding", pad=10)
ax.grid(True, axis="both")

cbar = fig.colorbar(sc, ax=ax)
cbar.set_label("Year")

legend_handles = [
    Line2D([0], [0], marker="o", linestyle="", markerfacecolor="none",
           markeredgecolor="#6F9FCB", markeredgewidth=1.1, markersize=7.5,
           label="Document-level text observations"),
    Line2D([0], [0], marker="o", linestyle="", markerfacecolor="#4C78A8",
           markeredgecolor="#1F2933", markeredgewidth=0.6, markersize=7.5,
           label="Province-year centroids"),
]
legend = ax.legend(handles=legend_handles, loc="upper right", frameon=True)
legend.get_frame().set_edgecolor("#CCCCCC")
legend.get_frame().set_linewidth(0.8)

out = out_dir / "Figure_3_topic_embedding_dual_layer_refined_v3.png"
fig.savefig(out, dpi=240, bbox_inches="tight")
plt.close(fig)
print(out)

import io
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

out_dir = Path(".")
zip_path = Path("/mnt/data/ppp论文数据(1).zip")

with zipfile.ZipFile(zip_path, "r") as zf:
    with zf.open("01_第3到第8部分_最终修正版/第5部分_核心实证识别/（5.1）识别框架、并表与模型设定/PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv") as f:
        panel = pd.read_csv(f)

panel["year"] = panel["year"].astype(int)
ever_treated = panel.groupby("province")["treat_share"].max().rename("ever_treated")
panel = panel.merge(ever_treated, on="province", how="left")
panel["group"] = np.where(panel["ever_treated"] > 0, "Ever treated", "Never treated")

vars_for_plot = [
    ("exec_share", "Execution share"),
    ("proc_share", "Procurement share"),
    ("treat_share", "Treatment share"),
    ("A_idx", "A index"),
]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#222222",
    "axes.linewidth": 0.8,
    "axes.labelsize": 11.5,
    "axes.titlesize": 13,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9.5,
    "grid.color": "#DADADA",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.6,
    "font.family": "DejaVu Sans",
})

group_order = ["Never treated", "Ever treated"]
group_colors = {
    "Never treated": "#A9B4C2",
    "Ever treated": "#355C7D",
}

fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.8))
axes = axes.ravel()
rng = np.random.default_rng(42)

for ax, (var, title) in zip(axes, vars_for_plot):
    data_left = panel.loc[panel["group"] == group_order[0], var].dropna().to_numpy()
    data_right = panel.loc[panel["group"] == group_order[1], var].dropna().to_numpy()

    parts = ax.violinplot(
        [data_left, data_right],
        positions=[0.85, 1.15],
        widths=0.24,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )
    for i, body in enumerate(parts["bodies"]):
        grp = group_order[i]
        body.set_facecolor(group_colors[grp])
        body.set_edgecolor(group_colors[grp])
        body.set_alpha(0.18)

    bp = ax.boxplot(
        [data_left, data_right],
        positions=[0.85, 1.15],
        widths=0.09,
        vert=True,
        patch_artist=True,
        showfliers=False,
        medianprops=dict(color="#222222", linewidth=1.3),
        whiskerprops=dict(color="#666666", linewidth=0.9),
        capprops=dict(color="#666666", linewidth=0.9),
    )
    for patch, grp in zip(bp["boxes"], group_order):
        patch.set_facecolor("white")
        patch.set_edgecolor(group_colors[grp])
        patch.set_linewidth(1.1)

    jitter_left = rng.normal(0.85, 0.018, size=len(data_left))
    jitter_right = rng.normal(1.15, 0.018, size=len(data_right))
    ax.scatter(jitter_left, data_left, s=13.5, alpha=0.34, color=group_colors[group_order[0]], linewidths=0)
    ax.scatter(jitter_right, data_right, s=13.5, alpha=0.34, color=group_colors[group_order[1]], linewidths=0)

    ax.scatter([0.85], [np.mean(data_left)], s=30, color=group_colors[group_order[0]], edgecolors="white", linewidths=0.5, zorder=4)
    ax.scatter([1.15], [np.mean(data_right)], s=30, color=group_colors[group_order[1]], edgecolors="white", linewidths=0.5, zorder=4)

    ax.set_title(title)
    ax.set_xticks([0.85, 1.15])
    ax.set_xticklabels(["Never treated", "Ever treated"])
    ax.grid(True, axis="y")
    ax.set_xlim(0.62, 1.38)

handles = [
    Line2D([0], [0], color=group_colors["Never treated"], lw=4, alpha=0.7, label="Never treated"),
    Line2D([0], [0], color=group_colors["Ever treated"], lw=4, alpha=0.7, label="Ever treated"),
    Line2D([0], [0], marker="o", linestyle="", color="#444444", markerfacecolor="#444444", label="Group mean"),
]
fig.legend(handles=handles, loc="upper center", ncol=3, frameon=True, bbox_to_anchor=(0.5, 1.01))

fig.suptitle("Figure C. Distribution board for key main-panel variables", y=1.05, fontsize=14)
fig.text(
    0.5, -0.015,
    "2×2 raincloud-style comparison by ever-treated status. This figure complements Table 3 by showing distribution shape and between-group dispersion for the core outcome, treatment and text-mechanism variables.",
    ha="center", fontsize=10
)

fig.tight_layout()
out = out_dir / "Figure_C_raincloud_planA_2x2_final_v3.png"
fig.savefig(out, dpi=300, bbox_inches="tight")
plt.close(fig)
print(out)

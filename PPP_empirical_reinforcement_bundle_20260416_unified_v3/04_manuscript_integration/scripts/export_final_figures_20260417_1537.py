from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
import numpy as np
import pandas as pd


STAMP = "20260417_1537"
ROOT = Path(__file__).resolve().parents[2]


PALETTE = {
    "baseline": "#1f4e79",
    "trend": "#b22222",
    "exec": "#1f4e79",
    "proc": "#b22222",
}

OUTCOME_LABELS_ZH = {
    "exec_share": "执行阶段占比",
    "proc_share": "采购阶段占比",
    "ppp_quality_zindex": "综合治理质量指数",
}
OUTCOME_LABELS_EN = {
    "exec_share": "exec_share",
    "proc_share": "proc_share",
    "ppp_quality_zindex": "ppp_quality_zindex",
}


def chinese_font() -> FontProperties | None:
    candidates = ["Microsoft YaHei", "SimHei", "SimSun"]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            plt.rcParams["axes.unicode_minus"] = False
            return FontProperties(fname=font_manager.findfont(name, fallback_to_default=False))
    return None


def save_png_svg(fig, out_prefix: Path) -> None:
    for suffix in [".png", ".svg"]:
        fig.savefig(out_prefix.with_suffix(suffix), dpi=300, bbox_inches="tight")


def export_fig8a() -> list[Path]:
    trend_path = ROOT / "01_trend_adjusted_DID" / "tables" / "trend_adjusted_did_results.xlsx"
    df = pd.read_excel(trend_path)
    fig_dir = ROOT / "01_trend_adjusted_DID" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    font = chinese_font()

    outputs: list[Path] = []

    for mode in ["diag", "paper"]:
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        y = np.arange(len(df))[::-1]
        for i, (_, row) in enumerate(df.iterrows()):
            ax.errorbar(
                row["canonical_baseline_coef"],
                y[i] + 0.12,
                xerr=1.96 * row["canonical_baseline_se"],
                fmt="o",
                color=PALETTE["baseline"],
                capsize=3,
                markersize=6,
                label="Baseline DID" if i == 0 else None,
            )
            ax.errorbar(
                row["trend_adjusted_coef"],
                y[i] - 0.12,
                xerr=1.96 * row["trend_adjusted_se"],
                fmt="o",
                color=PALETTE["trend"],
                capsize=3,
                markersize=6,
                label="Trend-adjusted DID" if i == 0 else None,
            )
        ax.axvline(0, color="black", linewidth=1)
        ax.grid(axis="x", alpha=0.2)
        labels = [OUTCOME_LABELS_EN[o] for o in df["outcome"]] if mode == "diag" else [OUTCOME_LABELS_ZH[o] for o in df["outcome"]]
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontproperties=font if mode == "paper" else None)
        if mode == "paper":
            ax.set_title("图8A 趋势调整型DID与基准DID结果比较", fontproperties=font)
            ax.set_xlabel("treat_share 系数（95%置信区间）", fontproperties=font)
            ax.legend(["基准 DID", "趋势调整型 DID"], frameon=False, prop=font)
            out_prefix = fig_dir / f"Figure_8A_trend_adjusted_did_{STAMP}"
        else:
            ax.set_title("Figure 8A diagnostic: baseline vs trend-adjusted DID")
            ax.set_xlabel("Coefficient on treat_share (95% CI)")
            ax.legend(frameon=False)
            out_prefix = fig_dir / f"Figure_8A_trend_adjusted_did_diagnostic_{STAMP}"
        fig.tight_layout()
        save_png_svg(fig, out_prefix)
        outputs.extend([out_prefix.with_suffix(".png"), out_prefix.with_suffix(".svg")])
        plt.close(fig)
    return outputs


def export_fig8b() -> list[Path]:
    per_path = ROOT / "02_leave_one_province_out_jackknife" / "tables" / "leave_one_province_out_results.xlsx"
    sum_path = ROOT / "02_leave_one_province_out_jackknife" / "tables" / "leave_one_province_out_stability_summary.xlsx"
    per_df = pd.read_excel(per_path, sheet_name="per_province")
    summary_df = pd.read_excel(sum_path)
    fig_dir = ROOT / "02_leave_one_province_out_jackknife" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    font = chinese_font()

    outputs: list[Path] = []

    for mode in ["diag", "paper"]:
        fig, axes = plt.subplots(2, 1, figsize=(9.2, 7.2), sharex=False)
        for ax, outcome in zip(axes, ["exec_share", "proc_share"]):
            sub = per_df.loc[per_df["outcome"] == outcome].copy().sort_values("coef").reset_index(drop=True)
            baseline = float(summary_df.loc[summary_df["outcome"] == outcome, "canonical_baseline_coef"].iloc[0])
            ax.scatter(np.arange(len(sub)), sub["coef"], color=PALETTE["exec"] if outcome == "exec_share" else PALETTE["proc"], s=22, alpha=0.9)
            ax.axhline(baseline, color="black", linestyle="--", linewidth=1)
            if mode == "paper":
                ax.set_title(f"{OUTCOME_LABELS_ZH[outcome]}：删一省后的系数稳定性", fontproperties=font)
                ax.set_ylabel("treat_share 系数", fontproperties=font)
            else:
                ax.set_title(f"{outcome}: leave-one-province-out stability")
                ax.set_ylabel("coef on treat_share")
            ax.set_xticks([0, len(sub) // 2, len(sub) - 1])
            ax.set_xticklabels(["min", "mid", "max"])
            ax.grid(axis="y", alpha=0.2)
        if mode == "paper":
            axes[-1].set_xlabel("删去单个省份后的排序位置", fontproperties=font)
            fig.suptitle("图8B 删一省诊断下核心推进结构结果的稳定性", fontproperties=font, y=0.99)
            out_prefix = fig_dir / f"Figure_8B_jackknife_stability_{STAMP}"
        else:
            axes[-1].set_xlabel("province deletion rank")
            fig.suptitle("Figure 8B diagnostic: leave-one-province-out stability", y=0.99)
            out_prefix = fig_dir / f"Figure_8B_jackknife_stability_diagnostic_{STAMP}"
        fig.tight_layout()
        save_png_svg(fig, out_prefix)
        outputs.extend([out_prefix.with_suffix(".png"), out_prefix.with_suffix(".svg")])
        plt.close(fig)
    return outputs


def main() -> None:
    outputs = export_fig8a() + export_fig8b()
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()

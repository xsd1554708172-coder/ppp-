from __future__ import annotations

from pathlib import Path

import pandas as pd


def main() -> None:
    script_path = Path(__file__).resolve()
    module_root = script_path.parents[1]
    bundle_root = script_path.parents[2]

    table_dir = module_root / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    baseline = pd.read_excel(
        bundle_root
        / "00_unified_baseline_reference"
        / "tables"
        / "unified_baseline_reference.xlsx",
        sheet_name="baseline_reference",
    )[["outcome", "official_coef", "official_p_value"]]

    trend = pd.read_excel(
        bundle_root
        / "01_trend_adjusted_DID"
        / "tables"
        / "trend_adjusted_did_results.xlsx"
    )[
        [
            "outcome",
            "trend_adjusted_coef",
            "trend_adjusted_p_value",
            "direction_same_as_baseline",
        ]
    ]

    leave = pd.read_excel(
        bundle_root
        / "02_leave_one_province_out_jackknife"
        / "tables"
        / "leave_one_province_out_stability_summary.xlsx"
    )[
        [
            "outcome",
            "n_sign_flip",
            "n_sig_jump_5pct",
            "max_abs_deviation_province",
            "max_abs_deviation",
        ]
    ]

    bootstrap = pd.read_excel(
        bundle_root
        / "03_small_sample_inference_wild_cluster_bootstrap"
        / "tables"
        / "small_sample_inference_summary.xlsx"
    )[["outcome", "wild_bootstrap_p", "module_role"]]

    summary = (
        baseline.merge(trend, on="outcome", how="left")
        .merge(leave, on="outcome", how="left")
        .merge(bootstrap, on="outcome", how="left")
    )

    def reading_rule(row: pd.Series) -> str:
        if row["outcome"] == "exec_share":
            return "基准 DID 最稳；趋势调整后方向仍为正但显著性减弱；leave-one-out 未出现方向翻转；更保守小样本推断仅支持边界说明。"
        if row["outcome"] == "proc_share":
            return "基准 DID 与趋势调整 DID 均支持负向结果；leave-one-out 未出现方向翻转，但显著性对个别省份敏感；更保守小样本推断只保留方向稳定。"
        return "质量型口径在基准 DID 下已不稳，趋势调整后方向转负且继续不显著；不应在正文中被抬升为主结论。"

    summary["recommended_reading"] = summary.apply(reading_rule, axis=1)
    summary.to_excel(table_dir / "robustness_defense_summary.xlsx", index=False)


if __name__ == "__main__":
    main()

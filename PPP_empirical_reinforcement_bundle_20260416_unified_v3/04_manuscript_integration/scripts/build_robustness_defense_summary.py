from pathlib import Path

import pandas as pd


def main() -> None:
    here = Path(__file__).resolve()
    integration_root = here.parents[1]
    bundle_root = here.parents[2]

    baseline = pd.read_excel(
        bundle_root / "00_unified_baseline_reference" / "tables" / "unified_baseline_reference.xlsx",
        sheet_name="manuscript_baseline",
    )[
        [
            "outcome",
            "official_coef",
            "official_se",
            "official_p_value",
            "official_nobs",
        ]
    ].rename(
        columns={
            "official_coef": "baseline_coef",
            "official_se": "baseline_se",
            "official_p_value": "baseline_p_value",
            "official_nobs": "baseline_nobs",
        }
    )

    trend = pd.read_excel(
        bundle_root / "01_trend_adjusted_DID" / "tables" / "trend_adjusted_did_results.xlsx"
    )[
        [
            "outcome",
            "outcome_label_zh",
            "trend_adjusted_coef",
            "trend_adjusted_se",
            "trend_adjusted_p_value",
            "strength_reading",
        ]
    ]

    loo = pd.read_excel(
        bundle_root
        / "02_leave_one_province_out_jackknife"
        / "tables"
        / "leave_one_province_out_stability_summary.xlsx"
    )[
        [
            "outcome",
            "n_sign_flip_vs_canonical_baseline",
            "n_sig_jump_5pct_vs_canonical_baseline",
            "max_abs_deviation_province",
            "max_abs_deviation",
        ]
    ]

    bootstrap = pd.read_excel(
        bundle_root
        / "03_small_sample_inference_wild_cluster_bootstrap"
        / "tables"
        / "wild_cluster_bootstrap_summary.xlsx"
    )[
        [
            "outcome",
            "wild_cluster_bootstrap_p_value",
            "reading_rule",
        ]
    ]

    summary = (
        baseline.merge(trend, on="outcome", how="left")
        .merge(loo, on="outcome", how="left")
        .merge(bootstrap, on="outcome", how="left")
    )

    summary["recommended_reading"] = summary["outcome"].map(
        {
            "exec_share": "主结论方向保持一致；趋势调整后强度减弱；删一省不翻符号；更保守推断下需保留统计强度敏感性。",
            "proc_share": "主结论防守性最强；趋势调整后仍显著负向；删一省不翻符号，但对个别省份存在强度敏感性。",
            "ppp_quality_zindex": "不应抬升；趋势调整后方向与强度均不稳；删一省波动较大；更保守推断亦不支持将其写成稳健主结果。",
        }
    )

    summary["module_role"] = summary["outcome"].map(
        {
            "exec_share": "defensive_robustness",
            "proc_share": "defensive_robustness",
            "ppp_quality_zindex": "boundary_result_only",
        }
    )

    out_path = integration_root / "tables" / "robustness_defense_summary.xlsx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="summary")


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import statsmodels.formula.api as smf


OUTCOMES = ["exec_share", "proc_share", "ppp_quality_zindex"]
CONTROLS = [
    "dfi",
    "digital_econ",
    "ln_rd_expenditure",
    "ln_tech_contract_value",
    "ln_patent_grants",
]
TREATMENT = "treat_share"
PROVINCE_COL = "province"
YEAR_COL = "year"
BASE_SAMPLE_FLAG = "baseline_sample_5_3"


@dataclass
class WorkspacePaths:
    workspace_root: Path
    bundle_root: Path
    panel_csv: Path
    baseline_long_table: Path
    event_study_long_table: Path | None
    current_docx: Path


def find_single(
    root: Path, pattern: str, preferred_substrings: tuple[str, ...] = ()
) -> Path:
    matches = sorted(root.rglob(pattern))
    if not matches:
        raise FileNotFoundError(f"Could not find pattern: {pattern}")
    if preferred_substrings:
        preferred = [
            p
            for p in matches
            if all(token.lower() in str(p).lower() for token in preferred_substrings)
        ]
        if len(preferred) == 1:
            return preferred[0]
        if len(preferred) > 1:
            matches = preferred
    if len(matches) > 1:
        raise ValueError(
            f"Pattern {pattern} is ambiguous under {root}: "
            + "; ".join(str(p) for p in matches[:5])
        )
    return matches[0]


def resolve_paths(script_path: Path) -> WorkspacePaths:
    bundle_root = script_path.resolve().parents[2]
    workspace_root = bundle_root.parent

    return WorkspacePaths(
        workspace_root=workspace_root,
        bundle_root=bundle_root,
        panel_csv=find_single(
            workspace_root,
            "PPP_3.6_model_ready_panel_v3_*.csv",
            preferred_substrings=("20260413_1048",),
        ),
        baseline_long_table=find_single(
            workspace_root,
            "PPP_*5.3*.csv",
            preferred_substrings=("20260413_1048",),
        ),
        event_study_long_table=next(
            iter(
                sorted(
                    p
                    for p in workspace_root.rglob("PPP_*5.4*.csv")
                    if "20260413_1048" in str(p)
                )
            ),
            None,
        ),
        current_docx=find_single(
            workspace_root,
            "PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_*.docx",
            preferred_substrings=("定点替换",),
        ),
    )


def load_main_panel(panel_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(panel_csv)
    required = {
        BASE_SAMPLE_FLAG,
        PROVINCE_COL,
        YEAR_COL,
        TREATMENT,
        *CONTROLS,
        *OUTCOMES,
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise KeyError(f"Missing required columns in main panel: {missing}")
    return df


def clean_baseline_sample(df: pd.DataFrame, outcomes: Iterable[str] = OUTCOMES) -> pd.DataFrame:
    keep = df.loc[df[BASE_SAMPLE_FLAG] == 1].copy()
    needed = [TREATMENT, PROVINCE_COL, YEAR_COL, *CONTROLS, *list(outcomes)]
    keep = keep.dropna(subset=needed)
    keep[PROVINCE_COL] = keep[PROVINCE_COL].astype(str)
    keep[YEAR_COL] = keep[YEAR_COL].astype(int)
    for col in [TREATMENT, *CONTROLS, *list(outcomes)]:
        keep[col] = pd.to_numeric(keep[col], errors="coerce")
    keep = keep.dropna(subset=[TREATMENT, *CONTROLS, *list(outcomes)])
    keep["year_idx"] = keep[YEAR_COL] - keep[YEAR_COL].min()
    return keep


def baseline_formula(outcome: str) -> str:
    rhs = " + ".join([TREATMENT, *CONTROLS, f"C({PROVINCE_COL})", f"C({YEAR_COL})"])
    return f"{outcome} ~ {rhs}"


def trend_adjusted_formula(outcome: str) -> str:
    base = baseline_formula(outcome)
    return f"{base} + C({PROVINCE_COL}):year_idx"


def fit_clustered(df: pd.DataFrame, formula: str):
    return smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df[PROVINCE_COL], "use_correction": True},
    )


def rerun_baseline_reference(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in OUTCOMES:
        fit = fit_clustered(df, baseline_formula(outcome))
        rows.append(
            {
                "outcome": outcome,
                "specification": "baseline_treat_share_twfe",
                "coef": float(fit.params[TREATMENT]),
                "se": float(fit.bse[TREATMENT]),
                "p_value": float(fit.pvalues[TREATMENT]),
                "nobs": int(fit.nobs),
                "province_fe": True,
                "year_fe": True,
                "controls": ", ".join(CONTROLS),
                "cluster": PROVINCE_COL,
                "treatment": TREATMENT,
            }
        )
    return pd.DataFrame(rows)


def read_official_baseline_rows(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    keep = df.loc[df["did_var"] == TREATMENT, ["depvar", "coef", "se", "p", "N", "estimation_note"]].copy()
    keep = keep.rename(
        columns={
            "depvar": "outcome",
            "coef": "official_coef",
            "se": "official_se",
            "p": "official_p_value",
            "N": "official_nobs",
        }
    )
    return keep

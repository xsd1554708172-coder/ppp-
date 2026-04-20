from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import numpy as np
from scipy import stats


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

CANONICAL_BASELINE_SHEET = "manuscript_baseline"
AUDIT_BASELINE_SHEET = "audit_rerun"
SPEC_ANCHOR_SHEET = "spec_anchor"


@dataclass
class WorkspacePaths:
    workspace_root: Path
    bundle_root: Path
    panel_csv: Path
    baseline_long_table: Path
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
    official_docx = (
        workspace_root
        / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260418_对象保留投稿版.docx"
    )
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
        current_docx=official_docx
        if official_docx.exists()
        else find_single(
            workspace_root,
            "*.docx",
            preferred_substrings=("20260418", "对象保留投稿版"),
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


def clean_baseline_sample(
    df: pd.DataFrame, outcomes: Iterable[str] = OUTCOMES
) -> pd.DataFrame:
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
    return f"{baseline_formula(outcome)} + C({PROVINCE_COL}):year_idx"


def _design_matrix(df: pd.DataFrame, outcome: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
    work = df[[outcome, TREATMENT, PROVINCE_COL, YEAR_COL, *CONTROLS]].copy()
    y = work[outcome].to_numpy(dtype=float)

    blocks = [pd.Series(1.0, index=work.index, name="intercept")]
    col_names = ["intercept"]

    for name in [TREATMENT, *CONTROLS]:
        blocks.append(work[name].astype(float))
        col_names.append(name)

    province_dummies = pd.get_dummies(work[PROVINCE_COL], prefix="province", drop_first=True)
    year_dummies = pd.get_dummies(work[YEAR_COL], prefix="year", drop_first=True)

    for col in province_dummies.columns:
        blocks.append(province_dummies[col].astype(float))
        col_names.append(col)
    for col in year_dummies.columns:
        blocks.append(year_dummies[col].astype(float))
        col_names.append(col)

    X = pd.concat(blocks, axis=1).to_numpy(dtype=float)
    return X, y, col_names


class ClusteredOLSResult:
    def __init__(self, params: pd.Series, bse: pd.Series, pvalues: pd.Series, nobs: int):
        self.params = params
        self.bse = bse
        self.pvalues = pvalues
        self.nobs = nobs


def fit_clustered(df: pd.DataFrame, formula: str):
    outcome = formula.split("~", 1)[0].strip()
    X, y, col_names = _design_matrix(df, outcome)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    xtx_inv = np.linalg.pinv(X.T @ X)

    groups = df[PROVINCE_COL].astype(str).to_numpy()
    unique_groups = pd.unique(groups)
    meat = np.zeros((X.shape[1], X.shape[1]), dtype=float)
    for g in unique_groups:
        idx = groups == g
        Xg = X[idx, :]
        eg = resid[idx]
        sg = Xg.T @ eg
        meat += np.outer(sg, sg)

    nobs = int(X.shape[0])
    nparams = int(X.shape[1])
    nclusters = int(len(unique_groups))
    correction = 1.0
    if nclusters > 1 and nobs > nparams:
        correction = (nclusters / (nclusters - 1.0)) * ((nobs - 1.0) / (nobs - nparams))
    vcov = xtx_inv @ meat @ xtx_inv * correction
    se = np.sqrt(np.clip(np.diag(vcov), a_min=0.0, a_max=None))
    dof = max(nclusters - 1, 1)
    tvals = beta / se
    pvals = 2.0 * stats.t.sf(np.abs(tvals), df=dof)

    params = pd.Series(beta, index=col_names)
    bse = pd.Series(se, index=col_names)
    pvalues = pd.Series(pvals, index=col_names)
    return ClusteredOLSResult(params=params, bse=bse, pvalues=pvalues, nobs=nobs)


def read_official_baseline_rows(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    keep = df.loc[
        df["did_var"] == TREATMENT,
        ["depvar", "coef", "se", "p", "N", "estimation_note"],
    ].copy()
    keep = keep.rename(
        columns={
            "depvar": "outcome",
            "coef": "official_coef",
            "se": "official_se",
            "p": "official_p_value",
            "N": "official_nobs",
            "estimation_note": "official_estimation_note",
        }
    )
    keep["canonical_source"] = "official_5_3_long_table"
    keep["canonical_treatment"] = TREATMENT
    keep["canonical_sample_flag"] = BASE_SAMPLE_FLAG
    return keep


def rerun_baseline_reference(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in OUTCOMES:
        fit = fit_clustered(df, baseline_formula(outcome))
        rows.append(
            {
                "outcome": outcome,
                "rerun_specification": "baseline_treat_share_twfe",
                "coef": float(fit.params[TREATMENT]),
                "se": float(fit.bse[TREATMENT]),
                "p_value": float(fit.pvalues[TREATMENT]),
                "nobs": int(fit.nobs),
                "province_fe": True,
                "year_fe": True,
                "cluster": PROVINCE_COL,
                "controls": ", ".join(CONTROLS),
                "treatment": TREATMENT,
            }
        )
    return pd.DataFrame(rows)


def build_manuscript_baseline_reference(official: pd.DataFrame) -> pd.DataFrame:
    merged = official.copy()
    merged["manuscript_face"] = True
    merged["manuscript_face_note"] = "Official 5.3 long-table anchor"
    return merged


def build_audit_rerun_reference(official: pd.DataFrame, rerun: pd.DataFrame) -> pd.DataFrame:
    merged = official.merge(rerun, on="outcome", how="left")
    merged["coef_diff_vs_official"] = merged["coef"] - merged["official_coef"]
    merged["se_diff_vs_official"] = merged["se"] - merged["official_se"]
    merged["p_diff_vs_official"] = merged["p_value"] - merged["official_p_value"]
    merged["matches_official_within_tolerance"] = (
        merged[["coef_diff_vs_official", "se_diff_vs_official", "p_diff_vs_official"]]
        .abs()
        .max(axis=1)
        .lt(1e-6)
    )
    return merged


def build_spec_anchor(base_df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "canonical_main_identification": [f"{TREATMENT} multi-period DID / TWFE"],
            "canonical_manuscript_baseline": [
                "Official 5.3 long-table anchor; rerun kept as audit only"
            ],
            "baseline_sample_flag": [BASE_SAMPLE_FLAG],
            "baseline_sample_nobs": [int(base_df.shape[0])],
            "province_count": [int(base_df[PROVINCE_COL].nunique())],
            "year_span": [f"{int(base_df[YEAR_COL].min())}-{int(base_df[YEAR_COL].max())}"],
            "cluster": [PROVINCE_COL],
            "fixed_effects": ["province FE + year FE"],
            "controls": [", ".join(CONTROLS)],
        }
    )


def baseline_reference_workbook(bundle_root: Path) -> Path:
    path = (
        bundle_root
        / "00_unified_baseline_reference"
        / "tables"
        / "unified_baseline_reference.xlsx"
    )
    if not path.exists():
        raise FileNotFoundError(
            "Unified baseline reference workbook not found: "
            f"{path}"
        )
    return path


def read_manuscript_baseline_reference(bundle_root: Path) -> pd.DataFrame:
    path = baseline_reference_workbook(bundle_root)
    keep = pd.read_excel(path, sheet_name=CANONICAL_BASELINE_SHEET)
    required = {"outcome", "official_coef", "official_se", "official_p_value", "official_nobs"}
    missing = sorted(required - set(keep.columns))
    if missing:
        raise KeyError(
            "Canonical manuscript baseline sheet is missing required columns: "
            f"{missing}"
        )
    return keep.copy()

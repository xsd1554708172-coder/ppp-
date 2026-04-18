
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.formula.api as smf
from scipy.stats import norm

controls = ["dfi","digital_econ","ln_rd_expenditure","ln_tech_contract_value","ln_patent_grants"]

def make_X(df, regressors):
    X = df[regressors].copy()
    prov = pd.get_dummies(df["province"], prefix="prov", drop_first=True, dtype=float)
    year = pd.get_dummies(df["year"].astype(int), prefix="year", drop_first=True, dtype=float)
    X = pd.concat([pd.Series(1.0, index=df.index, name="const"), X, prov, year], axis=1)
    return X

def coef_only(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta

def bootstrap_indirect_fast(data, x, m, y, controls, n_boot=1000, seed=42):
    d1 = data[[x,m,"province","year"] + controls].dropna().copy()
    fit_a = smf.ols(f"{m} ~ {x} + " + " + ".join(controls) + " + C(province) + C(year)", data=d1)\
        .fit(cov_type="cluster", cov_kwds={"groups": d1["province"]})
    a = fit_a.params[x]; sa = fit_a.bse[x]

    d2 = data[[x,m,y,"province","year"] + controls].dropna().copy()
    fit_b = smf.ols(f"{y} ~ {x} + {m} + " + " + ".join(controls) + " + C(province) + C(year)", data=d2)\
        .fit(cov_type="cluster", cov_kwds={"groups": d2["province"]})
    b = fit_b.params[m]; sb = fit_b.bse[m]
    direct = fit_b.params[x]

    z = (a*b) / np.sqrt((b*b*sa*sa) + (a*a*sb*sb))
    p = 2*(1-norm.cdf(abs(z)))

    common_provs = sorted(set(d1["province"].unique()).intersection(set(d2["province"].unique())))
    d1 = d1[d1["province"].isin(common_provs)].copy().reset_index(drop=True)
    d2 = d2[d2["province"].isin(common_provs)].copy().reset_index(drop=True)

    X1 = make_X(d1, [x] + controls)
    X2 = make_X(d2, [x, m] + controls)
    x_idx = list(X1.columns).index(x)
    m_idx = list(X2.columns).index(m)

    y1 = d1[m].to_numpy(dtype=float)
    y2 = d2[y].to_numpy(dtype=float)
    X1_np = X1.to_numpy(dtype=float)
    X2_np = X2.to_numpy(dtype=float)

    prov_pos1 = {p: np.where(d1["province"].to_numpy()==p)[0] for p in common_provs}
    prov_pos2 = {p: np.where(d2["province"].to_numpy()==p)[0] for p in common_provs}

    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        samp = rng.choice(common_provs, size=len(common_provs), replace=True)
        pos1 = np.concatenate([prov_pos1[p] for p in samp])
        pos2 = np.concatenate([prov_pos2[p] for p in samp])
        beta1 = coef_only(y1[pos1], X1_np[pos1, :])
        beta2 = coef_only(y2[pos2], X2_np[pos2, :])
        boot[i] = beta1[x_idx] * beta2[m_idx]
    return boot

if __name__ == "__main__":
    panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
    comp = pd.DataFrame({
        "exec_share": panel["exec_share"],
        "proc_share_neg": -panel["proc_share"],
        "prep_share_neg": -panel["prep_share"],
        "fiscal_pass_rate": panel["fiscal_pass_rate"],
        "vfm_pass_rate": panel["vfm_pass_rate"],
    })
    idx = comp.dropna().index
    pc = PCA(n_components=1).fit_transform(StandardScaler().fit_transform(comp.loc[idx])).ravel()
    if np.corrcoef(pc, panel.loc[idx, "exec_share"])[0,1] < 0:
        pc = -pc
    panel["ppp_quality_pca_rebuilt_fixed"] = np.nan
    panel.loc[idx, "ppp_quality_pca_rebuilt_fixed"] = pc

    for y in ["exec_share","proc_share","ppp_quality_pca_rebuilt_fixed"]:
        boot = bootstrap_indirect_fast(panel, "treat_share", "A_idx", y, controls, n_boot=1000, seed=42)
        print(y, np.quantile(boot, [0.025, 0.975]))

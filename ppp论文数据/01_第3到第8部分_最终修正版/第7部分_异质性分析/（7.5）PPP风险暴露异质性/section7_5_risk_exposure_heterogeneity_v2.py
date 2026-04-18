
import pandas as pd, numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.formula.api as smf

panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
risk_components = pd.DataFrame(index=panel.index)
risk_components['proc_share_risk'] = panel['proc_share']
risk_components['prep_share_risk'] = panel['prep_share']
risk_components['exec_share_risk'] = -panel['exec_share']
risk_components['fiscal_pass_risk'] = -panel['fiscal_pass_rate']
risk_components['vfm_pass_risk'] = -panel['vfm_pass_rate']
risk_components['C_idx_risk'] = panel['C_idx']
valid = risk_components.dropna()
risk_z = pd.DataFrame(StandardScaler().fit_transform(valid), index=valid.index, columns=valid.columns)
panel.loc[valid.index, 'ppp_risk_exposure_index'] = risk_z.mean(axis=1)
panel['high_ppp_risk_exposure'] = (panel['ppp_risk_exposure_index'] >= panel['ppp_risk_exposure_index'].median()).astype(int)
print(panel[['ppp_risk_exposure_index','high_ppp_risk_exposure']].head())

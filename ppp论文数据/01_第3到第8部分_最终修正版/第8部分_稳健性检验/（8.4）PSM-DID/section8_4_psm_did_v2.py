
import pandas as pd, numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv").sort_values(['province','year']).reset_index(drop=True)
match_covs = ['dfi','digital_econ','ln_rd_expenditure','ln_tech_contract_value','ln_patent_grants','exec_share','proc_share','prep_share']
for c in match_covs:
    panel[f'L1_{c}'] = panel.groupby('province')[c].shift(1)
psm_covs = [f'L1_{c}' for c in match_covs]
psm_df = panel[['province','year','did_any'] + psm_covs].dropna().copy()
X = psm_df[psm_covs].values
y = psm_df['did_any'].astype(int).values
logit = LogisticRegression(max_iter=2000, random_state=42).fit(X,y)
psm_df['pscore'] = logit.predict_proba(X)[:,1]
print(psm_df[['province','year','did_any','pscore']].head())

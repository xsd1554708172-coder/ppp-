
import pandas as pd, numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import LassoCV, LinearRegression

panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
base_controls = ['dfi','digital_econ','A_idx','B_idx','C_idx'] + [f'topic_{i}_share' for i in range(10)]
use = panel[['exec_share','treat_share','province','year'] + base_controls].dropna().copy()
X = use[base_controls].fillna(use[base_controls].median())
y = use['exec_share'].to_numpy()
d = use['treat_share'].to_numpy()
kf = KFold(n_splits=5, shuffle=True, random_state=42)
y_res = np.zeros(len(use)); d_res = np.zeros(len(use))
for tr, te in kf.split(X):
    my = LassoCV(cv=5, random_state=42, max_iter=20000).fit(X.iloc[tr], y[tr])
    md = LassoCV(cv=5, random_state=42, max_iter=20000).fit(X.iloc[tr], d[tr])
    y_res[te] = y[te] - my.predict(X.iloc[te])
    d_res[te] = d[te] - md.predict(X.iloc[te])
theta = LinearRegression(fit_intercept=False).fit(d_res.reshape(-1,1), y_res).coef_[0]
print('DML theta=', theta)

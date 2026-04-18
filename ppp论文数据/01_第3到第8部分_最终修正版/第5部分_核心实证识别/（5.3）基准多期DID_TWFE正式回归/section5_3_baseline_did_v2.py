
import pandas as pd, numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.formula.api as smf

panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
sub = pd.DataFrame({
    'exec_share': panel['exec_share'],
    'proc_share_neg': -panel['proc_share'],
    'prep_share_neg': -panel['prep_share'],
    'fiscal_pass_rate': panel['fiscal_pass_rate'],
    'vfm_pass_rate': panel['vfm_pass_rate'],
})
panel['ppp_quality_pca_rebuilt'] = PCA(n_components=1).fit_transform(StandardScaler().fit_transform(sub)).ravel()
controls = ['dfi','digital_econ','ln_rd_expenditure','ln_tech_contract_value','ln_patent_grants']
for y in ['ppp_quality_zindex','ppp_quality_pca_rebuilt','exec_share','proc_share','prep_share']:
    for did in ['did_intensity','did_any','treat_share']:
        df = panel[[y,did,'province','year']+controls].dropna().copy()
        fit = smf.ols(y + ' ~ ' + did + ' + ' + ' + '.join(controls) + ' + C(province) + C(year)', data=df).fit(cov_type='cluster', cov_kwds={'groups': df['province']})
        print(y, did, fit.params.get(did), fit.pvalues.get(did))

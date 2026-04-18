
import pandas as pd, numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.formula.api as smf
from plot_font_setup_cn import setup_chinese_fonts
setup_chinese_fonts()

panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
sub = pd.DataFrame({
    'exec_share': panel['exec_share'],
    'proc_share_neg': -panel['proc_share'],
    'prep_share_neg': -panel['prep_share'],
    'fiscal_pass_rate': panel['fiscal_pass_rate'],
    'vfm_pass_rate': panel['vfm_pass_rate'],
})
panel['ppp_quality_pca_rebuilt'] = PCA(n_components=1).fit_transform(StandardScaler().fit_transform(sub)).ravel()
first_treat = panel.loc[panel['did_any'] > 0].groupby('province')['year'].min()
panel['first_treat_year'] = panel['province'].map(first_treat)
panel['ever_treated'] = panel['first_treat_year'].notna().astype(int)
panel['event_time'] = panel['year'] - panel['first_treat_year']
def event_bin(x):
    if pd.isna(x): return np.nan
    if x <= -2: return -2
    if x >= 3: return 3
    return int(x)
panel['event_bin'] = panel['event_time'].apply(event_bin)
print(panel[['province','year','event_bin']].head())

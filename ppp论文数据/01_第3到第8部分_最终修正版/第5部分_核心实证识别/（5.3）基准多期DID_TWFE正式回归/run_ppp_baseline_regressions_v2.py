import pandas as pd, statsmodels.formula.api as smf

df=pd.read_csv('/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv')
controls=['dfi','digital_econ','base_station_density','software_gdp_share','it_service_gdp_share',
          'ln_rd_expenditure','ln_tech_contract_value','ln_patent_grants','ln_ppp_doc_n','ln_ppp_inv']

def run_fe(data, dep, rhs):
    formula = dep + ' ~ ' + ' + '.join(rhs) + ' + C(province) + C(year)'
    return smf.ols(formula, data=data).fit(cov_type='cluster', cov_kwds={'groups': data['province']})

for dep in ['ppp_quality_zindex','exec_share','proc_share','prep_share']:
    dat=df[['province','year',dep,'did_intensity']+controls].dropna().copy()
    res=run_fe(dat, dep, ['did_intensity']+controls)
    print(dep, res.params['did_intensity'], res.pvalues['did_intensity'])

import pandas as pd
panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
candidates = ['base_station_density','software_gdp_share','it_service_gdp_share','digital_econ','dfi','city_n','post']
for z in candidates:
    tmp = panel[[z,'treat_share','exec_share','proc_share']].dropna()
    if len(tmp)>5:
        print(z, 'corr_treat=', tmp[z].corr(tmp['treat_share']), 'corr_exec=', tmp[z].corr(tmp['exec_share']))


import pandas as pd
panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
first_treat = panel[panel['did_any'] > 0].groupby('province')['year'].min().rename('first_treat_year')
prov_years = panel.groupby('province')['year'].agg(min_year='min', max_year='max', obs_n='count').reset_index()
prov = prov_years.merge(first_treat, on='province', how='left')
prov['ever_treated'] = prov['first_treat_year'].notna().astype(int)
timing_dist = prov.groupby('first_treat_year', dropna=False).size().reset_index(name='province_n')
print(prov.head())
print(timing_dist)

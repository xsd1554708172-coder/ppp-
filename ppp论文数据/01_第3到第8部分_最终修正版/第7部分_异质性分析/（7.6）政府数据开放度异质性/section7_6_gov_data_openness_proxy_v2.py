
import pandas as pd
from sklearn.preprocessing import StandardScaler

panel = pd.read_csv("PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv")
proxy_components = panel[['A1_idx','A2_idx']].dropna()
proxy_z = pd.DataFrame(StandardScaler().fit_transform(proxy_components), index=proxy_components.index, columns=['A1_z','A2_z'])
panel.loc[proxy_z.index, 'gov_data_openness_proxy'] = proxy_z.mean(axis=1)
panel['high_gov_data_openness_proxy'] = (panel['gov_data_openness_proxy'] >= panel['gov_data_openness_proxy'].median()).astype(int)
print(panel[['gov_data_openness_proxy','high_gov_data_openness_proxy']].head())

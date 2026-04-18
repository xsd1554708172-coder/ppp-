# 第5部分 5.3 基准多期 DID/TWFE 正式回归（V2 四级十二类）

- 面板文件：`PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv`
- 识别方式：省-年 TWFE
- 固定效应：province FE + year FE
- 聚类：province
- 控制变量：dfi, digital_econ, base_station_density, software_gdp_share, it_service_gdp_share, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants
- 样本量：262

## 本批核心发现
- `treat_share -> exec_share`：0.3556，p=0.0004
- `treat_share -> proc_share`：-0.4023，p=0.0001
- `treat_share -> prep_share`：0.0466，p=0.2737
- `treat_share -> ppp_quality_zindex`：0.5253，p=0.2126
- `treat_share -> vfm_pass_rate`：0.0101，p=0.2816

## 说明
- 为复现旧版正式回归样本量与控制口径，本批未纳入 `city_n`。
- 当前 v2 panel 中没有可直接进入正式回归的 `ppp_quality_pca_rebuilt`，因此本批未报告 PCA 重建指标。
- 与旧版重叠结果对照表已写入 Excel。


use "/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear

* 构造PPP风险暴露指数（正式回归时请先标准化后求均值）
* 核心思路：proc_share、prep_share、C_idx 正向；exec_share、fiscal_pass_rate、vfm_pass_rate 反向
* 这里示意性写法，正式建议沿用Python结果文件中的构造口径

egen z_proc = std(proc_share)
egen z_prep = std(prep_share)
egen z_exec_neg = std(-exec_share)
egen z_fiscal_neg = std(-fiscal_pass_rate)
egen z_vfm_neg = std(-vfm_pass_rate)
egen z_C = std(C_idx)
gen ppp_risk_exposure_index = (z_proc + z_prep + z_exec_neg + z_fiscal_neg + z_vfm_neg + z_C) / 6

sum ppp_risk_exposure_index, detail
gen high_ppp_risk_exposure = ppp_risk_exposure_index >= r(p50)

foreach y in ppp_quality_pca_rebuilt exec_share proc_share {
    reghdfe `y' c.treat_share##i.high_ppp_risk_exposure dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
}

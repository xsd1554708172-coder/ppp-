
use "PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear
reghdfe A_idx treat_share dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
foreach y in exec_share proc_share ppp_quality_pca_rebuilt_fixed {
    reghdfe `y' treat_share A_idx dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
}
* 原版 province-level bootstrap 统计量请以 Python 导出的 Excel 文件为准

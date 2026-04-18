
use "PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear
reghdfe A_idx treat_share dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
reghdfe B_idx treat_share A_idx dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
reghdfe C_idx treat_share A_idx B_idx dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
foreach y in ppp_quality_pca_rebuilt_fixed exec_share proc_share {
    reghdfe `y' treat_share A_idx B_idx C_idx dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
}

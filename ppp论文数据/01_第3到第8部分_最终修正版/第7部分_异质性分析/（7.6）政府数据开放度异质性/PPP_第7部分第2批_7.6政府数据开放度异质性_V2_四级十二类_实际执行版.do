
use "PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear
egen z_A1 = std(A1_idx)
egen z_A2 = std(A2_idx)
gen gov_data_openness_proxy = (z_A1 + z_A2)/2
sum gov_data_openness_proxy, detail
gen high_gov_data_openness_proxy = gov_data_openness_proxy >= r(p50)
foreach y in ppp_quality_pca_rebuilt_fixed exec_share proc_share {
    reghdfe `y' c.treat_share##i.high_gov_data_openness_proxy dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
}


use "/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear

* 一阶段：did -> mediator
foreach m in A_idx B_idx C_idx ppp_governance_capacity_index ppp_norm_risk_index {
    reghdfe `m' did_intensity dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    reghdfe `m' did_any       dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    reghdfe `m' treat_share   dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
}

* 二阶段：outcome <- did + mediator
foreach y in ppp_quality_pca_rebuilt exec_share proc_share {
    foreach m in A_idx B_idx C_idx ppp_governance_capacity_index ppp_norm_risk_index {
        reghdfe `y' treat_share `m' dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
        reghdfe `y' did_any     `m' dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    }
}

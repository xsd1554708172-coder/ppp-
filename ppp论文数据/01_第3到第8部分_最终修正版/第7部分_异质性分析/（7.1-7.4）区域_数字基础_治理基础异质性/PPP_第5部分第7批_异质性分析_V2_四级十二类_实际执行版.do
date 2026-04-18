
use "/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear

* 生成异质性分组
sum digital_econ, detail
gen high_digital_econ = digital_econ >= r(p50)
sum dfi, detail
gen high_dfi = dfi >= r(p50)
sum A_idx, detail
gen high_A_idx = A_idx >= r(p50)
sum ppp_governance_capacity_index, detail
gen high_governance_capacity = ppp_governance_capacity_index >= r(p50)

* 交互项模型
foreach y in ppp_quality_pca_rebuilt exec_share proc_share {
    reghdfe `y' c.treat_share##i.high_digital_econ dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    reghdfe `y' c.treat_share##i.high_dfi dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    reghdfe `y' c.treat_share##i.high_A_idx dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    reghdfe `y' c.treat_share##i.high_governance_capacity dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
}

* 区域分组回归需先自行生成 region_group 后循环


use "/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear
* 重建 PCA 版治理质量指数（因为当前原始 ppp_quality_pca 为空）
pca exec_share proc_share prep_share fiscal_pass_rate vfm_pass_rate
predict ppp_quality_pca_rebuilt
replace ppp_quality_pca_rebuilt = -ppp_quality_pca_rebuilt if _n==1
* 说明：正式运行时应确保 proc_share、prep_share 已按负向处理后再做 PCA；这里 Python 版本为最终口径

* 基准 TWFE
foreach y in ppp_quality_zindex ppp_quality_pca_rebuilt exec_share proc_share prep_share {
    reghdfe `y' did_intensity dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    reghdfe `y' did_any       dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    reghdfe `y' treat_share   dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
}

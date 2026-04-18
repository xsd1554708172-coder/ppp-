
use "/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear

* 1) 替代结果变量/替代处理变量
foreach y in ppp_quality_zindex ppp_quality_pca_rebuilt exec_share proc_share prep_share {
    foreach d in did_intensity did_any treat_share {
        reghdfe `y' `d' dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    }
}

* 2) 滞后控制变量
xtset province year
foreach x in dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants {
    gen L1_`x' = L.`x'
}
foreach y in ppp_quality_pca_rebuilt exec_share proc_share {
    foreach d in did_any treat_share {
        reghdfe `y' `d' L1_dfi L1_digital_econ L1_ln_rd_expenditure L1_ln_tech_contract_value L1_ln_patent_grants, absorb(province year) vce(cluster province)
    }
}

* 3A) 剔除极端年份
preserve
keep if inrange(year, 2015, 2021)
foreach y in ppp_quality_pca_rebuilt exec_share proc_share {
    foreach d in did_any treat_share {
        reghdfe `y' `d' dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    }
}
restore

* 3B) 剔除直辖市与特殊地区
preserve
drop if inlist(province, "北京","上海","天津","重庆","西藏","新疆","宁夏","青海","海南")
foreach y in ppp_quality_pca_rebuilt exec_share proc_share {
    foreach d in did_any treat_share {
        reghdfe `y' `d' dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
    }
}
restore

* 3C) 文本样本门槛
capture confirm variable doc_count
if _rc==0 {
    preserve
    keep if doc_count >= 3
    foreach y in ppp_quality_pca_rebuilt exec_share proc_share {
        foreach d in did_any treat_share {
            reghdfe `y' `d' dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants, absorb(province year) vce(cluster province)
        }
    }
    restore
}


clear all
set more off

* 读取省-年面板变量
import delimited using "PPP_province_year_variables_v2_四级十二类_实际执行版.csv", varnames(1) clear encoding(utf8)
rename province province_name
destring year, replace
encode province_name, gen(province_id)

order province_name province_id year doc_count total_chars total_sentences
xtset province_id year

* 可直接用于后续并表的核心文本变量
gen txt_digi_ifc = A_idx
gen txt_norm = B_idx
gen txt_risk = C_idx
gen txt_govcap = ppp_governance_capacity_index
gen txt_normrisk = ppp_norm_risk_index

save "PPP_province_year_variables_v2_四级十二类_实际执行版.dta", replace

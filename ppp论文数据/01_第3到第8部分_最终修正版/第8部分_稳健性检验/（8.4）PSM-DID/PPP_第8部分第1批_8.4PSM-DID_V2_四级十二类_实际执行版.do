
use "/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear

* 说明：当前省—年样本并非理想型经典PSM-DID场景，
* 因为多数省份在2016年前后集中进入处理，真正从未处理省份较少。
* 因此本批结果应表述为“基于倾向得分匹配的 matched-sample DID / TWFE 稳健性检验”。

xtset province year

* 构造滞后协变量
foreach x in dfi digital_econ ln_rd_expenditure ln_tech_contract_value ln_patent_grants exec_share proc_share prep_share {
    gen L1_`x' = L.`x'
}

* 倾向得分匹配建议在Stata中用 teffects 或 psmatch2 实现；
* 这里给出回归口径说明，正式匹配样本请优先沿用Python输出。
* 匹配后再运行：
* reghdfe outcome did_any controls, absorb(province year) vce(cluster province)

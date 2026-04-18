clear all
set more off

* 1) 读取模型就绪面板
use "/mnt/data/PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.dta", clear

* 2) 面板设定
encode province, gen(pid)
xtset pid year

* 3) 基准变量标签
label var ppp_quality_zindex "PPP治理质量综合指数(Z)"
label var did_intensity "政务服务数字化改革强度(省内城市DID均值)"
label var A_idx "治理数字化接口指数"
label var B_idx "PPP规范治理指数"
label var C_idx "PPP风险识别指数"

* 4) 控制变量
global controls dfi digital_econ base_station_density software_gdp_share it_service_gdp_share ///
               ln_rd_expenditure ln_tech_contract_value ln_patent_grants

* 5) 建议先看描述统计
describe
summ ppp_quality_zindex did_intensity A_idx B_idx C_idx $controls

* 6) 双向固定效应基准
areg ppp_quality_zindex did_intensity $controls i.year, absorb(pid) vce(cluster pid)
eststo m1

* 7) 替代因变量
areg exec_share did_intensity $controls i.year, absorb(pid) vce(cluster pid)
eststo m2

areg proc_share did_intensity $controls i.year, absorb(pid) vce(cluster pid)
eststo m3

areg prep_share did_intensity $controls i.year, absorb(pid) vce(cluster pid)
eststo m4

* 8) 机制检验
areg A_idx did_intensity $controls i.year, absorb(pid) vce(cluster pid)
eststo m5

areg B_idx did_intensity $controls i.year, absorb(pid) vce(cluster pid)
eststo m6

areg C_idx did_intensity $controls i.year, absorb(pid) vce(cluster pid)
eststo m7

* 9) 联合模型
areg ppp_quality_zindex did_intensity A_idx B_idx C_idx $controls i.year, absorb(pid) vce(cluster pid)
eststo m8

* 10) 输出
capture which esttab
if _rc==0 {
    esttab m1 m2 m3 m4 m5 m6 m7 m8 using "/mnt/data/PPP_3.6_twfe_results_v1.rtf", ///
        replace se star(* 0.10 ** 0.05 *** 0.01) b(%9.4f) se(%9.4f) ///
        title("PPP治理质量：双向固定效应结果")
}

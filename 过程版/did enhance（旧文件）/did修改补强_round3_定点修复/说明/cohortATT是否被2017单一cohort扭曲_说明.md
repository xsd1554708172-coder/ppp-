# cohort ATT 是否被2017单一 cohort 扭曲

本轮对更稳健 cohort ATT 进行了 leave-one-cohort-out 敏感性检验。全cohort聚合下，`proc_share` 的估计为 -0.1244（p=0.0231），`exec_share` 为 0.0479（p=0.5602）。去掉 2017 单一 cohort 后，`proc_share` 变为 -0.0346（p=0.4164），`exec_share` 变为 -0.0386（p=0.5140）。

据此判断，2017 单一 cohort 对聚合结果的扭曲：**是**。若去掉 2017 后，采购阶段结果的显著性明显减弱或系数幅度收缩，则不能再把 cohort ATT 的增强效果解释为稳定补强，而只能理解为对单一 cohort 结构较为敏感的替代估计。

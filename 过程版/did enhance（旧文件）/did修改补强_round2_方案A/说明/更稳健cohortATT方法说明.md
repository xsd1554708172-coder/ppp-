# 更稳健cohortATT方法说明

- 本轮优先尝试 Sun & Abraham / csdid 类方法。
- Python 包可用性：linearmodels=False，differences=False，did=False，rpy2=False。
- 外部运行时可用性：Rscript=False，stata=False。
- 当前环境下不存在可直接调用的 Sun & Abraham / csdid 标准工具链，因此未做伪实现或空转调用。
- 替代方案：采用 interaction-weighted cohort ATT 聚合估计。做法是在清洁控制组与压缩窗口的Stack样本上，为不同cohort分别估计 post ATT，再按cohort样本量加权聚合，并保留cohort分项结果。
- 该方法比单一Stack DID更接近异质性处理效应稳健估计思路，但仍然只是补充识别，不替代主识别。
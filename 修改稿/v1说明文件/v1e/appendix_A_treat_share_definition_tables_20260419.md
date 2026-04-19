# v1e Appendix A：处理变量定义与重构说明

## 处理变量精确定义

- `post_t = 1[t >= 2016]`
- `treat_share_{pt} = treated_city_count_{pt} / city_n_{pt}`
- `did_intensity_{pt} = post_t * treat_share_{pt}`
- `did_any_{pt} = 1(did_intensity_{pt} > 0)`

## 当前仓库内可直接核实的样本流转
| step | count | source |
| --- | --- | --- |
| full_text_pool | 1472 | PPP_政策文本整合结果_1472篇.csv |
| doc_level_did_window | 1307 | PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv |
| province_year_balanced_window | 288 | PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv |
| panel_v3_all_observations | 266 | PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv |
| baseline_sample_5_3 | 262 | PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv::baseline_sample_5_3 |

## 当前口径下的处理时点摘要

| first_treatment_year | province_count |
| --- | --- |
| 2016 | 28 |
| 2017 | 1 |
| 未进入处理 | 3 |

## 输入文件

- `panel_v3`: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- `doc_level_v3`: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第4部分_文本变量构造\（4.1-4.4）文本变量构造与输出\PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv`
- `province_year_v3`: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第4部分_文本变量构造\（4.1-4.4）文本变量构造与输出\PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv`
- `text_pool_1472`: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\作图部分\PPP_BERTopic主题相似性矩阵_py与数据包\data\PPP_政策文本整合结果_1472篇.csv`
- `official_53`: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.3）基准多期DID_TWFE正式回归\PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
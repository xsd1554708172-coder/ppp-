# Treat Share Definition Tables

## ??????

| 变量 | 数据来源 | 聚合单元 | 聚合函数/定义 | 正文写法边界 |
|---|---|---|---|---|
| post_t | 数据总表（一切数据基础）.xlsx / 08_GovService_DID | 城市—年 → 省—年公共时间虚拟变量 | 1[t>=2016] | 2016作为统一启动点；正文需写明来源与口径，不宜仅写“改革后”。 |
| treat_share_{pt} | 同上 | 省—年 | (1/N_pt) × Σ_i treat_i | 主规格；连续强度更稳定，保留省内改革覆盖差异。 |
| did_intensity_{pt} | 同上 | 省—年 | (1/N_pt) × Σ_i DID_it = post_t × treat_share_{pt} | 替代处理变量；不作为正文主规格。 |
| did_any_{pt} | 同上 | 省—年 | 1(did_intensity_{pt} > 0) | 替代处理变量；用于对照连续强度规格。 |
| 写作建议 | — | — | 主规格固定为 treat_share | did_any 与 did_intensity 仅在稳健性或替代规格中出现。 |

## ????????

| 变量 | 精确定义 | 聚合层级 | 数据来源/依据 | 当前校验 |
|---|---|---|---|---|
| post_t | 1[t>=2016] | 城市—年 → 省—年公共时间虚拟变量 | 数据总表（一切数据基础）.xlsx：08_GovService_DID | 已与主面板逐行一致 |
| treat_share_{pt} | (1/N_pt) × Σ_i treat_i | 城市—年聚合到省—年（均值/占比） | 城市级 treat 字段 | 作为主规格进入5.3/6/7/8 |
| did_intensity_{pt} | (1/N_pt) × Σ_i DID_it = post_t × treat_share_{pt} | 城市—年聚合到省—年（均值） | 城市级 DID 字段 | 已逐行校验：max|did_intensity - treat_share×post| = 0 |
| did_any_{pt} | 1(did_intensity_{pt} > 0) | 城市—年聚合到省—年（二值化） | 由 did_intensity 派生 | 已逐行校验：差异行数 = 0 |
| 选择主规格的理由 | 连续强度变量比二元变量更保留改革覆盖差异 | 正文层面 | 与当前主回归、机制、稳健性结果一致 | 已同步写入根目录说明与写作骨架docx |


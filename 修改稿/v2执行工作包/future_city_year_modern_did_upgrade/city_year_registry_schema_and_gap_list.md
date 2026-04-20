# city-year treatment registry schema and gap list

| 字段 | 含义 | 当前状态 |
|---|---|---|
| province | 省份 | pseudo registry 可提供 |
| city | 城市名 | 当前仅 pseudo city-slot，非真实城市 |
| city_id | 城市代码 | 当前仅 pseudo slot id |
| year | 年份 | 可提供 |
| first_treat_year | 首次处理年份 | 当前无法真实确认 |
| treated | city-year 是否处理 | pseudo slot 可提供审计值 |
| treatment_source | 处理来源 | 应写明 inferred/proxy |
| source_note | 来源说明 | 必须写明不是原始名单 |
| aggregation_weight | 聚合权重 | 本轮默认等权 city-slot |

真实缺口：真实城市名单、处理阈值底表、权重底表、可区分未处理与未观测城市的 source。

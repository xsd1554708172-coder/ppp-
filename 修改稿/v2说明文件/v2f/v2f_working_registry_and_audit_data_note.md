# v2f working registry and province-year audit data note

本轮按用户确认，若无真实 city-year treatment registry 原始城市名单和处理阈值底表，则使用 implied/pseudo city-slot registry 作为工作数据进行省年审计与脚本接口运行。

## 文件

- working registry：`修改稿/v2说明文件/v2f/v2f_working_city_year_registry_from_implied_slots.csv`
- province-year audit：`修改稿/v2说明文件/v2f/v2f_province_year_treat_share_audit_working.csv`
- threshold proxy：`修改稿/v2说明文件/v2f/v2f_working_threshold_proxy.csv`

## 聚合口径

默认采用等权 city-slot 计数：省年 `treat_share` = treated city-slot 数 / city-slot 总数。该口径是审计/占位口径，不是官方真实城市名单。未来若取得真实城市名单、人口/项目数/财政权重或阈值底表，必须重建并与本口径并列核验。

```json
{
  "source_registry_exists": true,
  "source_audit_exists": true,
  "source_threshold_exists": true,
  "rule": "Use implied/pseudo city-slot registry as working city-year registry; never label as real city list.",
  "registry_rows": 2870,
  "working_registry_csv": "修改稿/v2说明文件/v2f/v2f_working_city_year_registry_from_implied_slots.csv",
  "working_registry_xlsx": "修改稿/v2说明文件/v2f/v2f_working_city_year_registry_from_implied_slots.xlsx",
  "audit_rows": 266,
  "audit_csv": "修改稿/v2说明文件/v2f/v2f_province_year_treat_share_audit_working.csv",
  "threshold_rows": 266,
  "threshold_csv": "修改稿/v2说明文件/v2f/v2f_working_threshold_proxy.csv"
}
```

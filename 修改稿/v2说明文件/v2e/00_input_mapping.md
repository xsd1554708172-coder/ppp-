# v2e Input Mapping

## Token

- `v2e`

## 正文底稿

- Markdown 底稿：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2d\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528.md`
- Word 对象保留底稿：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2d\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528_对象保留版.docx`

## 本轮依据

- v2e 修改建议/执行包目录：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\v2e修改建议`
- v2d DID 冲刺修订报告提取件：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\v2d修改建议\_codex_extracts\v2d_DID_冲刺修订报告_extracted.md`
- v2e 省年审计数据：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\v2e修改建议\v2e_province_year_treat_share_audit_from_v2d.csv`
- v2e 伪 city-slot registry：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\v2e修改建议\v2e_implied_city_slot_registry_from_v2d_treat_share.csv`

## Forward-apply 说明

本轮未覆盖 v2d 原始资产，而是从 v2d 最新正文 forward-apply 到 v2e。v2e 的 Word 版以 v2d 对象保留版 docx 为底稿直接修改 `word/document.xml`，尽量保留原包内图片、表格和对象关系；新增/改写公式均采用 Office Math 公式对象。

## 公式规则

自 v2e 起，Word 正式稿中的数学公式统一使用公式编辑器/Office Math 对象；Markdown 文件仅作为 Git 可审查文本留底，不作为正式公式排版来源。

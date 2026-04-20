# v2e Verification Report

## 1. 生成时间

- 2026-04-20 19:44:12

## 2. 文件存在性

- v2e Markdown：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2e\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2e_0420_1944.md`
- v2e Word：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2e\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2e_0420_1944_对象保留公式版.docx`
- v2e archive Markdown：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改稿留底\v2e\v2e_0420_1944.md`
- v2e archive Word：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改稿留底\v2e\v2e_0420_1944.docx`

## 3. 识别边界核查

- 主识别仍为 `treat_share` 多期 DID/TWFE。
- 没有把 trend-adjusted DID、逐省剔除、wild cluster bootstrap、stack DID、cohort ATT、PSM-DID、DML 或候选 IV 写成主识别。
- 没有写“event study 的平行趋势强证明表述”。
- 没有把 `ppp_quality_zindex` 写成治理质量全面提升的稳健主结论。
- 没有把 implied city-slot registry 写成真实城市名单。

## 4. 公式排版核查

- Word 正式稿已写入 Office Math `<m:oMath>` 对象。
- Markdown 留底明确说明公式以 Word 正式稿为准，不作为正式公式排版来源。

## 5. 数据/结果核查

- v2e 正文使用已有 v2d 正式值和 v2e rerun 审计快照，不新增虚构系数。
- 新生成的 province-year audit 和 implied city-slot registry 只作为审计/占位资产。
- 未修改原始数据总表、正式 source-of-truth xlsx、v2d 原始 docx。

## 6. 待最终命令核验

本文件由生成脚本预置；最终的 zip、XML、Git diff 核验结果会在脚本后续/人工检查中确认。

---

## 7. Fresh validation result

- 已执行严格核验脚本：通过。
- Word `.docx` 是可打开的 zip 包，包含 `word/document.xml`。
- Office Math `<m:oMath>` 对象计数：20。
- 已确认 Word XML 中不再保留以下纯文本公式片段：`Y_pt =`、`treat_share_{pt}`、`log((exec_share+c)/(proc_share+c))`、`post_t = 1[t>=2016]`。
- 已确认 Markdown 正文包含 v2e 执行稿说明、implied city-slot registry 说明、公式编辑器规则和唯一主识别边界。
- 已确认正文不含禁用强表述：event study 的平行趋势强证明表述、PPP治理质量显著提升的强证明表述、机制已被强证实的表述、所有补充检验均强化主结果、治理绩效全面改善的强表述。
- `git diff --check` 退出码 0。

## 8. 用户确认后的工作代理数据核查

- 用户已确认：真实 city-year treatment registry 原始城市名单仍缺，但本轮允许采用伪 city-slot registry 作为工作分析数据。
- 用户已确认：原始处理阈值底表仍缺，但本轮允许采用 `v2e_province_year_treat_share_audit_from_v2d.csv/.xlsx` 及其派生的 `v2e_working_threshold_proxy_from_province_year_audit.csv/.xlsx` 作为可用省年审计/阈值代理数据。
- 已生成并核查：`v2e_implied_city_slot_registry_from_v2d_treat_share.csv/.xlsx`，共 2870 条 implied city-slot 记录；该文件只能代表“由省年 treat_share 反推的伪 city-slot”，不是真实城市名单。
- 已生成并核查：`v2e_working_threshold_proxy_from_province_year_audit.csv/.xlsx`，共 266 条省年记录，其中 `use_for_analysis=True` 为 258 条；其阈值含义是“省年整数覆盖计数/覆盖率代理”，不是原始政策阈值底表。
- 已生成并核查：`v2e_working_registry_analysis_by_year.csv/.xlsx` 与 `v2e_working_registry_analysis_by_province.csv/.xlsx`，用于描述性审计和工作流衔接，不作为新的因果识别结果。
- 独立机制变量不主要依赖 city-year treatment registry 或阈值底表；审批时长、采购到执行间隔、退库率、在线服务指数、项目执行周期仍需独立过程数据。本轮仅生成数据可得性矩阵与项目披露完整度代理，不写作真实机制估计。
- 文本效度审计不依赖 treatment registry 或阈值底表；Cohen’s kappa / Krippendorff’s alpha 需要人工双标注数据。本轮没有发现可用双标注底表，因此未计算 kappa/alpha，且未把 A/B/C/D 文本变量写成强机制检验。

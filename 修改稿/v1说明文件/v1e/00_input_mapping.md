# 00_input_mapping

- token: `v1e`
- round_target: `基于 v1d 稿件和 v1d 修改建议产出 v1e`
- generated_at: `2026-04-19 Asia/Shanghai`

## 1. 读取的修改建议文件

本轮按用户指定，只从下列目录递归读取建议文件：

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1修改建议\v1d修改建议\`

实际读取到的文件：

1. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1修改建议\v1d修改建议\v1d 深度研究、问题诊断与重跑重构报告.docx`

### 主报告判定

- 主报告：`v1d 深度研究、问题诊断与重跑重构报告.docx`
- 判定理由：该文件不是零散文字建议，而是完整的深度研究/问题诊断/重跑重构报告；其内容覆盖样本链条、识别口径、share 因变量构成性约束、机制来源边界、wild cluster 推断、文本有效性与复现问题，因此应当作为本轮唯一主 review 报告。
- 辅助报告：本目录下未发现其他辅助建议文件。

## 2. 读取的 v1d 修订基底

本轮统一以用户指定的 v1d 成稿作为修订基底：

1. Markdown 基底：
   - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1d\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1d_codexrev_20260419.md`
2. Word 对象稿基底：
   - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1d\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1d_codexrev_20260419.docx`
3. 留底核对目录：
   - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1修改稿留底\v1d\`

## 3. Source of truth

本轮实际使用的 source-of-truth 包括：

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\PPP_v3结果层状态表_20260413_1345.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\数据总表（一切数据基础）.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\参考文献\`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\04_manuscript_integration\`

同时实际复核了与本轮 rerun 直接相关的正式结果资产：

- `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- `PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv`
- `PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv`
- `PPP_政策文本整合结果_1472篇.csv`

## 4. Aider 可用性检查

- 已读取：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\.aider.conf.yml`
- 已检查命令：`aider --version`
- 结果：**不可用**
- blocker：当前环境返回 `CommandNotFoundException`，说明 `aider` 未安装或未在 PATH 中。
- 本轮处理方式：**由 Codex 直接完成等效编辑**，并在本文件与 `03_delivery_note.md` 中明确记录该 blocker。

## 5. Git / 同步前置情况

- 已按仓库规则尝试评估同步脚本环境。
- 结果：`修改稿/scripts/sync_from_github.ps1` 无法直接执行同步，因为当前工作区存在大量既有未提交变更，脚本在 dirty worktree 条件下中止。
- 处理：本轮不伪装“已同步”；后续仅对本轮文件做精确 stage / commit / push。

## 6. authority hierarchy

本轮采用的 authority hierarchy 为：

1. `AGENTS.md`
2. `AI_RULES.txt`
3. 用户本轮指令（v1d -> v1e）
4. `修改稿/v1说明文件/v1d/` 下的最新 v1d 稿件（md + docx）
5. `修改稿/v1修改建议/v1d修改建议/` 下的主 review 报告
6. `PPP_v3结果层状态表_20260413_1345.xlsx`
7. `PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
8. `数据总表（一切数据基础）.xlsx`
9. `PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/` 中已经落地的正式整合稿与正式结果资产
10. `ppp论文数据/参考文献/`
11. 其他旧说明、旧日志、旧 patch 与旧中间稿（仅作从属参考，不得压过正式结果）

## 7. 本轮 fresh rerun / 重构范围

由于主报告明确触及样本定义、识别口径、结果值与附录透明度，本轮按要求执行了 fresh rerun / fresh reconstruction：

1. 正式 5.3 基准 DID/TWFE 结果 fresh rerun，并与官方长表逐项对齐。
2. `exec_share / proc_share` 对数比率补充估计 fresh rerun。
3. `1472 -> 1307 -> 288 -> 266 -> 262` 样本流转链 fresh reconstruction。
4. `treat_share` 的 province-year 层处理变量重构与首年处理时点表 fresh reconstruction。
5. 基准样本中 4 个未进入最终估计的兵团观察删样说明 fresh reconstruction。

## 8. 本轮未直接落地的事项

以下事项未被伪装为“已完成”：

- **Aider 编辑**：环境不可用。
- **city-level treatment registry / 原始 threshold 表**：当前仓库中未发现可直接审计的显式落地资产，因此只能做到 province-year 层重构，不能夸大为完整城市级复现包。
- **wild cluster bootstrap fresh rerun**：当前仓库缺少可直接一键复现的完整运行链与依赖环境，本轮保留已落地官方 manuscript-facing 数值，并在 verification 中显式标记 blocker。
- **trend-adjusted DID 作为 fresh manuscript-facing 替换值**：手工零依赖 rerun 与已落地官方 bundle 值不完全一致，因此该 fresh rerun 仅作为 diagnostic artifact 保存，不覆盖正文中的官方防守数值。
- **直接修改 `.xlsx` 原始工作簿**：本轮没有这样做。

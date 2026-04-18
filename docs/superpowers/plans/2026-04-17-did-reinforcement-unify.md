# DID Reinforcement Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 统一 baseline DID 参考值，重建 `trend-adjusted DID` 与 `leave-one-province-out` 为可复现模块，降格 `wild bootstrap / small-sample inference`，并产出可直接替换正文第 5.6 节的图表、表注、段落与 clean bundle。

**Architecture:** 以正式 V3 主面板和正文实际采用的 baseline DID 规格为唯一锚点，所有 reinforcement 子模块都回指同一套 baseline reference。工程层先统一输入输出与脚本，再分别重跑趋势调整和单省剔除，最后基于真实输出重写第 5.6 节、摘要补充句、结论补充句和 bundle README。

**Tech Stack:** Python (`pandas`, `statsmodels`, `matplotlib`, `openpyxl`, `zipfile/pathlib`), Word `.docx` XML 提取, Markdown/README/bundle packaging

---

### Task 1: 锁定正文主锚点与统一 baseline DID 规格

**Files:**
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.3）基准多期DID_TWFE正式回归\PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- Modify/Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\00_unified_baseline_reference\`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\00_unified_baseline_reference\unified_baseline_reference.xlsx`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\00_unified_baseline_reference\baseline_spec_readme.md`

- [ ] **Step 1: 抽取 `.docx` 中第 5 章表 4 与第 5.6 节锚点文本**

Run:

```powershell
@'
import zipfile, re, pathlib
doc = pathlib.Path(r"C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx")
with zipfile.ZipFile(doc) as z:
    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
print("表4" in xml, "5.6" in xml)
'@ | python -
```

Expected: 能确认 `.docx` 内存在表 4 和第 5.6 节文本锚点。

- [ ] **Step 2: 锁定 baseline DID 真实规格与变量口径**

Run:

```powershell
@'
import pandas as pd, pathlib
panel = pd.read_csv(pathlib.Path(r"C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv"))
print(panel.columns.tolist())
print(panel["baseline_sample_5_3"].sum())
'@ | python -
```

Expected: 明确 `baseline_sample_5_3`、`treat_share`、`exec_share`、`proc_share`、`ppp_quality_zindex` 和正式控制变量存在。

- [ ] **Step 3: clean rerun baseline DID 并导出统一 reference**

Run:

```powershell
python PPP_empirical_reinforcement_bundle_20260416_clean\scripts\rerun_unified_baseline.py
```

Expected: 生成唯一 baseline result 表，后续所有 reinforcement 子模块引用同一系数与同一规格说明。

- [ ] **Step 4: 记录 baseline 统一说明**

Write `baseline_spec_readme.md`，必须说明：
1. `.docx` 正文采用的 baseline DID 规格；
2. 重跑时是否与已有 5.3 长表完全一致；
3. 若存在轻微数值差异，哪个版本作为最终统一 reference，以及为什么。


### Task 2: 重建 `trend-adjusted DID` 模块

**Files:**
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\scripts\*`
- Modify/Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\scripts\run_trend_adjusted_did.py`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\tables\trend_adjusted_DID_results_unified.xlsx`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\figures\Figure_8A_baseline_vs_trend_adjusted_forest.png`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\text\trend_adjusted_replacement_text.md`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\README.md`

- [ ] **Step 1: 审核现有脚本是否仍引用旧 baseline 或旧路径**

Run:

```powershell
Get-ChildItem PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\scripts -File | Select-String -Pattern "20260413_1048|baseline|treat_share|C:\\\\Users"
```

Expected: 列出所有硬编码路径和旧 baseline 残留。

- [ ] **Step 2: 用统一 baseline 规格重跑 trend-adjusted DID**

Model:
- baseline RHS unchanged
- add province-specific linear trends
- outcomes: `exec_share`, `proc_share`, `ppp_quality_zindex`

Run:

```powershell
python PPP_empirical_reinforcement_bundle_20260416_clean\01_trend_adjusted_DID\scripts\run_trend_adjusted_did.py
```

Expected: 生成统一表和对照图。

- [ ] **Step 3: 生成正文可替换文字**

文本必须明确：
1. 这是 defensive robustness layer；
2. 若 `proc_share` 仍为负显著，可写“核心推进结构判断不完全依赖共同趋势设定”；
3. 若 `exec_share` 正向但显著性减弱，只能写“方向稳定，强度对趋势设定更敏感”；
4. `ppp_quality_zindex` 继续降格。


### Task 3: 重建 `leave-one-province-out` 模块并降格 `wild bootstrap`

**Files:**
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\02_leave_one_province_out_jackknife\*`
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\03_small_sample_inference_wild*`
- Modify/Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\02_leave_one_province_out_jackknife\scripts\run_leave_one_province_out.py`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\02_leave_one_province_out_jackknife\tables\leave_one_province_out_summary_unified.xlsx`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\02_leave_one_province_out_jackknife\figures\Figure_8B_leave_one_province_out_stability.png`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\03_small_sample_inference_wild*\text\small_sample_note_downgraded.md`

- [ ] **Step 1: 重跑 leave-one-province-out**

Run:

```powershell
python PPP_empirical_reinforcement_bundle_20260416_clean\02_leave_one_province_out_jackknife\scripts\run_leave_one_province_out.py
```

Expected: 生成每省剔除结果、符号翻转指示、显著性大幅衰减指示、稳定性图。

- [ ] **Step 2: 生成简明解释**

README 与 replacement text 必须区分：
1. sign never flip -> “核心结论并非由单一省份完全驱动”；
2. some deletion weakens p-values -> “方向稳定，但统计强度对个别地区敏感”；
3. 不能写 “completely robust”。

- [ ] **Step 3: 审核并降格 bootstrap / small-sample inference**

Run:

```powershell
Get-ChildItem PPP_empirical_reinforcement_bundle_20260416_clean\03_small_sample_inference_wild* -Recurse -File | Select-String -Pattern "robust|strong|confirm|稳健|强化|平行趋势"
```

Expected: 找出所有强表述并改成边界说明；正文只保留短段或转 appendix-level support。


### Task 4: 重写论文第 5.6 节与 bundle 集成

**Files:**
- Read/Modify integration notes for: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\manuscript_integration\section_5_6_replacement.md`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\manuscript_integration\abstract_and_conclusion_additions.md`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\manuscript_integration\table_figure_caption_notes.md`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\CHANGELOG.md`

- [ ] **Step 1: 抽取 `.docx` 的第 5.3–5.6 现有结构**

Run:

```powershell
@'
import zipfile, pathlib, re
doc = pathlib.Path(r"C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx")
with zipfile.ZipFile(doc) as z:
    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
for key in ["5.3","5.6","趋势","稳健性","bootstrap","leave-one"]:
    print(key, xml.find(key))
'@ | python -
```

Expected: 至少确认 5.3、5.6 与稳健性层文本锚点存在。

- [ ] **Step 2: 写出 section 5.6 exact replacement text**

结构必须是：
1. 5.6 总起段：说明本节判断推进结构结论在关键识别挑战下是否仍成立；
2. 5.6.1 趋势调整型防守检验；
3. 5.6.2 单一地区驱动风险诊断；
4. 5.6.3 更保守推断下的边界说明；
5. 5.6.4 其他补充识别与稳健性结果（very brief）。

- [ ] **Step 3: 统一表图与注释**

最少要生成：
1. `Figure_8A_baseline_vs_trend_adjusted_forest`
2. `Figure_8B_leave_one_province_out_stability`
3. robustness summary table note
4. short note for downgraded bootstrap

- [ ] **Step 4: 更新 bundle README 与 CHANGELOG**

必须说明：
1. baseline reference 已统一；
2. trend-adjusted DID 为正文主打防守层；
3. leave-one-province-out 为辅助诊断；
4. bootstrap 已降格；
5. 哪些句子用于替换 `.docx` 的摘要、结论和第 5.6 节。


### Task 5: 复核、代码审查与完成前验证

**Files:**
- Review all outputs under: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_clean\`

- [ ] **Step 1: 请求代码审查**

Dispatch review on:
1. baseline unification logic
2. trend-adjusted DID script
3. leave-one-province-out script
4. manuscript replacement text consistency

- [ ] **Step 2: 运行完成前验证**

Run:

```powershell
python PPP_empirical_reinforcement_bundle_20260416_clean\scripts\verify_reinforcement_bundle.py
```

Expected checks:
1. 主模型仍然是 `treat_share` DID/TWFE
2. 所有 reinforcement 模块使用同一 baseline reference
3. trend-adjusted DID 输出完整
4. leave-one-province-out 输出完整
5. bootstrap 文案已降格
6. section 5.6 replacement text 与 rerun outputs 一致
7. captions/notes 没有 overstate
8. final bundle 结构清晰

- [ ] **Step 3: 形成最终交付说明**

输出最终报告时，必须按用户指定结构给出：
1. What you inspected
2. What you changed
3. Verification evidence
4. Remaining risks / boundaries

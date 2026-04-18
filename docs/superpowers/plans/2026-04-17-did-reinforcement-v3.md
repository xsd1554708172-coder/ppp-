# DID Reinforcement v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变 `treat_share` DID/TWFE 主识别的前提下，把 `PPP_empirical_reinforcement_bundle_20260416_unified_v2` 收口为真正可交付、可复现、可直接整合进论文终稿的 `unified_v3` bundle。

**Architecture:** 先锁定唯一 manuscript-facing baseline reference，再分别重建 `trend-adjusted DID` 和 `leave-one-province-out` 模块，并把 `wild bootstrap / small-sample inference` 压缩为边界层支持。最后单独处理 manuscript integration：重写 section 5.6 patch、表图标题/图注/表注、摘要/结论补充句以及最终 patch map。所有模块统一指向同一套 baseline、同一套 README 口径和同一套论文层级。

**Tech Stack:** Python (`pandas`, `statsmodels`, `matplotlib`, `openpyxl`, `zipfile`, `pathlib`), Word `.docx` XML extraction, Markdown patch files

---

### Task 1: 创建 v3 bundle 骨架并锁定唯一 baseline reference

**Files:**
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\**\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- Read: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\**\PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- Read/Copy from: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v2\`
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\`
- Create: `...\00_unified_baseline_reference\scripts\build_unified_baseline_reference.py`
- Create: `...\00_unified_baseline_reference\tables\unified_baseline_reference.xlsx`
- Create: `...\00_unified_baseline_reference\notes\baseline_spec_readme.md`
- Modify/Create: `...\bundle_common.py`

- [ ] **Step 1: 读取 manuscript anchor 与正式 baseline 锚点**

Run:

```bash
python - <<'PY'
import zipfile, re, pathlib
doc = pathlib.Path(r"C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx")
with zipfile.ZipFile(doc) as z:
    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
text = re.sub(r"</w:p>", "\n", re.sub(r"<[^>]+>", "", xml))
for key in ["5.3", "5.6", "表4"]:
    print(key, key in text)
PY
```

Expected: 确认 `.docx` 中存在表4与 section 5.6 锚点。

- [ ] **Step 2: 只保留一个 manuscript-facing baseline**

Run:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py
```

Expected: 输出 workbook 同时保存 official vs rerun comparison，但文稿可见层只引用 `official_*` 列。

- [ ] **Step 3: 修正公共路径解析**

Requirement:
- `bundle_common.py` 不得依赖绝对路径；
- 不得再残留 `current_bundle_root` 或 v2 外部清洁 bundle 路径；
- 发现多个候选文件时必须优先匹配正式 1048 版，或直接报 ambiguous error。


### Task 2: 重建 trend-adjusted DID 为正文主防守层

**Files:**
- Read: `...\01_trend_adjusted_DID\scripts\run_trend_adjusted_did.py`
- Create/Modify: `...\01_trend_adjusted_DID\scripts\run_trend_adjusted_did.py`
- Create: `...\01_trend_adjusted_DID\tables\trend_adjusted_did_results.xlsx`
- Create: `...\01_trend_adjusted_DID\figures\Figure_8A_baseline_vs_trend_adjusted_forest_diagnostic.png`
- Create: `...\01_trend_adjusted_DID\figures\Figure_8A_baseline_vs_trend_adjusted_forest_manuscript.png`
- Create: `...\01_trend_adjusted_DID\text\trend_adjusted_did_body_insert.md`
- Create: `...\01_trend_adjusted_DID\notes\trend_adjusted_did_notes.md`
- Create: `...\01_trend_adjusted_DID\scripts\README.md`

- [ ] **Step 1: 保持正文 baseline 口径一致重跑**

Run:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
```

Expected: 对 `exec_share`、`proc_share`、`ppp_quality_zindex` 输出统一结果表，并把比较基线锚定到唯一 baseline reference。

- [ ] **Step 2: 同时导出工程诊断版图与论文版图**

Requirements:
- 诊断版图保留变量英文名与内部对照结构；
- 论文版图使用更接近正文表述的标签，不裸露代码变量名；
- 图注、坐标、标题与正文第5章用语一致；
- 若环境允许，同时导出 `.png` 与 `.svg`。

- [ ] **Step 3: 生成正文替换文本**

规则：
- `proc_share` 若仍显著负向，可写“核心推进结构判断并不完全依赖共同趋势设定”；
- `exec_share` 若仅方向稳定但强度减弱，必须写明“统计强度对趋势设定更敏感”；
- `ppp_quality_zindex` 继续降格。


### Task 3: 重建 leave-one-province-out 并统一到同一 baseline

**Files:**
- Read: `...\02_leave_one_province_out_jackknife\scripts\run_leave_one_province_out.py`
- Create/Modify: `...\02_leave_one_province_out_jackknife\scripts\run_leave_one_province_out.py`
- Create: `...\02_leave_one_province_out_jackknife\tables\leave_one_province_out_results.xlsx`
- Create: `...\02_leave_one_province_out_jackknife\tables\leave_one_province_out_stability_summary.xlsx`
- Create: `...\02_leave_one_province_out_jackknife\figures\Figure_8B_leave_one_province_out_stability_diagnostic.png`
- Create: `...\02_leave_one_province_out_jackknife\figures\Figure_8B_leave_one_province_out_stability_manuscript.png`
- Create: `...\02_leave_one_province_out_jackknife\text\leave_one_province_out_body_insert.md`
- Create: `...\02_leave_one_province_out_jackknife\notes\leave_one_province_out_notes.md`
- Create: `...\02_leave_one_province_out_jackknife\scripts\README.md`

- [ ] **Step 1: 重跑单省剔除循环**

Run:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
```

Expected: 输出逐省删除结果、摘要表、sign-flip 计数、显著性明显减弱计数、最大偏离省份。

- [ ] **Step 2: baseline reference 全部统一**

Requirement:
- 图中的 reference line；
- summary 表中的 baseline 列；
- 正文 body insert 中的比较语句；
必须全部回指同一个 canonical baseline。

- [ ] **Step 3: 产出论文版图**

Requirement:
- 论文版图要明确这是“删一省后的系数稳定性图”；
- 让读者能直接理解“方向稳定，但强度对个别地区敏感”；
- 若需要点名最大偏离省份，优先放在图注或 notes 中，而不是挤在图里。


### Task 4: 将 bootstrap / small-sample inference 压缩为边界层，并统一方法命名

**Files:**
- Read: `...\03_small_sample_inference_wild_cluster_bootstrap\scripts\*`
- Read: `...\03_small_sample_inference_wild_cluster_bootstrap\inputs\baseline_did_bootstrap_or_permutation_pvalues.xlsx`
- Create/Modify: `...\03_small_sample_inference_wild_cluster_bootstrap\scripts\summarize_small_sample_inference.py`
- Create: `...\03_small_sample_inference_wild_cluster_bootstrap\tables\small_sample_inference_summary.xlsx`
- Create: `...\03_small_sample_inference_wild_cluster_bootstrap\text\bootstrap_body_insert.md`
- Create: `...\03_small_sample_inference_wild_cluster_bootstrap\notes\small_sample_inference_notes.md`
- Create: `...\03_small_sample_inference_wild_cluster_bootstrap\scripts\README.md`

- [ ] **Step 1: 核对方法名**

Requirement:
- 如果正文、文件名、README 用的是 `wild cluster bootstrap`，它们必须一致；
- 如果输入表本质上混合了 bootstrap / permutation 信息，则对正文和 README 改成更保守、更准确的总称，不得错叫方法名。

- [ ] **Step 2: 输出边界层摘要**

Expected:
- `exec_share` / `proc_share`：只写方向稳定，但更保守推断下统计强度更敏感；
- `ppp_quality_zindex`：继续降格；
- 这一层只能放短段或附录级支持。


### Task 5: 重写 manuscript integration 层并收口 5.6

**Files:**
- Read: `...\04_manuscript_integration\text\section_5_6_replacement.md`
- Read: `...\04_manuscript_integration\text\abstract_and_conclusion_additions.md`
- Read: `...\04_manuscript_integration\notes\table_figure_caption_notes.md`
- Read: `...\04_manuscript_integration\notes\manuscript_update_map.md`
- Create/Modify: `...\04_manuscript_integration\text\section_5_6_final.md`
- Create/Modify: `...\04_manuscript_integration\text\abstract_final_patch.md`
- Create/Modify: `...\04_manuscript_integration\text\conclusion_final_patch.md`
- Create/Modify: `...\04_manuscript_integration\notes\table_figure_caption_notes.md`
- Create/Modify: `...\04_manuscript_integration\notes\FINAL_MANUSCRIPT_PATCH.md`
- Create: `...\04_manuscript_integration\tables\robustness_defense_summary.xlsx`

- [ ] **Step 1: 压短 5.6.4**

Requirement:
- `stack DID`
- `cohort ATT`
- `dynamic supplementary identification`
只能做 very brief mention；
- 只保留边界诊断角色；
- 不展开年份、cohort 敏感性、额外系数细节。

- [ ] **Step 2: section 5.6 做成最终落稿版**

Structure must be:
- 5.6 总起段
- 5.6.1 趋势调整型防守检验
- 5.6.2 单一地区驱动风险诊断
- 5.6.3 更保守推断下的边界说明
- 5.6.4 其他补充识别与稳健性结果（简述）

- [ ] **Step 3: 输出最终 patch 文件**

`FINAL_MANUSCRIPT_PATCH.md` must include:
- 原位置
- 应删除内容
- 应替换内容
- 应新增内容
- 对应表/图编号
- 注意事项


### Task 6: 打包为最终干净 bundle 并验证

**Files:**
- Create: `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\README.md`
- Create: `...\CHANGELOG.md`
- Verify all bundle outputs

- [ ] **Step 1: 清理命名与冗余**

Requirement:
- bundle 名称、README 标题、运行说明、脚本路径、图表名称一致；
- 无乱码文件名；
- 无对 v2/v3 以外 bundle 的运行依赖说明。

- [ ] **Step 2: Fresh verification**

Run:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py
```

Then verify:
- 所有模块只引用同一 baseline；
- `Figure_8A` / `Figure_8B` 有论文版和工程版；
- `5.6.4` 明显压短；
- `small-sample inference` 命名、README、正文口径一致；
- final patch 文件可直接交给人工整合 manuscript。

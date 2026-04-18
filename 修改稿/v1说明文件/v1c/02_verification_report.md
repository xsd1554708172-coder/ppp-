# v1c Verification Report

## Verification Scope

- token detection 与输入角色判定
- 正式结果口径核对
- manuscript-facing 关键段落核查
- `.md` / `.docx` 同步核查
- 对象保留式 `.docx` 结构核查
- no-`v2` write 核查

## Fresh Checks Performed

### 1. Token and input checks

- `修改稿\v1` 本轮仅检测到 `v1c`。
- `修改稿\v1修改建议` 中已存在 `v1c` 的 exact-token 建议文件。
- `修改稿\v1` 中仍缺失 `v1c` token-local 正文稿件本体；该缺口已在 `MISSING_INPUTS.md` 中单独记录。

### 2. Formal result-entity checks

#### Baseline DID (`5.3`)

- 已从正式结果实体核对：
  - `exec_share` × `treat_share` = `0.3556277048`
  - `proc_share` × `treat_share` = `-0.4022774861`
  - `ppp_quality_zindex` × `treat_share` = `0.5252969356`
  - `ppp_quality_zindex` 的 `p = 0.2126`

#### PSM-DID sensitivity (`8.4`)

- 已从正式结果实体核对：
  - `exec_share` × `treat_share` = `-0.5360932308`，`p = 0.0871`
  - `proc_share` × `treat_share` = `0.3104223083`，`p = 0.3739`
  - `ppp_quality_zindex` × `treat_share` = `-2.6388945174`，`p < 0.001`

#### Verification implication

- 上述 fresh checks 支撑了本轮正文中的三个关键口径：
  - `exec_share` / `proc_share` 才是主结果
  - `ppp_quality_zindex` 不能承担主结论
  - `PSM-DID` 必须被解释为敏感性暴露，而不是稳健性加码

### 3. Manuscript-level checks

- `标题`
  - 已由问句式强表述收束为 `政务服务数字化改革与PPP项目推进结构调整`

- `摘要`
  - 已压缩为 `344` 字符
  - 保留 `treat_share` 主识别与 `exec_share` / `proc_share` 主结果
  - 未抬升 `ppp_quality_zindex`

- `理论机制`
  - H2 已改写为“程序环境调整推动采购向执行转换”
  - 不再直接重复 H1 主效应

- `事件研究与动态路径`
  - 已明确写入前趋势可能来源
  - 已明确保留 TWFE 动态系数加权特性的识别边界
  - 未出现“事件研究证明平行趋势成立”表述

- `敏感性与边界诊断`
  - 第 5.6.4 节已将 `PSM-DID`、`DML`、`IV` 统一写为敏感性暴露/边界诊断

- `政策建议`
  - 已按主体拆分到：
    - 政务服务管理部门
    - 发展改革部门
    - 财政与行业主管部门
    - 审计/监管/项目管理部门

### 4. `.md` / `.docx` sync checks

- 已从新 `.md` 提取并核对以下关键位置：
  - 标题
  - 摘要
  - H2
  - 动态路径核心段
  - 敏感性解释段
  - 政策含义段

- 已从新 `.docx` 直接抽取 `word/document.xml` 段落文本，确认上述关键位置同步存在。

### 5. Object-preserving `.docx` structure checks

- 已将新 `.docx` 与原对象保留投稿版逐项比较 zip 内 file entries。
- fresh result：
  - `same_file_entries = True`
- 含义：
  - 本轮 `.docx` 修订仅改动文本层 `document.xml`
  - 原对象稿中的图片/关系文件/file-entry 集保持不变

### 6. No-`v2` write check

- 本轮写入仅发生在：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1c`
- 未向任何 `v2` 目录写入新文件。

### 7. Package check

- 已 fresh 确认交付包存在：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1c\v1c_codex_revision_bundle_20260418.zip`
- 已 fresh 确认 zip 内包含：
  - 新 `.md`
  - 新 `.docx`
  - `00_input_mapping.md`
  - `01_revision_tasklist.md`
  - `MISSING_INPUTS.md`
  - `02_verification_report.md`
  - `03_delivery_note.md`

## Verification Verdict

- `v1c` 已完成基于 official fallback base 的实质性修订。
- 本轮没有把 suggestion 层、patch 层或分析层冒充为正文完成。
- 仍然存在的唯一残余输入风险是：
  - token-local `v1c` 正文稿件本体缺失
  - 因而无法证明新稿与缺失正文逐字对应

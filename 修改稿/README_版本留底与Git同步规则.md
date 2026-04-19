# 修改稿版本留底与 Git 同步规则

最后更新：2026-04-19

本目录用于管理 `v1*` 与 `v2*` 两条论文修改线的工作稿、修改建议、说明文件、留底版本、自动索引和操作日志。

## 目录分工

- `v1初始版/`
  - 放当前正在处理的 `v1*` 工作稿。
- `v1修改建议/`
  - 放 `v1*` 对应的评审意见、深度研究报告和 revision report。
  - 必须按 token 子目录归档，例如 `v1c修改建议/`、`v1d修改建议/`。
  - 不再接受同级散放评审文件。
- `v1说明文件/`
  - 放每轮 `v1*` 修改后的 input mapping、tasklist、verification、delivery note 和 zip 交付包。
- `v1修改稿留底/`
  - 放每次交付后的 `v1*` 成稿留底。
- `v2初始版/`
  - 放当前正在处理的 `v2*` 工作稿。
- `v2修改建议/`
  - 放 `v2*` 对应的评审意见、深度研究报告和 revision report。
  - 必须按 token 子目录归档，例如 `v2c修改建议/`、`v2d修改建议/`。
  - 不再接受同级散放评审文件。
- `v2说明文件/`
  - 放每轮 `v2*` 修改后的 input mapping、tasklist、verification、delivery note 和 zip 交付包。
- `v2修改稿留底/`
  - 放每次交付后的 `v2*` 成稿留底。
- `索引/`
  - 放自动生成的 `修改稿索引总览.md`、`v1修改稿索引.md`、`v2修改稿索引.md`。
- `操作日志/`
  - 放每次操作新增的一份日志文件。
  - 日志精确到秒，不覆盖旧文件。

## 留底规则

- 每次完成一轮 `v1*` 或 `v2*` 修改后，必须把最终稿复制到对应留底目录。
- 留底目录按 token 建子目录保存：
  - `v1修改稿留底/v1a/`
  - `v2修改稿留底/v2b/`
- 留底文件名保持简短，统一使用：
  - `<version-token>_<MMDD_HHMM>.<ext>`
  - 例如：`v1d_0419_1533.docx`
  - 例如：`v2d_0419_1528.md`

## 每轮任务的收尾要求

开始新任务前：

1. 先从 GitHub 远端同步最新工作区。

完成一轮修改后：

1. 完成正文、表图、附录、说明文件和必要的数据侧更新。
2. 对正文、表图、结果值和说明文件做一致性核查。
3. 将最终稿复制到对应留底目录。
4. 在对应 token 的说明文件目录中放入：
   - `00_input_mapping.md`
   - `01_revision_tasklist.md`
   - `02_verification_report.md`
   - `03_delivery_note.md`
   - zip 交付包
5. 自动刷新 `修改稿/索引/`。
6. 自动新增一份 `修改稿/操作日志/` 日志文件。
7. 更新本地 Git 仓库并推送到 GitHub。

## 操作日志规则

- 每次操作新增一份独立日志，不覆盖旧日志。
- 日志必须把以下字段分开记录：
  - `被审源稿`
  - `修订输出`
  - `归档输出`
  - `读取的修改建议`
- 不再用“源稿件”笼统指代最终输出文件。

## 修改建议摆放规则

- 评审意见、深度研究报告、review report 一律收进对应 token 的修改建议子目录。
- 如果发现评审报告副本被放在 `v1初始版/`、`v2初始版/` 或修改建议根目录，必须清理并归并到：
  - `v1修改建议/<token>修改建议/`
  - `v2修改建议/<token>修改建议/`

## 数据、结果与重跑规则

- 只要修改建议触及以下任何一类内容，默认都要至少执行一轮可审计的 fresh rerun：
  - 样本定义
  - 识别策略
  - 结果数值
  - 表图
  - 稳健性
  - 附录
  - 变量工程
- 如果无法重跑，必须在 verification 和 delivery note 里明确写出 blocker。
- `no rerun` 不能再作为这类任务的正常收尾口径。

## 推荐脚本

- 留底归档：
  - `修改稿/scripts/archive_revision_output.py`
- 索引刷新：
  - `修改稿/scripts/refresh_revision_indexes.py`
- 操作日志：
  - `修改稿/scripts/write_revision_operation_log.py`
- Git 同步：
  - `修改稿/scripts/git_sync_workspace.ps1`
- 远端同步：
  - `修改稿/scripts/sync_from_github.ps1`
- 一键收尾：
  - `修改稿/scripts/finalize_revision_task.ps1`

## 说明

- 留底是历史快照，不覆盖旧文件。
- 每次执行 `finalize_revision_task.ps1` 时，应自动完成：
  - 留底
  - 刷新索引
  - 新增操作日志
  - Git 提交与推送

# 修改稿版本留底与 Git 同步规则

本目录用于管理 `v1*` 与 `v2*` 两套修改线程的稿件、修改建议、说明文件、留底文章、自动索引和操作日志。

## 目录分工

- `v1初始版/`
  - 放当前正在处理的 `v1*` 工作稿。
- `v1修改建议/`
  - 放 `v1*` 对应的修改建议，且建议按 `v1c修改建议/` 这种 token 文件夹继续分组。
- `v1说明文件/`
  - 放每轮 `v1*` 修改后的说明文件、核查报告和 zip 交付包。
- `v1修改稿留底/`
  - 放每次完成后的 `v1*` 新文章留底。
- `v2初始版/`
  - 放当前正在处理的 `v2*` 工作稿。
- `v2修改建议/`
  - 放 `v2*` 对应的修改建议，且建议按 `v2c修改建议/` 这种 token 文件夹继续分组。
- `v2说明文件/`
  - 放每轮 `v2*` 修改后的说明文件、核查报告和 zip 交付包。
- `v2修改稿留底/`
  - 放每次完成后的 `v2*` 新文章留底。
- `索引/`
  - 放自动生成的 `修改稿索引总览.md`、`v1修改稿索引.md`、`v2修改稿索引.md`。
- `操作日志/`
  - 放每次操作单独生成的一份日志文件，精确到秒，不覆盖旧文件。

## 留底规则

- 每次完成一轮 `v1*` 或 `v2*` 修改后，必须把新的文章成稿复制到对应留底目录。
- 留底目录按版本 token 分子文件夹保存。
  - 例如：`v1a` 放在 `v1修改稿留底/v1a/`
  - 例如：`v2b` 放在 `v2修改稿留底/v2b/`
- 留底文件名必须简短，统一使用：
  - `<version-token>_<MMDD_HHMM>.<ext>`
  - 示例：`v1a_0419_0012.docx`
  - 示例：`v2b_0419_1426.md`
- 时间精度固定到月 / 日 / 小时 / 分钟，不要再额外拼接冗长说明。

## 每轮任务结束前必须做的事

0. 开始新任务前，先同步 GitHub 远端最新内容到本地运行环境。
1. 完成正文修改、数据修改、重跑或图表更新。
2. 完成逐项核查，确保正文、表图、结果和说明一致。
3. 将最终新文章复制到对应留底目录，并按规则命名。
4. 将本轮说明文件、核查报告和 zip 交付包放入对应说明文件目录。
5. 自动刷新 `修改稿/索引/`。
6. 自动新增一份 `修改稿/操作日志/` 日志文件。
7. 运行 Git 同步流程，把整个工作环境更新到 GitHub 仓库。

## Git 同步要求

- 仓库名称目标：`ppp论文项目`
- 当前本地仓库已配置的实际 GitHub 远端 slug：`ppp-`
- 仓库中的远端同步信号文件：
  - `00_环境说明与索引/REMOTE_SYNC_SIGNAL.json`
- 每次完成修改后都要执行：
  - `git add -A`
  - `git commit`
  - `git push`
- 每次开始新任务前都要执行：
  - `git fetch`
  - `git pull --rebase`
- 如果远端未配置或 GitHub 认证不可用，必须在说明文件里明确记录阻塞原因。

## 推荐脚本

- 留底归档脚本：
  - `修改稿/scripts/archive_revision_output.py`
- Git 同步脚本：
  - `修改稿/scripts/git_sync_workspace.ps1`
- 远端拉取同步脚本：
  - `修改稿/scripts/sync_from_github.ps1`
- 修改稿索引刷新脚本：
  - `修改稿/scripts/refresh_revision_indexes.py`
- 修改稿操作日志脚本：
  - `修改稿/scripts/write_revision_operation_log.py`
- 远端变更检测并安全同步脚本：
  - `修改稿/scripts/check_remote_signal_and_sync.ps1`
- 开关守卫脚本：
  - `修改稿/scripts/guarded_sync_check.ps1`
- 持续轮询监听脚本：
  - `修改稿/scripts/watch_remote_sync.ps1`
- Windows 自动同步统一开关脚本：
  - `修改稿/scripts/set_windows_auto_sync.ps1`
- Windows 计划任务注册脚本：
  - `修改稿/scripts/register_windows_remote_sync_tasks.ps1`
- Windows 计划任务彻底卸载脚本：
  - `修改稿/scripts/unregister_windows_remote_sync_tasks.ps1`
- Windows 自动同步手动停止脚本：
  - `修改稿/scripts/stop_windows_auto_sync.ps1`
- Windows 计划任务启动包装脚本：
  - `修改稿/scripts/run_hidden_sync_check.cmd`
- 一键收尾脚本：
  - `修改稿/scripts/finalize_revision_task.ps1`

## 说明

- 留底是历史快照，不覆盖旧文件。
- 工作稿可以继续迭代，但每次交付级修改都必须生成新的留底文件。
- 每次执行 `finalize_revision_task.ps1` 时，会自动刷新 `修改稿/索引/` 并新建一份 `修改稿/操作日志/` 文件。
- 不要把临时锁文件、Word 自动生成锁文件或 Python 缓存当作有效稿件。
- `REMOTE_SYNC_SIGNAL.json` 会在本地提交并推送时自动刷新。
- `LOCAL_SYNC_STATE.json` 是本地状态文件，只用于记录最近一次检查/同步状态，不进入 Git。
- `AUTO_SYNC_CONTROL.json` 是本地自动同步开关文件，不进入 Git。
- 如果需要不打开 Codex 也自动同步，可注册：
  - 一个每 5 分钟检查一次的 Windows 计划任务
  - 一个登录即检查一次的 Startup 自启快捷方式
- 日常开启/关闭统一使用 `修改稿/scripts/set_windows_auto_sync.ps1`。
- 如果只是想临时关闭，不要删 Startup 自启快捷方式，直接用统一开关脚本切到 `Disable`，或使用 `stop_windows_auto_sync.ps1` 这个便捷包装脚本。
- 只有在你明确要彻底移除自动同步入口时，才使用 `unregister_windows_remote_sync_tasks.ps1`。

# 修改稿操作日志

本目录用于保存“每次操作一份文件”的日志。

规则：

- 每次收尾或关键修改动作，新增一份日志文件。
- 日志文件名精确到秒，不覆盖旧文件。
- 推荐文件名格式：
  - `YYYYMMDD_HHMMSS__series__token__action.md`
- 日志由脚本 `修改稿/scripts/write_revision_operation_log.py` 自动生成。

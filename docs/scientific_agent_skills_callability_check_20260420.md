# Scientific Agent Skills 调用状态复核

- 复核时间：2026-04-20 17:26:30
- Codex skills 标准目录：C:\Users\陈楚玲\.codex\skills
- 用户 skills 数量（不含 .system）：134

## 1. 磁盘层面可发现性

| skill | SKILL.md 存在 | frontmatter name | name 匹配 | 路径 |
|---|---:|---|---:|---|
| scientific-writing | True | scientific-writing | True | C:\Users\陈楚玲\.codex\skills\scientific-writing\SKILL.md |
| peer-review | True | peer-review | True | C:\Users\陈楚玲\.codex\skills\peer-review\SKILL.md |
| citation-management | True | citation-management | True | C:\Users\陈楚玲\.codex\skills\citation-management\SKILL.md |
| literature-review | True | literature-review | True | C:\Users\陈楚玲\.codex\skills\literature-review\SKILL.md |
| statistical-analysis | True | statistical-analysis | True | C:\Users\陈楚玲\.codex\skills\statistical-analysis\SKILL.md |

结论：上述关键 skills 已经安装到 Codex 标准 skills 目录，磁盘层面可发现，且元数据 name 匹配。

## 2. 当前会话能否直接自动调用

当前正在运行的 Codex 会话在本轮安装前已经加载了系统提供的 available skills 列表；该列表中尚未出现 scientific-writing、peer-review、citation-management、literature-review、statistical-analysis。因此，本会话内无法证明它们已经进入自动触发列表。

可操作结论：

1. 现在已经可以通过文件路径读取这些 SKILL.md，并按其中规则手动遵循。
2. 若要让 Codex 在提示词中像普通 skill 一样自动识别和调用，建议重启 Codex 或开启新会话。
3. 重启/新会话后，可用一句测试提示词验证：请使用 scientific-writing 和 peer-review 检查论文摘要是否符合顶刊克制表达。

## 3. 本轮未做的事

- 未全量运行 scientific workflow。
- 未改动论文正文或数据。
- 未安装 gh、node、npm、npx、uv 等全局工具。
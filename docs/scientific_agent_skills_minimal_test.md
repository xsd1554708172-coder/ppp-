# Scientific Agent Skills 最小可用性测试

- 测试时间：2026-04-20 17:21:46
- Codex skills 标准目录：C:\Users\陈楚玲\.codex\skills
- 测试方式：读取已安装 SKILL.md 元数据，并按 scientific-writing 的“完整段落、克制学术表达”要求执行一个低风险句子改写测试。

## 1. 必需 skills 元数据核验

| skill | SKILL.md 存在 | frontmatter name | 路径 |
|---|---:|---|---|
| scientific-writing | True | scientific-writing | C:\Users\陈楚玲\.codex\skills\scientific-writing\SKILL.md |
| peer-review | True | peer-review | C:\Users\陈楚玲\.codex\skills\peer-review\SKILL.md |
| citation-management | True | citation-management | C:\Users\陈楚玲\.codex\skills\citation-management\SKILL.md |
| literature-review | True | literature-review | C:\Users\陈楚玲\.codex\skills\literature-review\SKILL.md |
| statistical-analysis | True | statistical-analysis | C:\Users\陈楚玲\.codex\skills\statistical-analysis\SKILL.md |

## 2. 最小测试输入

> 将“主结果在方向上稳定但统计强度有限”改写为论文中克制、完整的一句话。

## 3. 最小测试输出

补充检验显示，核心结果在方向上保持一致，但其统计强度对识别设定和样本扰动仍具有一定敏感性，因此本文将其解释为主识别结论的防守性证据，而非额外的强因果识别。

## 4. 判定

- 元数据核验：通过。
- 低风险调用验证：通过读取并应用 scientific-writing 指令完成，不涉及重计算或外部数据库调用。
- 说明：当前会话的系统级 skills 列表可能不会热更新；若要在 Codex UI 中自动触发这些 skills，建议重启 Codex 或开启新会话。
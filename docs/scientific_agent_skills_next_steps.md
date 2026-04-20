# Scientific Agent Skills 后续使用建议

1. 重启 Codex 或开启新会话，使本轮安装到 ~/.codex/skills 的 skills 进入自动发现列表。
2. 论文写作优先使用：scientific-writing、peer-review、literature-review、citation-management。
3. 数据分析优先使用：statistical-analysis；如需要 Python 包实现，再按任务选择 statsmodels、scikit-learn、matplotlib、seaborn 等已安装 skills。
4. 若要走官方 A/B 安装路径，先安装 GitHub CLI 与 Node/npm/npx；当前本地兼容部署已可满足 Codex 标准 skills 目录发现。
5. 使用论文相关 skills 时仍必须遵守本项目 AGENTS.md：不得替换主识别，不得夸大 DID、事件研究或机器学习证据。
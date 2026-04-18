# never_treated数量差异说明

- 正式V3主面板中的never-treated数量为 3：新疆生产建设兵团, 海南, 青海。
- baseline_sample_5_3过滤后的never-treated数量为 2：海南, 青海。
- 差异来源是 `新疆生产建设兵团` 在正式主面板中存在，但 `baseline_sample_5_3=0`，因此在进入Stack DID估计前已被排除，而不是被窗口二次剔除。
- 根据主面板记录，该地区未进入正式基准样本，原因是上游官方样本过滤而非本轮脚本的控制组构造问题。

## 被排除地区在正式主面板中的记录
province  year  baseline_sample_5_3  text_observed  text_missing  baseline_controls_complete
新疆生产建设兵团  2015                    0              0             1                           0
新疆生产建设兵团  2016                    0              0             1                           0
新疆生产建设兵团  2017                    0              0             1                           0
新疆生产建设兵团  2020                    0              0             1                           0
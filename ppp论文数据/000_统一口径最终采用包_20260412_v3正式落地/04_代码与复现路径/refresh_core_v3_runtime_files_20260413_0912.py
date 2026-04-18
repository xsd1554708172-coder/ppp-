from pathlib import Path
import json, shutil, re

ROOT = Path(__file__).resolve().parents[3]
TS = "20260413_0912"

def pick(prefix, suffix):
    matches = [p for p in ROOT.rglob(f"{prefix}*{suffix}") if '99_历史说明与证据_勿引用' not in str(p)]
    if not matches:
        raise FileNotFoundError(f"No file for {prefix}*{suffix}")
    matches = sorted(matches)
    return matches[-1]

panel_xlsx = pick('PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_', '.xlsx')
panel_csv = pick('PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_', '.csv')
risk_csv = pick('PPP_project_level_risk_model_data_v3_无泄漏严格版_标签统一_', '.csv')
cfg_path = ROOT / '02_第9部分_最终可用内容' / 'config.json'
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
    cfg['data_path'] = str(risk_csv.relative_to(ROOT)).replace('\\','/')
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
print('OK', panel_xlsx.name, panel_csv.name, risk_csv.name)

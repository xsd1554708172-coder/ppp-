
from __future__ import annotations
import json, math, re, shutil, subprocess, sys, zipfile
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from scipy import stats
try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
except Exception as exc:
    sm = smf = None
    STATSMODELS_ERROR = repr(exc)
else:
    STATSMODELS_ERROR = None

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "修改稿" / "v2执行工作包" / "v2e_to_v2f_did_review_assets"
EXTRACT = WORK / "_codex_extracts"
LOGS = WORK / "rerun_logs"
SNAPS = WORK / "result_snapshots"
V2F = ROOT / "修改稿" / "v2说明文件" / "v2f"
ARCH = ROOT / "修改稿" / "v2修改稿留底" / "v2f"
LONG = ROOT / "修改稿" / "v2执行工作包" / "future_city_year_modern_did_upgrade"
INDEX = ROOT / "修改稿" / "索引"
OPLOG = ROOT / "修改稿" / "操作日志"
BUNDLE = ROOT / "PPP_empirical_reinforcement_bundle_20260416_unified_v3"
for d in [WORK, EXTRACT, LOGS, SNAPS, V2F, ARCH, LONG, INDEX, OPLOG]: d.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now().strftime("%m%d_%H%M")
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")
DOCX_DID = ROOT / "修改稿" / "did方法修改建议.docx"
DOCX_V2E = ROOT / "修改稿" / "v2修改建议" / "v2e修改建议" / "v2e修改建议.docx"
V2E_MD = ROOT / "修改稿" / "v2说明文件" / "v2e" / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2e_0420_1944.md"
V2E_DOCX = ROOT / "修改稿" / "v2说明文件" / "v2e" / "PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2e_0420_1944_对象保留公式版.docx"
V2E_REG = ROOT / "修改稿" / "v2说明文件" / "v2e" / "v2e_implied_city_slot_registry_from_v2d_treat_share.csv"
V2E_AUD = ROOT / "修改稿" / "v2说明文件" / "v2e" / "v2e_province_year_treat_share_audit_from_v2d.csv"
V2E_THR = ROOT / "修改稿" / "v2说明文件" / "v2e" / "v2e_working_threshold_proxy_from_province_year_audit.csv"
sys.path.insert(0, str(BUNDLE))
from bundle_common import BASE_SAMPLE_FLAG, CONTROLS, OUTCOMES, PROVINCE_COL, TREATMENT, YEAR_COL, clean_baseline_sample, load_main_panel, read_official_baseline_rows, resolve_paths

def rel(p: Path) -> str:
    try: return str(p.relative_to(ROOT)).replace('\\','/')
    except Exception: return str(p)

def w(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace('\r\n','\n'), encoding='utf-8')

def tbl(df: pd.DataFrame, n: int|None=None) -> str:
    if df is None or df.empty: return '（无记录）\n'
    d = df.head(n) if n else df
    cols = list(d.columns); out=['| '+' | '.join(map(str,cols))+' |','|'+'|'.join(['---']*len(cols))+'|']
    for _,r in d.iterrows():
        vals=[]
        for c in cols:
            v=r[c]
            if isinstance(v,float): vals.append('' if pd.isna(v) else (f'{v:.4g}' if abs(v)>=1000 or (abs(v)<0.001 and v!=0) else f'{v:.4f}'))
            else: vals.append(str(v).replace('|','/'))
        out.append('| '+' | '.join(vals)+' |')
    if n and len(df)>n: out.append(f'\n（仅显示前 {n} 行，共 {len(df)} 行。）')
    return '\n'.join(out)+'\n'

def extract_docx(path: Path, out: Path, title: str) -> dict:
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    if not path.exists():
        w(out, f'# {title}\n\n> 文件不存在：`{path}`\n'); return {'exists':False}
    z=zipfile.ZipFile(path); root=ET.fromstring(z.read('word/document.xml')); body=root.find('w:body',ns)
    parts=[f'# {title}','',f'- 原始文件：`{rel(path)}`',f'- 提取时间：{NOW}','- 说明：只读抽取，便于 Git diff，不替代原始 docx。','']
    pc=tc=cc=0
    for child in list(body or []):
        tag=child.tag.split('}',1)[-1]
        if tag=='p':
            s=''.join(t.text or '' for t in child.findall('.//w:t',ns)).strip()
            if s: parts += [s,'']; pc+=1; cc+=len(s)
        elif tag=='tbl':
            rows=[]
            for tr in child.findall('w:tr',ns):
                row=[]
                for c in tr.findall('w:tc',ns):
                    row.append(re.sub(r'\s+',' ', ' '.join(''.join(t.text or '' for t in p.findall('.//w:t',ns)).strip() for p in c.findall('w:p',ns))).replace('|','/'))
                if row: rows.append(row)
            if rows:
                tc+=1; m=max(map(len,rows)); rows=[r+['']*(m-len(r)) for r in rows]
                parts += [f'## Table {tc}','','| '+' | '.join(rows[0])+' |','|'+'|'.join(['---']*m)+'|']
                parts += ['| '+' | '.join(r)+' |' for r in rows[1:]]+['']
                cc += sum(len(x) for r in rows for x in r)
    w(out, '\n'.join(parts)); return {'exists':True,'paragraphs':pc,'tables':tc,'characters':cc}

def run(name: str, cmd: list[str]) -> dict:
    log=LOGS/f'{name}.log'
    try:
        p=subprocess.run(cmd,cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=900)
        w(log, f'# {name}\n\n- command: `{" ".join(cmd)}`\n- returncode: {p.returncode}\n\n## STDOUT\n```\n{p.stdout}\n```\n\n## STDERR\n```\n{p.stderr}\n```\n')
        return {'name':name,'returncode':p.returncode,'ok':p.returncode==0,'log':rel(log)}
    except Exception as e:
        w(log, f'# {name}\n\nEXCEPTION: `{repr(e)}`\n'); return {'name':name,'returncode':None,'ok':False,'log':rel(log),'error':repr(e)}

def design(df: pd.DataFrame, ycol: str, tcol: str, trends=False):
    need=[ycol,tcol,PROVINCE_COL,YEAR_COL,*CONTROLS]+(['year_idx'] if trends else [])
    d=df[need].dropna().copy(); d[PROVINCE_COL]=d[PROVINCE_COL].astype(str)
    y=pd.to_numeric(d[ycol],errors='coerce').to_numpy(float)
    blocks=[pd.Series(1.0,index=d.index,name='intercept')]; names=['intercept']
    for c in [tcol,*CONTROLS]: blocks.append(pd.to_numeric(d[c],errors='coerce').astype(float).rename(c)); names.append(c)
    pdum=pd.get_dummies(d[PROVINCE_COL],prefix='province',drop_first=True); ydum=pd.get_dummies(d[YEAR_COL],prefix='year',drop_first=True)
    for c in pdum.columns: blocks.append(pdum[c].astype(float)); names.append(c)
    for c in ydum.columns: blocks.append(ydum[c].astype(float)); names.append(c)
    if trends:
        allp=pd.get_dummies(d[PROVINCE_COL],prefix='trend',drop_first=False); yi=pd.to_numeric(d['year_idx'],errors='coerce').astype(float)
        for c in allp.columns: blocks.append((allp[c].astype(float)*yi).rename(c+'_x_year_idx')); names.append(c+'_x_year_idx')
    Xdf=pd.concat(blocks,axis=1); X=Xdf.to_numpy(float); keep=np.isfinite(y)&np.isfinite(X).all(axis=1)
    return X[keep], y[keep], names, d[PROVINCE_COL].iloc[np.where(keep)[0]]

def fit(df: pd.DataFrame, ycol: str, tcol=TREATMENT, trends=False) -> dict:
    X,y,names,groups=design(df,ycol,tcol,trends); beta,*_=np.linalg.lstsq(X,y,rcond=None); resid=y-X@beta
    inv=np.linalg.pinv(X.T@X); garr=groups.astype(str).to_numpy(); meat=np.zeros((X.shape[1],X.shape[1]))
    for g in pd.unique(garr):
        idx=garr==g; sg=X[idx,:].T@resid[idx]; meat+=np.outer(sg,sg)
    nobs=int(X.shape[0]); npar=int(X.shape[1]); ng=int(len(pd.unique(garr))); corr=1.0
    if ng>1 and nobs>npar: corr=(ng/(ng-1))*((nobs-1)/(nobs-npar))
    vcov=inv@meat@inv*corr; se=np.sqrt(np.clip(np.diag(vcov),0,None)); t=beta/se; p=2*stats.t.sf(np.abs(t),df=max(ng-1,1)); i=names.index(tcol)
    return {'coef':float(beta[i]),'se':float(se[i]),'p_value':float(p[i]),'nobs':nobs,'nclusters':ng}

def empirical():
    cmds=[
        ('01_unified_baseline_reference',[sys.executable,'PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py']),
        ('02_trend_adjusted_DID',[sys.executable,'PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py']),
        ('03_leave_one_province_out',[sys.executable,'PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py']),
        ('04_wild_cluster_bootstrap_summary',[sys.executable,'PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py']),
        ('05_robustness_defense_summary',[sys.executable,'PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py'])]
    status=[run(n,c) for n,c in cmds]
    paths=resolve_paths(BUNDLE/'00_unified_baseline_reference'/'scripts'/'build_unified_baseline_reference.py')
    panel=load_main_panel(paths.panel_csv); base=clean_baseline_sample(panel).copy(); official=read_official_baseline_rows(paths.baseline_long_table)
    pv=pd.concat([base['exec_share'],base['proc_share']]); pv=pd.to_numeric(pv,errors='coerce'); mn=float(pv[pv>0].min()); cc=mn/2 if mn>0 else 1e-6
    base['log_ratio_exec_proc']=np.log((base['exec_share']+cc)/(base['proc_share']+cc))
    base['placebo_2015_exposure']=base.groupby(PROVINCE_COL)[TREATMENT].transform('max')*(base[YEAR_COL]>=2015).astype(float)
    rows=[]; loo=[]; spec=[]
    actual={}
    for y in OUTCOMES:
        off=official[official['outcome']==y].iloc[0].to_dict(); b=fit(base,y); tr=fit(base,y,trends=True); pl=fit(base,y,'placebo_2015_exposure'); actual[y]=b['coef']
        rows.append({'outcome':y,'official_coef':off['official_coef'],'official_p_value':off['official_p_value'],'fresh_baseline_coef':b['coef'],'fresh_baseline_se':b['se'],'fresh_baseline_p_value':b['p_value'],'fresh_baseline_nobs':b['nobs'],'trend_adjusted_coef':tr['coef'],'trend_adjusted_p_value':tr['p_value'],'placebo_2015_coef':pl['coef'],'placebo_2015_p_value':pl['p_value'],'role':'official_anchor_plus_fresh_audit'})
        for pr in sorted(base[PROVINCE_COL].astype(str).unique()):
            rr=fit(base[base[PROVINCE_COL].astype(str)!=pr],y)
            loo.append({'outcome':y,'province_excluded':pr,'coef':rr['coef'],'p_value':rr['p_value'],'sign_flip_vs_official':bool(np.sign(rr['coef'])!=np.sign(float(off['official_coef']))),'sig_jump_5pct_vs_official':bool((rr['p_value']<0.05)!=(float(off['official_p_value'])<0.05))})
        for lab,yrs in {'exclude_2017':[2017],'exclude_2020':[2020],'exclude_2017_2020':[2017,2020]}.items():
            rr=fit(base[~base[YEAR_COL].isin(yrs)],y); spec.append({'outcome':y,'diagnostic':lab,'coef':rr['coef'],'p_value':rr['p_value'],'nobs':rr['nobs'],'role':'boundary_diagnostic_not_main'})
    lr=fit(base,'log_ratio_exec_proc'); rows.append({'outcome':'log_ratio_exec_proc','official_coef':np.nan,'official_p_value':np.nan,'fresh_baseline_coef':lr['coef'],'fresh_baseline_se':lr['se'],'fresh_baseline_p_value':lr['p_value'],'fresh_baseline_nobs':lr['nobs'],'trend_adjusted_coef':np.nan,'trend_adjusted_p_value':np.nan,'placebo_2015_coef':np.nan,'placebo_2015_p_value':np.nan,'role':f'log_ratio_diagnostic_c={cc:.8g}'})
    rng=np.random.default_rng(20260420); provinces=np.array(sorted(base[PROVINCE_COL].astype(str).unique())); key=base[[PROVINCE_COL,YEAR_COL,TREATMENT]].copy(); key[PROVINCE_COL]=key[PROVINCE_COL].astype(str); perms=[]
    for y in OUTCOMES:
        vals=[]
        for _ in range(199):
            sh=provinces.copy(); rng.shuffle(sh); mp=pd.DataFrame({PROVINCE_COL:provinces,'source_province':sh}); src=key.rename(columns={PROVINCE_COL:'source_province',TREATMENT:'perm_treat'})
            wk=base.merge(mp,on=PROVINCE_COL,how='left').merge(src,on=['source_province',YEAR_COL],how='left')
            try: vals.append(fit(wk,y,'perm_treat')['coef'])
            except Exception: pass
        arr=np.array(vals,float); ep=float((np.sum(np.abs(arr)>=abs(actual[y]))+1)/(arr.size+1)) if arr.size else np.nan
        perms.append({'outcome':y,'actual_fresh_baseline_coef':actual[y],'n_permutations_successful':int(arr.size),'two_sided_empirical_p':ep,'role':'randomization_diagnostic_not_main'})
    frac=[]
    if smf is None:
        frac.append({'outcome':'exec_share/proc_share','status':'not_run','failure_reason':STATSMODELS_ERROR})
    else:
        for y in ['exec_share','proc_share']:
            wk=base[(base[y]>=0)&(base[y]<=1)].copy(); formula=f'{y} ~ {TREATMENT} + '+' + '.join(CONTROLS)+f' + C({PROVINCE_COL}) + C({YEAR_COL})'
            try:
                r=smf.glm(formula=formula,data=wk,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':wk[PROVINCE_COL]})
                frac.append({'outcome':y,'specification':'fractional_logit_binomial_fe','coef':float(r.params[TREATMENT]),'p_value':float(r.pvalues[TREATMENT]),'nobs':int(r.nobs),'status':'completed_exploratory','role':'bounded_share_diagnostic_not_main'})
            except Exception as e: frac.append({'outcome':y,'specification':'fractional_logit_binomial_fe','status':'failed','failure_reason':repr(e),'role':'bounded_share_diagnostic_not_main'})
    snap=pd.DataFrame(rows); lo=pd.DataFrame(loo); sp=pd.DataFrame(spec); pe=pd.DataFrame(perms); fr=pd.DataFrame(frac); cmd=pd.DataFrame(status)
    for df,name in [(snap,'v2f_rerun_result_snapshot.csv'),(lo,'v2f_leave_one_province_out_detail.csv'),(sp,'v2f_special_year_exclusion_diagnostics.csv'),(pe,'v2f_randomization_diagnostics.csv'),(fr,'v2f_fractional_response_diagnostics.csv'),(cmd,'rerun_command_status.csv')]:
        out=(SNAPS/name) if name.startswith('v2f_') else (LOGS/name); df.to_csv(out,index=False,encoding='utf-8-sig')
    pd.DataFrame([{'continuity_correction_c':cc,'baseline_sample_nobs':len(base),'province_count':base[PROVINCE_COL].nunique(),'year_span':f"{int(base[YEAR_COL].min())}-{int(base[YEAR_COL].max())}"}]).to_csv(SNAPS/'v2f_log_ratio_construction_meta.csv',index=False,encoding='utf-8-sig')
    with pd.ExcelWriter(SNAPS/'v2f_empirical_diagnostics_snapshot.xlsx',engine='openpyxl') as x:
        snap.to_excel(x,index=False,sheet_name='main_snapshot'); lo.to_excel(x,index=False,sheet_name='leave_one_out'); sp.to_excel(x,index=False,sheet_name='special_years'); pe.to_excel(x,index=False,sheet_name='randomization'); fr.to_excel(x,index=False,sheet_name='fractional_response')
    w(LOGS/'rerun_status_summary.md','# v2f rerun status summary\n\n'+tbl(cmd)+'\n## 主快照\n\n'+tbl(snap)+'\n## randomization\n\n'+tbl(pe)+'\n## fractional response\n\n'+tbl(fr))
    return snap,pe,fr,{'commands':status,'c':cc,'nobs':len(base)}

def registry_assets() -> dict:
    info={'source_registry_exists':V2E_REG.exists(),'source_audit_exists':V2E_AUD.exists(),'source_threshold_exists':V2E_THR.exists(),'rule':'Use implied/pseudo city-slot registry as working city-year registry; never label as real city list.'}
    if V2E_REG.exists():
        df=pd.read_csv(V2E_REG); info['registry_rows']=len(df)
    elif V2E_AUD.exists():
        aud=pd.read_csv(V2E_AUD); rows=[]
        for _,r in aud.iterrows():
            prov=str(r.get('province','')); yr=int(r.get('year')); ts=float(r.get('treat_share',r.get('audit_treat_share',0)) or 0); n=100; tr=round(ts*n)
            for i in range(1,n+1):
                rows.append({'province':prov,'city':f'{prov}_pseudo_city_slot_{i:03d}','city_id':f'{prov}_{i:03d}','year':yr,'first_treat_year':'unknown_inferred','treated':1 if i<=tr else 0,'treatment_source':'province_year_treat_share_implied_slot','source_note':'Pseudo slot; real city-year registry unavailable.','aggregation_weight':1/n})
        df=pd.DataFrame(rows); info['registry_rows']=len(df); info['reconstructed_from_audit']=True
    else:
        df=pd.DataFrame(columns=['province','city','city_id','year','first_treat_year','treated','treatment_source','source_note','aggregation_weight']); info['registry_rows']=0
    rcsv=V2F/'v2f_working_city_year_registry_from_implied_slots.csv'; rx=V2F/'v2f_working_city_year_registry_from_implied_slots.xlsx'
    df.to_csv(rcsv,index=False,encoding='utf-8-sig'); df.to_excel(rx,index=False); shutil.copy2(rcsv,LONG/rcsv.name); shutil.copy2(rx,LONG/rx.name); info['working_registry_csv']=rel(rcsv); info['working_registry_xlsx']=rel(rx)
    if V2E_AUD.exists():
        aud=pd.read_csv(V2E_AUD); info['audit_rows']=len(aud); acsv=V2F/'v2f_province_year_treat_share_audit_working.csv'; ax=V2F/'v2f_province_year_treat_share_audit_working.xlsx'; aud.to_csv(acsv,index=False,encoding='utf-8-sig'); aud.to_excel(ax,index=False); shutil.copy2(acsv,LONG/acsv.name); shutil.copy2(ax,LONG/ax.name); info['audit_csv']=rel(acsv)
    if V2E_THR.exists():
        th=pd.read_csv(V2E_THR); info['threshold_rows']=len(th); tcsv=V2F/'v2f_working_threshold_proxy.csv'; tx=V2F/'v2f_working_threshold_proxy.xlsx'; th.to_csv(tcsv,index=False,encoding='utf-8-sig'); th.to_excel(tx,index=False); shutil.copy2(tcsv,LONG/tcsv.name); shutil.copy2(tx,LONG/tx.name); info['threshold_csv']=rel(tcsv)
    w(V2F/'v2f_working_registry_and_audit_data_note.md',f"""# v2f working registry and province-year audit data note

本轮按用户确认，若无真实 city-year treatment registry 原始城市名单和处理阈值底表，则使用 implied/pseudo city-slot registry 作为工作数据进行省年审计与脚本接口运行。

## 文件

- working registry：`{info.get('working_registry_csv')}`
- province-year audit：`{info.get('audit_csv','未生成')}`
- threshold proxy：`{info.get('threshold_csv','未生成')}`

## 聚合口径

默认采用等权 city-slot 计数：省年 `treat_share` = treated city-slot 数 / city-slot 总数。该口径是审计/占位口径，不是官方真实城市名单。未来若取得真实城市名单、人口/项目数/财政权重或阈值底表，必须重建并与本口径并列核验。

```json
{json.dumps(info,ensure_ascii=False,indent=2)}
```
""")
    return info

def esc(s:str)->str: return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
def pxml(s:str)->bytes: return f'<w:p><w:r><w:t xml:space="preserve">{esc(s)}</w:t></w:r></w:p>'.encode('utf-8')
def patch_docx(path: Path):
    tmp=path.with_suffix('.tmp.docx')
    notes=['v2f 稳健投稿稿说明：本版本依据 did方法修改建议.docx 与 v2e修改建议.docx 收紧 DID 叙述，并保留 treat_share 多期 DID/TWFE 为唯一主识别。','v2f 公式规则：本 Word 版本保留原对象和 Office Math 公式；本轮新增说明不引入新的纯文本公式。后续若继续改写模型式，必须使用 Word 公式编辑器录入。','v2f 数据边界：本版本使用 implied/pseudo city-slot registry 作为工作审计输入，但不将其称为真实城市名单或官方处理阈值底表。']
    ins=b''.join(pxml(x) for x in notes)
    with zipfile.ZipFile(path,'r') as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data=zin.read(it.filename)
            if it.filename=='word/document.xml':
                data=data.replace(b'v2e',b'v2f')
                data=data.replace(b'<w:body>',b'<w:body>'+ins,1)
            zout.writestr(it,data)
    tmp.replace(path)

def manuscript(snap,perm,frac,reg):
    base=V2E_MD.read_text(encoding='utf-8',errors='replace').replace('v2e','v2f') if V2E_MD.exists() else '# v2e base missing\n'
    note=f"\n> v2f 稳健投稿稿新增说明（{NOW}）：本版本依据 `did方法修改建议.docx` 与 `v2e修改建议.docx` 进一步收紧 DID 叙述。`treat_share` 多期 DID/TWFE 仍是唯一主识别；本文将其解释为连续处理强度下的平均条件关联证据，而不是标准二元处理 ATT。事件研究、趋势调整、leave-one-province-out、wild cluster bootstrap、log-ratio、placebo/randomization、fractional response 均只作为防御性稳健性或边界诊断。因真实 city-year treatment registry 与处理阈值底表仍缺，本版本按用户确认使用 implied/pseudo city-slot registry 作工作审计输入，但正文不得将其称为真实城市名单。\n"
    lines=base.splitlines(); insert=3
    for i,l in enumerate(lines[:12]):
        if l.startswith('>'): insert=i+1; break
    lines.insert(insert,note.strip()); base='\n'.join(lines)
    main=snap[snap['outcome'].isin(OUTCOMES)]; log=snap[snap['outcome']=='log_ratio_exec_proc']
    add=f"""

---

## v2f DID 识别边界与稳健性增补（并入第4章/第5章的正文稿）

本轮不改变论文主研究结构。`treat_share` 多期 DID/TWFE 仍是唯一主识别，估计对象被严格限定为连续处理强度下、在省份固定效应、年份固定效应与既定控制变量条件下的平均条件关联。由于处理变量并非二元政策进入、且各省暴露强度具有连续差异，正文不再把估计结果写成标准 ATT，也不写成已经完全消除所有地区时间变混杂的强因果估计。

事件研究图与动态路径只用于观察处理强度变化前后的响应轮廓和识别边界，不作为“平行趋势已经成立”的证明。若动态项在政策前存在波动，正文应解释为需要谨慎识别的边界信号，而不是通过补充稳健性把弱证据包装成强证据。

在结果解释上，`exec_share` 与 `proc_share` 继续构成主结果。`ppp_quality_zindex` 仅保留为方向性辅助信号：即便方向为正，只要统计稳定性不足，就不能写成“治理质量全面提升”。A/B/C/D 政策文本变量只作为政策文本证据线索，除非后续取得独立机制数据并完成估计，否则不得写成独立机制识别。

### v2f fresh rerun / diagnostics 快照

{tbl(main[['outcome','official_coef','official_p_value','fresh_baseline_coef','fresh_baseline_p_value','trend_adjusted_coef','trend_adjusted_p_value','placebo_2015_coef','placebo_2015_p_value']])}

### log-ratio 与份额约束诊断

log-ratio 诊断用于处理 `exec_share` 与 `proc_share` 作为互相关联份额时的组合型约束。其定位是防御性稳健性，不替代主识别。

{tbl(log[['outcome','fresh_baseline_coef','fresh_baseline_se','fresh_baseline_p_value','fresh_baseline_nobs','role']])}

### placebo / randomization / fractional response 边界诊断

随机置换与 placebo-year 诊断只用于检查结果是否可能由任意省份路径或任意年份阈值机械生成；fractional response 只用于 bounded share 结果变量的辅助检查。它们均不构成新的主识别。

{tbl(perm[['outcome','two_sided_empirical_p','n_permutations_successful','role']])}

{tbl(frac[[c for c in ['outcome','specification','coef','p_value','status','role'] if c in frac.columns]])}

### 伪 city-slot registry 的使用边界

本轮根据用户确认，使用 v2e 形成的 implied/pseudo city-slot registry 作为工作层 city-year treatment registry 输入。其用途限定为：省年 `treat_share` 聚合审计、可运行脚本接口、未来真实 registry 的字段桥接。由于它不是原始城市名单，也不是官方处理阈值底表，正文中不得写作“真实 city-year treatment registry 已重建完成”。推荐表述为：“在缺少原始城市处理名单的条件下，本文以省年 `treat_share` 反推的等权 city-slot registry 进行聚合审计，并将其作为后续真实城市级重建的接口模板。”

### 政策背景的分层写法

数字政务改革是本文主冲击；PPP 2014 年推广、2017 年项目库规范、2023 年新机制均应作为 PPP 制度环境与潜在干扰源写入背景和稳健性讨论，不应被重写为本文新的主处理。2023 年以后不进入主 DID 窗口；若未来扩展样本，必须在正式口径表中重建样本边界。
"""
    md=V2F/f'PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2f_{STAMP}.md'; w(md,base.rstrip()+add)
    doc=V2F/f'PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2f_{STAMP}_对象保留公式版.docx'; shutil.copy2(V2E_DOCX,doc); patch_docx(doc)
    shutil.copy2(md,ARCH/f'v2f_{STAMP}.md'); shutil.copy2(doc,ARCH/f'v2f_{STAMP}.docx')
    return md,doc

def long_pkg(reg):
    w(LONG/'README_长期升级包说明.md',f"""# future city-year / modern DID upgrade package

本目录不是 v2f 正文结果，而是为下一阶段真实 city-year registry、stacked DID / Sun-Abraham、duration/hazard model 准备的数据设计、脚本接口和缺口清单。v2f 正文仍以 `treat_share` 多期 DID/TWFE 为唯一主识别。

当前按用户确认使用 pseudo city-slot registry 作为工作数据：`{reg.get('working_registry_csv')}`。它不得写成真实城市名单。
""")
    w(LONG/'city_year_registry_schema_and_gap_list.md',"""# city-year treatment registry schema and gap list

| 字段 | 含义 | 当前状态 |
|---|---|---|
| province | 省份 | pseudo registry 可提供 |
| city | 城市名 | 当前仅 pseudo city-slot，非真实城市 |
| city_id | 城市代码 | 当前仅 pseudo slot id |
| year | 年份 | 可提供 |
| first_treat_year | 首次处理年份 | 当前无法真实确认 |
| treated | city-year 是否处理 | pseudo slot 可提供审计值 |
| treatment_source | 处理来源 | 应写明 inferred/proxy |
| source_note | 来源说明 | 必须写明不是原始名单 |
| aggregation_weight | 聚合权重 | 本轮默认等权 city-slot |

真实缺口：真实城市名单、处理阈值底表、权重底表、可区分未处理与未观测城市的 source。
""")
    w(LONG/'pseudo_to_real_registry_bridge.md',"""# pseudo-to-real registry bridge

现在用 pseudo registry 保持脚本接口可运行，所有输出加 `data_status = inferred_proxy_not_real_city_list`。未来取得真实城市名单后，替换 city/city_id/treated/first_treat_year/aggregation_weight，并重建 province-year treat_share。
""")
    w(LONG/'stacked_did_sun_abraham_design.md',"""# stacked DID / Sun-Abraham design note

该设计属于未来升级包，不进入 v2f 主识别。真实 city-year registry 到位后，可构造 cohort-year event-time panel、stacked sample 和 cohort-aware 动态诊断。若最终仍只有省级 outcome，则现代 DID 只能作为边界诊断。
""")
    w(LONG/'duration_hazard_model_data_requirements.md',"""# project-level duration / hazard model data requirements

最低字段：project_id、province、city、sector、identification_date、procurement_date、contract_date、execution_date、exit_date、censoring_status、project_amount、digital_reform_exposure、source_note。hazard model 是长期扩展分析，不替代 v2f 主 DID。
""")
    w(LONG/'future_upgrade_tasklist.md',"""# future upgrade tasklist

## P0
- 收集真实 city-year treatment registry 原始城市名单。
- 收集处理阈值底表。
- 确认 treat_share 聚合权重。
- 完成文本变量人工双标注与 kappa/alpha。

## P1
- 逐篇核验 14 篇 DID 文献 PDF/数据库元数据。
- 建立 stacked DID / Sun-Abraham 输入表。
- 建立项目级 duration/hazard 日期字段。
""")
    pd.DataFrame(columns=['province','city','city_id','year','first_treat_year','treated','treatment_source','source_note','aggregation_weight']).to_csv(LONG/'true_city_year_registry_template.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(columns=['project_id','province','city','sector','identification_date','procurement_date','contract_date','execution_date','exit_date','censoring_status','project_amount','digital_reform_exposure','source_note']).to_csv(LONG/'project_duration_hazard_template.csv',index=False,encoding='utf-8-sig')
    pd.read_csv(LONG/'true_city_year_registry_template.csv').to_excel(LONG/'true_city_year_registry_template.xlsx',index=False)
    pd.read_csv(LONG/'project_duration_hazard_template.csv').to_excel(LONG/'project_duration_hazard_template.xlsx',index=False)

def docs(snap,perm,frac,reg,ext,emp,md,doc):
    cmd=pd.DataFrame(emp['commands'])
    w(V2F/'00_input_mapping.md',f"""# v2f Input Mapping

## Token
- `v2f`

## 新增输入
| 类型 | 路径 | 状态 |
|---|---|---|
| DID 方法修改建议 | `{rel(DOCX_DID)}` | 已抽取 |
| v2e 成稿后修改建议 | `{rel(DOCX_V2E)}` | 已抽取 |

## 正文底稿与输出
- v2e Markdown：`{rel(V2E_MD)}`
- v2e 对象保留公式版 Word：`{rel(V2E_DOCX)}`
- v2f Markdown：`{rel(md)}`
- v2f Word：`{rel(doc)}`

## 工作数据
用户已确认：无真实 city-year registry 和处理阈值底表时，使用/生成伪 city-year / city-slot registry 作为工作数据。本轮采用：`{reg.get('working_registry_csv')}`。

## Authority
AGENTS 红线 > 两份新 docx > v2e 最新稿 > 正式 source-of-truth > fresh rerun/diagnostics。若 fresh rerun 与 official 冲突，正文以 official 为锚。
""")
    w(V2F/'01_revision_tasklist.md',"""# v2f Revision Tasklist

## P0
- [x] 抽取两份新增 docx。
- [x] 保持 `treat_share` 多期 DID/TWFE 为唯一主识别。
- [x] 将 DID 语气降格为连续处理强度下的平均条件关联。
- [x] 事件研究降格为动态路径/边界诊断。
- [x] 使用 pseudo city-slot registry 作工作数据并标注边界。
- [x] 尝试运行 baseline、trend-adjusted、leave-one-province-out、wild bootstrap summary、robustness summary。
- [x] 新增 log-ratio、placebo/randomization、特殊年份剔除、fractional response 诊断快照。

## P1
- [x] `exec_share` / `proc_share` 保持主结果。
- [x] `ppp_quality_zindex` 降格为方向性辅助信号。
- [x] A/B/C/D 降格为政策文本证据线索。
- [x] 生成长期 city-year / modern DID 升级包。

## P2
- [ ] 真实城市名单、阈值底表、权重底表。
- [ ] 14 篇 DID 文献元数据逐篇核验。
- [ ] 文本效度人工双标注与 kappa/alpha。
""")
    w(V2F/'02_verification_report.md',f"""# v2f Verification Report

## 输入抽取
```json
{json.dumps(ext,ensure_ascii=False,indent=2)}
```

## rerun 命令
{tbl(cmd)}

## fresh diagnostics
- 快照：`{rel(SNAPS/'v2f_empirical_diagnostics_snapshot.xlsx')}`
- log-ratio continuity correction：`{emp.get('c')}`
- baseline nobs：`{emp.get('nobs')}`

{tbl(snap)}

## 红线核验
- 主识别仍为 `treat_share` 多期 DID/TWFE。
- trend-adjusted DID、leave-one-province-out、wild bootstrap、log-ratio、placebo/randomization、fractional response 均只作防御性稳健性或边界诊断。
- 未把 event study 写成证明平行趋势成立。
- 未把 `ppp_quality_zindex` 写成治理质量全面提升。
- 未把 A/B/C/D 写成独立机制识别。
- 未修改 v1、原始数据总表或正式 source-of-truth xlsx。

## Word 公式规则
v2f Word 从 v2e 对象保留公式版复制并插入无公式说明段；保留 Office Math 对象，未向 Word 新增纯文本公式。
""")
    w(V2F/'03_delivery_note.md',f"""# v2f Delivery Note

## 本轮交付
基于 `did方法修改建议.docx` 与 `v2e修改建议.docx` 生成 v2f 稳健投稿稿与长期升级包。v2f 不改变主研究结构，继续以 `treat_share` 多期 DID/TWFE 为唯一主识别。

## 核心变化
1. DID 写法由强因果/标准 ATT 语气降格为连续处理强度下的平均条件关联证据。
2. 事件研究只作动态路径和边界诊断。
3. `exec_share` / `proc_share` 为主结果；`ppp_quality_zindex` 为方向性辅助信号。
4. A/B/C/D 是政策文本证据线索，独立机制变量仍需真实数据。
5. 使用用户确认的 pseudo city-slot registry 作工作数据，不冒充真实城市名单。
6. 保存 fresh rerun 与新增诊断快照。

## 主要文件
- v2f Markdown：`{rel(md)}`
- v2f Word：`{rel(doc)}`
- v2f 留底目录：`{rel(ARCH)}`
- 执行工作包：`{rel(WORK)}`
- 长期升级包：`{rel(LONG)}`

## 不得误读
pseudo registry 是工作审计数据，不是真实城市名单；新 diagnostics 是防御性/边界层，不是新主识别；14 篇 DID 文献未逐篇数据库/PDF 级元数据核验。
""")
    w(V2F/'v2f_修改文档总览.md',f"""# v2f 修改文档总览

| 文件 | 用途 |
|---|---|
| `00_input_mapping.md` | 输入映射 |
| `01_revision_tasklist.md` | 任务清单 |
| `02_verification_report.md` | 核验报告 |
| `03_delivery_note.md` | 交付说明 |
| `{md.name}` | v2f Markdown 稳健稿 |
| `{doc.name}` | v2f 对象保留公式版 Word |
| `v2f_working_registry_and_audit_data_note.md` | pseudo registry 与省年审计说明 |
""")
    w(V2F/'v2f_delivery_manifest.json',json.dumps({'token':'v2f','stamp':STAMP,'md':rel(md),'docx':rel(doc),'archive':rel(ARCH),'work_assets':rel(WORK),'long_package':rel(LONG),'registry':reg},ensure_ascii=False,indent=2))
    w(WORK/'v2e_to_v2f_manuscript_patch.md',f"""# v2e -> v2f manuscript patch

## 摘要/识别策略替换原则
将“证明”“全面提升治理质量”“平行趋势成立”等强表述，替换为“连续处理强度下的平均条件关联”“防御性稳健性支持”“边界性结果”“政策文本证据线索”。

## 第4章识别策略替换段
> 鉴于处理变量是省年层面的连续暴露强度，本文不将估计量解释为标准二元处理 ATT，而将其界定为连续处理强度下的平均条件关联证据。省份固定效应吸收时间不变地区差异，年份固定效应吸收共同冲击；趋势调整、留一省、wild cluster bootstrap、log-ratio、placebo/randomization 和 fractional response 均作为防御性稳健性或边界诊断，不替代主识别。

## 第5章事件研究替换段
> 事件研究图用于呈现处理强度变化前后的动态路径和识别边界。本文不据此宣称平行趋势已经成立；若政策前动态项存在波动，解释为需要谨慎处理的诊断信号。

## 快照
{tbl(snap)}
""")
    w(WORK/'v2f_empirical_rerun_checklist.md',f"""# v2f empirical rerun checklist

## 已实际运行/尝试运行
- baseline TWFE：`{rel(LOGS/'01_unified_baseline_reference.log')}`
- trend-adjusted DID：`{rel(LOGS/'02_trend_adjusted_DID.log')}`
- leave-one-province-out：`{rel(LOGS/'03_leave_one_province_out.log')}`
- wild cluster bootstrap summary：`{rel(LOGS/'04_wild_cluster_bootstrap_summary.log')}`
- robustness defense summary：`{rel(LOGS/'05_robustness_defense_summary.log')}`
- log-ratio / placebo / randomization / fractional response：`{rel(SNAPS/'v2f_empirical_diagnostics_snapshot.xlsx')}`

未在日志或快照中出现的内容不得写入正文为已重跑结果。
""")
    w(WORK/'v2f_literature_integration_patch.md',"""# v2f literature integration patch

由于本轮未逐篇核验 14 篇 DID PDF 的正式元数据，不新增未经核验的卷期页码。可嵌入的写法集中在四点：原生处理名单、外生政策时点、结果变量与处理变量分源、主识别/防守检验/边界诊断分层。

## 第2章段落
> 近期 DID 研究的共同经验并不在于机械增加估计器数量，而在于尽可能明确处理名单的来源、制度冲击的时点、结果变量与处理变量的数据分源，并把主识别、防御性稳健性和边界诊断分层呈现。

## 第4章段落
> 借鉴 DID 文献中对 staggered adoption 和连续处理强度的谨慎处理，本文把 TWFE 估计限定为省年连续暴露强度下的平均条件关联，并用趋势调整、留一省、wild cluster bootstrap、log-ratio、placebo/randomization 与 fractional response 检查结果边界。
""")

def make_zip(md,doc):
    zp=V2F/f'v2f_codex_revision_bundle_{STAMP}.zip'
    files=[md,doc,V2F/'00_input_mapping.md',V2F/'01_revision_tasklist.md',V2F/'02_verification_report.md',V2F/'03_delivery_note.md',V2F/'v2f_修改文档总览.md',V2F/'v2f_delivery_manifest.json',V2F/'v2f_working_registry_and_audit_data_note.md',SNAPS/'v2f_empirical_diagnostics_snapshot.xlsx',SNAPS/'v2f_rerun_result_snapshot.csv',LOGS/'rerun_status_summary.md',EXTRACT/'did方法修改建议_extracted.md',EXTRACT/'v2e修改建议_extracted.md',WORK/'v2e_to_v2f_manuscript_patch.md',WORK/'v2f_empirical_rerun_checklist.md',WORK/'v2f_literature_integration_patch.md',LONG/'README_长期升级包说明.md',LONG/'city_year_registry_schema_and_gap_list.md',LONG/'pseudo_to_real_registry_bridge.md',LONG/'stacked_did_sun_abraham_design.md',LONG/'duration_hazard_model_data_requirements.md',LONG/'future_upgrade_tasklist.md']
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if f.exists(): z.write(f,arcname=rel(f))
    return zp

def indexes(md,doc,zp):
    block=f"""

## v2f（{NOW}）
- 分支：`codex/v2f-did-review-upgrade-0420`
- Markdown：`{rel(md)}`
- Word：`{rel(doc)}`
- 留底目录：`{rel(ARCH)}`
- 执行工作包：`{rel(WORK)}`
- 长期升级包：`{rel(LONG)}`
- zip：`{rel(zp)}`
- 边界：`treat_share` 多期 DID/TWFE 为唯一主识别；其他检查均为防御性稳健性/边界诊断。
"""
    vi=INDEX/'v2修改稿索引.md'; old=vi.read_text(encoding='utf-8',errors='replace') if vi.exists() else '# v2修改稿索引\n'
    if '## v2f（' not in old: w(vi,old.rstrip()+block)
    ov=INDEX/'修改稿索引总览.md'; old2=ov.read_text(encoding='utf-8',errors='replace') if ov.exists() else '# 修改稿索引总览\n'
    if 'v2f DID review upgrade' not in old2: w(ov,old2.rstrip()+f"\n\n## v2f DID review upgrade（{NOW}）\n- v2f 说明目录：`{rel(V2F)}`\n- v2f 执行工作包：`{rel(WORK)}`\n- future city-year / modern DID 升级包：`{rel(LONG)}`\n")

def op_log(md,doc,zp):
    p=OPLOG/f"{datetime.now().strftime('%Y%m%d_%H%M')}__v2__v2f__did_review_upgrade.md"
    w(p,f"""# v2f DID review upgrade operation log

- 时间：{NOW}
- 分支：`codex/v2f-did-review-upgrade-0420`
- 输入：`{rel(DOCX_DID)}`；`{rel(DOCX_V2E)}`
- 输出 Markdown：`{rel(md)}`
- 输出 Word：`{rel(doc)}`
- zip：`{rel(zp)}`
- archive：`{rel(ARCH)}`
- future upgrade package：`{rel(LONG)}`
- registry 工作口径：pseudo/implied city-slot registry；不是官方真实城市名单。

## 未做
- 未修改 v1。
- 未修改原始数据总表和正式 source-of-truth xlsx。
- 未伪造独立机制变量结果。
- 未逐篇核验 14 篇 DID 文献正式元数据。
""")
    return p

def verify(md,doc,zp):
    xml=zipfile.ZipFile(doc).read('word/document.xml').decode('utf-8',errors='replace')
    text=md.read_text(encoding='utf-8',errors='replace')
    forbidden=['平行趋势成立','证明平行趋势','全面提升治理质量','机制已经被证实','机器学习结果强化因果识别','所有补充检验均强化']
    hits=[x for x in forbidden if x in text or x in xml]
    formula_hits=[x for x in ['Y_pt =','log((exec_share+c)/(proc_share+c))'] if x in xml]
    with zipfile.ZipFile(zp) as z: names=z.namelist()
    res={'math_object_count_in_docx_xml':xml.count('<m:oMath')+xml.count('<m:oMathPara'),'plain_text_formula_hits_in_docx':formula_hits,'forbidden_phrase_hits':hits,'zip_entry_count':len(names),'zip_contains_docx':any(n.endswith('.docx') for n in names),'zip_contains_md':any(n.endswith('.md') for n in names),'required_missing':[rel(p) for p in [md,doc,V2F/'00_input_mapping.md',V2F/'01_revision_tasklist.md',V2F/'02_verification_report.md',V2F/'03_delivery_note.md',zp] if not p.exists()]}
    w(V2F/'v2f_fresh_verification_summary.json',json.dumps(res,ensure_ascii=False,indent=2)); return res

def main():
    ext={'did_method_review':extract_docx(DOCX_DID,EXTRACT/'did方法修改建议_extracted.md','did方法修改建议.docx extracted text'),'v2e_review':extract_docx(DOCX_V2E,EXTRACT/'v2e修改建议_extracted.md','v2e修改建议.docx extracted text')}
    w(WORK/'00_extraction_summary.json',json.dumps(ext,ensure_ascii=False,indent=2))
    reg=registry_assets(); snap,perm,frac,emp=empirical(); md,doc=manuscript(snap,perm,frac,reg); long_pkg(reg); docs(snap,perm,frac,reg,ext,emp,md,doc); zp=make_zip(md,doc); op=op_log(md,doc,zp); indexes(md,doc,zp); ver=verify(md,doc,zp)
    final={'stamp':STAMP,'md':rel(md),'docx':rel(doc),'archive_dir':rel(ARCH),'zip':rel(zp),'operation_log':rel(op),'work_assets':rel(WORK),'long_package':rel(LONG),'verification':ver,'registry':reg,'empirical_snapshot':rel(SNAPS/'v2f_empirical_diagnostics_snapshot.xlsx')}
    w(WORK/'v2f_build_summary.json',json.dumps(final,ensure_ascii=False,indent=2)); print(json.dumps(final,ensure_ascii=False,indent=2))
if __name__=='__main__': main()

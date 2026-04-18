
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from scipy.stats import gaussian_kde
from matplotlib.lines import Line2D
from pathlib import Path
import json, math
from PIL import Image, ImageDraw

sns.set_theme(style='white')
plt.rcParams['font.family'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

COLORS = {
    'blue':'#4C667A','red':'#8C5A5A','grey':'#7F8790','lightblue':'#A7B7C7',
    'lightred':'#D3B4B4','dark':'#2F3540','green':'#6B8F71','orange':'#C48A3A'
}
dep_map = {
    'ppp_quality_zindex':'Quality Z',
    'ppp_quality_pca_rebuilt':'Quality PCA',
    'ppp_quality_pca_rebuilt_fixed':'Quality PCA fixed',
    'exec_share':'Execution share','proc_share':'Procurement share','prep_share':'Preparation share',
    'fiscal_pass_rate':'Fiscal pass','vfm_pass_rate':'VFM pass'
}
did_map = {'did_intensity':'DID intensity', 'did_any':'DID any', 'treat_share':'Treat share'}
spec_order = ['L1_fullsample_outcome_treatment','L2_lagged_controls','L3A_drop_2014_2022','L3B_drop_special_regions','L3C_doccount_ge_3']
spec_label = {
    'L1_fullsample_outcome_treatment':'Baseline set','L2_lagged_controls':'Lagged controls',
    'L3A_drop_2014_2022':'Drop edge years','L3B_drop_special_regions':'Drop special regions','L3C_doccount_ge_3':'Doc count ≥ 3'
}

base = Path(__file__).resolve().parents[1]
inp = base / 'input_data'
out = base / 'charts_regenerated'
out.mkdir(exist_ok=True)

rob_all = pd.read_excel(inp/'robustness.xlsx', sheet_name='全部稳健性结果')
rob_summary = pd.read_excel(inp/'robustness.xlsx', sheet_name='主规格摘要')
psm_balance = pd.read_excel(inp/'psm.xlsx', sheet_name='匹配前后平衡性')
psm_did = pd.read_excel(inp/'psm.xlsx', sheet_name='匹配后DID结果')
psm_support = pd.read_excel(inp/'psm.xlsx', sheet_name='共同支撑样本')
iv_candidates = pd.read_excel(inp/'iv.xlsx', sheet_name='候选IV筛查')
dml_summary = pd.read_excel(inp/'dml.xlsx', sheet_name='DML结果汇总')
dml_fold_pca = pd.read_excel(inp/'dml.xlsx', sheet_name='fold_ppp_quality_pca_rebu')
dml_fold_exec = pd.read_excel(inp/'dml.xlsx', sheet_name='fold_exec_share')
dml_fold_proc = pd.read_excel(inp/'dml.xlsx', sheet_name='fold_proc_share')
baseline_long = pd.read_excel(inp/'baseline.xlsx', sheet_name='正式回归结果长表')

rob_all['dep_label'] = rob_all['depvar'].map(dep_map).fillna(rob_all['depvar'])
rob_all['did_label'] = rob_all['did_var'].map(did_map).fillna(rob_all['did_var'])
rob_all['spec_label'] = rob_all['spec'].map(spec_label).fillna(rob_all['spec'])
rob_all['neglog10p'] = -np.log10(np.clip(rob_all['p'],1e-12,1))
rob_all['sign'] = np.where(rob_all['coef']>=0,'Positive','Negative')
rob_all['sig'] = rob_all['p']<0.1
x_order = [spec_label[s] for s in spec_order]
y_order = [dep_map[k] for k in ['exec_share','proc_share','prep_share','ppp_quality_pca_rebuilt','ppp_quality_zindex']]

# replicate charts (same logic as bundle creation)
# 8_1
fig, ax = plt.subplots(figsize=(11,6.5))
plot_df = rob_all.copy(); x_pos={x:i for i,x in enumerate(x_order)}; y_pos={y:i for i,y in enumerate(y_order[::-1])}
markers={'DID intensity':'o','DID any':'s','Treat share':'D'}
for did, mk in markers.items():
    sub=plot_df[plot_df['did_label']==did]
    sizes = 80 + 350*np.minimum(np.abs(sub['coef'])/sub['coef'].abs().max(),1)
    colors = [COLORS['blue'] if c>=0 else COLORS['red'] for c in sub['coef']]
    edge = ['black' if s else 'white' for s in sub['sig']]
    ax.scatter([x_pos[s] for s in sub['spec_label']], [y_pos[y] for y in sub['dep_label']],
               s=sizes, c=colors, marker=mk, edgecolors=edge, linewidths=1, alpha=0.9)
ax.set_xticks(range(len(x_order))); ax.set_xticklabels(x_order, rotation=20, ha='right'); ax.set_yticks(range(len(y_order))); ax.set_yticklabels(list(y_order[::-1]))
ax.set_title('Figure 8-1. Robustness architecture map', fontsize=14, weight='bold'); ax.set_xlabel('Robustness specification family'); ax.set_ylabel('Outcome')
for spine in ax.spines.values(): spine.set_visible(False); ax.grid(False)
legend_elements=[Line2D([0],[0], marker='o', color='w', label='DID intensity', markerfacecolor=COLORS['grey'], markersize=8),
                 Line2D([0],[0], marker='s', color='w', label='DID any', markerfacecolor=COLORS['grey'], markersize=8),
                 Line2D([0],[0], marker='D', color='w', label='Treat share', markerfacecolor=COLORS['grey'], markersize=8),
                 Line2D([0],[0], marker='o', color='w', label='Positive coef', markerfacecolor=COLORS['blue'], markersize=8),
                 Line2D([0],[0], marker='o', color='w', label='Negative coef', markerfacecolor=COLORS['red'], markersize=8),
                 Line2D([0],[0], marker='o', color='w', label='p < 0.10', markerfacecolor=COLORS['grey'], markeredgecolor='black', markersize=8)]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02,1), frameon=False)
fig.tight_layout(); [fig.savefig(out/f'Figure_8_1_robustness_architecture_map.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_2
fig, ax = plt.subplots(figsize=(10,6.5))
for dep, sub in rob_all.groupby('dep_label'):
    ax.scatter(sub['coef'], sub['neglog10p'], s=40 + 0.4*sub['N'], label=dep, alpha=.8)
for _, r in rob_all.sort_values('neglog10p', ascending=False).head(8).iterrows():
    ax.text(r['coef'], r['neglog10p']+0.03, f"{r['dep_label']}|{r['did_label']}", fontsize=7)
ax.axvline(0, color='grey', lw=1); ax.axhline(-np.log10(0.1), color=COLORS['grey'], lw=1, ls='--')
ax.set_title('Figure 8-2. Effect-significance frontier across robustness checks', fontsize=14, weight='bold')
ax.set_xlabel('Estimated coefficient'); ax.set_ylabel('-log10(p-value)'); ax.legend(frameon=False, bbox_to_anchor=(1.02,1), loc='upper left')
for spine in ax.spines.values(): spine.set_visible(False)
fig.tight_layout(); [fig.savefig(out/f'Figure_8_2_effect_significance_frontier.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_3
key = rob_all[(rob_all['did_var']=='treat_share') & (rob_all['depvar'].isin(['exec_share','proc_share','ppp_quality_pca_rebuilt']))].copy()
key['spec_label'] = pd.Categorical(key['spec_label'], categories=x_order, ordered=True)
fig, axes = plt.subplots(1,3, figsize=(14,4), sharex=True)
for ax, dep in zip(axes, ['exec_share','proc_share','ppp_quality_pca_rebuilt']):
    sub=key[key['depvar']==dep].sort_values('spec_label'); x=np.arange(len(sub))
    ax.plot(x, sub['coef'], color=COLORS['dark'], lw=1.8)
    ax.scatter(x, sub['coef'], c=[COLORS['blue'] if c>=0 else COLORS['red'] for c in sub['coef']], s=70)
    ax.axhline(0, color='grey', lw=1); ax.set_xticks(x); ax.set_xticklabels(sub['spec_label'], rotation=25, ha='right', fontsize=8); ax.set_title(dep_map[dep], fontsize=11)
    for xi, (_, r) in enumerate(sub.iterrows()):
        ax.plot([xi,xi],[r['coef']-1.96*r['se'], r['coef']+1.96*r['se']], color=COLORS['grey'], lw=1)
    for spine in ax.spines.values(): spine.set_visible(False)
axes[0].set_ylabel('Coefficient')
fig.suptitle('Figure 8-3. Treat-share stability for key outcomes', fontsize=14, weight='bold', y=1.02)
fig.tight_layout(); [fig.savefig(out/f'Figure_8_3_treatshare_stability_panels.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_4
bal=psm_balance.copy(); bal['abs_before']=bal['smd_before'].abs(); bal['abs_after']=bal['smd_after'].abs(); bal=bal.sort_values('abs_before')
fig, ax = plt.subplots(figsize=(10,6)); y=np.arange(len(bal))
ax.hlines(y, bal['abs_after'], bal['abs_before'], color=COLORS['lightblue'], lw=2)
ax.scatter(bal['abs_before'], y, color=COLORS['red'], label='Before matching', s=45)
ax.scatter(bal['abs_after'], y, color=COLORS['blue'], label='After matching', s=45)
ax.axvline(0.1, color=COLORS['grey'], ls='--', lw=1)
ax.set_yticks(y); ax.set_yticklabels(bal['variable']); ax.set_xlabel('Absolute standardized mean difference')
ax.set_title('Figure 8-4. Balance improvement after matching (Love plot)', fontsize=14, weight='bold')
ax.legend(frameon=False, loc='lower right'); [spine.set_visible(False) for spine in ax.spines.values()]
fig.tight_layout(); [fig.savefig(out/f'Figure_8_4_psm_love_plot.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_5
fig, ax = plt.subplots(figsize=(10,5))
for grp, color, sign in [(1,COLORS['blue'],1),(0,COLORS['red'],-1)]:
    sub=psm_support[psm_support['did_any']==grp]['pscore'].dropna()
    kde=gaussian_kde(sub); xs=np.linspace(sub.min(), sub.max(), 200); ys=kde(xs)
    ax.fill_between(xs, 0, sign*ys, color=color, alpha=0.35); ax.plot(xs, sign*ys, color=color, lw=2, label='Treated' if grp==1 else 'Control')
ax.axhline(0, color='grey', lw=1); ax.set_yticks([]); ax.set_xlabel('Propensity score')
ax.set_title('Figure 8-5. Common support in matched sample', fontsize=14, weight='bold')
ax.legend(frameon=False, loc='upper center', ncol=2); [spine.set_visible(False) for spine in ax.spines.values()]
fig.tight_layout(); [fig.savefig(out/f'Figure_8_5_common_support_mirror_density.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_6
base_any = baseline_long[baseline_long['did_var']=='did_any'][['depvar','coef','se','p']].copy().rename(columns={'coef':'coef_base','se':'se_base','p':'p_base'})
comp = psm_did.merge(base_any, left_on='outcome', right_on='depvar', how='left'); comp['label'] = comp['outcome'].map(dep_map); comp = comp[comp['label'].notna()].sort_values('coef')
fig, ax = plt.subplots(figsize=(10,5)); y=np.arange(len(comp))
ax.hlines(y, comp['coef_base'], comp['coef'], color=COLORS['lightblue'], lw=2)
ax.scatter(comp['coef_base'], y, color=COLORS['grey'], s=55, label='Baseline DID (did_any)')
ax.scatter(comp['coef'], y, color=COLORS['blue'], s=55, label='Matched-sample DID')
ax.axvline(0, color='grey', lw=1); ax.set_yticks(y); ax.set_yticklabels(comp['label']); ax.set_xlabel('Coefficient')
ax.set_title('Figure 8-6. Baseline vs matched-sample DID', fontsize=14, weight='bold')
ax.legend(frameon=False, loc='lower right'); [spine.set_visible(False) for spine in ax.spines.values()]
fig.tight_layout(); [fig.savefig(out/f'Figure_8_6_matched_vs_baseline_dumbbell.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_7
iv=iv_candidates.copy(); iv['max_direct_corr']=iv[['corr_with_pca_quality','corr_with_exec_share','corr_with_proc_share']].abs().max(axis=1)
fig, ax = plt.subplots(figsize=(9,6)); colors=[COLORS['red'] if s=='不建议' else COLORS['blue'] for s in iv['screening']]
ax.scatter(iv['corr_with_treat_share'], iv['max_direct_corr'], s=120, c=colors, alpha=0.85)
for _, r in iv.iterrows(): ax.text(r['corr_with_treat_share']+0.005, r['max_direct_corr']+0.003, r['candidate_iv'], fontsize=8)
ax.set_xlabel('Relevance with treatment (corr with treat_share)'); ax.set_ylabel('Exclusion risk (max abs corr with outcomes)')
ax.set_title('Figure 8-7. IV candidate screening quadrant', fontsize=14, weight='bold')
ax.axvline(0.5, color=COLORS['grey'], ls='--', lw=1); ax.axhline(0.1, color=COLORS['grey'], ls='--', lw=1)
[spine.set_visible(False) for spine in ax.spines.values()]
fig.tight_layout(); [fig.savefig(out/f'Figure_8_7_iv_candidate_quadrant.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_8
iv_long = iv.melt(id_vars=['candidate_iv','screening'], value_vars=['corr_with_treat_share','corr_with_pca_quality','corr_with_exec_share','corr_with_proc_share'], var_name='metric', value_name='corr')
metric_order=['corr_with_treat_share','corr_with_pca_quality','corr_with_exec_share','corr_with_proc_share']
metric_label={'corr_with_treat_share':'With treatment','corr_with_pca_quality':'With quality PCA','corr_with_exec_share':'With exec share','corr_with_proc_share':'With proc share'}
fig, axes = plt.subplots(1,4, figsize=(15,4), sharey=True)
for ax, met in zip(axes, metric_order):
    sub=iv_long[iv_long['metric']==met].sort_values('corr'); y=np.arange(len(sub))
    ax.hlines(y, 0, sub['corr'], color=[COLORS['blue'] if c>=0 else COLORS['red'] for c in sub['corr']], lw=3)
    ax.scatter(sub['corr'], y, color=[COLORS['blue'] if c>=0 else COLORS['red'] for c in sub['corr']], s=50)
    ax.axvline(0, color='grey', lw=1); ax.set_title(metric_label[met], fontsize=10); ax.set_xlabel('Correlation')
    if ax is axes[0]: ax.set_yticks(y); ax.set_yticklabels(sub['candidate_iv'])
    else: ax.set_yticks(y); ax.set_yticklabels([])
    [spine.set_visible(False) for spine in ax.spines.values()]
fig.suptitle('Figure 8-8. Candidate IV correlation profiles', fontsize=14, weight='bold', y=1.04)
fig.tight_layout(); [fig.savefig(out/f'Figure_8_8_iv_candidate_profiles.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_9
base_treat = baseline_long[baseline_long['did_var']=='treat_share'][['depvar','coef','se','p']].copy().rename(columns={'coef':'coef_base','se':'se_base','p':'p_base'})
dml = dml_summary.copy(); dml['depvar']=dml['outcome'].replace({'ppp_quality_pca_rebuilt_fixed':'ppp_quality_pca_rebuilt'})
comp2 = dml.merge(base_treat, on='depvar', how='left'); comp2['label']=comp2['depvar'].map(dep_map)
fig, ax = plt.subplots(figsize=(9,4.5)); y=np.arange(len(comp2))
ax.hlines(y, comp2['coef_base'], comp2['theta_dml'], color=COLORS['lightblue'], lw=2)
ax.scatter(comp2['coef_base'], y, color=COLORS['grey'], s=55, label='Baseline TWFE (treat_share)')
ax.scatter(comp2['theta_dml'], y, color=COLORS['green'], s=55, label='DML estimate')
ax.axvline(0, color='grey', lw=1); ax.set_yticks(y); ax.set_yticklabels(comp2['label']); ax.set_xlabel('Coefficient')
ax.set_title('Figure 8-9. Baseline vs DML estimates', fontsize=14, weight='bold')
ax.legend(frameon=False, loc='lower right'); [spine.set_visible(False) for spine in ax.spines.values()]
fig.tight_layout(); [fig.savefig(out/f'Figure_8_9_dml_vs_baseline_dumbbell.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_10
folds = {'Quality PCA fixed':dml_fold_pca, 'Execution share':dml_fold_exec, 'Procurement share':dml_fold_proc}
fig, axes = plt.subplots(2,3, figsize=(14,7), sharex='col')
for col,(title, df) in enumerate(folds.items()):
    ax=axes[0,col]; ax.plot(df['fold'], df['alpha_y'], marker='o', color=COLORS['blue'], label='alpha_y'); ax.plot(df['fold'], df['alpha_d'], marker='s', color=COLORS['red'], label='alpha_d'); ax.set_title(title, fontsize=11)
    if col==0: ax.set_ylabel('Penalty parameter'); [spine.set_visible(False) for spine in ax.spines.values()]; ax.legend(frameon=False, fontsize=8)
    ax=axes[1,col]; ax.plot(df['fold'], df['nonzero_y'], marker='o', color=COLORS['blue'], label='nonzero_y'); ax.plot(df['fold'], df['nonzero_d'], marker='s', color=COLORS['red'], label='nonzero_d'); ax.set_xlabel('Fold')
    if col==0: ax.set_ylabel('Selected controls'); [spine.set_visible(False) for spine in ax.spines.values()]
fig.suptitle('Figure 8-10. DML cross-fitting diagnostics by fold', fontsize=14, weight='bold', y=1.02)
fig.tight_layout(); [fig.savefig(out/f'Figure_8_10_dml_fold_diagnostics.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

# 8_11
score = []
for dep in ['exec_share','proc_share','ppp_quality_pca_rebuilt']:
    for spec in spec_order:
        sub=rob_all[(rob_all['depvar']==dep)&(rob_all['did_var']=='treat_share')&(rob_all['spec']==spec)]
        if len(sub):
            r=sub.iloc[0]
            val=1 if (r['p']<0.1 and r['coef']>0) else (-1 if (r['p']<0.1 and r['coef']<0) else (0.25 if r['coef']>0 else -0.25))
            score.append({'row':dep_map[dep],'col':spec_label[spec],'value':val})
    dmldep = dep if dep!='ppp_quality_pca_rebuilt' else 'ppp_quality_pca_rebuilt_fixed'
    psmrow = psm_did[psm_did['outcome']==dep]
    if len(psmrow):
        r=psmrow.iloc[0]; val=1 if (r['p']<0.1 and r['coef']>0) else (-1 if (r['p']<0.1 and r['coef']<0) else (0.25 if r['coef']>0 else -0.25)); score.append({'row':dep_map[dep],'col':'Matched DID','value':val})
    dmrow = dml_summary[dml_summary['outcome']==dmldep]
    if len(dmrow):
        r=dmrow.iloc[0]; val=1 if (r['p']<0.1 and r['theta_dml']>0) else (-1 if (r['p']<0.1 and r['theta_dml']<0) else (0.25 if r['theta_dml']>0 else -0.25)); score.append({'row':dep_map[dep],'col':'DML','value':val})
score_df=pd.DataFrame(score)
pivot=score_df.pivot(index='row', columns='col', values='value').loc[[dep_map['exec_share'],dep_map['proc_share'],dep_map['ppp_quality_pca_rebuilt']], x_order+['Matched DID','DML']]
fig, ax = plt.subplots(figsize=(11,3.5)); cmap=sns.color_palette(["#A55D5D","#E7E7E7","#5C748A"], as_cmap=True)
sns.heatmap(pivot, cmap=cmap, center=0, cbar=False, linewidths=0.5, linecolor='white', annot=False, ax=ax)
for i,row in enumerate(pivot.index):
    for j,col in enumerate(pivot.columns):
        v=pivot.loc[row,col]; text='+' if v==1 else ('-' if v==-1 else ('(+)' if v>0 else '(-)')); ax.text(j+0.5, i+0.5, text, ha='center', va='center', fontsize=10, color='black')
ax.set_title('Figure 8-11. Robustness evidence scorecard', fontsize=14, weight='bold'); ax.set_xlabel('Specification / method'); ax.set_ylabel('')
plt.xticks(rotation=25, ha='right'); plt.yticks(rotation=0)
fig.tight_layout(); [fig.savefig(out/f'Figure_8_11_robustness_scorecard.{ext}', dpi=300, bbox_inches='tight') for ext in ['png','pdf','svg']]; plt.close(fig)

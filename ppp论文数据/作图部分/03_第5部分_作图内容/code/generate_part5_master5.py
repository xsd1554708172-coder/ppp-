
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
import statsmodels.api as sm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input_data")
OUT_DIR = os.path.join(BASE_DIR, "charts_regenerated")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style='white')

main_blue='#355C7D'
main_red='#7B3F46'
main_gray='#505050'
light_gray='#D9D9D9'
slate='#6C7A89'

panel = pd.read_csv(os.path.join(INPUT_DIR, 'part5_model_ready_panel.csv'))
timing = pd.read_excel(os.path.join(INPUT_DIR, 'part5_descriptive_diagnostics.xlsx'), sheet_name='省份处理时点')
res = pd.read_excel(os.path.join(INPUT_DIR, 'part5_baseline_did.xlsx'), sheet_name='正式回归结果长表')
dyn = pd.read_excel(os.path.join(INPUT_DIR, 'part5_event_study.xlsx'), sheet_name='动态系数长表')

# Figure 5-1: treatment timing panelview
years = sorted(panel.year.unique())
timing['sort_key'] = timing['first_treat_year'].fillna(9999)
timing = timing.sort_values(['sort_key', 'province'])
provinces = timing['province'].tolist()
status = pd.DataFrame(index=provinces, columns=years, dtype=float)
for p in provinces:
    sub = panel[panel.province == p]
    for y in years:
        ss = sub[sub.year == y]
        if ss.empty:
            status.loc[p, y] = np.nan
        else:
            ever = timing.loc[timing.province == p, 'ever_treated'].iloc[0]
            status.loc[p, y] = 2 if ever == 0 else float(ss.iloc[0]['did_any'])
doc_bar = panel.groupby('province')['ppp_doc_n'].sum().reindex(provinces)

fig = plt.figure(figsize=(12.8, 9.2))
gs = fig.add_gridspec(1, 2, width_ratios=[5.3, 1.2], wspace=0.05)
ax = fig.add_subplot(gs[0, 0]); axb = fig.add_subplot(gs[0, 1], sharey=ax)
cmap = ListedColormap(['#E6E6E6', main_blue, '#B8B8B8'])
norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)
sns.heatmap(status, ax=ax, cmap=cmap, norm=norm, cbar=False, mask=status.isna(), linewidths=0)
ax.set_xlabel('Year'); ax.set_ylabel('Province')
ax.set_title('Figure 5-1. Treatment timing and sample coverage', loc='left', fontsize=14, fontweight='bold', pad=10)
ax.tick_params(axis='x', labelrotation=0, labelsize=9); ax.tick_params(axis='y', labelsize=9)
axb.barh(np.arange(len(provinces)) + 0.5, doc_bar.values, color=slate, height=0.82)
axb.set_xlabel('PPP count', fontsize=10)
axb.tick_params(axis='x', labelsize=8); axb.tick_params(axis='y', left=False, labelleft=False)
for sp in ['top', 'right', 'left']: axb.spines[sp].set_visible(False)
for sp in ['top', 'right', 'left', 'bottom']: ax.spines[sp].set_visible(False)
legend = [
    plt.Line2D([0], [0], color='#E6E6E6', lw=8, label='Untreated'),
    plt.Line2D([0], [0], color=main_blue, lw=8, label='Treated'),
    plt.Line2D([0], [0], color='#B8B8B8', lw=8, label='Never treated')
]
ax.legend(handles=legend, frameon=False, ncol=3, bbox_to_anchor=(0, 1.04), loc='upper left')
fig.text(0.01, 0.01, 'Rows are provinces and columns are years; the right bar shows total PPP project counts by province.', fontsize=9, color=main_gray)
fig.tight_layout(rect=[0, 0.03, 1, 0.97])
for ext in ['png', 'pdf', 'svg']:
    fig.savefig(os.path.join(OUT_DIR, f'Figure_5_1_treatment_timing_panelview.{ext}'), dpi=300, bbox_inches='tight')
plt.close(fig)

# Figure 5-3: main results forest plot
res2 = res[res.did_var == 'treat_share'].copy()
order = ['exec_share', 'proc_share', 'prep_share', 'ppp_quality_pca_rebuilt', 'ppp_quality_zindex']
labels = {
    'exec_share': 'Execution share',
    'proc_share': 'Procurement share',
    'prep_share': 'Preparation share',
    'ppp_quality_pca_rebuilt': 'Governance quality (PCA rebuilt)',
    'ppp_quality_zindex': 'Governance quality (Z-index)'
}
res2 = res2[res2.depvar.isin(order)].copy()
res2['depvar'] = pd.Categorical(res2['depvar'], categories=order, ordered=True)
res2 = res2.sort_values('depvar')
res2['ci_low'] = res2['coef'] - 1.96 * res2['se']
res2['ci_high'] = res2['coef'] + 1.96 * res2['se']

fig, ax = plt.subplots(figsize=(8.8, 5.8))
y = np.arange(len(res2))
cols = [main_blue if c > 0 else main_red for c in res2['coef']]
ax.axvline(0, color=light_gray, lw=1.2)
for i, row in enumerate(res2.itertuples(index=False)):
    ax.plot([row.ci_low, row.ci_high], [i, i], color=cols[i], lw=2)
    ax.scatter(row.coef, i, s=52, color=cols[i], zorder=3)
    ax.text(row.ci_high + (res2['ci_high'].max() - res2['ci_low'].min()) * 0.03, i, f'{row.coef:.3f}', va='center', fontsize=9, color=main_gray)
ax.set_yticks(y)
ax.set_yticklabels([labels[d] for d in res2['depvar']])
ax.set_xlabel('Estimated coefficient of treat_share (95% CI)')
ax.set_title('Figure 5-3. Baseline DID estimates for core outcomes', loc='left', fontsize=14, fontweight='bold')
for sp in ['top', 'right', 'left']: ax.spines[sp].set_visible(False)
fig.text(0.01, 0.01, 'Dots indicate coefficients and horizontal lines indicate 95% confidence intervals.', fontsize=9, color=main_gray)
fig.tight_layout(rect=[0, 0.03, 1, 0.96])
for ext in ['png', 'pdf', 'svg']:
    fig.savefig(os.path.join(OUT_DIR, f'Figure_5_3_main_results_forest.{ext}'), dpi=300, bbox_inches='tight')
plt.close(fig)

# Figure 5-5: event-study triptych
fig, axes = plt.subplots(3, 1, figsize=(9.2, 9.4), sharex=True)
outcomes = ['exec_share', 'proc_share', 'ppp_quality_pca_rebuilt']
titles = {
    'exec_share': 'Execution share',
    'proc_share': 'Procurement share',
    'ppp_quality_pca_rebuilt': 'Governance quality (PCA rebuilt)'
}
for ax, outcome in zip(axes, outcomes):
    d = dyn[dyn.outcome == outcome].sort_values('event_bin')
    color = main_blue if outcome != 'proc_share' else main_red
    ax.axhline(0, color=light_gray, lw=1)
    ax.axvline(-0.01, color='#B0B0B0', lw=1, ls='--')
    ax.errorbar(
        d['event_bin'], d['coef'],
        yerr=[d['coef'] - d['ci_low_95'], d['ci_high_95'] - d['coef']],
        fmt='o-', color=color, ecolor=main_gray, elinewidth=1.1, capsize=3, markersize=4
    )
    ax.set_title(titles[outcome], loc='left', fontsize=12)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    ax.tick_params(labelsize=9)
axes[-1].set_xlabel('Event time')
fig.suptitle('Figure 5-5. Dynamic treatment effects (event study)', x=0.01, y=0.98, ha='left', fontsize=14, fontweight='bold')
fig.text(0.01, 0.01, 'The dashed vertical line marks treatment onset. These figures are used for dynamic display rather than as decisive proof of parallel trends.', fontsize=9, color=main_gray)
fig.tight_layout(rect=[0, 0.03, 1, 0.96])
for ext in ['png', 'pdf', 'svg']:
    fig.savefig(os.path.join(OUT_DIR, f'Figure_5_5_event_study_triptych.{ext}'), dpi=300, bbox_inches='tight')
plt.close(fig)

# Figure 5-8: placebo distribution
controls = ['dfi', 'digital_econ', 'base_station_density', 'software_gdp_share', 'it_service_gdp_share', 'ln_rd_expenditure', 'ln_tech_contract_value', 'ln_patent_grants']
placebo = pd.read_csv(os.path.join(INPUT_DIR, 'part5_placebo_coefficients_generated.csv'))['placebo_coef'].values
dfp = panel[['province', 'year', 'exec_share', 'did_intensity'] + controls].dropna().copy()

def build_X(df, treat_col):
    X = df[[treat_col] + controls].copy()
    X = pd.concat([
        X,
        pd.get_dummies(df['province'], prefix='prov', drop_first=True),
        pd.get_dummies(df['year'].astype(str), prefix='year', drop_first=True)
    ], axis=1)
    X = sm.add_constant(X, has_constant='add')
    return X.astype(float)

X_actual = build_X(dfp, 'did_intensity')
actual_fit = sm.OLS(dfp['exec_share'].astype(float), X_actual).fit()
actual_coef = actual_fit.params['did_intensity']

fig, ax = plt.subplots(figsize=(8.5, 5.4))
sns.histplot(placebo, bins=32, stat='density', color=slate, alpha=0.45, edgecolor='white', ax=ax)
sns.kdeplot(placebo, color=main_blue, lw=2, ax=ax)
ax.axvline(actual_coef, color=main_red, lw=2.4)
ax.text(actual_coef, ax.get_ylim()[1] * 0.95, f'Actual coef = {actual_coef:.3f}', color=main_red, ha='left', va='top', fontsize=10)
ax.set_xlabel('Placebo coefficient (exec_share)')
ax.set_ylabel('Density')
ax.set_title('Figure 5-8. Placebo distribution', loc='left', fontsize=14, fontweight='bold')
for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
fig.text(0.01, 0.01, 'Treatment onset is randomly reassigned while preserving the treatment-timing distribution; the vertical line shows the observed coefficient.', fontsize=9, color=main_gray)
fig.tight_layout(rect=[0, 0.03, 1, 0.96])
for ext in ['png', 'pdf', 'svg']:
    fig.savefig(os.path.join(OUT_DIR, f'Figure_5_8_placebo_distribution.{ext}'), dpi=300, bbox_inches='tight')
plt.close(fig)

# Figure 5-10: project progress state space
yr = panel.groupby('year').agg(exec_share=('exec_share', 'mean'), proc_share=('proc_share', 'mean'), prep_share=('prep_share', 'mean')).reset_index()
fig, ax = plt.subplots(figsize=(8.8, 6.4))
sizes = 300 + (yr['prep_share'] - yr['prep_share'].min()) / (yr['prep_share'].max() - yr['prep_share'].min() + 1e-9) * 700
sc = ax.scatter(yr['proc_share'], yr['exec_share'], s=sizes, c=yr['year'], cmap='Blues', alpha=0.88, edgecolor='white', linewidth=0.9)
ax.plot(yr['proc_share'], yr['exec_share'], color=light_gray, lw=1.2, zorder=0)
for _, r in yr.iterrows():
    ax.text(r['proc_share'] + 0.004, r['exec_share'] + 0.003, str(int(r['year'])), fontsize=8, color=main_gray)
ax.set_xlabel('Procurement-stage share')
ax.set_ylabel('Execution-stage share')
ax.set_title('Figure 5-10. Project progress state transition', loc='left', fontsize=14, fontweight='bold')
for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Year', fontsize=10)
fig.text(0.01, 0.01, 'Point size indicates the preparation-stage share; the line connects yearly means in the procurement–execution state space.', fontsize=9, color=main_gray)
fig.tight_layout(rect=[0, 0.03, 1, 0.96])
for ext in ['png', 'pdf', 'svg']:
    fig.savefig(os.path.join(OUT_DIR, f'Figure_5_10_project_progress_state_space.{ext}'), dpi=300, bbox_inches='tight')
plt.close(fig)

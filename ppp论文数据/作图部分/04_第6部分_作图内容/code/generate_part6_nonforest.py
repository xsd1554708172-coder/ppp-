
import os, json
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, PathPatch
from matplotlib.path import Path
import matplotlib as mpl

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT = os.path.join(BASE_DIR, "input_data")
OUT = os.path.join(BASE_DIR, "charts_regenerated")
os.makedirs(OUT, exist_ok=True)

POS='#3E5C76'; NEG='#8C3B3B'; LIGHT='#D9D9D9'; MID='#8AA1B1'; DARK='#2B3A42'
mpl.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','axes.edgecolor':'#333333',
                     'axes.labelcolor':'#222222','xtick.color':'#222222','ytick.color':'#222222',
                     'font.size':11,'axes.grid':False})

stage1=pd.read_excel(os.path.join(INPUT,'part6_main_mechanism.xlsx'),sheet_name='一阶段机制回归')
summary=pd.read_excel(os.path.join(INPUT,'part6_main_mechanism.xlsx'),sheet_name='主规格摘要')
chain=pd.read_excel(os.path.join(INPUT,'part6_chain_mechanism.xlsx'),sheet_name='链式步骤回归')
chain_out=pd.read_excel(os.path.join(INPUT,'part6_chain_mechanism.xlsx'),sheet_name='结果方程_含ABC')
boot=pd.read_excel(os.path.join(INPUT,'part6_strict_mediation_bootstrap.xlsx'),sheet_name='Sobel_OriginalBootstrap')
base_did=pd.read_excel(os.path.join(INPUT,'part5_baseline_did.xlsx'),sheet_name='正式回归结果长表')

def save_all(fig, stem):
    for ext in ['png','pdf','svg']:
        fig.savefig(os.path.join(OUT, f'{stem}.{ext}'), dpi=300 if ext=='png' else None, bbox_inches='tight')
    plt.close(fig)

# shared tables
stage1_ts=stage1[stage1.did_var=='treat_share'].set_index('mediator')
chain_fix=chain_out.copy()
outs=['exec_share','proc_share','ppp_quality_pca_rebuilt_fixed']

# Figure 6A path diagram
fig, ax = plt.subplots(figsize=(10,6))
ax.axis('off')
nodes = {'Treat': (0.08,0.5),'A_idx': (0.38,0.75),'B_idx': (0.38,0.50),'C_idx': (0.38,0.25),
         'exec_share': (0.78,0.72),'proc_share': (0.78,0.50),'pca_quality': (0.78,0.28)}
for n,(x,y) in nodes.items():
    ax.add_patch(Circle((x,y), 0.055, facecolor='white', edgecolor=DARK, lw=1.8))
    ax.text(x,y,n.replace('_','\n'),ha='center',va='center',fontsize=10)
path_specs=[('Treat','A_idx',stage1_ts.loc['A_idx','coef_did'], stage1_ts.loc['A_idx','p_did']),
            ('Treat','B_idx',stage1_ts.loc['B_idx','coef_did'], stage1_ts.loc['B_idx','p_did']),
            ('Treat','C_idx',stage1_ts.loc['C_idx','coef_did'], stage1_ts.loc['C_idx','p_did'])]
for out_key,out_name in [('exec_share','exec_share'),('proc_share','proc_share'),('pca_quality','ppp_quality_pca_rebuilt_fixed')]:
    tmp=chain_fix[chain_fix.outcome==out_name].set_index('key_var')
    for med in ['A_idx','B_idx','C_idx']:
        path_specs.append((med,out_key,tmp.loc[med,'coef'],tmp.loc[med,'p']))
    path_specs.append(('Treat', out_key, tmp.loc['treat_share','coef'], tmp.loc['treat_share','p']))
maxcoef=max(abs(p[2]) for p in path_specs)
for s,t,coef,p in path_specs:
    color = POS if coef>=0 else NEG
    alpha = 0.85 if p<0.1 else 0.35
    lw = 1.5 + min(4, abs(coef)/maxcoef*4)
    style='solid' if p<0.1 else (0,(3,3))
    arrow = FancyArrowPatch(nodes[s], nodes[t], arrowstyle='-|>', mutation_scale=12,
                            connectionstyle="arc3,rad=0.0", linewidth=lw,
                            linestyle=style, color=color, alpha=alpha)
    ax.add_patch(arrow)
    mx=(nodes[s][0]+nodes[t][0])/2; my=(nodes[s][1]+nodes[t][1])/2
    ax.text(mx, my+0.03, f'{coef:.2f}', fontsize=9, color=color, ha='center')
ax.text(0.02,0.95,'Mechanism path summary',fontsize=15,fontweight='bold',ha='left')
ax.text(0.02,0.91,'Solid = p<0.10; dashed = unstable path',fontsize=10,color='#555555',ha='left')
save_all(fig,'Figure_6A_mechanism_path_diagram')

# Figure 6B flow alluvial
fig, ax = plt.subplots(figsize=(11,6))
ax.axis('off')
left_nodes=['Treat']; mid_nodes=['A_idx','B_idx','C_idx']; right_nodes=['exec_share','proc_share','pca_quality']
x_left,x_mid,x_right=0.08,0.45,0.82
y_left=[0.5]; y_mid=[0.75,0.5,0.25]; y_right=[0.72,0.50,0.28]
for x, ys, labels in [(x_left,y_left,left_nodes),(x_mid,y_mid,mid_nodes),(x_right,y_right,right_nodes)]:
    for y,lbl in zip(ys,labels):
        ax.add_patch(Rectangle((x-0.04,y-0.045),0.08,0.09,facecolor='white',edgecolor=DARK,lw=1.5))
        ax.text(x,y,lbl.replace('_','\n'),ha='center',va='center',fontsize=10)
flows=[]
for med in mid_nodes:
    coef=stage1_ts.loc[med,'coef_did']; p=stage1_ts.loc[med,'p_did']
    flows.append((x_left,0.5,x_mid,y_mid[mid_nodes.index(med)],coef,p))
for out_key,out_name in [('exec_share','exec_share'),('proc_share','proc_share'),('pca_quality','ppp_quality_pca_rebuilt_fixed')]:
    tmp=chain_fix[chain_fix.outcome==out_name].set_index('key_var')
    for med in mid_nodes:
        coef=tmp.loc[med,'coef']; p=tmp.loc[med,'p']
        flows.append((x_mid,y_mid[mid_nodes.index(med)],x_right,y_right[right_nodes.index(out_key)],coef,p))
maxcoef=max(abs(f[4]) for f in flows)
def flow_patch(x0,y0,x1,y1,width,color,alpha=0.6):
    dx=(x1-x0)*0.45
    verts=[(x0,y0+width/2),(x0+dx,y0+width/2),(x1-dx,y1+width/2),(x1,y1+width/2),
           (x1,y1-width/2),(x1-dx,y1-width/2),(x0+dx,y0-width/2),(x0,y0-width/2),(x0,y0+width/2)]
    codes=[Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.LINETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.CLOSEPOLY]
    return PathPatch(Path(verts,codes), facecolor=color, edgecolor='none', alpha=alpha)
for x0,y0,x1,y1,coef,p in flows:
    color=POS if coef>=0 else NEG
    width=0.012 + 0.04*abs(coef)/maxcoef
    alpha=0.75 if p<0.1 else 0.25
    ax.add_patch(flow_patch(x0+0.04,y0,x1-0.04,y1,width,color,alpha))
ax.text(0.02,0.95,'Mechanism flow from treatment to mediators to outcomes',fontsize=15,fontweight='bold')
ax.text(0.02,0.91,'Flow width ∝ absolute coefficient; faded flows are statistically unstable',fontsize=10,color='#555555')
save_all(fig,'Figure_6B_mechanism_flow_alluvial')

# Figure 6C waterfall
fig, axes = plt.subplots(1,3,figsize=(13,4))
for ax, (_,row) in zip(axes, boot.iterrows()):
    total=row['direct']+row['indirect']
    vals=[row['direct'], row['indirect']]
    labels=['Direct','Indirect']
    basev=0
    for i,(v,lbl) in enumerate(zip(vals,labels), start=1):
        c=POS if v>=0 else NEG
        ax.bar(i, v, bottom=basev if v>=0 else basev+v, color=c, width=0.6)
        ax.text(i, basev+v+(0.02 if v>=0 else -0.02), f'{v:.2f}', ha='center', va='bottom' if v>=0 else 'top', fontsize=9)
        basev += v
    ax.scatter(3,total,color=DARK,s=50)
    ax.text(3,total, f' total {total:.2f}', ha='left', va='center', fontsize=9)
    ax.axhline(0,color='#666666',lw=1)
    ax.set_xticks([1,2,3], ['Direct','Indirect','Total'])
    ax.set_title(str(row['outcome']).replace('_fixed',''), fontsize=11)
fig.suptitle('Direct and indirect effect decomposition',fontsize=15,fontweight='bold',y=1.03)
save_all(fig,'Figure_6C_decomposition_waterfall')

# Figure 6D bootstrap distributions
fig, axes = plt.subplots(1,3,figsize=(13,4))
xgrid=np.linspace(-0.5,0.5,400)
for ax, (_,row) in zip(axes, boot.iterrows()):
    m=row['boot_mean']; sd=max(row['boot_sd'], 1e-3)
    y=(1/(sd*np.sqrt(2*np.pi)))*np.exp(-0.5*((xgrid-m)/sd)**2)
    ax.fill_between(xgrid,y,color=MID,alpha=0.6)
    ax.axvline(0,color='#666666',lw=1)
    ax.axvline(row['indirect'], color=NEG if row['indirect']<0 else POS, lw=2)
    ax.axvspan(row['boot_ci_low'], row['boot_ci_high'], color=LIGHT, alpha=0.9)
    ax.set_title(str(row['outcome']).replace('_fixed',''), fontsize=11)
    ax.text(0.02,0.95,f"95% CI [{row['boot_ci_low']:.2f}, {row['boot_ci_high']:.2f}]",transform=ax.transAxes,va='top',fontsize=9)
fig.suptitle('Bootstrap distribution of indirect effect (original bootstrap)',fontsize=15,fontweight='bold',y=1.03)
save_all(fig,'Figure_6D_bootstrap_indirect_distribution')

# Figure 6E evidence scorecard
rows=['did→A','did→B','did→C','A→exec','B→exec','C→exec','A→proc','B→proc','C→proc','A→quality','B→quality','C→quality','A→B','B→C']
cols=['exec_share','proc_share','ppp_quality_pca_rebuilt_fixed']
sigmap={}
for med in ['A_idx','B_idx','C_idx']:
    r=stage1_ts.loc[med]; sigmap[f'did→{med[0]}']=(r['coef_did'],r['p_did'])
chain_tmp={out: chain_fix[chain_fix.outcome==out].set_index('key_var') for out in cols}
mat=[]
for row in rows:
    vals=[]
    for out in cols:
        if row.startswith('did'):
            coef,p=sigmap[row]
        elif row in ['A→B','B→C']:
            rr=chain[(chain['dependent']=='B_idx') & (chain['key_var']=='A_idx')].iloc[0] if row=='A→B' else chain[(chain['dependent']=='C_idx') & (chain['key_var']=='B_idx')].iloc[0]
            coef,p=rr['coef'],rr['p']
        else:
            med={'A':'A_idx','B':'B_idx','C':'C_idx'}[row[0]]
            rr=chain_tmp[out].loc[med]
            coef,p=rr['coef'],rr['p']
        vals.append((coef,p))
    mat.append(vals)
fig, ax=plt.subplots(figsize=(8,8))
ax.set_xlim(-0.5,len(cols)-0.5); ax.set_ylim(-0.5,len(rows)-0.5); ax.invert_yaxis()
for i,rowname in enumerate(rows):
    for j,colname in enumerate(cols):
        coef,p=mat[i][j]
        color=POS if coef>=0 else NEG
        size=80+220*(1-min(1,p/0.1))
        alpha=0.9 if p<0.1 else 0.3
        ax.scatter(j,i,s=size,color=color,alpha=alpha,edgecolor='none')
        ax.text(j,i,f"{coef:.2f}",ha='center',va='center',fontsize=8,color='white' if p<0.1 else '#222')
ax.set_xticks(range(len(cols)), ['Exec','Proc','Quality'])
ax.set_yticks(range(len(rows)), rows)
for spine in ax.spines.values(): spine.set_visible(False)
ax.tick_params(length=0)
ax.set_title('Mechanism evidence scorecard\nSize = statistical strength; color = sign',fontsize=14,fontweight='bold')
save_all(fig,'Figure_6E_mechanism_evidence_scorecard')

# Figure 6F attenuation dumbbell
baseline = base_did[base_did.did_var=='treat_share'].set_index('depvar')['coef']
meds=['A_idx','B_idx','C_idx','ppp_governance_capacity_index','ppp_norm_risk_index']
sum_t=summary[summary.did_var=='treat_share'].copy()
fig, axes = plt.subplots(1,3, figsize=(13,4))
for ax,out in zip(axes, ['exec_share','proc_share','ppp_quality_pca_rebuilt']):
    sub=sum_t[sum_t.outcome==out].set_index('mediator')
    y=np.arange(len(meds))
    basecoef=baseline[out]
    for yi,med in enumerate(meds):
        newcoef=sub.loc[med,'coef_did']
        color=POS if newcoef>=0 else NEG
        ax.plot([basecoef,newcoef],[yi,yi], color=LIGHT, lw=2)
        ax.scatter(basecoef, yi, color=DARK, s=35, zorder=3)
        ax.scatter(newcoef, yi, color=color, s=55, zorder=3)
        ax.text(newcoef, yi+0.12, f'{newcoef:.2f}', fontsize=8, ha='center')
    ax.axvline(0,color='#666666',lw=1)
    ax.set_yticks(y, ['A','B','C','GovCap','NormRisk'])
    ax.set_title(out.replace('_',' '), fontsize=11)
    ax.set_xlabel('Treat coefficient')
axes[0].set_ylabel('Mediator added')
fig.suptitle('Direct-effect attenuation after adding each mediator',fontsize=15,fontweight='bold',y=1.03)
save_all(fig,'Figure_6F_direct_effect_attenuation')

print("Regenerated charts written to charts_regenerated/")

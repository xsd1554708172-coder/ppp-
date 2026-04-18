import os, re, random, json
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

torch.set_num_threads(1)
SEED=42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
LABEL_COLS=['A1','A2','B1','B2','B3','B4','C1','C2','C3']
OUT_XLSX='/mnt/data/PPP_第3部分深度学习终版增强_V2_四级十二类_实际执行版.xlsx'
OUT_CSV='/mnt/data/PPP_deep_autocoding_bestmodel_v2_四级十二类_实际执行版.csv'
OUT_DTA='/mnt/data/PPP_deep_autocoding_bestmodel_v2_四级十二类_实际执行版.dta'

def clean_text(t):
    if pd.isna(t): return ''
    t=str(t)
    t=re.sub(r'【法宝引证码】.*?\n',' ',t)
    t=re.sub(r'原文链接[:：]?\s*https?://\S+',' ',t)
    t=re.sub(r'https?://\S+',' ',t)
    t=re.sub(r'\s+',' ',t)
    return t.strip()

def char_tokens(text, max_chars=180):
    text=clean_text(text)[:max_chars]
    return [ch for ch in text if ch.strip()]

def metrics(y_true, y_pred):
    return {
        'micro_f1':f1_score(y_true,y_pred,average='micro',zero_division=0),
        'macro_f1':f1_score(y_true,y_pred,average='macro',zero_division=0),
        'micro_precision':precision_score(y_true,y_pred,average='micro',zero_division=0),
        'micro_recall':precision_score(y_true,y_pred,average='micro',zero_division=0) if False else recall_score(y_true,y_pred,average='micro',zero_division=0),
        'subset_accuracy':accuracy_score(y_true,y_pred),
    }

def per_label_metrics(y_true, y_pred, model_name):
    rows=[]
    for i,lab in enumerate(LABEL_COLS):
        rows.append({'model':model_name,'label':lab,'f1':f1_score(y_true[:,i],y_pred[:,i],zero_division=0),'precision':precision_score(y_true[:,i],y_pred[:,i],zero_division=0),'recall':recall_score(y_true[:,i],y_pred[:,i],zero_division=0),'support':int(y_true[:,i].sum())})
    return rows

# load labels
labels = pd.read_excel('/mnt/data/PPP_V2正式试编码结果.xlsx', sheet_name='120篇文档评分矩阵')
for c in LABEL_COLS:
    labels[c] = (pd.to_numeric(labels[c], errors='coerce').fillna(0) > 0).astype(int)
# load texts from full table but only needed columns
raw = pd.read_excel('/mnt/data/数据总表.xlsx', sheet_name='政府与社会资本合作_txt文本整合结果', usecols=['序号','文件名','文件内容'])
raw['text']=raw['文件内容'].map(clean_text)
# merge by sequence id or filename
merge_cols=['序号'] if '序号' in labels.columns else ['文件名']
data=labels[['序号','文件名']+LABEL_COLS].merge(raw[['序号','文件名','text']], on=merge_cols, how='left')
if data['text'].isna().mean() > 0.2 and '文件名' in labels.columns:
    data=labels[['文件名']+LABEL_COLS].merge(raw[['序号','文件名','text']], on=['文件名'], how='left')

data['text']=data['text'].fillna('').map(clean_text)
data=data[data['text'].str.len()>0].reset_index(drop=True)
print('merged data', data.shape)

# split with label coverage
best=None
for seed in range(42, 300):
    train_df, test_df = train_test_split(data, test_size=0.2, random_state=seed, shuffle=True)
    tr_df, val_df = train_test_split(train_df, test_size=0.25, random_state=seed, shuffle=True)
    ok=True
    for df in [train_df, tr_df, val_df, test_df]:
        if (df[LABEL_COLS].sum()==0).any():
            ok=False; break
    if ok:
        best=(seed, train_df.reset_index(drop=True), tr_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)); break
seed, train_df, tr_df, val_df, test_df = best
print('split seed', seed, len(train_df), len(tr_df), len(val_df), len(test_df))
Y_train=train_df[LABEL_COLS].values.astype(int)
Y_tr=tr_df[LABEL_COLS].values.astype(int)
Y_val=val_df[LABEL_COLS].values.astype(int)
Y_test=test_df[LABEL_COLS].values.astype(int)

# baseline svc
comparison=[]; per_label=[]
vec=TfidfVectorizer(analyzer='char', ngram_range=(2,4), min_df=1)
Xtrain=vec.fit_transform(train_df['text'])
Xtest=vec.transform(test_df['text'])
svc=OneVsRestClassifier(LinearSVC(random_state=SEED))
svc.fit(Xtrain, Y_train)
pred_svc=svc.predict(Xtest)
m=metrics(Y_test, pred_svc)
m.update({'model':'LinearSVC','augmentation':'No','threshold':np.nan,'train_size':len(train_df),'val_size':0,'test_size':len(test_df)})
comparison.append(m)
per_label.extend(per_label_metrics(Y_test,pred_svc,'LinearSVC'))
print('LinearSVC micro_f1', m['micro_f1'])

# tokenization / vocab from labeled texts only for speed
all_texts = data['text'].tolist()
all_toks = [char_tokens(t) for t in all_texts]
tr_toks = [char_tokens(t) for t in tr_df['text'].tolist()]
val_toks = [char_tokens(t) for t in val_df['text'].tolist()]
test_toks = [char_tokens(t) for t in test_df['text'].tolist()]
ctr=Counter();
for toks in all_toks: ctr.update(toks)
vocab={'<pad>':0,'<unk>':1}
for tok,cnt in ctr.items():
    if cnt>=2: vocab[tok]=len(vocab)
print('vocab size', len(vocab))

class MultiLabelDataset(Dataset):
    def __init__(self, token_lists, labels=None, max_len=180):
        self.labels=labels
        self.seqs=[]
        for toks in token_lists:
            ids=[vocab.get(t,1) for t in toks[:max_len]]
            if not ids: ids=[1]
            self.seqs.append(ids)
    def __len__(self): return len(self.seqs)
    def __getitem__(self, idx):
        x=torch.tensor(self.seqs[idx], dtype=torch.long)
        if self.labels is None: return x
        return x, torch.tensor(self.labels[idx], dtype=torch.float32)

def collate(batch):
    if isinstance(batch[0], tuple):
        xs, ys = zip(*batch)
        lengths=torch.tensor([len(x) for x in xs], dtype=torch.long)
        m=max(lengths).item()
        pad=torch.zeros(len(xs), m, dtype=torch.long)
        for i,x in enumerate(xs): pad[i,:len(x)] = x
        return pad, lengths, torch.stack(ys)
    else:
        xs=batch
        lengths=torch.tensor([len(x) for x in xs], dtype=torch.long)
        m=max(lengths).item()
        pad=torch.zeros(len(xs), m, dtype=torch.long)
        for i,x in enumerate(xs): pad[i,:len(x)] = x
        return pad, lengths

def loaders(train_toks, train_y, val_toks, val_y, test_toks, test_y, batch=16):
    train_dl=DataLoader(MultiLabelDataset(train_toks, train_y), batch_size=batch, shuffle=True, collate_fn=collate)
    val_dl=DataLoader(MultiLabelDataset(val_toks, val_y), batch_size=batch, shuffle=False, collate_fn=collate)
    test_dl=DataLoader(MultiLabelDataset(test_toks, test_y), batch_size=batch, shuffle=False, collate_fn=collate)
    pos=train_y.sum(axis=0); neg=len(train_y)-pos
    pos_weight=torch.tensor((neg+1)/(pos+1), dtype=torch.float32)
    return train_dl, val_dl, test_dl, pos_weight

class FastTextClassifier(nn.Module):
    def __init__(self, vocab_size, emb_dim, num_labels):
        super().__init__(); self.emb=nn.Embedding(vocab_size, emb_dim, padding_idx=0); self.fc=nn.Linear(emb_dim, num_labels)
    def forward(self, x, lengths):
        e=self.emb(x); mask=(x!=0).unsqueeze(-1)
        pooled=(e*mask).sum(1)/mask.sum(1).clamp(min=1)
        return self.fc(pooled)

class TextCNNClassifier(nn.Module):
    def __init__(self, vocab_size, emb_dim, num_labels):
        super().__init__(); self.emb=nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.convs=nn.ModuleList([nn.Conv1d(emb_dim, 16, k) for k in [2,3,4]])
        self.fc=nn.Linear(16*3, num_labels)
    def forward(self, x, lengths):
        e=self.emb(x).transpose(1,2)
        outs=[torch.max(torch.relu(conv(e)), dim=2).values for conv in self.convs]
        return self.fc(torch.cat(outs, dim=1))

class BiLSTMAttentionClassifier(nn.Module):
    def __init__(self, vocab_size, emb_dim, num_labels):
        super().__init__(); self.emb=nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.lstm=nn.LSTM(emb_dim, 16, bidirectional=True, batch_first=True)
        self.attn=nn.Linear(32,1); self.fc=nn.Linear(32, num_labels)
    def forward(self, x, lengths):
        e=self.emb(x)
        packed=nn.utils.rnn.pack_padded_sequence(e, lengths.cpu(), batch_first=True, enforce_sorted=False)
        out,_=self.lstm(packed)
        out,_=nn.utils.rnn.pad_packed_sequence(out, batch_first=True)
        mask=torch.arange(out.size(1))[None,:] < lengths[:,None]
        scores=self.attn(out).squeeze(-1).masked_fill(~mask, -1e9)
        w=torch.softmax(scores, dim=1).unsqueeze(-1)
        ctx=(out*w).sum(1)
        return self.fc(ctx)

def train_torch(model, train_dl, val_dl, pos_weight, epochs=4, lr=1e-3):
    opt=torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn=nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    best_state=None; best_thr=0.5; best_f1=-1; hist=[]
    for epoch in range(epochs):
        model.train(); total=0.0
        for x,lengths,y in train_dl:
            opt.zero_grad(); logits=model(x,lengths); loss=loss_fn(logits,y); loss.backward(); opt.step(); total += float(loss)*len(y)
        model.eval(); ys=[]; ps=[]
        with torch.no_grad():
            for x,lengths,y in val_dl:
                probs=torch.sigmoid(model(x,lengths)).cpu().numpy(); ps.append(probs); ys.append(y.cpu().numpy())
        yv=np.vstack(ys); pv=np.vstack(ps)
        local_best=-1; local_thr=0.5
        for thr in [0.35,0.4,0.45,0.5,0.55]:
            pred=(pv>=thr).astype(int); f1=f1_score(yv,pred,average='micro',zero_division=0)
            if f1>local_best: local_best=f1; local_thr=thr
        hist.append({'epoch':epoch+1,'train_loss':total/len(train_dl.dataset),'val_micro_f1':local_best,'thr':local_thr})
        if local_best>best_f1:
            best_f1=local_best; best_thr=local_thr; best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(best_state)
    return model, best_thr, pd.DataFrame(hist)

def pred_torch(model, loader, thr):
    model.eval(); probs=[]
    with torch.no_grad():
        for x,lengths,y in loader:
            probs.append(torch.sigmoid(model(x,lengths)).cpu().numpy())
    probs=np.vstack(probs)
    return (probs>=thr).astype(int)

def eda_chars(toks):
    toks=toks.copy()
    if len(toks)<10: return toks
    i,j=random.sample(range(len(toks)),2); toks[i], toks[j]=toks[j], toks[i]
    kept=[ch for ch in toks if random.random()>0.05]
    if len(kept)>=8: toks=kept
    pos=random.randrange(len(toks)); toks.insert(pos, toks[pos])
    return toks[:180]

# fasttext
train_dl,val_dl,test_dl,posw = loaders(tr_toks, Y_tr, val_toks, Y_val, test_toks, Y_test)
for name, cls, lr, aug in [
    ('FastText', FastTextClassifier, 2e-3, False),
    ('TextCNN', TextCNNClassifier, 1e-3, False),
    ('EDA+BiLSTM-Attention', BiLSTMAttentionClassifier, 1e-3, True),
]:
    x_train=tr_toks; y_train=Y_tr
    if aug:
        x_train = tr_toks + [eda_chars(t) for t in tr_toks]
        y_train = np.vstack([Y_tr, Y_tr])
    train_dl,val_dl,test_dl,posw = loaders(x_train, y_train, val_toks, Y_val, test_toks, Y_test)
    model=cls(len(vocab),24,len(LABEL_COLS))
    model, thr, hist = train_torch(model, train_dl, val_dl, posw, epochs=4, lr=lr)
    pred=pred_torch(model, test_dl, thr)
    m=metrics(Y_test, pred)
    m.update({'model':name,'augmentation':'EDA' if aug else 'No','threshold':thr,'train_size':len(y_train),'val_size':len(val_df),'test_size':len(test_df)})
    comparison.append(m)
    per_label.extend(per_label_metrics(Y_test,pred,name))
    print(name, 'micro_f1', m['micro_f1'])

comp=pd.DataFrame(comparison)
order=['LinearSVC','FastText','TextCNN','EDA+BiLSTM-Attention']
comp['model']=pd.Categorical(comp['model'], categories=order, ordered=True)
comp=comp.sort_values('model').reset_index(drop=True)
comp['rank_by_micro_f1']=comp['micro_f1'].rank(ascending=False,method='dense').astype(int)
print(comp[['model','micro_f1','macro_f1','micro_precision','micro_recall','subset_accuracy','rank_by_micro_f1']])

# best model predictions on 120 labeled sample for export
best_model=comp.sort_values('micro_f1', ascending=False).iloc[0]['model']
if best_model=='LinearSVC':
    pred_all = svc.predict(vec.transform(data['text']))
else:
    # retrain best deep model on all labeled data with 10% holdout for threshold selection
    hold = data.sample(frac=0.1, random_state=SEED)
    fit = data.drop(index=hold.index)
    fit_toks=[char_tokens(t) for t in fit['text']]
    hold_toks=[char_tokens(t) for t in hold['text']]
    fit_y=fit[LABEL_COLS].values.astype(int)
    hold_y=hold[LABEL_COLS].values.astype(int)
    if best_model=='FastText': cls, lr, x_train, y_train = FastTextClassifier, 2e-3, fit_toks, fit_y
    elif best_model=='TextCNN': cls, lr, x_train, y_train = TextCNNClassifier, 1e-3, fit_toks, fit_y
    else: cls, lr, x_train, y_train = BiLSTMAttentionClassifier, 1e-3, fit_toks + [eda_chars(t) for t in fit_toks], np.vstack([fit_y, fit_y])
    train_dl,val_dl,_,posw = loaders(x_train, y_train, hold_toks, hold_y, hold_toks, hold_y)
    model=cls(len(vocab),24,len(LABEL_COLS))
    model, thr, _ = train_torch(model, train_dl, val_dl, posw, epochs=4, lr=lr)
    all_ds=MultiLabelDataset([char_tokens(t) for t in data['text']], None)
    all_dl=DataLoader(all_ds, batch_size=16, shuffle=False, collate_fn=collate)
    model.eval(); probs=[]
    with torch.no_grad():
        for x,lengths in all_dl:
            probs.append(torch.sigmoid(model(x,lengths)).cpu().numpy())
    pred_all=(np.vstack(probs)>=thr).astype(int)

fname_col='文件名' if '文件名' in data.columns else ('文件名_x' if '文件名_x' in data.columns else '文件名_y')
full_out=data[['序号',fname_col]].copy()
full_out=full_out.rename(columns={fname_col:'文件名'})
for i,lab in enumerate(LABEL_COLS): full_out[f'{lab}_pred']=pred_all[:,i]
full_out['best_model']=best_model
with pd.ExcelWriter(OUT_XLSX, engine='openpyxl') as writer:
    comp.to_excel(writer, sheet_name='模型比较总表', index=False)
    pd.DataFrame(per_label).to_excel(writer, sheet_name='分标签指标', index=False)
    pd.DataFrame({'item':['split_seed','total_labeled','train_total','train_inner','val_inner','test_total','vocab_size','best_model'], 'value':[seed,len(data),len(train_df),len(tr_df),len(val_df),len(test_df),len(vocab),best_model]}).to_excel(writer, sheet_name='训练测试划分', index=False)
    full_out.to_excel(writer, sheet_name='120样本自动编码_最佳模型', index=False)
full_out.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
full_out.to_stata(OUT_DTA, write_index=False, version=118)
print('saved', OUT_XLSX)

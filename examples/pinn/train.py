# Real PINN training for damped oscillator u''+mu u'+k u=0 (mu=4,k=400,u0=1,v0=0). Saves snapshots to train_data.json.gz
import torch, json, gzip, numpy as np
from pathlib import Path
torch.manual_seed(123)
d, w0 = 2.0, 20.0; mu_true, k = 2*d, w0**2
def exact(t):
    w = np.sqrt(w0**2-d**2); phi = np.arctan(-d/w); A = 1/(2*np.cos(phi))
    return np.exp(-d*t)*2*A*np.cos(phi+w*t)
class FCN(torch.nn.Module):
    def __init__(s): super().__init__(); s.net = torch.nn.Sequential(torch.nn.Linear(1,32),torch.nn.Tanh(),torch.nn.Linear(32,32),torch.nn.Tanh(),torch.nn.Linear(32,32),torch.nn.Tanh(),torch.nn.Linear(32,1))
    def forward(s,x): return s.net(x)
tg = np.linspace(0,1,241); tg_t = torch.tensor(tg,dtype=torch.float32).view(-1,1)
td = np.linspace(0,0.36,10); ud = exact(td) + 0.0*np.random.default_rng(0).normal(size=10)
td_t = torch.tensor(td,dtype=torch.float32).view(-1,1); ud_t = torch.tensor(ud,dtype=torch.float32).view(-1,1)
tc = torch.linspace(0,1,40).view(-1,1).requires_grad_(True)
def run(physics, inverse=False, steps=20000, snaps=40):
    torch.manual_seed(123); net = FCN(); params = list(net.parameters())
    mu = torch.nn.Parameter(torch.tensor(0.0)) if inverse else None
    if inverse: params.append(mu)
    opt = torch.optim.Adam(params, lr=1e-3)
    out = {'snap':[], 'step':[], 'loss':[], 'ldata':[], 'lphys':[], 'mu':[]}
    snap_at = set(np.unique(np.round(np.geomspace(1, steps, snaps)).astype(int)).tolist())
    for i in range(1, steps+1):
        opt.zero_grad()
        ld = torch.mean((net(td_t)-ud_t)**2); loss = ld; lp = torch.tensor(0.)
        if physics:
            u = net(tc); du = torch.autograd.grad(u, tc, torch.ones_like(u), create_graph=True)[0]
            ddu = torch.autograd.grad(du, tc, torch.ones_like(du), create_graph=True)[0]
            m = mu if inverse else mu_true
            lp = torch.mean((ddu + m*du + k*u)**2); loss = ld + 1e-4*lp
        loss.backward(); opt.step()
        if i in snap_at:
            with torch.no_grad(): out['snap'].append([round(float(v),4) for v in net(tg_t).view(-1)])
            out['step'].append(i); out['loss'].append(float(loss)); out['ldata'].append(float(ld)); out['lphys'].append(float(lp)); out['mu'].append(float(mu) if inverse else None)
    return out
res = {'t': tg.tolist(), 'exact': [round(float(v),4) for v in exact(tg)], 'td': td.tolist(), 'ud': ud.tolist(), 'tc': tc.detach().view(-1).tolist(),
       'nn': run(False, steps=6000), 'pinn': run(True), 'inv': run(True, inverse=True)}
with gzip.open(Path(__file__).with_name('train_data.json.gz'), 'wt', encoding='utf8', compresslevel=9) as f:
    json.dump(res, f)
for k2 in ['nn','pinn','inv']:
    s = np.array(res[k2]['snap'][-1]); print(k2, 'final L2 err', float(np.sqrt(np.mean((s-np.array(res['exact']))**2))), 'mu', res[k2]['mu'][-1])

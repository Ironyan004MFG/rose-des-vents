"""Cou de secours (lot F du tieffelin) : quand neck_label ne trouve pas le trait de mâchoire, on cherche colonne par colonne
l'ombre du menton (le plus sombre dans le bas du visage) et on étiquette COU la peau qui est dessous."""
import numpy as np, heads
from PIL import Image
from scipy import ndimage as ndi
def neck_cols(lot,k,ey):
    lab=np.load(f'assets/head_{lot}_{k}_lab.npy')
    if (lab==heads.COU).sum()>150: return 0
    t=np.array(Image.open(f'assets/head_{lot}_{k}.png').convert('RGBA')).astype(float);g=ndi.gaussian_filter(t[...,:3].mean(-1),1.2)
    sk=lab==1;ys=np.where(sk.any(1))[0];
    if not len(ys): return 0
    bot=ys[-1];top=int(bot-0.16*(bot-ys[0]));xs=[];rs=[];ends=[]
    for x in np.where(sk[top:bot+1].any(0))[0]:
        col=np.where(sk[top:bot+1,x])[0]+top
        if len(col)<6: continue
        seg=g[col[0]:col[-1]+1,x];xs.append(x);rs.append(col[0]+int(np.argmin(seg[:max(1,int(len(seg)*.85))])));ends.append(col[-1])
    if not xs: return 0
    from scipy.ndimage import median_filter
    rs=np.maximum(np.array(rs),median_filter(np.array(rs),size=31,mode='nearest'))   # l'ombre des lèvres au milieu ne compte pas : on suit la courbe du menton
    for x,r,e in zip(xs,rs,ends):
        below=np.arange(r+2,e+1);m=sk[below,x];lab[below[m],x]=heads.COU
    # ne garder que la plus grande plage connexe qui touche le bas
    c,q=ndi.label(lab==heads.COU)
    if q>1:
        sz=ndi.sum(np.ones_like(c),c,range(1,q+1));keep=1+int(np.argmax(sz));lab[(c>0)&(c!=keep)]=1
    np.save(f'assets/head_{lot}_{k}_lab.npy',lab);return int((lab==heads.COU).sum())

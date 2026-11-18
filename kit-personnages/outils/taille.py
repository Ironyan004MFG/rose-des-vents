import numpy as np,glob,os
from PIL import Image
from scipy import ndimage as ndi
K='/home/claude/rose-des-vents/kit-personnages'
def geo(png,lab):
    L=np.load(lab);im=np.array(Image.open(png).convert('RGBA')).astype(float);g=ndi.gaussian_filter(im[...,:3].mean(-1),0.8);sk=(L==1)
    cs=[]
    for y in range(214,240,2):
        lab_,n=ndi.label(sk[y]);c=lab_[256]
        if c==0:
            xs=np.where(sk[y,236:276])[0]
            if not len(xs): continue
            c=lab_[236+xs[len(xs)//2]]
        seg=np.where(lab_==c)[0];cs.append((seg[0]+seg[-1])/2)
    cx=int(round(np.median(cs))) if cs else 256
    best=None
    for y in range(175,228):
        zs=[x for x in list(range(cx-24,cx-8))+list(range(cx+8,cx+24)) if sk[y,x]]
        if len(zs)<14: continue
        v=g[y,zs].mean()
        if best is None or v<best[0]: best=(v,y)
    if not best: return None
    ey=best[1];cen=sk[:,cx-10:cx+10];ys=np.where(cen.any(1))[0];ch=ys[-1]
    return dict(cx=cx,ey=ey,ch=int(ch),h=int(ch-ey))
def race(r):
    out={}
    for f in sorted(glob.glob(f'{K}/{r}/tete/lot*/head_*.png')):
        g=geo(f,f[:-4]+'_matieres.npy')
        if g: out[f.split('/')[-2]+'/'+os.path.basename(f)[5:-4]]=g
    return out

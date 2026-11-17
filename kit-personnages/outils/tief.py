"""Lots de têtes du tieffelin : vides entre les mèches retirés, cornes (MAGENTA) -> matière 72, plume/pierre (ORANGE, lots sans mailles) -> 31."""
import numpy as np, heads
from PIL import Image
from scipy import ndimage as ndi
def voids(lot,n=8):
    """Les plages de blanc pur enfermées entre mèches ou sous une plume, blanches aussi dans le calque, deviennent transparentes."""
    M=heads.split_map(f'../{lot}/map.png',n=n)
    for k in range(1,n+1):
        im=Image.open(f'../{lot}/t{k}.png').convert('RGBA');a=np.array(im);w,h=im.size;m=np.array(Image.fromarray(M[k-1].astype('uint8')).resize((w,h),Image.NEAREST))
        wh=(a[...,:3].mean(-1)>236)&(a[...,3]>40);c,q=ndi.label(wh);cut=np.zeros_like(wh)
        for j in range(1,q+1):
            r=c==j
            if r.sum()>=25 and (m[r]==0).mean()>.6: cut|=r
        a[ndi.binary_dilation(cut,iterations=1),3]=0;Image.fromarray(a).save(f'../{lot}/t{k}.png')
def build(lot,eyes,names,s=.44,plume=True,**kw):
    heads.grid(lot,n=len(eyes));voids(lot,len(eyes));T=heads.centers(lot,eyes);heads.build_lotU(lot,T,s=s,**kw)
    for k,nm in names.items():
        L=np.load(f'assets/head_{lot}_{k}_lab.npy');L[L==31]=heads.CORNE
        if plume and k not in kw.get('mail',()) and k not in kw.get('camail',{}): L[L==60]=31
        np.save(f'assets/head_{lot}_{k}_lab.npy',L)
    return T

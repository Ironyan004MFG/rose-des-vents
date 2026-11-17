# Masques affinés pour toutes les pièces + teinte
from PIL import Image,ImageFilter
import numpy as np
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import seg
PAL={1:(255,128,0),2:(0,90,255),3:(0,210,70),5:(255,32,48),6:(255,217,0),4:(128,128,128)}   # 1 peau 2 cheveux 3 barbe 4 métal 5 tissu 6 cuir
def refine(n,er=2):
    im=np.array(Image.open(f'assets/{n}.png').convert('RGBA')).astype(float);al=im[...,3]>40
    i=np.array(Image.open(f'assets/{n}_id.png').convert('RGBA')).astype(int)
    lum=ndi.gaussian_filter(im[...,:3].mean(-1),0.8);mk=np.zeros(al.shape,int)
    for l,rgb in PAL.items():
        m=(np.abs(i[...,:3]-np.array(rgb)).sum(-1)<40)&al
        if m.any(): mk[ndi.binary_erosion(m,iterations=er)]=l
    return watershed(255-lum,mk,mask=al)
LAB={}
def labels(n):
    if n not in LAB: LAB[n]=np.load('head_fix_lab.npy') if n.startswith('head') else refine(n)
    return LAB[n]
G={1:.8,2:.75,3:.75,5:.75,6:.7}
HEAD=None                                   # (nom, couleurs en plus) : remplace la tête tressée par une autre tête de heads.py
def tint(n,cols):
    if n.startswith('head') and HEAD:
        import heads;return heads.tint(HEAD[0],{**{k:v for k,v in cols.items() if k in (1,2,3)},4:'#9aa0a6',**HEAD[1]})
    a=np.array(Image.open('assets/head_fix.png' if n.startswith('head') else f'assets/{n}.png').convert('RGBA')).astype(float);lab=labels(n)
    lum=(a[...,0]*.3+a[...,1]*.59+a[...,2]*.11)/255;out=a.copy()
    for l,col in cols.items():
        m=lab==l
        if not m.any(): continue
        w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.7))).astype(float)/255
        if n.startswith('head') and l in (1,3):      # joues : la peau se fond dans les favoris, sans coupure nette
            w3=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2.6))).astype(float)/255
            Y,X=np.mgrid[0:512,0:512];z=((X<216)|(X>296))&(Y>246)&(Y<282);zs=np.array(Image.fromarray((z*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2))).astype(float)/255
            w=w*(1-zs)+w3*zs
        f=np.clip(lum/lum[m].mean()*G[l],0,1.35);C=np.array([int(col[j:j+2],16) for j in (1,3,5)],float)
        for j in range(3): out[...,j]=out[...,j]*(1-w)+np.clip(C[j]*f,0,255)*w
    o_=Image.fromarray(out.astype('uint8'))
    if n.startswith('head'):
        import heads;o_=heads.raise_(o_,heads.RAISE['fix'])      # règle de hauteur : sourcils sur la ligne des épaules
    return o_
ORDER=['boots_dwarf_90','arm_right_dwarf_relaxed_90','arm_left_dwarf_relaxed_90','body_dwarf_relaxed_90','head_dwarf_braided_90']
def char(cloth,skin,hair,leather='#3a2a1c',beard=None):
    c=Image.new('RGBA',(512,512));cols={5:cloth,1:skin,2:hair,3:beard or hair,6:leather}
    for n in ORDER: c.alpha_composite(tint(n,cols))
    return c
if __name__=='__main__':
    V=[('#2f6a34','#c98f6a','#8a4a22'),('#7a2a26','#e2b592','#2a2422'),('#2d4a7a','#8a5a3c','#b9b3aa'),('#5a4a6e','#d9a47e','#c9a23a')]
    O=Image.new('RGBA',(512*4,512),(140,105,70,255));cs=[char(*v) for v in V]
    for k,c in enumerate(cs): O.alpha_composite(c,(k*512,0))
    O.crop((0,60,2048,450)).save('../k_tinted.png')
    Z=Image.new('RGBA',(512,512),(140,105,70,255));Z.alpha_composite(cs[0]);Z.crop((90,70,422,400)).resize((1328,1320),Image.LANCZOS).save('../k_zoom.png')

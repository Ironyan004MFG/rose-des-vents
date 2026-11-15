# Fermier : matières classées par leur valeur de gris (règle donnée à GPT) — 1 peau, 14 chemise, 5 salopette, 6 corde/bretelles, 7 intérieur du col
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import norm,bodyseg,full,kit,legs,r2
def prep(src,tag,like='../adv/src3.png'):
    norm.normalize_like(src,like,f'../far/n_{tag}.png') if like else norm.normalize(src,f'../far/n_{tag}.png')
    a=np.array(Image.open(f'../far/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1)
    line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
    area=ndi.sum(al,comp,idx);cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T;ml=ndi.mean(lum,comp,idx)
    H,W=al.shape;shirt=bodyseg.poly([(545,215),(705,215),(705,560),(545,560)],(H,W));fs=ndi.mean(shirt.astype(float),comp,idx)
    kind=np.where(ml>165,1,np.where(ml>125,14,np.where(ml>88,5,6)))
    kind[(fs>0.5)&(ml<100)]=7
    kind[(kind==1)&(np.abs(cx-627)<250)]=14                 # rien de clair au centre n'est de la peau
    lab=np.zeros((H,W),int);lab[comp>0]=kind[comp[comp>0]-1]
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    return a,lab
SC=0.29
def prep_pose(src,tag,base_src,base_tag):
    """Pose dérivée d'une image validée : le torse est identique au pixel près, donc on reprend ses matières telles quelles
    et on ne classe que la zone qui a changé (bras, mains, objet)."""
    b,lb=prep(base_src,base_tag);norm.normalize_like(src,'../adv/src3.png',f'../far/n_{tag}.png')
    a=np.array(Image.open(f'../far/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1)
    ch=ndi.binary_dilation(ndi.binary_opening(np.abs(a-b).max(-1)>10,iterations=1),iterations=6)
    ls=ndi.gaussian_filter(lum,1.0);line=(ls<bodyseg.LT)&al;l3=ndi.gaussian_filter(lum,2.5)
    from skimage.segmentation import watershed
    mk=np.where(ch,0,lb)                                             # le torse validé sert de graines
    mk[ndi.binary_erosion(ch&al&(l3>185),iterations=3)]=1            # cœur clair des mains
    core=ch&al&~line
    mk[ndi.binary_erosion(core&(l3>135)&(l3<168),iterations=6)&(mk==0)]=14   # manche
    mk[ndi.binary_erosion(core&(l3>88)&(l3<118),iterations=6)&(mk==0)]=5     # salopette
    lab=watershed(255-ls,mk,mask=al)
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    return a,lab
def char(a,lab,shirt,over,sk,hr,rope='#6b5a3a',pants='#5a4a32'):
    full.G.update({14:.85,6:.85,5:.75});cols={1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512));c.alpha_composite(legs.legs(pants,'#3a2a1c'))
    c.alpha_composite(full.place(full.tint(a,lab,{14:shirt,5:over,1:sk,6:rope,7:'#3a2e26'}),SC,(625,360)));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols));full.G[6]=.7;return c
if __name__=='__main__':
    import advp
    a,lab=prep('../far/relaxed2.png','relaxed2');b,lb=advp.prep('../adv/src3.png','rel')
    O=Image.new('RGBA',(512*4,512),(140,105,70,255))
    O.alpha_composite(char(a,lab,'#d8cdb0','#5a6f8a','#c98f6a','#8a4a22'),(0,0));O.alpha_composite(char(a,lab,'#b9a27a','#6a4a32','#8a5a3c','#2a2422'),(512,0));O.alpha_composite(char(a,lab,'#e6dfd0','#4a6a3a','#e2b592','#c9a23a'),(1024,0));O.alpha_composite(advp.char(b,lb,*r2.V[0]),(1536,0))
    O.crop((0,40,2048,512)).resize((1920,442),Image.LANCZOS).save('../far_cmp2.png')

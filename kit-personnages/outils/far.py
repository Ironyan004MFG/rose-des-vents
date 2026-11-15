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
    """Pose dérivée d'une image validée : on reprend les matières du torse validé partout où le dessin n'a pas changé
    (à un petit décalage près), et on ne classe que la zone des bras."""
    from skimage.segmentation import watershed
    b,lb=prep(base_src,base_tag);norm.normalize_like(src,'../adv/src3.png',f'../far/n_{tag}.png')
    a=np.array(Image.open(f'../far/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1)
    lb_=b[...,:3].mean(-1)*(b[...,3]>60);la_=lum*al;z=(slice(330,1150),slice(420,840));best=(1e9,0,0)
    for dy in range(-8,9,2):
        for dx in range(-8,9,2):
            e=np.abs(np.roll(np.roll(lb_,dy,0),dx,1)[z]-la_[z]).mean()
            if e<best[0]: best=(e,dy,dx)
    _,dy,dx=best;lbs=np.roll(np.roll(lb,dy,0),dx,1);bs=np.roll(np.roll(lb_,dy,0),dx,1)
    d=np.abs(ndi.gaussian_filter(bs,2.5)-ndi.gaussian_filter(la_,2.5))
    ch=ndi.binary_dilation(ndi.binary_opening(d>24,iterations=3),iterations=8)|(al&(lbs==0))
    ls=ndi.gaussian_filter(lum,1.0);l3=ndi.gaussian_filter(lum,2.5)
    tex=np.sqrt(ndi.gaussian_filter((lum-ndi.gaussian_filter(lum,5))**2,5))          # la chemise a des plis, la peau est lisse
    lab=np.where(ch,0,lbs);found=[]
    for LT2 in (95,75,bodyseg.LT):                                    # trait de plus en plus permissif : on ferme d'abord les contours faibles (bord de manche)
        free=al&ch&(ls>=LT2)&(lab==0)
        for c in found: free&=~c
        comp,k=ndi.label(free)
        if not k: continue
        idx=np.arange(1,k+1);ml=ndi.mean(lum,comp,idx);area=ndi.sum(al,comp,idx);sd=ndi.standard_deviation(l3,comp,idx);cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T
        for i in range(k):
            if area[i]<150: continue
            if LT2>bodyseg.LT and sd[i]>16 and area[i]>6000: continue     # encore deux matières mélangées : on réessaie avec un trait plus permissif
            m=comp==i+1
            if ml[i]>122: found.append(m)                                 # clair : manche ou peau, tranché plus bas selon la position le long du bras
            else: lab[m]=5 if ml[i]>88 else 6
    # le long de chaque bras, la manche est près de l'épaule et la peau (avant-bras, main) au bout
    for side,S in ((-1,bodyseg.SHO[0]),(1,bodyseg.SHO[1])):
        cs=[(m,np.hypot(*(np.array(ndi.center_of_mass(m))[::-1]-np.array(S)))) for m in found if (np.array(ndi.center_of_mass(m))[1]-627)*side>150]
        if not cs: continue
        dmax=max(d for _,d in cs)
        for m,d in cs: lab[m]=1 if d>0.62*dmax else 14
    for m in found:
        if abs(ndi.center_of_mass(m)[1]-627)<=150: lab[m]=14
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    print(tag,'décalage',dy,dx,'zone changée %',round(float((ch&al).mean()*100),1))
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

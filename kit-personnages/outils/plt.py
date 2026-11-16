# Armure de plates sans tabard (paladin, clerc en armure, guerrier). Corps dessiné par GPT (plt/relaxed.png) : il a sa propre silhouette
# (plus long que le garde, bras plus écartés), donc ses propres poses. Matières : 4 métal, 9 bordure (teintable), 15 cotte de mailles, 6 ceinture.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import grd,full,kit,legs
CHEST=(256,350);CHEST_SIZE=92;DY=34                      # emblème sur le plastron ; les bottes sont descendues (le corps est plus long)
def prep(src='../plt/relaxed.png',tag='relaxed'):
    import norm
    top,l,r=norm.collar(src);s=(norm.REF[2]-norm.REF[1])/(r-l);cx=(l+r)/2;rcx=(norm.REF[1]+norm.REF[2])/2
    Image.open(src).convert('RGBA').transform((1254,1500),Image.AFFINE,(1/s,0,cx-rcx/s,0,1/s,top-norm.REF[0]/s),Image.BICUBIC).save(f'../plt/n_{tag}.png')
    a=np.array(Image.open(f'../plt/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1);H,W=al.shape
    line=(ndi.gaussian_filter(lum,1.0)<grd.bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1);ml=ndi.mean(lum,comp,idx);ar=ndi.sum(al,comp,idx);cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T
    inner=ndi.binary_erosion(comp>0,iterations=5)&~ndi.binary_dilation(line,iterations=4);hp=lum-ndi.gaussian_filter(lum,1.6);ni=ndi.sum(inner,comp,idx);tx=np.sqrt(ndi.sum(hp**2*inner,comp,idx)/np.maximum(ni,1))
    kind=np.where(ml>125,4,np.where(ml<68,6,np.where(tx>7.5,15,9)));kind[(ar>40000)&(np.abs(cx-627)<60)&(cy<600)&(ml<90)]=7;kind[(kind==9)&(np.abs(cx-627)>300)]=15
    lab=np.zeros((H,W),int);lab[comp>0]=kind[comp[comp>0]-1];_,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    big=comp==(np.argmax(np.where((np.abs(cx-627)<80)&(cy>700)&(cy<950),ar,0))+1);return a,lab,ndi.binary_fill_holes(big)
def char(P,trim,sk='#c98f6a',hr='#8a4a22',metal='#aeb4bc',mail='#6a6e76',belt='#3a2a1c',pants='#4a4a52',emb=None,ph=0,H=560):
    a,lab,plast=P;full.G.update({4:.95,9:.85,15:.75,6:.7,7:.6});c=Image.new('RGBA',(512,H));c.alpha_composite(legs.legs(pants,'#3a2a1c',ph),(0,DY))
    def pl(im):
        w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));return o
    c.alpha_composite(pl(full.tint(a,lab,{4:metal,9:trim,15:mail,6:belt,7:'#2a2622'})))
    if emb is not None:
        m=pl(Image.fromarray((plast*255).astype('uint8')).convert('RGBA')).split()[0];e=Image.new('RGBA',(512,H));e.alpha_composite(emb,(round(CHEST[0]-emb.size[0]/2),round(CHEST[1]-emb.size[1]/2)))
        e.putalpha(Image.fromarray(np.minimum(np.array(e.split()[3]),np.array(m))));c.alpha_composite(e)
    hd=Image.new('RGBA',(512,H));hd.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}));c.alpha_composite(hd);return c

# --- Poses : on réutilise les BRAS du garde validé (marches, main qui tient…) sur le torse de plates -------------------------------------------
# Ordre des couches : torse de plates (sans ses bras) < bras du garde (sans ses épaulières) < épaulières de plates.
def _sides(a,lab,ymin=560):
    """Bras (cotte de mailles, brassards, gantelets) d'un corps normalisé : tout ce qui est relié à la cotte de mailles, hors épaulières."""
    H,W=lab.shape;yy,xx=np.mgrid[:H,:W];al=a[...,3]>60;lum=a[...,:3].mean(-1);m4=(lab==4);c,k=ndi.label(m4);idx=range(1,k+1)
    cy,cx=np.array(ndi.center_of_mass(m4,c,idx)).T;sz=ndi.sum(m4,c,idx)
    paul=np.isin(c,[i+1 for i in range(k) if cy[i]<ymin+60 and abs(cx[i]-627)>200 and sz[i]>4000])
    arm=(lab==15)|np.isin(c,[i+1 for i in range(k) if abs(cx[i]-627)>330 and cy[i]>=ymin+60])|((lab==28))
    arm=ndi.binary_dilation(arm,iterations=5)&al&((lum<95)|arm)&~paul;paul=ndi.binary_dilation(paul,iterations=5)&al&((lum<70)|paul)
    return arm&~paul,paul
BASE={}
def pose(ga,glab,src='../plt/relaxed2.png'):
    """ga, glab : une pose du garde (image normalisée + matières). Renvoie la même pose en armure de plates."""
    if 'p' not in BASE:
        a,lab,plast=prep(src,'relaxed2');arm,paul=_sides(a,lab);T=a.copy();T[arm|paul,3]=0
        sil=T[...,3]>60;hole=ndi.binary_fill_holes(ndi.binary_closing(sil|paul,iterations=30))&~sil&(arm|paul)        # le torse caché derrière ses bras : rebouché
        good=sil&(lab==4)&(a[...,:3].mean(-1)>110);_,ix=ndi.distance_transform_edt(~good,return_indices=True);T[hole]=a[ix[0],ix[1]][hole];T[hole,3]=255;tl=lab.copy();tl[hole]=4
        E_=a.copy();E_[~paul,3]=0;BASE['p']=(T,tl,E_,lab,plast)
    T,tl,E_,lab,plast=BASE['p'];H=T.shape[0];G=np.zeros_like(T);G[:ga.shape[0]]=ga[:H];gl=np.zeros(tl.shape,int);gl[:glab.shape[0]]=glab[:H];garm,_=_sides(G,gl);G[~garm,3]=0
    def over(X,Y):
        x=X[...,3:]/255;y=Y[...,3:]/255;oa=x+y*(1-x);o=np.zeros_like(X);o[...,:3]=(X[...,:3]*x+Y[...,:3]*y*(1-x))/np.maximum(oa,1e-6);o[...,3:]=oa*255;return o
    o=over(E_,over(G,T));l=np.where(E_[...,3]>60,lab,np.where(G[...,3]>60,gl,tl));l[o[...,3]<=60]=0;return o,l,plast

def coif(P):
    """Pour une tête sans barbe ni cou visible (heaume fermé sur les autres races) : l'INTÉRIEUR de l'encolure est rempli de mailles, à plat,
    dans l'anneau du gorgerin. On ne voit donc jamais le trou du col, et rien ne dépasse sur le plastron (pas de bavette)."""
    a,lab,plast=P;a=a.copy();lab=lab.copy();m=lab==15;c,k=ndi.label(m);big=c==(np.argmax(ndi.sum(m,c,range(1,k+1)))+1);d=ndi.distance_transform_edt(big);y,x=np.unravel_index(np.argmax(d),d.shape);r=int(d[y,x]*0.68)
    pa=a[y-r:y+r,x-r:x+r,:3];row=np.hstack([pa,pa[:,::-1]]);T=np.tile(np.vstack([row,row[::-1]]),(20,20,1))[:lab.shape[0],:lab.shape[1]]
    hole=lab==7;dd=ndi.distance_transform_edt(hole);sh=np.clip(0.55+dd/70.0,0.55,1.0)[...,None]              # ombre au bord, sous le gorgerin
    a[hole,:3]=(T*sh)[hole];lab[hole]=15;return a,lab,plast

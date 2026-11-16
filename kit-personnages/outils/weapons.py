# Armes tenues dans le poing (pose « grip ») : dessinées à part, verticales. Ici : fond blanc retiré si besoin, matières (4 métal, 28 bois, 6 cuir),
# mise à l'échelle sur la largeur du manche, raccourci en hauteur (vue plongeante), puis glissées dans le poing : les doigts repassent par-dessus.
import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import bodyseg,full,grd
# prise : hauteur (pixels de l'image d'origine) où le poing serre l'arme ; len : raccourci en hauteur
W={'spear':dict(grip=1060,len=.9,longer=(450,740,300)),'halberd':dict(grip=1060,len=.9,longer=(450,740,300)),'axe':dict(grip=930,len=.8,flip=True),'mace':dict(grip=1050,len=.8),'sword':dict(grip=1010,len=.8),
   'hammer':dict(k=1.55,grip=900,len=.8,split=405,cap=(195,85))}       # marteau de forge : tête en métal au-dessus de 'split', bout du manche (cap) en bois
SHAFT=15.5                                        # largeur du manche sur le personnage (couvre le bout de manche de la pose)
C={}
def prep(n):
    if n in C: return C[n]
    a=np.array(Image.open(f'../obj/item_{n}.png').convert('RGBA')).astype(float)
    if W[n].get('flip'): a=a[:,::-1].copy()        # lame tournée vers l'extérieur, loin de la tête
    if W[n].get('longer'):                         # arme d'allonge : on étire seulement un tronçon de hampe nue, au-dessus de la prise (la pointe garde sa forme)
        y0,y1,add=W[n]['longer'];mid=np.array(Image.fromarray(a[y0:y1].astype('uint8')).resize((a.shape[1],y1-y0+add),Image.BICUBIC)).astype(float);a=np.concatenate([a[:y0],mid,a[y1:]],0)
    lum=a[...,:3].mean(-1)
    if (a[...,3]>200).mean()>0.9:                 # fond blanc opaque : on retire tout ce qu'on atteint depuis le bord sans traverser un trait
        free=lum>225;lab,k=ndi.label(free);edge=np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]);out=np.isin(lab,edge[edge>0])
        out=ndi.binary_dilation(out,iterations=2);a[...,3]=np.where(out,0,255);a[...,3]=ndi.gaussian_filter(a[...,3],0.7)*(~out)
    al=a[...,3]>60;line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1);ml=ndi.mean(lum,comp,idx)
    kind=np.where(ml>128,4,np.where(ml>92,28,6));lab=np.zeros(al.shape,int);lab[comp>0]=kind[comp[comp>0]-1]
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    if 'split' in W[n]:
        yy,xx=np.mgrid[:al.shape[0],:al.shape[1]];sp=W[n]['split'];cy,cw=W[n]['cap'];lab[al&(yy<sp)]=4;lab[al&(yy>=sp)]=28;lab[al&(yy<cy)&(np.abs(xx-al.shape[1]/2)<cw)]=28
    g=W[n]['grip'];xs=np.where(al[g])[0];C[n]=(a,lab,(xs.min()+xs.max())/2,xs.max()-xs.min()+1);return C[n]
def layer(n,metal='#aeb4bc',wood='#8a6a42',leather='#4a3424'):
    """Arme teintée, à l'échelle du personnage ; renvoie (image, point de prise dans cette image)."""
    a,lab,cx,wd=prep(n);full.G.update({4:.95,28:.8,6:.75});t=full.tint(a,lab,{4:metal,28:wood,6:leather})
    sx=SHAFT/wd*W[n].get('k',1);sy=sx*W[n]['len'];w,h=t.size;t=t.resize((round(w*sx),round(h*sy)),Image.LANCZOS);return t,(cx*sx,W[n]['grip']*sy)
def char(P,n,tab,bord,dy=150,H=680,**kw):
    """Garde (pose grip) + arme n dans le poing. Toile 512 × H, personnage décalé de dy vers le bas."""
    a,lab=P;c=Image.new('RGBA',(512,H));c.alpha_composite(grd.char(a,lab,tab,bord,**kw),(0,dy))
    fx,fy=256+(grd.GRIP[0]-625)*.29,229+(grd.GRIP[1]-360)*.29+dy
    t,(gx,gy)=layer(n,metal=kw.get('metal','#aeb4bc'));c.alpha_composite(t,(round(fx-gx),round(fy-gy)))
    full.G.update(grd.G);b=np.array(full.tint(a,lab,{4:kw.get('metal','#aeb4bc'),5:tab,9:bord,15:'#6a6e76',16:'#3e3a3a',6:'#3a2a1c',7:'#2a2622',28:'#8a6a42'})).astype(float)
    b[...,3]*=grd.fist(a,lab);c.alpha_composite(full.place(Image.fromarray(b.astype('uint8')),0.29,(625,360)),(0,dy));return c

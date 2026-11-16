# Objets de la carte (lanterne, arc, carquois, ballot, hache de bûcheron) : dessins isolés sur fond blanc. Ici : fond retiré, matières, teinte.
# Matières : 4 métal, 28 bois, 6 cuir, 30 verre (lumière), 31 plumes, 32 toile, 33 couverture
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import bodyseg,full
COL={4:'#aeb4bc',28:'#8a6a42',6:'#4a3424',30:'#ffd98a',31:'#ece6d4',32:'#b89c6c',33:'#7a3a34'}
full.G.update({4:.95,28:.8,6:.75,30:1.05,31:.9,32:.85,33:.8})
def _kind(n,ml,cx,cy):
    if n=='lantern': return np.where(ml>205,30,4)
    if n=='bow': return np.where(ml<70,6,28)
    if n=='quiver': return np.where(ml>150,31,np.where(ml>95,28,6))
    if n=='woodaxe': return np.where(ml>128,4,28)
    if n=='bundle': return np.where(ml>170,4,np.where(ml<85,6,np.where(cy<470,33,32)))
C={}
def prep(n):
    if n in C: return C[n]
    a=np.array(Image.open(f'../obj/item_{n}.png').convert('RGBA')).astype(float);lum=a[...,:3].mean(-1)
    if (a[...,3]>200).mean()>0.9:
        free=lum>232;lab,k=ndi.label(free);edge=np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]);out=np.isin(lab,edge[edge>0])
        out=ndi.binary_dilation(out,iterations=2);a[...,3]=np.where(out,0,255);a[...,3]=ndi.gaussian_filter(a[...,3],0.7)*(~out)
    al=a[...,3]>60;line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1);ml=ndi.mean(lum,comp,idx)
    cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T;kind=_kind(n,ml,cx,cy);lab=np.zeros(al.shape,int);lab[comp>0]=kind[comp[comp>0]-1]
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    if n=='lantern':                               # vitres : les zones très claires ; l'intérieur de l'anneau est un trou
        hole,k2=ndi.label((lum>245)&al)
        for i in range(1,k2+1):
            if ndi.center_of_mass(hole==i)[0]<330: a[...,3][ndi.binary_dilation(hole==i,iterations=2)]=0
        al=a[...,3]>60;lab[~al]=0;lab[ndi.binary_opening((lum>218)&al,iterations=2)]=30
    ys,xs=np.where(al);C[n]=(a,lab,(xs.min(),ys.min(),xs.max()+1,ys.max()+1));return C[n]
def layer(n,h,cols=None,rot=0,flip=False):
    """Objet teinté, haut de h pixels (avant rotation). Renvoie l'image recadrée sur l'objet."""
    a,lab,bb=prep(n);full.G.update({4:.95,28:.8,6:.75,30:1.05,31:.9,32:.85,33:.8});t=full.tint(a,lab,{**COL,**(cols or {})}).crop(bb)
    if flip: t=t.transpose(Image.FLIP_LEFT_RIGHT)
    t=t.resize((max(1,round(t.size[0]*h/t.size[1])),h),Image.LANCZOS);return t.rotate(rot,Image.BICUBIC,expand=True) if rot else t
def put(c,t,center): c.alpha_composite(t,(round(center[0]-t.size[0]/2),round(center[1]-t.size[1]/2)));return c

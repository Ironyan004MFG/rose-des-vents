"""Découpe le calque d'un lot avec les boîtes de la planche GRISE (même taille) : quand deux coiffes du calque se touchent, split_map les fusionne."""
import numpy as np,heads
from PIL import Image
from scipy import ndimage as ndi
_orig=heads.split_map
def by_grey(path,n=8,rows=2):
    g=path.replace('map.png','gris.png');im=np.array(Image.open(g).convert('RGB')).astype(float);lum=im.mean(-1);c,k=ndi.label(lum>236)
    edge=np.unique(np.r_[c[0],c[-1],c[:,0],c[:,-1]]);bg=ndi.binary_dilation(np.isin(c,edge[edge>0]),iterations=3);fig=ndi.binary_fill_holes(~bg);cc,kk=ndi.label(fig)
    sz=ndi.sum(fig,cc,range(1,kk+1));ids=[i+1 for i in np.argsort(sz)[::-1][:n]];obs=ndi.find_objects(cc);mid=im.shape[0]/rows
    cells=sorted([(obs[i-1],i) for i in ids],key=lambda t:(int(((t[0][0].start+t[0][0].stop)/2)//mid),t[0][1].start))
    m=np.array(Image.open(path).convert('RGB')).astype(int);out=[]
    for sl,i in cells:
        p=m[sl];r,gg,b=p[...,0],p[...,1],p[...,2];lab=np.zeros(r.shape,np.uint8);lab[(r>150)&(gg<110)&(b<110)]=1;lab[(b>150)&(r<110)&(gg<110)]=2;lab[(gg>150)&(r<130)&(b<130)]=4;lab[(r>150)&(gg>150)&(b<110)]=8;lab[(r>150)&(b>150)&(gg<120)]=31;lab[(gg>150)&(b>150)&(r<120)]=6;lab[(r>200)&(gg>80)&(gg<=170)&(b<90)]=60
        lab[~ndi.binary_dilation(cc[sl]==i,iterations=4)]=0;out.append(lab)
    return out
def on(): heads.split_map=by_grey

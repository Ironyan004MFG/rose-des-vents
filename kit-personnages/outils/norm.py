# Ramène chaque corps au cadrage de référence (col au même endroit, même échelle), d'après la forme du col
from PIL import Image
import numpy as np
def collar(path):
    a=np.array(Image.open(path).convert('RGBA'))[...,3]>60
    cols=np.where(a[:,560:700].any(0))[0];top=min(np.where(a[:,560+c])[0].min() for c in cols)
    row=a[top+70];xs=np.where(row)[0];xs=xs[(xs>300)&(xs<960)]
    # largeur du col : plage continue autour du centre
    c=627;l=c
    while l>0 and row[l-1]: l-=1
    r=c
    while r<len(row)-1 and row[r+1]: r+=1
    return top,l,r
REF=collar('../c7/originaux_1254/body_dwarf_coat_relaxed.png')
def normalize(path,out):
    top,l,r=collar(path);s=(REF[2]-REF[1])/(r-l);im=Image.open(path).convert('RGBA')
    cx=(l+r)/2;rcx=(REF[1]+REF[2])/2
    # x' = rcx + s*(x-cx) ; y' = REF_top + s*(y-top)
    o=im.transform((1254,1400),Image.AFFINE,(1/s,0,cx-rcx/s,0,1/s,top-REF[0]/s),Image.BICUBIC);o.save(out);return s,top,(l,r)
if __name__=='__main__':
    import glob,os
    print('ref',REF);os.makedirs('../r2/n',exist_ok=True)
    for g in sorted(glob.glob('../r2/*/body_*.png')): print(os.path.basename(g),normalize(g,'../r2/n/'+os.path.basename(g)))

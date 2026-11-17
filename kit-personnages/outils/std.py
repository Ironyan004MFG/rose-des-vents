# CORPS STANDARD (morphologies non trapues : halfelin, humain, elfe, tieffelin, demi-orc). Carrure = pourpoint du nain resserré de 20 %
# (standard/reference_corps_standard.png). GPT dessine le corps gris, puis son CALQUE de matières en aplats ; plus aucune graine à poser.
# Couleurs du calque -> matières : ROUGE 1 peau, BLEU 5 étoffe principale, JAUNE 14 tunique / chemise, CYAN 6 cuir, VERT 4 métal,
# MAGENTA 33 toile (couverture), ORANGE 7 intérieur de l'encolure.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import brb,cui,full,legs,morpho
def labels_from_map(path):
    m=np.array(Image.open(path).convert('RGB')).astype(int);r,g,b=m[...,0],m[...,1],m[...,2];lab=np.zeros(r.shape,np.uint8)
    lab[(r>150)&(g<110)&(b<110)]=1;lab[(b>150)&(r<110)&(g<110)]=5;lab[(r>180)&(g>180)&(b<120)]=14;lab[(g>140)&(b>180)&(r<140)]=6
    lab[(g>120)&(r<130)&(b<130)]=4;lab[(r>180)&(b>180)&(g<120)]=33;lab[(r>200)&(g>80)&(g<=175)&(b<90)]=7
    fg=ndi.binary_fill_holes(ndi.binary_closing((m.max(-1)-m.min(-1)>60),iterations=2));c,k=ndi.label(fg);fg=c==(np.argmax(ndi.sum(fg,c,range(1,k+1)))+1);ys,xs=np.where(fg);return lab[ys.min():ys.max()+1,xs.min():xs.max()+1]
def prep(grey,mp,tag=''):
    """grey : corps détouré (RGBA, cadrage de la référence) ; mp : son calque. Renvoie (image, étiquettes) normalisées comme les corps du nain."""
    im=Image.open(grey).convert('RGBA');a=np.array(im).astype(float);al=a[...,3]>40;ys,xs=np.where(al);L=np.zeros(al.shape,np.uint8);m=labels_from_map(mp)
    L[ys.min():ys.max()+1,xs.min():xs.max()+1]=np.array(Image.fromarray(m).resize((xs.max()-xs.min()+1,ys.max()-ys.min()+1),Image.NEAREST))
    _,ix=ndi.distance_transform_edt(L==0,return_indices=True);L=L[ix[0],ix[1]];L[~al]=0
    top,l,r=brb.norm.collar(grey);s=cui.SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-brb.norm.REF[0]/s)
    A=np.array(im.transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);Lb=np.array(Image.fromarray(L).transform((1254,1500),Image.AFFINE,M,Image.NEAREST)).astype(int);return A,Lb
G={1:.8,5:.72,14:.85,6:.72,4:.95,33:.8,7:1.0}
def shade(sk,k=.74):
    return '#%02x%02x%02x'%tuple(int(int(sk[i:i+2],16)*k*f) for i,f in ((1,1.0),(3,.95),(5,.92)))
def char(P,cols,pants='#4a4038',boots='#3a2a1c',ph=0,H=560,larg=.8):
    """Sous une tête sans barbe, l'intérieur de l'encolure (7) est la PEAU du cou, un peu plus foncée (ombre du menton).
    cols : {matière: couleur}. Les jambes du nain sont resserrées à la même largeur que le corps standard."""
    a,lab=P;full.G.update(G);c=Image.new('RGBA',(512,H));lg=morpho.body(brb._legs(pants,boots,ph),larg=larg);c.alpha_composite(lg,((512-lg.size[0])//2,brb.DY))
    im=full.tint(a,lab,{7:shade(cols[1]),**cols});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o);return c

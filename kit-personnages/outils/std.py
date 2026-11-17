# CORPS STANDARD (morphologies non trapues : halfelin, humain, elfe, tieffelin, demi-orc). Carrure = pourpoint du nain resserré de 20 %
# (standard/reference_corps_standard.png). GPT dessine le corps gris, puis son CALQUE de matières en aplats ; plus aucune graine à poser.
# Couleurs du calque -> matières : ROUGE 1 peau, BLEU 5 étoffe principale, JAUNE 14 tunique / chemise, CYAN 6 cuir, VERT 4 métal,
# MAGENTA 33 toile (couverture), ORANGE 7 intérieur de l'encolure.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import brb,cui,full,legs,morpho
def labels_from_map(path):
    # silhouette = tout ce qui n'est pas le fond blanc (les traits noirs relient les zones)
    m=np.array(Image.open(path).convert('RGB')).astype(int);r,g,b=m[...,0],m[...,1],m[...,2];lab=np.zeros(r.shape,np.uint8)
    lab[(r>150)&(g<110)&(b<110)]=1;lab[(b>150)&(r<110)&(g<110)]=5;lab[(r>180)&(g>180)&(b<120)]=14;lab[(g>140)&(b>180)&(r<140)]=6
    lab[(g>120)&(r<130)&(b<130)]=4;lab[(r>180)&(b>180)&(g<120)]=33;lab[(r>200)&(g>80)&(g<=175)&(b<90)]=7
    fg=ndi.binary_fill_holes(ndi.binary_opening(m.min(-1)<215,iterations=2));c,k=ndi.label(fg);fg=c==(np.argmax(ndi.sum(fg,c,range(1,k+1)))+1);ys,xs=np.where(fg);return lab[ys.min():ys.max()+1,xs.min():xs.max()+1]
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

def prep_from(grey,ref):
    """Pose dessinée à partir de `ref` (déjà préparé) : même torse, bras déplacés. Les matières ne viennent PAS d'un calque de la pose
    (le calque GPT d'une pose ne retombe jamais exactement sur son gris) : on mesure le déplacement de chaque point entre le gris de `ref`
    et celui de la pose (flot optique), et on déplace les matières de `ref` du même mouvement."""
    import cv2
    im=Image.open(grey).convert('RGBA');top,l,r=brb.norm.collar(grey);s=cui.SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-brb.norm.REF[0]/s)
    A=np.array(im.transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);A0,L0=ref;al=A[...,3]>40
    g=lambda X:np.where(X[...,3]>40,X[...,:3].mean(-1),255.).astype('uint8');G1,G0=g(A),g(A0)
    dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM);dis.setFinestScale(1);fl=dis.calc(G1,G0,None);yy,xx=np.mgrid[0:1500,0:1254].astype('float32')   # pour chaque point de la pose : où il était dans ref
    L=cv2.remap(L0.astype('uint8'),xx+fl[...,0],yy+fl[...,1],cv2.INTER_NEAREST);W=cv2.remap(G0,xx+fl[...,0],yy+fl[...,1],cv2.INTER_LINEAR)
    bad=ndi.binary_opening(np.abs(W.astype(float)-G1)>60,iterations=2);L=L.astype(int);L[bad]=0
    _,ix=ndi.distance_transform_edt(L==0,return_indices=True);L=L[ix[0],ix[1]];L[~al]=0;print('déplacement max :',round(float(np.hypot(fl[...,0],fl[...,1])[al].max())),'px ; points non retrouvés :',round(100*bad[al].mean(),1),'%');return A,L

def paint(P,polys):
    """Retouche des matières d'une pose : polys = [(matière, [(x,y),...]), ...] sur la toile normalisée (1254 x 1500), appliqués dans l'ordre.
    Pour un membre qui change de forme (bras tendu) : le flot optique ne le retrouve pas, on pose ses bandes à la main."""
    from PIL import ImageDraw
    A,L=P;L=L.copy()
    for lab,pts in polys:
        m=Image.new('L',(1254,1500),0);ImageDraw.Draw(m).polygon(pts,fill=255);L[(np.array(m)>0)&(A[...,3]>40)]=lab
    return A,L
def snap(P,box,thr=85,mats=(1,14,6)):
    """Dans la boîte (x0,y0,x1,y1), cale les matières sur le DESSIN : chaque plage fermée par des traits foncés prend la matière majoritaire
    qu'elle contient (parmi `mats`). Les polygons de `paint` n'ont alors plus besoin de suivre les bords au pixel près."""
    A,L=P;L=L.copy();x0,y0,x1,y1=box;g=A[y0:y1,x0:x1,:3].mean(-1);al=A[y0:y1,x0:x1,3]>40;sub=L[y0:y1,x0:x1];ok=np.isin(sub,mats)&al
    c,k=ndi.label(ok&(ndi.gaussian_filter(g,1.2)>thr))
    for i in range(1,k+1):
        m=c==i
        if m.sum()<150: continue
        v=np.bincount(sub[m],minlength=64);sub[m]=v.argmax()
    lines=ok&(c==0);_,ix=ndi.distance_transform_edt((c==0)|~ok,return_indices=True);sub[lines]=sub[ix[0],ix[1]][lines];L[y0:y1,x0:x1]=sub;return A,L
# aventurier standard, bras tendu (à gauche de l'image) : manche du manteau, revers clair, avant-bras, bracelet, main ouverte
REACH_ADV=[(5,[(150,450),(385,450),(385,760),(330,760),(330,600),(150,600)]),
           (1,[(214,630),(392,630),(374,700),(332,724),(215,716)]),
           (14,[(200,602),(240,580),(300,586),(386,612),(394,632),(384,642),(350,651),(300,656),(232,652),(200,640)]),
           (6,[(200,716),(324,712),(334,742),(304,806),(205,800)]),
           (1,[(100,800),(205,798),(304,804),(306,1150),(100,1150)])]

def mage(grey='../std/mage_relaxed.png',mp='../std/mage_relaxed_map.png'):
    """Mage standard au repos. Le calque peint en ORANGE tout le rond de l'encolure, col compris : la face intérieure du col montant
    (anneau clair autour du trou sombre) est rendue à la robe (5)."""
    A,L=prep(grey,mp);g=ndi.gaussian_filter(A[...,:3].mean(-1),3);ring=(L==7)&(g>92);ring=ndi.binary_opening(ring,iterations=3);cc,k=ndi.label(ring);ring=cc==(1+np.argmax(ndi.sum(ring,cc,range(1,k+1))));L=L.copy();L[ring]=5;return A,L

def pierce(path,thr=244,minsize=600):
    """Vides blancs enfermés (entre un bras et le corps) : le détourage ne les atteint pas depuis le bord. On les rend transparents."""
    im=Image.open(path).convert('RGBA');a=np.array(im);w=(a[...,:3].min(-1)>thr)&(a[...,3]>40);c,k=ndi.label(w);n=0
    for i in range(1,k+1):
        m=c==i
        if m.sum()>=minsize: a[ndi.binary_dilation(m,iterations=2),3]=0;n+=1
    Image.fromarray(a).save(path);return n
# mage standard, bras tendu : seule la main est à poser (la manche est retrouvée par le flot) ; 5 = intérieur sombre de la manche
REACH_MAGE=[(1,[(128,905),(160,842),(200,802),(302,802),(310,1060),(120,1060)]),(5,[(300,790),(345,790),(345,885),(304,885)])]

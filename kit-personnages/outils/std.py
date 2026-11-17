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
    im=full.tint(a,lab,{7:shade(cols[1]),**cols});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-(625+(w-1254)//2)*.29),round(229-360*.29)));c.alpha_composite(o);return c

def prep_from(grey,ref,pad=0):
    """Pose dessinée à partir de `ref` (déjà préparé) : même torse, bras déplacés. Les matières ne viennent PAS d'un calque de la pose
    (le calque GPT d'une pose ne retombe jamais exactement sur son gris) : on mesure le déplacement de chaque point entre le gris de `ref`
    et celui de la pose (flot optique), et on déplace les matières de `ref` du même mouvement."""
    import cv2
    im=Image.open(grey).convert('RGBA');top,l,r=brb.norm.collar(grey);s=cui.SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s-pad/s,0,1/s,top-brb.norm.REF[0]/s)
    # pad : marge ajoutée à gauche et à droite de la toile normalisée, pour un objet qui dépasse (fourche, canne)
    W_=1254+2*pad;A=np.array(im.transform((W_,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);A0,L0=ref;A0=np.pad(A0,((0,0),(pad,pad),(0,0)));L0=np.pad(L0,((0,0),(pad,pad)));al=A[...,3]>40
    g=lambda X:np.where(X[...,3]>40,X[...,:3].mean(-1),255.).astype('uint8');G1,G0=g(A),g(A0)
    dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM);dis.setFinestScale(1);fl=dis.calc(G1,G0,None);yy,xx=np.mgrid[0:1500,0:W_].astype('float32')   # pour chaque point de la pose : où il était dans ref
    L=cv2.remap(L0.astype('uint8'),xx+fl[...,0],yy+fl[...,1],cv2.INTER_NEAREST);W=cv2.remap(G0,xx+fl[...,0],yy+fl[...,1],cv2.INTER_LINEAR)
    bad=ndi.binary_opening(np.abs(W.astype(float)-G1)>60,iterations=2);L=L.astype(int);L[bad]=0
    _,ix=ndi.distance_transform_edt(L==0,return_indices=True);L=L[ix[0],ix[1]];L[~al]=0;print('déplacement max :',round(float(np.hypot(fl[...,0],fl[...,1])[al].max())),'px ; points non retrouvés :',round(100*bad[al].mean(),1),'%');return A,L

def paint_light(P,polys,thr=105):
    """Comme paint, mais seulement sur ce qui est CLAIR (peau, toile claire) : les parties foncées voisines (salopette) gardent leur matière."""
    A,L0=P;g=ndi.gaussian_filter(A[...,:3].mean(-1),2);_,L=paint(P,polys);dark=(g<=thr)&(L!=L0);L[dark]=np.where(L0[dark]==1,5,L0[dark]);return A,L
def paint(P,polys):
    """Retouche des matières d'une pose : polys = [(matière, [(x,y),...]), ...] sur la toile normalisée (1254 x 1500), appliqués dans l'ordre.
    Pour un membre qui change de forme (bras tendu) : le flot optique ne le retrouve pas, on pose ses bandes à la main."""
    from PIL import ImageDraw
    A,L=P;L=L.copy()
    for lab,pts in polys:
        m=Image.new('L',(A.shape[1],A.shape[0]),0);ImageDraw.Draw(m).polygon([tuple(p) for p in pts],fill=255);L[(np.array(m)>0)&(A[...,3]>40)]=lab
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

def prep_fit(grey,mp,sig=6):
    """Comme prep, mais le calque est d'abord RECALÉ sur le gris : GPT ne repeint jamais exactement la même image (corde, pièces, col
    décalés de 10 à 30 px). On compare les TRAITS foncés des deux images (floutés) et on déforme le calque pour qu'ils se superposent."""
    import cv2
    im=Image.open(grey).convert('RGBA');a=np.array(im).astype(float);al=a[...,3]>40;ys,xs=np.where(al);y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    m=np.array(Image.open(mp).convert('RGB')).astype(int);fg=ndi.binary_fill_holes(ndi.binary_opening(m.min(-1)<215,iterations=2));c,k=ndi.label(fg);fg=c==(np.argmax(ndi.sum(fg,c,range(1,k+1)))+1)
    my,mx=np.where(fg);mc=Image.fromarray(m[my.min():my.max()+1,mx.min():mx.max()+1].astype('uint8')).resize((x1-x0,y1-y0),Image.LANCZOS);mc=np.array(mc).astype(int)
    lab=labels_from_map(mp);lab=np.array(Image.fromarray(lab).resize((x1-x0,y1-y0),Image.NEAREST))
    g=a[y0:y1,x0:x1,:3].mean(-1);eg=((g<75)|~al[y0:y1,x0:x1]).astype(float);em=(mc.max(-1)<90).astype(float)
    f=lambda e:np.clip(ndi.gaussian_filter(e,sig)*255*2.2,0,255).astype('uint8');dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM);fl=dis.calc(f(eg),f(em),None)
    fl[...,0]=ndi.gaussian_filter(fl[...,0],12);fl[...,1]=ndi.gaussian_filter(fl[...,1],12);yy,xx=np.mgrid[0:y1-y0,0:x1-x0].astype('float32')
    lw=cv2.remap(lab.astype('uint8'),xx+fl[...,0],yy+fl[...,1],cv2.INTER_NEAREST);L=np.zeros(al.shape,np.uint8);L[y0:y1,x0:x1]=lw
    _,ix=ndi.distance_transform_edt(L==0,return_indices=True);L=L[ix[0],ix[1]];L[~al]=0;print('recalage du calque : déplacement moyen',round(float(np.hypot(fl[...,0],fl[...,1]).mean()),1),'px, max',round(float(np.hypot(fl[...,0],fl[...,1]).max())))
    top,l,r=brb.norm.collar(grey);s=cui.SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-brb.norm.REF[0]/s)
    A=np.array(im.transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);Lb=np.array(Image.fromarray(L).transform((1254,1500),Image.AFFINE,M,Image.NEAREST)).astype(int);return A,Lb

# FERMIER standard : le calque GPT ne retombe pas sur le gris (corde, pièces, bretelles déplacées). Les matières sont posées par polygones
# grossiers sur la toile normalisée, puis calées sur les traits du dessin (snap). 14 chemise, 5 salopette, 6 corde, 33 pièces, 4 métal.
_mx=lambda pts:[(1250-x,y) for x,y in pts]
_circ=lambda x,y,r:[(x+r*np.cos(t),y+r*np.sin(t)) for t in np.linspace(0,6.283,24)]
_ARM=[(205,628),(352,618),(378,650),(368,815),(225,815)]
_BUCK=[(416,486),(493,470),(501,536),(427,549)]
FARMER=[(14,[(0,0),(1254,0),(1254,1500),(0,1500)]),(1,_ARM),(1,_mx(_ARM)),
        (5,[(403,292),(452,280),(470,440),(490,530),(540,556),(710,556),(760,530),(780,440),(798,280),(847,292),(852,560),(882,700),(955,930),(900,1015),(625,1070),(350,1015),(295,930),(368,700),(398,560)]),
        (7,_circ(625,332,173)),(7,[(560,470),(690,470),(628,520)]),
        (6,[(358,712),(450,742),(560,768),(625,762),(690,768),(800,742),(890,712),(890,752),(800,792),(705,805),(745,930),(678,940),(650,832),(600,832),(562,950),(500,932),(548,805),(450,792),(358,752)]),
        (33,[(693,610),(735,598),(782,624),(772,692),(740,702),(690,680)]),(33,[(384,868),(490,924),(456,1016),(347,952)]),
        (4,_BUCK),(4,_mx(_BUCK)),(4,_circ(467,558,11)),(4,_circ(783,558,11)),(4,_circ(600,512,10)),(4,_circ(650,512,10)),(4,_circ(650,538,10))]
def farmer_labels(A):
    """Polygones grossiers + gris : dans la zone de la salopette, ce qui est clair est de la chemise ; la corde est claire, les pièces
    sont d'un gris moyen, la salopette est foncée. Les avant-bras ne prennent que ce qui est clair (le reste est la salopette)."""
    from PIL import ImageDraw
    al=A[...,3]>40;g=ndi.gaussian_filter(A[...,:3].mean(-1),2.5);L=np.zeros(al.shape,int)
    def poly(pts):
        m=Image.new('L',(1254,1500),0);ImageDraw.Draw(m).polygon([tuple(p) for p in pts],fill=255);return (np.array(m)>0)&al
    D={k:np.zeros(al.shape,bool) for k in (1,5,7,6,33,4)}
    for lab,pts in FARMER[1:]: D[lab]|=poly(pts)
    L[al]=14;ov=D[5]&(g<128);ov=ndi.binary_closing(ov,iterations=4)&D[5];X=np.arange(1254)[None,:];ov&=~((g>146)&((X<405)|(X>845)));L[ov]=5
    arm=ndi.binary_dilation(D[1],iterations=12)&al&(g>=128)&~D[5]|(D[1]&(g>=128));L[arm&(L!=5)]=1;L[D[1]&(g>=140)]=1
    L[D[7]]=7;rope=D[6]&(g>104);rope=ndi.binary_closing(ndi.binary_opening(rope,iterations=2),iterations=5)&D[6];L[rope]=6
    for pts in (FARMER[7][1],FARMER[8][1]):
        p=poly(pts);inner=ndi.binary_fill_holes(ndi.binary_closing(p&(g>88),iterations=5))&ndi.binary_dilation(p,iterations=6)&al;L[inner&(L!=6)]=33
    L[D[4]]=4;L[~al]=0;return L
def farmer(grey='../std/far_relaxed.png'):
    A,L2=prep(grey,'../std/far_relaxed_map2.png');L=farmer_labels(A);g=ndi.gaussian_filter(A[...,:3].mean(-1),2.5);m=(L==5)&np.isin(L2,(14,1))&(g>120);L[m]=L2[m]      # bords clairs des bretelles : le 2e calque de GPT les voit mieux
    return collar(snap((A,L),(150,560,1100,840),thr=80,mats=(1,14)),14)

def collar(P,to,thr=92):
    """Le bord et la paroi intérieure de l'encolure appartiennent au VÊTEMENT (col de chemise, de tunique, de robe), pas à la peau :
    dans le rond de l'encolure (7), seul le fond sombre reste le cou. `to` = matière du vêtement."""
    A,L=P;g=ndi.gaussian_filter(A[...,:3].mean(-1),3);n=L==7;dome=n&(g<=thr);cc,k=ndi.label(dome)
    if k: dome=ndi.binary_fill_holes(cc==(1+np.argmax(ndi.sum(dome,cc,range(1,k+1)))))
    L=L.copy();L[n&~dome]=to;return A,L
# fermier standard, bras tendu : avant-bras nu et main ouverte (le flot perd le bout des doigts)
REACH_FARMER=[(1,[(160,740),(215,700),(222,612),(340,600),(332,700),(318,830),(298,925),(160,925)])]

# FERMIER AU PANIER. Coordonnées relevées sur la toile normalisée ; _d décale celles lues sur l'aperçu quadrillé (150,500).
# 61 osier, 62 carottes, 63 fanes, 64 chou, 65 navets, 66 pommes de terre, 67 oignons.
G.update({61:.8,62:.85,63:.8,64:.85,65:.9,66:.8,67:.85})
_d=lambda pts:[(x+150,y+500) for x,y in pts]
_ell=lambda cx,cy,rx,ry:[(cx+rx*np.cos(t),cy+ry*np.sin(t)) for t in np.linspace(0,6.283,48)]
_FARM=[(95,104),(250,98),(258,228),(150,228),(100,160)];_HAND=[(150,228),(258,228),(272,300),(250,320),(220,300),(200,330),(205,385),(215,422),(175,390),(150,330)]
CARRY_FARMER=[(61,_ell(625,917,287,264))]+[(l,_d(p)) for l,p in [
    (63,[(268,200),(310,200),(350,180),(440,175),(465,215),(460,285),(410,282),(400,298),(372,290),(340,303),(300,300),(268,270)]),(63,[(245,315),(340,315),(345,350),(330,385),(290,395),(250,385)]),
    (62,[(338,305),(372,292),(400,300),(408,283),(455,285),(470,330),(470,400),(445,432),(415,405),(380,372),(350,340)]),
    (64,[(470,215),(560,205),(650,230),(672,285),(640,360),(600,395),(540,385),(490,350),(458,290)]),
    (65,[(275,385),(345,385),(375,410),(370,470),(330,495),(280,470),(268,420)]),(65,[(358,430),(385,400),(400,425),(445,435),(455,480),(420,510),(370,505),(352,470)]),
    (66,[(448,405),(500,385),(545,405),(555,440),(585,455),(590,490),(555,512),(500,510),(470,480),(445,450)]),
    (67,[(555,400),(600,365),(615,380),(650,400),(665,430),(640,455),(590,455),(560,440)]),(67,[(620,360),(665,325),(680,345),(705,370),(712,405),(690,425),(660,415),(645,395)])]]
CARRY_ARMS=[(1,_d(_FARM)),(1,_d(_HAND)),(1,_mx(_d(_FARM))),(1,_mx(_d(_HAND)))]
def farmer_carry(P):
    P=paint(P,CARRY_FARMER);P=paint_light(P,CARRY_ARMS[::2],thr=120);P=paint(P,CARRY_ARMS[1::2])
    P=snap(P,(200,580,1050,1120),thr=78,mats=(1,14,61,62,63,64,65,66,67))
    # carottes et fanes se touchent sans trait fermé entre elles : on les repose après le calage (parties claires seulement)
    A,L=P;g=ndi.gaussian_filter(A[...,:3].mean(-1),2);Q=paint(P,[CARRY_FARMER[3],CARRY_FARMER[2]]);L2=Q[1];m=(L2!=L)&(g>80)&np.isin(L,(62,63,65,61));L=L.copy();L[m]=L2[m];return A,L

# FERMIER À LA FOURCHE (toile élargie de pad=120 : coordonnées décalées d'autant). 68 = bois du manche, 4 = fer des dents.
G.update({68:.85})
FORK_FARMER=[(14,[(1005,380),(1215,380),(1215,600),(1005,600)]),(4,[(1015,40),(1215,40),(1215,356),(1084,356),(1084,300),(1015,300)]),
             (68,[(1088,352),(1138,352),(1138,1105),(1088,1105)]),(1,[(1056,596),(1172,596),(1172,716),(1074,716)])]
def farmer_fork(P):
    P=paint_light(P,FORK_FARMER[:1],thr=120);P=paint(P,FORK_FARMER[1:]);return snap(P,(1000,360,1260,730),thr=80,mats=(1,14,68))

# FERMIER, FOURCHE AU TRAVAIL (tenue à deux mains, en biais). Coordonnées lues sur l'aperçu quadrillé, décalées de (150,450).
_w=lambda pts:[(x+150,y+450) for x,y in pts]
WORK_FARMER=[(14,_w([(640,170),(650,60),(830,60),(840,170),(800,250),(770,235),(650,185)])),(14,_w([(70,40),(250,40),(260,134),(200,152),(100,152),(70,110)])),
             (68,_w([(268,235),(300,212),(545,470),(515,500)])),
             (1,_w([(196,152),(262,136),(318,205),(318,250),(285,278),(245,270),(215,250),(190,215)])),
             (1,_w([(650,185),(775,238),(752,305),(612,368),(555,440),(480,455),(430,420),(415,375),(450,345),(540,330),(600,250)])),
             (4,_w([(495,480),(530,455),(560,480),(640,560),(640,655),(520,668),(495,560)]))]
def farmer_work(P):
    P=paint_light(P,WORK_FARMER[:2],thr=120);P=paint(P,WORK_FARMER[2:]);P=snap(P,(200,440,1060,930),thr=80,mats=(1,14,68));P=paint_light(P,WORK_FARMER[5:],thr=125)
    # autour des dents, le flot laisse des restes : tout ce qui est foncé y est la salopette
    A,L=P;g=ndi.gaussian_filter(A[...,:3].mean(-1),2);Q=paint(P,[(5,_w([(540,440),(680,440),(680,640),(540,640)]))])[1];m=(Q!=L)&(g<118)&(L!=68);L=L.copy();L[m]=5;return A,L

# FERMIER PÊCHEUR (toile élargie pad=120). GPT ne dessine que le manche tenu à deux mains ; canne, fil et bouchon sont ajoutés en code.
_f=lambda pts:[(x+150,y+150) for x,y in pts]
FISH_FARMER=[(14,_f([(195,330),(260,210),(380,150),(440,330),(455,470),(380,470),(250,500),(200,470)])),(14,_f([(760,330),(900,200),(980,420),(975,500),(940,550),(880,470),(790,470)])),
             (68,_f([(180,35),(215,15),(695,790),(650,815)])),
             (1,_f([(240,500),(385,470),(440,485),(500,470),(545,500),(555,565),(525,625),(440,630),(330,615),(245,565)])),
             (1,_f([(775,470),(885,470),(945,550),(920,605),(770,690),(680,765),(600,760),(555,700),(530,650),(560,600),(650,600),(740,560)]))]
def farmer_fish(P):
    P=paint_light(P,FISH_FARMER[:2],thr=120);P=paint_light(P,FISH_FARMER[2:3],thr=60);P=paint_light(P,FISH_FARMER[3:],thr=118);return rim(snap(P,(300,150,1200,1000),thr=80,mats=(1,14,68)))

def fishing(c,P,top=160,H=800,length=215,bob=0.0,bend=0.0,over=46):
    """c : fermier pêcheur (std.char), P : sa pose (pour lire le manche, matière 68). Renvoie une toile plus haute (personnage décalé de `top`)
    avec la canne, le fil qui retombe dans l'eau DEVANT lui (bas de l'image) et le bouchon. La canne est posée PAR-DESSUS le haut du manche
    dessiné, sur son axe exact, à sa largeur et à sa couleur : elle se fond dedans (pas de raccord). bend : flexion ; bob : enfoncement du bouchon."""
    from PIL import ImageDraw
    A,L=P;pad=(L.shape[1]-1254)//2;ys,xs=np.where(L==68);X=256+(xs-pad-625)*.29;Y=229+(ys-360)*.29;m=np.array([X.mean(),Y.mean()]);D=np.stack([X-m[0],Y-m[1]],1)
    u=np.linalg.svd(D,full_matrices=False)[2][0];u=u if u[1]<0 else -u;s=D@u;n=np.array([-u[1],u[0]]);near=s>np.percentile(s,70);w0=2*np.percentile(np.abs(D[near]@n),96);e=m+u*np.percentile(s,99.5)   # e : bout haut du manche
    ca=np.array(c).astype(float);sel=(np.abs(D@n)<w0*.25)&near;px=ca[np.clip(Y[sel].round().astype(int),0,ca.shape[0]-1),np.clip(X[sel].round().astype(int),0,511),:3];W=tuple(int(v) for v in px.mean(0))
    K=3;o=Image.new('RGBA',(512*K,H*K));d=ImageDraw.Draw(o);x0,y0=e-u*over;y0+=top;pts=[]
    for i in range(61):
        q=i/60;k=max(0,(q*(length+over)-over)/length);pts.append((x0+u[0]*(length+over)*q+bend*14*k*k,y0+u[1]*(length+over)*q,w0-(w0-2.4)*k**.75))
    def band(ws):
        l=[];r=[]
        for (px_,py_,_),w in zip(pts,ws):
            l.append(((px_+n[0]*w/2)*K,(py_+n[1]*w/2)*K));r.append(((px_-n[0]*w/2)*K,(py_-n[1]*w/2)*K))
        return l+r[::-1]
    i0=next(i for i,p in enumerate(pts) if p[1]<e[1]+top+1)                      # premier point au-delà du manche dessiné
    d.polygon(band([p[2]+2.0 for p in pts])[i0:len(pts)*2-i0],fill=(30,22,16,255));d.polygon(band([p[2]-(1.6 if i<i0 else 0) for i,p in enumerate(pts)]),fill=W+(255,))
    tx,ty,_=pts[-1];bx,by=tx+70,H-52+bob*5;q=[((1-v)**2*tx+2*v*(1-v)*(tx+8)+v*v*bx,(1-v)**2*ty+2*v*(1-v)*(ty+(by-ty)*.55)+v*v*by) for v in np.linspace(0,1,40)]
    d.line([(x*K,y*K) for x,y in q],fill=(235,232,220,235),width=round(1.3*K))
    d.ellipse([(bx-13)*K,(by-5)*K,(bx+13)*K,(by+7)*K],outline=(225,235,245,150),width=K);d.ellipse([(bx-6)*K,(by-7)*K,(bx+6)*K,(by+5)*K],fill=(240,236,226,255),outline=(30,22,16,255),width=K);d.pieslice([(bx-6)*K,(by-7)*K,(bx+6)*K,(by+5)*K],180,360,fill=(190,50,40,255),outline=(30,22,16,255),width=K)
    o=o.resize((512,H),Image.LANCZOS);out=Image.new('RGBA',(512,H));out.alpha_composite(c,(0,top));out.alpha_composite(o);return out

def rim(P,frm=5,to=1,thr=128,r=14):
    """Liseré clair resté à la matière `frm` (salopette) le long d'un membre posé devant elle : ce qui est clair et collé à `to` (peau) lui revient."""
    A,L=P;g=ndi.gaussian_filter(A[...,:3].mean(-1),1.5);m=(L==frm)&(g>thr)&ndi.binary_dilation(L==to,iterations=r);L=L.copy();L[m]=to;return A,L

# FERMIER QUI MÈNE UNE BÊTE (pad=120) : le poing à droite de l'image tient un bout de corde (6). La longueur jusqu'à la bête est ajoutée en code.
LEAD_FARMER=[(1,[(1025,600),(1150,590),(1160,700),(1155,790),(1090,805),(1020,790)]),(6,[(1140,690),(1175,615),(1215,612),(1212,680),(1165,725)]),(6,[(1018,758),(1060,752),(1062,800),(1050,848),(1015,842)])]
def farmer_lead(P): return snap(paint(P,LEAD_FARMER),(1000,580,1240,860),thr=80,mats=(1,6,14))

def adventurer(grey='../std/adv_relaxed.png',mp='../std/adv_relaxed_map.png'):
    """Aventurier standard au repos ; le bord de l'encolure est le col de la tunique (14), pas de la peau."""
    return collar(prep(grey,mp),14)

# BARBARE FEMME : le flot retrouve le bras ; restent à poser la main ouverte (bras tendu) et les deux bouts du manche (prise d'arme, 68 = bois).
REACH_BARB_F=[(1,[(100,822),(295,822),(295,1070),(100,1070)])]
GRIP_BARB_F=[(68,[(298,605),(352,605),(352,668),(298,668)]),(68,[(296,800),(350,800),(350,855),(296,855)])]
def barb_f_reach(P): return _brace(paint(paint_light(P,REACH_BARB_F,thr=120),[(1,[(100,852),(300,852),(328,862),(330,1070),(100,1070)])]),(165,762,292,836))      # sous le bracelet, toute la main est de la peau (ombres comprises)
def barb_f_grip(P):
    A,L=paint(P,GRIP_BARB_F);g=ndi.gaussian_filter(A[...,:3].mean(-1),2);m=(L==68)&(g>150)&(np.arange(L.shape[0])[:,None]>640);L[m]=1;return A,L      # le haut du pouce reste en peau

def _brace(P,box):
    """Bracelet clouté d'un bras qui a bougé : dans la boîte, ce qui est très clair est un clou (métal), le reste est du cuir."""
    A,L=P;L=L.copy();x0,y0,x1,y1=box;g=ndi.gaussian_filter(A[...,:3].mean(-1),1.5)[y0:y1,x0:x1];al=A[y0:y1,x0:x1,3]>40;s=L[y0:y1,x0:x1];s[al&(g>168)]=4;s[al&(g<=168)]=6;return A,L

def guard(grey='../std/grd_relaxed.png',mp='../std/grd_relaxed_map.png'):
    """Garde standard. NE PAS passer `pierce` sur une armure : les reflets blancs du métal seraient percés. Dans le calque, ORANGE = mailles
    partout (manches, flancs, encolure remplie) -> 15 ; aucune peau."""
    A,L=prep(grey,mp);L=L.copy();L[L==7]=15;L[L==1]=4;G.update({5:.85,15:.8,14:.85,4:.95});return A,L

# GARDE STANDARD. Prise d'arme : gantelet (métal) et bouts du manche (68). Lanterne (toile élargie pad=120) : bras et lanterne en métal,
# vitres = 70 (lueur, à teinter en jaune chaud et à faire vaciller) ; le vide blanc entre le bras et le corps est rendu transparent.
G.update({70:1.0})
GRIP_GUARD=[(4,[(215,592),(265,572),(350,600),(380,612),(448,625),(448,715),(395,737),(300,737),(225,692)]),(68,[(378,548),(422,548),(422,614),(378,614)]),(68,[(376,722),(422,722),(422,790),(376,790)])]
def guard_grip(P): return paint(P,GRIP_GUARD)
def guard_lantern(P):
    from PIL import ImageDraw
    A,L=P;A=A.copy();g=A[...,:3].mean(-1)
    m=Image.new('L',(A.shape[1],A.shape[0]),0);ImageDraw.Draw(m).polygon([(425,585),(510,585),(510,810),(425,810)],fill=255);hole=(np.array(m)>0)&(A[...,:3].min(-1)>236);A[ndi.binary_dilation(hole,iterations=2),3]=0
    P=paint((A,L),[(4,[(250,548),(462,548),(455,700),(470,800),(470,1260),(250,1260)])]);A,L=P
    box=np.zeros(L.shape,bool);box[1015:1165,300:440]=True;gl=box&(ndi.gaussian_filter(g,1.5)>205);gl=ndi.binary_opening(gl,iterations=2);L[gl]=70;L[A[...,3]<=40]=0;return A,L

def plates(grey='../std/plt_relaxed.png'):
    """Plates standard. Le calque de GPT a redessiné un autre corps (inutilisable) : tout est métal (4) ; les mailles (15) sont reprises du
    garde là où le dessin est resté grenu (manches, encolure) ; la ceinture (6) est la grande bande sombre du torse."""
    A,_=prep(grey,'../std/grd_relaxed_map.png');A0,L0=guard();al=A[...,3]>40;g=A[...,:3].mean(-1);L=np.where(al,4,0)
    v=ndi.gaussian_filter((g-ndi.gaussian_filter(g,3))**2,6)**.5;mail=ndi.binary_dilation(L0==15,iterations=6)&(v>17)&al;mail=ndi.binary_opening(ndi.binary_closing(mail,iterations=6),iterations=4);L[mail]=15
    # la ceinture : bande courbe relevée sur un gros plan (coordonnées du gros plan -> toile), limitée à ce qui est sombre (la boucle reste en métal)
    Z=[(215,418),(330,452),(450,478),(570,478),(690,452),(800,420),(800,482),(690,524),(570,552),(450,552),(330,524),(215,480)]
    pts=[((130+x/4-256)/.29+625,(230+y/4-229)/.29+360) for x,y in Z];Lb=paint((A,np.where(al,4,0)),[(6,pts)])[1];L[(Lb==6)&(ndi.gaussian_filter(g,1.5)<150)]=6
    G.update({15:.8,4:.95,6:.75});return A,L

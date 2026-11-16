# Forgeron (bras et épaules nus, tablier de cuir retenu par une lanière autour du cou, large ceinture). Corps dessiné par GPT, ses propres poses.
# Matières : 1 peau, 35 tablier, 6 cuir (lanière, ceinture), 4 métal (boucle, rivets), 7 intérieur de l'encolure.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import brb,full,kit,legs
SEEDS={7:[(628,420),(540,430),(720,430),(628,300),(628,520),(560,290),(700,290)],
 6:[(628,165),(400,330),(857,330),(420,450),(835,450),(500,530),(760,530),(350,810),(900,810),(450,850),(800,850),(250,760),(1000,760),(500,880),(760,880),(592,872),(665,872)],
 35:[(628,620),(550,650),(700,650),(628,720),(450,740),(800,740),(628,1000),(400,950),(850,950),(300,900),(950,900),(500,1060),(750,1060),(628,1080),(250,890),(1000,890)],
 4:[(628,828),(555,885),(700,885),(628,940)],
 1:[(300,330),(950,330),(250,450),(1000,450),(150,560),(1100,560),(100,650),(1150,650),(120,820),(1130,820),(330,600),(930,600),(300,700),(960,700),(400,600),(860,600),(160,860),(1100,860),(60,700),(1190,700)]}
SC=0.851            # l'encolure de ce dessin est plus étroite que les autres : on fixe l'échelle sur celle du barbare (même carrure), pas sur le col
def prep(src,tag,seeds=SEEDS,ref=None):
    keep=brb.prep.__globals__;import skimage.segmentation as sk
    a=np.array(Image.open(src).convert('RGBA')).astype(float);al=a[...,3]>40;lum0=a[...,:3].mean(-1);lum=ndi.gaussian_filter(lum0,1.2);mk=np.zeros(al.shape,int)
    for l,pts in seeds.items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=sk.watershed(255-lum,mk,mask=al);yy,xx=np.mgrid[:al.shape[0],:al.shape[1]]
    riv=ndi.binary_opening((lab==35)&(lum0>150),iterations=3);riv=ndi.binary_dilation(riv,iterations=5)&(lab==35)&(lum0>95);lab[riv]=4          # rivets : petites pastilles claires sur le tablier
    top,l,r=brb.norm.collar(ref or src);s=SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-brb.norm.REF[0]/s)
    A=np.array(Image.fromarray(a.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);L=np.array(Image.fromarray(lab.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.NEAREST)).astype(int)
    brb.T=(s,cx,rcx,top,brb.norm.REF[0]);print(tag,'collar',top,l,r,round(s,3));return A,L
def char(P,apron='#5a3e28',sk='#c98f6a',hr='#8a4a22',cuir='#2e2118',metal='#aeb4bc',pants='#4a4038',ph=0,H=560,head=True):
    a,lab=P;full.G.update({1:.8,35:.72,6:.7,4:.95,7:.6,28:.8});c=Image.new('RGBA',(512,H));c.alpha_composite(brb._legs(pants,'#3a2a1c',ph),(0,brb.DY))
    im=full.tint(a,lab,{1:sk,35:apron,6:cuir,4:metal,7:'#2a2622',28:'#8a6a42'});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o)
    if head:
        hd=Image.new('RGBA',(512,H));hd.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}));c.alpha_composite(hd)
    return c
W1=dict(SEEDS)
W1[1]=[(300,330),(950,330),(250,450),(1000,450),(150,480),(1100,560),(110,560),(1150,650),(150,650),(120,640),(190,670),(1130,750),(1090,820),(990,930),(960,900),(1020,960),(330,600),(930,600),(290,690),(900,640),(400,600),(860,600)]
W1[6]=[(628,165),(400,330),(857,330),(420,450),(835,450),(500,530),(760,530),(350,810),(900,810),(450,850),(800,850),(250,760),(960,790),(500,880),(760,880),(592,872),(665,872)]
W1[35]=[(628,620),(550,650),(700,650),(628,720),(450,740),(800,740),(628,1000),(400,950),(850,950),(300,900),(880,1040),(500,1060),(750,1060),(628,1080),(250,890)]
def walk(R,W,t,**kw):
    import math
    u=min(1,max(0,(abs(t)-.3)/.4));u=u*u*(3-2*u);base=char(R,ph=t*math.pi/2,**kw)
    if u<=0: return base
    o=char(W if t>0 else brb.mirror(W),ph=t*math.pi/2,**kw);return Image.blend(base,o,u) if u<1 else o
# --- Main qui tient (frg/grip.png) : le poing de gauche serre un bout de manche ; l'outil ou l'arme (weapons.py) se glisse dedans ---------------
GR=dict(SEEDS)
GR[1]=[(300,330),(950,330),(250,450),(1000,450),(150,520),(80,600),(120,640),(250,770),(220,740),(280,790),(240,830),(290,722),(1100,560),(1150,650),(1130,820),(1100,860),(1190,700),(330,600),(930,600),(960,700),(400,600),(860,600)]
GR[6]=[(628,165),(400,330),(857,330),(420,450),(835,450),(500,530),(760,530),(350,810),(900,810),(450,850),(800,850),(1000,760),(500,880),(760,880),(592,872),(665,872)]
GR[35]=[(628,620),(550,650),(700,650),(628,720),(450,740),(800,740),(628,1000),(400,950),(850,950),(300,905),(950,900),(500,1060),(750,1060),(628,1080),(290,935),(1000,890)]
GR[28]=[(255,650),(262,675),(228,885),(235,900)]
def grip(src='../frg/grip.png',ref='../frg/relaxed.png'):
    a,lab=prep(src,'grip',GR,ref=ref);H,W=lab.shape;yy,xx=np.mgrid[:H,:W];(x0,y0),(x1,y1)=brb.nrm(178,688),brb.nrm(330,865)
    fist=(lab==1)&(xx>x0)&(xx<x1)&(yy>y0)&(yy<y1);fist=ndi.binary_dilation(fist,iterations=3)&(a[...,3]>60)&(lab!=28);gx,gy=brb.nrm(247,775);return (a,lab),(gx,gy),fist
def armed(G,weapon,dy=160,H=720,metal='#aeb4bc',**kw):
    import weapons
    from PIL import ImageFilter
    P,(gx,gy),fist=G;P=(P[0].copy(),P[1]);P[0][P[1]==28,3]=0;c=Image.new('RGBA',(512,H));          # le bout de manche de la pose est retiré : l'arme le remplace
    c.alpha_composite(char(P,metal=metal,H=H-dy,**kw),(0,dy))
    fx,fy=256+(gx-625)*.29,229+(gy-360)*.29+dy;t,(wx,wy)=weapons.layer(weapon,metal=metal);c.alpha_composite(t,(round(fx-wx),round(fy-wy)))
    a,lab=P;b=np.array(full.tint(a,lab,{1:kw.get('sk','#c98f6a')})).astype(float);b[...,3]*=np.array(Image.fromarray((fist*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.0))).astype(float)/255
    im=Image.fromarray(b.astype('uint8'));w0,h0=im.size;im=im.resize((round(w0*.29),round(h0*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(im,(round(256-625*.29),round(229-360*.29)+dy));c.alpha_composite(o);return c

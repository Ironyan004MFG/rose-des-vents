# Barbare (torse nu, fourrure sur les épaules, pagne de fourrure). Corps dessiné par GPT, avec ses propres poses (bras nus).
# Matières : 1 peau, 34 fourrure, 6 cuir (ceinturon, bracelets, collier), 4 métal (boucle), 7 intérieur de l'encolure, 16 cuisses.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import full,kit,legs,norm
DY=0
def cut(src,out):
    im=np.array(Image.open(src).convert('RGB')).astype(float);lum=im.mean(-1);c,k=ndi.label(lum>236);edge=np.unique(np.r_[c[0],c[-1],c[:,0],c[:,-1]])
    bg=ndi.binary_dilation(np.isin(c,edge[edge>0]),iterations=3);fig=ndi.binary_fill_holes(~bg);cc,kk=ndi.label(fig);fig=cc==(np.argmax(ndi.sum(fig,cc,range(1,kk+1)))+1)
    al=ndi.gaussian_filter(fig.astype(float),0.7)*fig*255;Image.fromarray(np.dstack([im,al]).round().astype('uint8')).save(out)
SEEDS={7:[(628,400),(540,420),(720,420),(628,520),(628,300)],
 6:[(628,170),(410,330),(850,330),(430,430),(830,430),(500,220),(760,220),(130,740),(1125,740),(60,740),(1190,740),(200,730),(1060,730),(300,800),(950,800),(420,860),(840,860),(520,900),(740,900),(505,880),(750,880),(505,935),(750,935)],
 34:[(300,330),(950,330),(250,420),(1000,420),(400,520),(860,520),(500,560),(760,560),(200,400),(1060,400),(330,250),(930,250),(320,470),(940,470),(628,1040),(400,1000),(850,1000),(300,930),(960,930),(500,1060),(760,1060),(628,1100)],
 1:[(628,680),(450,680),(800,680),(580,760),(680,760),(500,760),(760,760),(350,650),(900,650),(110,580),(1150,580),(150,520),(1110,520),(90,640),(1170,640),(140,840),(1130,840),(110,860),(1150,860),(560,700),(700,700)],
 4:[(628,900),(628,842),(562,900),(696,900),(628,962)],
 16:[(285,1045),(965,1045)]}
T=None
def nrm(x,y):
    s,cx,rcx,top,r0=T;return rcx+s*(x-cx),r0+s*(y-top)                # point de l'image de GPT -> image normalisée
def prep(src,tag,seeds=SEEDS,ref=None):
    a=np.array(Image.open(src).convert('RGBA')).astype(float);al=a[...,3]>40;lum=ndi.gaussian_filter(a[...,:3].mean(-1),1.2);mk=np.zeros(al.shape,int)
    for l,pts in seeds.items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=watershed(255-lum,mk,mask=al);yy,xx=np.mgrid[:al.shape[0],:al.shape[1]];lab[(lab==4)&(np.hypot(xx-628,yy-900)>92)]=6          # seul le disque de la boucle est en métal
    top,l,r=norm.collar(ref or src);s=(norm.REF[2]-norm.REF[1])/(r-l);cx=(l+r)/2;rcx=(norm.REF[1]+norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-norm.REF[0]/s)
    A=np.array(Image.fromarray(a.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);L=np.array(Image.fromarray(lab.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.NEAREST)).astype(int)
    global T;T=(s,cx,rcx,top,norm.REF[0])
    A[L==16,3]=0;L[L==16]=0                                  # les bouts de cuisses dessinés par GPT sont retirés : les jambes viennent de legs.py
    return A,L
def _legs(pants,cuir,ph):
    # le pagne est court : on voit le vide laissé à la taille par la jambe qui descend ; on le rebouche en prolongeant le tissu du dessus
    L=np.array(legs.legs(pants,cuir,ph));op=L[...,3]>128;H=L.shape[0]
    for y in range(380,440):
        gap=~op[y]&op[y-1]&op[y:min(H,y+10)].any(0);L[y,gap]=L[y-1,gap];op[y,gap]=True
    return Image.fromarray(L)
def char(P,fur='#6a5a48',sk='#c98f6a',hr='#8a4a22',cuir='#3a2a1c',metal='#aeb4bc',pants='#4a3a2a',ph=0,H=560,head=True):
    a,lab=P;full.G.update({1:.8,34:.72,6:.7,4:.9,7:.6,16:.7,28:.8});c=Image.new('RGBA',(512,H));c.alpha_composite(_legs(pants,cuir,ph),(0,DY))
    im=full.tint(a,lab,{1:sk,34:fur,6:cuir,4:metal,7:'#2a2622',16:pants,28:'#8a6a42'});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o)
    if head:
        hd=Image.new('RGBA',(512,H));hd.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:cuir}));c.alpha_composite(hd)
    return c
W1=dict(SEEDS);W1[1]=[(628,680),(450,680),(800,680),(580,760),(680,760),(500,760),(760,760),(350,650),(900,650),(560,700),(700,700),
 (110,500),(150,470),(80,520),(140,715),(110,700),(170,700),(1090,560),(1060,650),(1120,600),(1000,700),(950,1010),(920,990),(980,1050),(1010,1020)]
W1[6]=[(628,170),(410,330),(850,330),(430,430),(830,430),(500,220),(760,220),(120,620),(70,610),(180,640),(1040,880),(980,850),(1110,920),(1080,900),(300,800),(880,810),(420,860),(840,860),(520,900),(740,900),(505,880),(750,880),(505,935),(750,935)]
W1[34]=[(300,330),(950,330),(250,420),(1000,420),(400,520),(860,520),(500,560),(760,560),(200,400),(1060,400),(330,250),(930,250),(320,470),(940,470),(628,1040),(400,1000),(800,1010),(300,930),(500,1060),(760,1060),(628,1100)]
W1[16]=[(285,1045)]
def mirror(P):
    a,lab=P;sh=2*625-1253;A=np.zeros_like(a);L=np.zeros_like(lab);f=a[:,::-1];g=lab[:,::-1]          # miroir autour de x=625
    if sh>=0: A[:,sh:]=f[:,:a.shape[1]-sh];L[:,sh:]=g[:,:a.shape[1]-sh]
    else: A[:,:sh]=f[:,-sh:];L[:,:sh]=g[:,-sh:]
    return A,L
def walk(R,W,t,**kw):
    """t de -1 (marche 3) à +1 (marche 1), 0 = repos : fondu entre les poses, jambes en phase."""
    import math
    u=min(1,max(0,(abs(t)-.3)/.4));u=u*u*(3-2*u);base=char(R,ph=t*math.pi/2,**kw)
    if u<=0: return base
    o=char(W if t>0 else mirror(W),ph=t*math.pi/2,**kw);return Image.blend(base,o,u) if u<1 else o

# --- Main qui tient (brb/grip.png) : le poing de gauche serre un bout de manche ; l'arme (weapons.py) se glisse dedans --------------------------
GR=dict(SEEDS);GR[1]=[(628,680),(450,680),(800,680),(580,760),(680,760),(500,760),(760,760),(350,650),(900,650),(560,700),(700,700),
 (110,570),(160,540),(70,600),(250,790),(220,760),(280,800),(240,840),(290,745),(230,745),(1150,580),(1110,520),(1170,640),(1130,840),(1150,860)]
GR[6]=[(628,170),(410,330),(850,330),(430,430),(830,430),(500,220),(760,220),(140,740),(90,720),(100,800),(180,700),(1125,740),(1190,740),(1060,730),(360,830),(950,800),(420,860),(840,860),(520,900),(740,900),(505,880),(750,880),(505,935),(750,935)]
GR[34]=[(300,330),(950,330),(250,420),(1000,420),(400,520),(860,520),(500,560),(760,560),(200,400),(1060,400),(330,250),(930,250),(320,470),(940,470),(628,1040),(400,1000),(850,1000),(330,965),(960,930),(500,1060),(760,1060),(628,1100)]
GR[28]=[(258,680),(262,702),(240,905),(245,922)]
def grip(src='../brb/grip.png',ref='../brb/relaxed.png'):
    a,lab=prep(src,'grip',GR,ref=ref);H,W=lab.shape;yy,xx=np.mgrid[:H,:W];(x0,y0),(x1,y1)=nrm(175,712),nrm(335,890)
    fist=(lab==1)&(xx>x0)&(xx<x1)&(yy>y0)&(yy<y1);fist=ndi.binary_dilation(fist,iterations=3)&(a[...,3]>60)&(lab!=28)&(lab!=6);gx,gy=nrm(252,800);return (a,lab),(gx,gy),fist
def armed(G,weapon,dy=160,H=720,metal='#aeb4bc',wood='#8a6a42',**kw):
    import weapons
    from PIL import ImageFilter
    P,(gx,gy),fist=G;P=(P[0].copy(),P[1]);P[0][P[1]==28,3]=0;c=Image.new('RGBA',(512,H));          # le bout de manche de la pose est retiré : l'arme le remplace
    c.alpha_composite(char(P,metal=metal,H=H-dy,**kw),(0,dy))
    fx,fy=256+(gx-625)*.29,229+(gy-360)*.29+dy;t,(wx,wy)=weapons.layer(weapon,metal=metal);c.alpha_composite(t,(round(fx-wx),round(fy-wy)))
    a,lab=P;b=np.array(full.tint(a,lab,{1:kw.get('sk','#c98f6a')})).astype(float);b[...,3]*=np.array(Image.fromarray((fist*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.0))).astype(float)/255
    im=Image.fromarray(b.astype('uint8'));w0,h0=im.size;im=im.resize((round(w0*.29),round(h0*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(im,(round(256-625*.29),round(229-360*.29)+dy));c.alpha_composite(o);return c

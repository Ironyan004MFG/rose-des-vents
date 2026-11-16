# Pourpoint (habit de ville symétrique : noble, marchand, barde, érudit). Col droit, rangée de boutons, manchettes, ceinture fine, basque, galons.
# Matières : 5 étoffe, 9 galon (bandes claires, détectées par leur clarté), 6 ceinture, 4 métal (boutons, boucle), 1 peau, 7 intérieur de l'encolure.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import brb,cui,full,kit,heads
heads.G[15]=.78
SEEDS={7:[(628,420),(628,300),(540,400),(720,400),(628,500)],
 5:[(400,650),(850,650),(300,450),(950,450),(150,600),(1100,600),(200,400),(1050,400),(450,300),(800,300),(400,1050),(850,1050),(500,800),(760,800),(300,1000),(950,1000),(120,680),(1130,680),(500,1100),(760,1100)],
 6:[(400,925),(850,925),(500,950),(750,955),(300,880),(950,880)],
 4:[(585,960),(668,960),(628,937),(628,985)],
 1:[(130,820),(1120,820),(100,850),(1150,850),(170,860),(1080,860),(140,800),(1110,800)]}
def prep(src,tag,seeds=SEEDS,ref=None,btn=(560,925),gal_thr=112):
    a=np.array(Image.open(src).convert('RGBA')).astype(float);al=a[...,3]>40;l0=a[...,:3].mean(-1);lum=ndi.gaussian_filter(l0,1.2);mk=np.zeros(al.shape,int)
    for l,pts in seeds.items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=watershed(255-lum,mk,mask=al);yy,xx=np.mgrid[:al.shape[0],:al.shape[1]]
    gal=(lab==5)&(ndi.gaussian_filter(l0,2.0)>gal_thr);gal=ndi.binary_opening(gal,iterations=1);lab[gal]=9                      # galons, col, manchettes : les bandes claires de l'étoffe
    bt=(lab!=1)&(lab!=7)&(l0>168)&(np.abs(xx-628)<34)&(yy>btn[0])&(yy<btn[1]);bt=ndi.binary_dilation(ndi.binary_opening(bt,iterations=2),iterations=5)&al&(l0>95);lab[bt]=4        # boutons
    top,l,r=brb.norm.collar(ref or src);s=cui.SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-brb.norm.REF[0]/s)
    A=np.array(Image.fromarray(a.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);L=np.array(Image.fromarray(lab.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.NEAREST)).astype(int)
    brb.T=(s,cx,rcx,top,brb.norm.REF[0]);print(tag,'collar',top,l,r);return A,L
def char(P,cloth='#5a2a4a',trim='#c9a23a',belt='#3a2a1c',metal='#d8c070',sk='#c98f6a',hr='#8a4a22',pants='#3a3440',ph=0,H=560,head='nain',extra=None):
    a,lab=P;full.G.update({1:.8,5:.72,9:.85,6:.7,4:.95,7:.6});c=Image.new('RGBA',(512,H));c.alpha_composite(brb._legs(pants,'#3a2a1c',ph),(0,brb.DY))
    full.G.update({28:.85,55:.75,56:.95,57:.8,58:.8});im=full.tint(a,lab,{**{1:sk,5:cloth,9:trim,6:belt,4:metal,7:'#2a2622'},**(extra or {})});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o)
    if head: hd=Image.new('RGBA',(512,H));hd.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}) if head=='nain' else heads.tint(head,{1:sk,2:hr,3:hr,4:'#c4c8ce',15:'#6a6e76',8:'#f2eee4'}));c.alpha_composite(hd)
    return c
# --- Marche : tenue symétrique, donc la marche 3 est le miroir de la marche 1.
W1={7:SEEDS[7],
 5:[(400,650),(800,650),(300,450),(950,450),(450,300),(800,300),(400,1050),(780,1080),(500,1100),(500,800),(760,800),(200,400),(120,480),(160,350),(1050,500),(1100,650),(1050,800),(230,800),(250,950),(300,1000),(700,1100),(1020,892),(965,905),(1075,882),(1000,870),(1050,905)],
 6:[(400,925),(800,925),(500,950),(750,955),(300,880)],
 4:SEEDS[4],
 1:[(100,650),(130,670),(80,630),(150,640),(950,1000),(990,1030),(930,970),(1000,980)]}
def walk(R,W,t,**kw):
    import math
    u=min(1,max(0,(abs(t)-.3)/.4));u=u*u*(3-2*u);base=char(R,ph=t*math.pi/2,**kw)
    if u<=0: return base
    o=char(W if t>0 else brb.mirror(W),ph=t*math.pi/2,**kw);return Image.blend(base,o,u) if u<1 else o
# --- Bras tendu (prp/reach.png) : main ouverte, paume vers le haut, pour payer ou recevoir. PALM = centre de la paume (image de GPT), pour y poser une pièce.
RE={7:SEEDS[7],
 5:[(400,650),(850,650),(300,450),(950,450),(1100,600),(200,400),(1050,400),(450,300),(800,300),(400,1050),(850,1050),(500,800),(760,800),(300,1000),(950,1000),(1130,680),(500,1100),(760,1100),(150,520),(120,600),(250,560),(170,655),(200,640),(130,670)],
 6:SEEDS[6],4:SEEDS[4],
 1:[(1120,820),(1150,850),(1080,860),(1110,800),(160,740),(120,780),(190,790),(100,820),(150,830),(70,740),(200,730)]}
PALM=(150,770)
def reach(src='../prp/reach.png',ref='../prp/relaxed.png'):
    P=prep(src,'reach',RE,ref=ref);return P,brb.nrm(*PALM)
def coin(c,C,dy=0,col='#e8c44a'):
    """Pose une pièce dans la paume (c : personnage monté avec la pose de reach())."""
    from PIL import ImageDraw
    px,py=C[1];x,y=256+(px-625)*.29,229+(py-360)*.29+dy;d=ImageDraw.Draw(c);d.ellipse([x-6,y-5,x+6,y+5],fill='#3a2a1c');d.ellipse([x-4.6,y-3.8,x+4.6,y+3.8],fill=col);d.ellipse([x-3,y-3,x,y-.5],fill='#fff2b0');return c

# --- Barde au luth (prp/lute.png) : pose complète, les deux bras sur l'instrument, d'un seul tenant. 28 = table du luth, 55 = manche, chevillier, chevalet.
LU={7:SEEDS[7],
 5:[(450,500),(800,500),(300,450),(950,450),(200,550),(1100,600),(450,300),(800,300),(400,650),(1150,700),(150,600),(300,950),(400,1050),(500,1000),(560,1100),(700,1150),(250,900),(1000,1130),(900,1165),(270,700),(1030,740),(1060,790),(230,720),(500,650),(750,600)],
 28:[(700,750),(900,700),(1000,950),(700,950),(850,1050),(1050,800),(650,850),(780,700),(830,850),(790,820),(870,880),(1100,900),(950,1050),(620,780),(760,1000)],
 55:[(450,790),(520,830),(400,765),(480,850),(80,690),(60,720),(130,725),(170,700),(100,790),(150,815),(200,690),(1040,880),(1030,930),(230,740),(120,650)],
 1:[(300,800),(330,850),(260,830),(380,820),(300,760),(900,800),(950,850),(880,760),(930,900),(960,780),(350,780)]}
def lute(src='../prp/lute.png',ref='../prp/relaxed.png'): return prep(src,'lute',LU,ref=ref,btn=(560,725))
def bard(P,wood='#c89a5a',neck='#4a2e1c',H=560,**kw):
    """Le luth et les deux mains repassent DEVANT la barbe (comme le panier du fermier), sinon la barbe a l'air d'être dans l'instrument."""
    from PIL import ImageFilter
    c=char(P,extra={28:wood,55:neck},H=H,**kw);a,lab=P;m=np.isin(lab,(28,55,1));m=ndi.binary_dilation(m,iterations=4)&(a[...,3]>60)&~np.isin(lab,(5,9,4,7))|np.isin(lab,(28,55,1))
    b=np.array(char(P,extra={28:wood,55:neck},H=H,**dict(kw,head=None)));top=Image.fromarray(b)
    mk=Image.fromarray((m*255).astype('uint8'));w,h=mk.size;mk=mk.resize((round(w*.29),round(h*.29)),Image.LANCZOS);M=Image.new('L',(512,H));M.paste(mk,(round(256-625*.29),round(229-360*.29)));M=M.filter(ImageFilter.GaussianBlur(0.6))
    top.putalpha(Image.fromarray(np.minimum(np.array(top.split()[3]),np.array(M))));c.alpha_composite(top);return c

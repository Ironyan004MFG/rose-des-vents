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
def prep(src,tag,seeds=SEEDS,ref=None,btn=(560,925)):
    a=np.array(Image.open(src).convert('RGBA')).astype(float);al=a[...,3]>40;l0=a[...,:3].mean(-1);lum=ndi.gaussian_filter(l0,1.2);mk=np.zeros(al.shape,int)
    for l,pts in seeds.items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=watershed(255-lum,mk,mask=al);yy,xx=np.mgrid[:al.shape[0],:al.shape[1]]
    gal=(lab==5)&(ndi.gaussian_filter(l0,2.0)>112);gal=ndi.binary_opening(gal,iterations=1);lab[gal]=9                      # galons, col, manchettes : les bandes claires de l'étoffe
    bt=(lab!=1)&(lab!=7)&(l0>168)&(np.abs(xx-628)<34)&(yy>btn[0])&(yy<btn[1]);bt=ndi.binary_dilation(ndi.binary_opening(bt,iterations=2),iterations=5)&al&(l0>95);lab[bt]=4        # boutons
    top,l,r=brb.norm.collar(ref or src);s=cui.SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-brb.norm.REF[0]/s)
    A=np.array(Image.fromarray(a.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);L=np.array(Image.fromarray(lab.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.NEAREST)).astype(int)
    brb.T=(s,cx,rcx,top,brb.norm.REF[0]);print(tag,'collar',top,l,r);return A,L
def char(P,cloth='#5a2a4a',trim='#c9a23a',belt='#3a2a1c',metal='#d8c070',sk='#c98f6a',hr='#8a4a22',pants='#3a3440',ph=0,H=560,head='nain'):
    a,lab=P;full.G.update({1:.8,5:.72,9:.85,6:.7,4:.95,7:.6});c=Image.new('RGBA',(512,H));c.alpha_composite(brb._legs(pants,'#3a2a1c',ph),(0,brb.DY))
    im=full.tint(a,lab,{1:sk,5:cloth,9:trim,6:belt,4:metal,7:'#2a2622'});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o)
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

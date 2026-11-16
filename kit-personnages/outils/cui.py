# Cuisinier / serveur (chemise à manches roulées, tablier de taille noué sur le côté, torchon). La toque fait le cuisinier. Corps GPT, ses propres poses.
# Matières : 1 peau, 14 chemise, 35 tablier, 36 bande de taille et nœud, 37 torchon, 7 intérieur de l'encolure.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import brb,full,kit,legs
SC=0.851
SEEDS={7:[(628,420),(540,400),(720,400),(628,300),(628,530),(628,250),(500,300),(760,300)],
 14:[(360,430),(900,430),(450,520),(820,520),(628,170),(400,250),(860,250),(250,380),(1000,380),(180,500),(1080,500),(150,620),(1110,620),(100,560),(1160,560),(450,650),(800,650),(628,720),(350,700),(900,700),(540,600),(720,600),(628,620)],
 1:[(110,700),(1150,700),(80,740),(1180,740),(140,830),(1110,830),(110,800),(1150,800),(170,860),(1080,860)],
 36:[(500,800),(700,810),(628,805),(780,800),(240,730),(1000,730),(950,770),(880,775),(830,810),(940,810),(870,900),(900,950),(860,980),(960,850)],
 35:[(628,950),(500,1000),(750,1000),(628,1100),(450,900),(780,900),(350,1050),(950,1000),(1000,900),(220,900),(900,1100)],
 37:[(320,760),(300,850),(330,950),(380,900),(270,930),(350,1000),(390,800)]}
def prep(src,tag,seeds=SEEDS,ref=None):
    a=np.array(Image.open(src).convert('RGBA')).astype(float);al=a[...,3]>40;lum=ndi.gaussian_filter(a[...,:3].mean(-1),1.2);mk=np.zeros(al.shape,int)
    for l,pts in seeds.items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=watershed(255-lum,mk,mask=al);top,l,r=brb.norm.collar(ref or src);s=SC;cx=(l+r)/2;rcx=(brb.norm.REF[1]+brb.norm.REF[2])/2;M=(1/s,0,cx-rcx/s,0,1/s,top-brb.norm.REF[0]/s)
    A=np.array(Image.fromarray(a.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.BICUBIC)).astype(float);L=np.array(Image.fromarray(lab.astype('uint8')).transform((1254,1500),Image.AFFINE,M,Image.NEAREST)).astype(int)
    brb.T=(s,cx,rcx,top,brb.norm.REF[0]);print(tag,'collar',top,l,r);return A,L
def char(P,shirt='#d8cfb8',apron='#ece6d6',sash='#8a4a3a',towel='#f2eee4',sk='#c98f6a',hr='#8a4a22',pants='#4a4038',ph=0,H=560,head=True):
    a,lab=P;full.G.update({1:.8,14:.8,35:.8,36:.75,37:.9,7:.6,28:.8});c=Image.new('RGBA',(512,H));c.alpha_composite(brb._legs(pants,'#3a2a1c',ph),(0,brb.DY))
    im=full.tint(a,lab,{1:sk,14:shirt,35:apron,36:sash,37:towel,7:'#2a2622',28:'#8a6a42'});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o)
    if head:
        hd=Image.new('RGBA',(512,H));hd.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}));c.alpha_composite(hd)
    return c
W1=dict(SEEDS)
W1[14]=[(360,430),(900,430),(450,520),(820,520),(628,170),(400,250),(860,250),(250,380),(1000,380),(180,500),(1080,500),(150,350),(100,420),(1110,620),(1160,560),(1050,640),(450,650),(800,650),(628,720),(350,700),(900,700),(540,600),(720,600),(628,620)]
W1[1]=[(120,620),(150,650),(100,650),(75,580),(1050,820),(1010,860),(1080,790),(960,960),(930,945),(1000,1000),(990,925)]
W1[36]=[(500,800),(700,810),(628,805),(780,800),(240,730),(880,775),(830,810),(870,900),(860,980)]
W1[35]=[(628,950),(500,1000),(750,1000),(628,1100),(450,900),(780,900),(350,1050),(220,900),(900,1100)]
# La tenue n'est PAS symétrique (torchon d'un côté, nœud de l'autre) : pas de miroir, la marche 3 est dessinée par GPT elle aussi.
W3=dict(SEEDS)
W3[14]=[(360,430),(900,430),(450,520),(820,520),(628,170),(400,250),(860,250),(250,380),(1000,380),(180,500),(1080,500),(150,580),(100,620),(200,620),(1050,420),(1120,480),(1150,530),(450,650),(800,650),(628,720),(350,700),(900,700),(540,600),(720,600),(628,620)]
W3[1]=[(100,740),(150,760),(190,800),(120,900),(160,930),(100,930),(200,900),(1150,625),(1130,690),(1100,700),(1170,690)]
W3[36]=[(500,800),(700,810),(628,805),(780,800),(1000,760),(880,775),(830,810),(940,810),(870,900),(900,950),(860,980),(960,850)]
W3[35]=[(628,950),(500,1000),(750,1000),(628,1100),(450,900),(780,900),(350,1050),(950,1000),(1000,900),(300,1080),(900,1100)]
def walk(R,W,V,t,**kw):
    """t de -1 (marche 3, V) à +1 (marche 1, W), 0 = repos (R)."""
    import math
    u=min(1,max(0,(abs(t)-.3)/.4));u=u*u*(3-2*u);base=char(R,ph=t*math.pi/2,**kw)
    if u<=0: return base
    o=char(W if t>0 else V,ph=t*math.pi/2,**kw);return Image.blend(base,o,u) if u<1 else o
# --- Bras qui porte une assiette VIDE (cui/carry.png) : bras et assiette dessinés d'un seul tenant. Matière 38 = assiette. Les menus se posent dessus.
CA=dict(SEEDS)
CA[14]=[(360,430),(900,430),(450,520),(820,520),(628,170),(400,250),(860,250),(250,380),(1000,380),(180,500),(1080,500),(150,620),(100,560),(1000,540),(1100,510),(1170,540),(970,600),(950,640),(450,650),(800,650),(628,720),(350,700),(900,700),(540,600),(720,600),(628,620)]
CA[1]=[(110,700),(80,740),(140,830),(110,800),(170,860),(1050,620),(1100,600),(1150,650),(1050,680),(1150,590),(1160,730),(1185,760)]
CA[36]=[(500,800),(700,810),(628,805),(240,730),(780,775),(740,830),(760,860),(770,950),(770,1000),(720,840)]
CA[35]=[(628,950),(500,1000),(680,1000),(628,1100),(450,900),(350,1050),(220,900),(700,1150),(600,880)]
CA[38]=[(1010,900),(900,900),(1100,950),(1010,1000),(1010,800),(1010,712),(800,900),(1225,900),(1010,1085),(860,760),(1170,1040),(850,1050)]
PLATE=dict(c=(1012,900),r=165)                   # centre et rayon utile de l'assiette, dans l'image de GPT
def carry(src='../cui/carry.png',ref='../cui/relaxed.png'):
    P=prep(src,'carry',CA,ref=ref);return P,brb.nrm(*PLATE['c'])
def served(C,food=None,plate='#c9c4b8',dy=0,**kw):
    """C = carry() ; food : image RGBA d'un menu (déjà teintée), posée au centre de l'assiette."""
    P,(px,py)=C;a,lab=P;full.G.update({38:.9});a2=np.array(full.tint(a,lab,{38:plate})).astype(float);c=char((a2,np.where(lab==38,0,lab)),**kw)
    if food is not None:
        d=round(2*PLATE['r']*SC*.29*1.12);f=food.resize((d,round(d*food.size[1]/food.size[0])),Image.LANCZOS);fx,fy=256+(px-625)*.29,229+(py-360)*.29+dy;c.alpha_composite(f,(round(fx-f.size[0]/2),round(fy-f.size[1]/2)))
    return c
# --- Menus posés sur l'assiette (obj/menu_1.png volaille-pommes de terre-persil, obj/menu_2.png pain-fromage-raisin) : chaque aliment a sa couleur.
MENUS={1:dict(seeds={40:[(350,330),(250,420),(450,280),(560,230),(200,300),(330,450)],41:[(720,130),(745,150),(690,110),(650,160)],42:[(130,560),(200,560),(100,640),(230,700),(160,520),(240,540)],43:[(640,430),(380,640),(620,640),(700,480),(330,600),(560,700)]},
               cols={40:'#a8642e',41:'#e8dcc0',42:'#4f8a3a',43:'#c9a05a'}),
       2:dict(seeds={44:[(220,200),(620,130),(170,400),(120,300),(400,90),(690,250)],45:[(470,300),(370,350),(570,250),(650,330),(300,400)],46:[(270,620),(370,500),(220,560),(420,720),(150,600),(440,640),(330,740)],
                     47:[(620,400),(540,520),(680,510),(780,480),(500,680),(600,650),(740,600),(660,720),(570,420)],48:[(770,350),(735,410)]},
               cols={44:'#a8763e',45:'#e6cf9a',46:'#e8c44a',47:'#6a3a7a',48:'#6b5a3a'})}
def menu(n):
    a=np.array(Image.open(f'../obj/menu_{n}.png').convert('RGBA')).astype(float);al=a[...,3]>40;mk=np.zeros(al.shape,int);M=MENUS[n]
    for l,pts in M['seeds'].items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=watershed(255-ndi.gaussian_filter(a[...,:3].mean(-1),1.2),mk,mask=al);full.G.update({k:.85 for k in M['cols']});t=full.tint(a,lab,M['cols']);ys,xs=np.where(al);return t.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
# --- Objets de table : assiette seule (obj/item_plate.png, parfaitement ronde, à plat) et chopes (obj/item_mug_1..3.png : anse à gauche, en haut, à droite).
def plate(col='#c9c4b8',food=None,size=120):
    a=np.array(Image.open('../obj/item_plate.png').convert('RGBA')).astype(float);lab=(a[...,3]>60)*38;full.G.update({38:.9});t=full.tint(a,lab,{38:col}).resize((size,size),Image.LANCZOS)
    if food is not None:
        d=round(size*.80);f=food.resize((d,round(d*food.size[1]/food.size[0])),Image.LANCZOS);t.alpha_composite(f,((size-f.size[0])//2,(size-f.size[1])//2))
    return t
def mug(i,foam='#f3ead2',wood='#8a6a42',metal='#aeb4bc',size=70):
    """Matières : 39 mousse, 28 bois (douelles, anse), 4 métal (cercle et rivets, sous la mousse)."""
    a=np.array(Image.open(f'../obj/item_mug_{i}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=ndi.gaussian_filter(a[...,:3].mean(-1),1.5)
    fo=ndi.binary_opening(al&(lum>165),iterations=8);c,k=ndi.label(fo);fo=ndi.binary_fill_holes(c==(np.argmax(ndi.sum(fo,c,range(1,k+1)))+1));from skimage.morphology import convex_hull_image;fo=ndi.binary_erosion(convex_hull_image(ndi.binary_dilation(fo,iterations=6)&al&(lum>95)),iterations=2)
    cy,cx=ndi.center_of_mass(fo);R=np.sqrt(fo.sum()/np.pi);yy,xx=np.mgrid[:al.shape[0],:al.shape[1]];rr=np.hypot(xx-cx,yy-cy)
    me=al&~fo&(lum>118)&(yy>cy+R*.35)&(rr>R*1.12)&(rr<R*1.75);me=ndi.binary_closing(ndi.binary_opening(me,iterations=2),iterations=7)&al&~fo
    lab=np.where(al,28,0);lab[me]=4;lab[fo]=39;full.G.update({39:.97,28:.8,4:.95});t=full.tint(a,lab,{39:foam,28:wood,4:metal})
    return t.resize((round(size*t.size[0]/t.size[1]),size),Image.LANCZOS)
def mug_empty(i,wood='#8a6a42',metal='#aeb4bc',size=70):
    """Chope vide (obj/item_mug_empty_1..3.png, mêmes anses que les pleines) : bois partout, cercle et rivets en métal."""
    a=np.array(Image.open(f'../obj/item_mug_empty_{i}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=ndi.gaussian_filter(a[...,:3].mean(-1),1.5);yy,xx=np.mgrid[:al.shape[0],:al.shape[1]];ys,xs=np.where(al)
    me=al&(lum>150)&(yy>ys.min()+(ys.max()-ys.min())*.5);me=ndi.binary_closing(ndi.binary_opening(me,iterations=2),iterations=7)&al
    lab=np.where(al,28,0);lab[me]=4;full.G.update({28:.8,4:.95});t=full.tint(a,lab,{28:wood,4:metal});return t.resize((round(size*t.size[0]/t.size[1]),size),Image.LANCZOS)

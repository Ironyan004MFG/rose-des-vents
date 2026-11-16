# Serveuse (chemise à manches bouffantes, corsage lacé, jupe ample, petit tablier de taille noué sur le côté, torchon). Même carrure que le cuisinier.
# Matières : 1 peau, 14 chemise, 49 corsage, 50 jupe, 35 tablier, 36 rubans (taille, nœuds), 37 torchon, 7 intérieur de l'encolure.
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import brb,cui,full,kit,heads
heads.G[15]=.78
SEEDS={7:[(628,420),(628,300),(540,400),(720,400),(628,520)],
 14:[(628,585),(480,545),(780,545),(420,430),(840,430),(628,170),(450,280),(810,280),(230,400),(1030,400),(150,450),(1100,450),(200,520),(1060,520),(250,590),(1010,590),(170,610),(1090,610)],
 49:[(340,300),(920,300),(330,450),(930,450),(400,650),(860,650),(500,700),(760,700),(450,740),(800,740),(700,640),(560,640),(540,740),(720,740)],
 36:[(450,780),(700,790),(628,790),(760,790),(870,790),(830,850),(920,830),(860,950),(300,690),(950,690),(140,520),(1110,520),(130,585),(1120,585)],
 35:[(628,900),(550,1000),(720,1000),(628,1040),(500,880),(760,880)],
 37:[(330,760),(300,880),(350,950),(280,930),(380,1000),(400,820)],
 50:[(250,800),(1000,800),(230,900),(1020,900),(300,1050),(950,1050),(500,1130),(760,1130),(628,1150),(960,950)],
 1:[(110,700),(1150,700),(80,740),(1180,740),(140,830),(1110,830),(170,860),(1080,860),(150,660),(1110,660)]}
def prep(src,tag,seeds=SEEDS,ref=None): return cui.prep(src,tag,seeds,ref)
def char(P,shirt='#f0ece2',bodice='#7a2e2e',skirt='#3e4a5e',apron='#f4f1ea',ribbon='#c8a24a',towel='#f2eee4',sk='#c98f6a',hr='#8a4a22',shoes='#3a2a1c',ph=0,H=560,head='coif_f',hdy=0):
    a,lab=P;full.G.update({1:.8,14:.85,49:.75,50:.72,35:.85,36:.8,37:.9,7:.6});c=Image.new('RGBA',(512,H));c.alpha_composite(brb._legs(skirt,shoes,ph),(0,brb.DY))
    im=full.tint(a,lab,{1:sk,14:shirt,49:bodice,50:skirt,35:apron,36:ribbon,37:towel,7:'#2a2622'});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o)
    if head:
        hd=Image.new('RGBA',(512,H));hd.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}) if head=='nain' else heads.tint(head,{1:sk,2:hr,3:hr,4:'#c4c8ce',15:'#6a6e76',8:'#f2eee4'}));c.alpha_composite(hd,(0,hdy)) if hdy>=0 else c.alpha_composite(hd.crop((0,-hdy,512,H)),(0,0))
    return c

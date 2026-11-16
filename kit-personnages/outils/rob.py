# Robe de dame noble (corps féminin, même carrure que la serveuse). La jupe descend au sol : PAS de jambes, la marche se fait avec les bras.
# Matières : 5 étoffe, 9 galons et chaîne (bandes claires), 51 plastron, 37 dentelle des poignets, 4 métal (médaillon, perles), 1 peau, 7 encolure.
import numpy as np
from PIL import Image
import brb,prp,full,kit,heads
SEEDS={7:[(628,300),(628,400),(560,350),(700,350),(628,220)],
 5:[(450,500),(810,500),(430,590),(830,590),(250,350),(1000,350),(200,480),(1050,480),(300,280),(950,280),(400,800),(850,800),(628,900),(300,1000),(950,1000),(628,1050),(150,850),(1100,850),(500,1000),(760,1000),(330,560),(930,560),(120,950),(1130,950),(628,95),(420,300),(840,300),(628,438),(500,432),(760,432),(410,180),(850,180),(628,1190),(300,1130),(950,1130),(90,860),(1165,860)],
 51:[(590,540),(670,540),(560,490),(700,490),(600,600),(656,600)],
 1:[(230,690),(1020,690),(200,700),(1050,700),(250,670),(1000,670)],
 37:[(210,600),(1030,600),(160,620),(1090,615),(250,612),(990,612),(200,575),(1040,575)],
 4:[(628,675),(605,690),(650,690),(628,655)]}
def prep(src,tag,seeds=SEEDS,ref=None): return prp.prep(src,tag,seeds,ref,btn=(450,625),gal_thr=128)
def char(P,cloth='#5a2a4a',trim='#c9a23a',front='#d8c8a8',lace='#f2eee4',metal='#d8c070',sk='#c98f6a',hr='#8a4a22',H=560,head='naine'):
    a,lab=P;full.G.update({1:.8,5:.72,9:.85,51:.85,37:.9,4:.95,7:.6});c=Image.new('RGBA',(512,H))
    im=full.tint(a,lab,{1:sk,5:cloth,9:trim,51:front,37:lace,4:metal,7:'#2a2622'});w,h=im.size;t=im.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(t,(round(256-625*.29),round(229-360*.29)));c.alpha_composite(o)
    if head: hd=Image.new('RGBA',(512,H));hd.alpha_composite(heads.tint(head,{1:sk,2:hr,3:hr,4:'#c4c8ce',15:'#6a6e76',8:'#f2eee4'}));c.alpha_composite(hd)
    return c

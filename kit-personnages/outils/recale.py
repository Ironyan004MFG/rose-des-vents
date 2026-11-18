"""Recale chaque tête de tieffelin sur la même tête d'elfe : échelle et décalage trouvés par corrélation des traits du visage (ncc.py)."""
import json,numpy as np
from PIL import Image
K='/home/claude/rose-des-vents/kit-personnages'
def tr(im,s,dx,dy,res):
    a=(1/s,0,256-(256+dx)/s,0,1/s,200-(200+dy)/s);return im.transform((512,512),Image.AFFINE,a,resample=res)
N=json.load(open('ncc.json'));log=[]
for key,(v,s,dx,dy) in N.items():
    if v<0.4: continue
    if v<0.55: s=1.0
    s=min(s,1.0)
    if abs(s-1)<0.03: s=1.0
    if s==1.0 and abs(dx)<2 and abs(dy)<2: continue
    lot,f=key.split('/');p=f'{K}/tieffelin/tete/{lot}/{f}';q=p[:-4]+'_matieres.npy'
    tr(Image.open(p).convert('RGBA'),s,dx,dy,Image.BICUBIC).save(p)
    L=Image.fromarray(np.load(q));np.save(q,np.array(tr(L,s,dx,dy,Image.NEAREST)))
    log.append((key,s,dx,dy))
for l in log: print(l)

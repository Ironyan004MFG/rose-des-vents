"""Tieffelin : visages à la taille de l'elfe (hommes 51 px des yeux au menton, femmes 48 px ; l'humain fait 59), jamais agrandis ;
centrage sur l'axe du visage de la tête elle-même (pas sur l'elfe, dont certaines têtes sont décentrées)."""
import numpy as np,taille,json
from PIL import Image
K=taille.K
def tr(im,s,dx,cx,cy,res):
    a=(1/s,0,cx-(cx+dx)/s,0,1/s,cy-cy/s);return im.transform((512,512),Image.AFFINE,a,resample=res)
T=taille.race('tieffelin');log=[]
for key,v in T.items():
    lot,n=key.split('/');s=1.0;dx=0
    if not n.startswith('m_c') and not n.startswith('f_c') and n!='m_s_roublard':
        tgt=48 if n.startswith('f_') else 51;s=float(np.clip(tgt/v['h'],0.85,1.0))
        if s>0.97: s=1.0
    if n!='m_s_roublard' and abs(v['cx']-256)>=4: dx=256-v['cx']
    if s==1.0 and dx==0: continue
    p=f'{K}/tieffelin/tete/{lot}/head_{n}.png';q=p[:-4]+'_matieres.npy'
    tr(Image.open(p).convert('RGBA'),s,dx,256,v['ey'],Image.BICUBIC).save(p)
    np.save(q,np.array(tr(Image.fromarray(np.load(q)),s,dx,256,v['ey'],Image.NEAREST)));log.append((key,v['h'],round(s,3),dx))
for l in log: print(l)
json.dump(log,open('taille_fix.json','w'))

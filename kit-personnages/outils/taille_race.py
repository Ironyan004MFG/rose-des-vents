"""Ramène les visages d'une race à une hauteur cible (yeux -> menton), en réduisant autour de l'œil (jamais d'agrandissement) et en recentrant
sur l'axe du visage. Têtes casquées (visage peu mesurable) : réduction médiane de la race."""
import numpy as np,taille,json,sys
from PIL import Image
K=taille.K
def tr(im,s,dx,cx,cy,res):
    a=(1/s,0,cx-(cx+dx)/s,0,1/s,cy-cy/s);return im.transform((512,512),Image.AFFINE,a,resample=res)
def run(race,th,tf,lo=0.82):
    T=taille.race(race);S={}
    for key,v in T.items():
        n=key.split('/')[1]
        if n.startswith(('m_c','f_c')) or n=='m_s_roublard' or not (50<=v['h']<=68): continue
        S[key]=float(np.clip((tf if n.startswith('f_') else th)/v['h'],lo,1.0))
    med=float(np.median(list(S.values())));log=[]
    for key,v in T.items():
        lot,n=key.split('/');s=S.get(key,med);s=1.0 if s>0.985 else s
        dx=256-v['cx'] if (n!='m_s_roublard' and abs(v['cx']-256)>=4 and not n.startswith(('m_c','f_c'))) else 0
        if s==1.0 and dx==0: continue
        p=f'{K}/{race}/tete/{lot}/head_{n}.png';q=p[:-4]+'_matieres.npy';ey=v['ey'] if not n.startswith(('m_c','f_c')) else 200
        tr(Image.open(p).convert('RGBA'),s,dx,256,ey,Image.BICUBIC).save(p)
        np.save(q,np.array(tr(Image.fromarray(np.load(q)),s,dx,256,ey,Image.NEAREST)));log.append((key,v['h'],round(s,3),dx))
    return med,log
if __name__=='__main__':
    med,log=run(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))
    print('médiane',med);[print(l) for l in log]

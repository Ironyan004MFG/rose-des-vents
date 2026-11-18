"""Remonte les têtes « enfoncées dans le cou » : yeux mesurés sous la ligne des épaules (y > 200) ramenés à 200, plus celles signalées par Yannick."""
import numpy as np,taille
from PIL import Image
K=taille.K
SIGNALEES={('humain','m_s_druide'),('tieffelin','m_s_druide'),('tieffelin','m_s_marin'),('tieffelin','m_s_fermier'),('tieffelin','f_v_chignon')}
def up(p,d):
    q=p[:-4]+'_matieres.npy';im=Image.open(p).convert('RGBA');o=Image.new('RGBA',(512,512));o.paste(im,(0,-d));o.save(p)
    L=np.load(q);M=np.zeros_like(L);M[:512-d]=L[d:];np.save(q,M)
log=[]
for r in ('humain','tieffelin'):
    T=taille.race(r)
    for key,v in T.items():
        lot,n=key.split('/')
        if n.startswith(('m_c','f_c')) or n=='m_s_roublard': continue
        d=max(0,v['ey']-200)+(5 if (r,n) in SIGNALEES else 0);d=min(d,9)
        if d<2: continue
        up(f'{K}/{r}/tete/{lot}/head_{n}.png',d);log.append((r,key,d))
for l in log: print(l)

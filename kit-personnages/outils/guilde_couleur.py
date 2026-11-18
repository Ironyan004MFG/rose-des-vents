"""Colore un employé de la Guilde : gris + calque (ROUGE peau, BLEU poils, MAGENTA veste, JAUNE liserés, VERT métal, CYAN cuir, ORANGE autres tissus, VIOLET cornes/défenses, GRIS objets)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
PURS={'peau':(255,0,0),'poils':(0,0,255),'veste':(255,0,255),'galon':(255,255,0),'metal':(0,255,0),'cuir':(0,255,255),'tissu':(255,140,0),'corne':(128,0,255),'objet':(128,128,128)}
def hx(c): c=c.lstrip('#');return np.array([int(c[i:i+2],16) for i in (0,2,4)])/255
def labels(cal,fg):
    a=cal.astype(float);ks=list(PURS);P=np.array([PURS[k] for k in ks],float)
    d=((a[:,:,None,:]-P[None,None])**2).sum(-1);lab=d.argmin(-1);sat=a.max(-1)-a.min(-1)
    bad=(d.min(-1)>60**2)|((a.min(-1)>225))
    lab=lab.astype(int);lab[bad]=-1
    # cases inconnues dans la silhouette : matière voisine la plus proche
    idx=ndi.distance_transform_edt(lab<0,return_distances=False,return_indices=True)
    lab=lab[idx[0],idx[1]];lab[~fg]=-1;return lab,ks
def colore(gris,calque,cols,blancs=False):
    g=np.array(Image.open(gris).convert('RGB')).astype(float)/255;L=g.mean(-1)
    cal=np.array(Image.open(calque).convert('RGB').resize(Image.open(gris).size)).astype(int)
    # fond = blanc dans le gris ET blanc dans le calque : y compris les vides enfermés (entre bras et corps, dans les cheveux)
    fond=(L>0.88)&(cal.min(-1)>215)
    fg=~fond;fg=ndi.binary_opening(fg,iterations=1)
    c,n=ndi.label(fg);s=ndi.sum(fg,c,range(1,n+1));fg=np.isin(c,1+np.where(s>max(400,s.max()*0.002))[0])
    # petits trous de quelques pixels (reflets) : rebouchés
    trous=ndi.binary_fill_holes(fg)&~fg;ct,nt=ndi.label(trous);st=ndi.sum(trous,ct,range(1,nt+1));fg|=np.isin(ct,1+np.where(st<40)[0])
    lab,ks=labels(cal,fg)
    # liseré blanc au bord (le calque déborde un peu du dessin) : retiré, sauf les cheveux blancs
    d=ndi.distance_transform_edt(fg);halo=fg&(d<=5)&(L>0.955)&((lab!=ks.index('poils'))|(not blancs))
    fg&=~halo;lab[halo]=-1
    out=np.zeros(g.shape)
    for i,k in enumerate(ks):
        m=lab==i
        if not m.any(): continue
        t=hx(cols.get(k,'#808080'));l=L[m][:,None]
        # incrustation : la teinte prend les ombres et les lumières du dessin
        out[m]=np.where(l<0.5,2*t*l,1-2*(1-t)*(1-l))
    a=(fg*255).astype(np.uint8);a=np.array(Image.fromarray(a).filter(__import__('PIL.ImageFilter',fromlist=['x']).GaussianBlur(1)))
    return Image.fromarray(np.dstack([(out.clip(0,1)*255).astype(np.uint8),a]),'RGBA')
BASE={'veste':'#26355e','galon':'#d4a640','metal':'#d8b050','cuir':'#6a4426','tissu':'#c8b898','objet':'#c8b494','corne':'#3a2a32'}
EMP={
 'pax':dict(peau='#9a7a86',poils='#e8e0d4',veste='#8a1e22',tissu='#b89a78',metal='#e0b84a'),
 'oswin':dict(peau='#ecc4a8',poils='#f2f0ea'),
 'tamsin':dict(peau='#b89ad8',poils='#1e1a24',corne='#3a2a3e'),
 'corisande':dict(peau='#e4bc9c',poils='#b8b4ac'),
 'hrolf':dict(peau='#7e9070',poils='#1c1a1a',corne='#ece4cc'),
 'durgan':dict(peau='#e4ac8c',poils='#b24a26'),
 'seraphine':dict(peau='#f2d8c8',poils='#dcdee4'),
 'elenwe':dict(peau='#ecc8aa',poils='#6a3e22',objet='#b88a5a'),
 'bert':dict(peau='#eab094',poils='#4e321e'),
 'jiwoo':dict(peau='#ecc6a0',poils='#16141a'),
}
if __name__=='__main__':
    import sys
    ims=[]
    for n,c in EMP.items():
        im=colore(f'guilde/{n}/{n}_relaxed.png',f'guilde/{n}/{n}_relaxed_calque.png',dict(BASE,**c),blancs=n in ('pax','oswin','corisande','seraphine'));im.save(f'guilde/{n}/{n}_relaxed_couleur.png');ims.append(im)
    W,H=360,480;S=Image.new('RGBA',(5*W,2*H),(139,105,72,255))
    for i,im in enumerate(ims): S.alpha_composite(im.resize((W,H),Image.LANCZOS),((i%5)*W,(i//5)*H))
    S.convert('RGB').save('planches/guilde_couleur.png')

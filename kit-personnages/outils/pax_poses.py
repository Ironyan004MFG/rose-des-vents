"""Poses de Pax : recale chaque calque sur son gris (échelle + décalage), puis colore."""
import sys,numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0,'outils')
POSES=['cafe_repos','cafe_pas1','cafe_pas3','pas1','pas3','discute','rire','boire']
def sil_g(f):a=np.array(Image.open(f).convert('L')).astype(float)/255;return ndi.binary_fill_holes(ndi.binary_opening(a<0.88,iterations=2))
def sil_c(im):a=np.array(im.convert('RGB')).astype(int);return ndi.binary_fill_holes(ndi.binary_opening(a.min(-1)<215,iterations=2))
def warp(im,s,dx,dy):
    W,H=im.size;cx,cy=W/2,H/2
    # x_src = (x - cx - dx)/s + cx
    return im.transform((W,H),Image.AFFINE,(1/s,0,cx-(cx+dx)/s,0,1/s,cy-(cy+dy)/s),resample=Image.NEAREST,fillcolor=(255,255,255))
def recale(gris,cal):
    Gf=sil_g(gris);C0=Image.open(cal).convert('RGB');best=(-1,)
    def sc(k,s,dx,dy):
        G=Gf[::k,::k];c=C0.resize((Gf.shape[1]//k,Gf.shape[0]//k),Image.NEAREST);C=sil_c(warp(c,s,dx/k,dy/k));h,w=min(G.shape[0],C.shape[0]),min(G.shape[1],C.shape[1]);G=G[:h,:w];C=C[:h,:w]
        return (G&C).sum()/(G|C).sum()
    for s in np.arange(0.96,1.041,0.01):
        for dy in range(-24,25,4):
            for dx in range(-24,25,4):
                v=sc(4,s,dx,dy)
                if v>best[0]:best=(v,s,dx,dy)
    _,s0,dx0,dy0=best
    for s in (s0-0.005,s0,s0+0.005):
        for dy in range(dy0-3,dy0+4):
            for dx in range(dx0-3,dx0+4):
                v=sc(2,s,dx,dy)
                if v>best[0]:best=(v,s,dx,dy)
    return best
if __name__=='__main__':
    for n in sys.argv[1:] or POSES:
        g=f'guilde/pax/pax_{n}.png';c=f'guilde/pax/pax_{n}_calque.png'
        iou,s,dx,dy=recale(g,c);print(n,round(iou,4),round(s,3),dx,dy,flush=True)
        if abs(s-1)>1e-3 or dx or dy: warp(Image.open(c).convert('RGB'),s,dx,dy).save(c)

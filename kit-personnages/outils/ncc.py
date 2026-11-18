import numpy as np,glob,os,json,sys
from PIL import Image
from scipy import ndimage as ndi
K='/home/claude/rose-des-vents/kit-personnages'
yy,xx=np.mgrid[186:256,224:290].astype(float)
def lum(p):
    a=np.array(Image.open(p).convert('RGBA')).astype(float);l=a[...,:3].mean(-1)*(a[...,3]/255);return l-ndi.gaussian_filter(l,4)
def samp(l,s,dx,dy):
    X=(xx-256-dx)/s+256;Y=(yy-200-dy)/s+200;return ndi.map_coordinates(l,[Y,X],order=1)
def ncc(a,b):
    a=a-a.mean();b=b-b.mean();return (a*b).sum()/np.sqrt((a*a).sum()*(b*b).sum()+1e-9)
def best(e,t):
    E=samp(e,1,0,0);B=(-2,)
    for s in np.arange(0.84,1.07,0.02):
        for dy in range(-10,11,2):
            for dx in range(-14,15,2):
                v=ncc(E,samp(t,s,dx,dy))
                if v>B[0]: B=(v,round(float(s),2),dx,dy)
    # affinage
    v0,s0,dx0,dy0=B
    for s in np.arange(s0-0.02,s0+0.021,0.01):
        for dy in range(dy0-2,dy0+3):
            for dx in range(dx0-2,dx0+3):
                v=ncc(E,samp(t,s,dx,dy))
                if v>B[0]: B=(v,round(float(s),2),dx,dy)
    return B
if __name__=='__main__':
    out={}
    for f in sorted(glob.glob(f'{K}/tieffelin/tete/lot*/head_*.png')):
        lot=f.split('/')[-2];n=os.path.basename(f);e=f'{K}/elfe/tete/{lot}/{n}'
        r=best(lum(e),lum(f));out[lot+'/'+n]=r;print(lot[-1],n[5:-4].ljust(22),'ncc %.2f s=%.2f dx=%d dy=%d'%r,flush=True)
    json.dump(out,open('ncc.json','w'))

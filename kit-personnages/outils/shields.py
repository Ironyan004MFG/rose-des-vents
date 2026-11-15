# Boucliers : dessinés bien de face par GPT ; ici on sépare métal (4) et face (5), puis on l'incline (écrasement horizontal) pour le poser sur l'avant-bras, vu du dessus.
import numpy as np,math
from PIL import Image
from scipy import ndimage as ndi
import bodyseg,full
C={}
def prep(n):
    if n in C: return C[n]
    im=Image.open(f'../obj/item_shield_{n}.png').convert('RGBA');a=np.array(im).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1)
    line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1);ml=ndi.mean(lum,comp,idx)
    kind=np.where(ml>118,4,5);lab=np.zeros(al.shape,int);lab[comp>0]=kind[comp[comp>0]-1]
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    ys,xs=np.where(al);C[n]=(a,lab,(xs.min(),ys.min(),xs.max()+1,ys.max()+1));return C[n]
def flat(n,face,metal='#aeb4bc'):
    a,lab,bb=prep(n);full.G.update({4:.95,5:.85});return full.tint(a,lab,{4:metal,5:face}).crop(bb)
def worn(n,face,metal='#aeb4bc',h=118,squash=0.58,rot=-8):
    """Bouclier prêt à poser : hauteur h (pixels du personnage), écrasé en largeur, légèrement tourné."""
    t=flat(n,face,metal);w0,h0=t.size;t=t.resize((max(1,round(w0*h/h0*squash)),h),Image.LANCZOS)
    return t.rotate(rot,Image.BICUBIC,expand=True)

def front(n,face,metal='#aeb4bc',w=150,tilt=0.86,rot=10):
    """Bouclier tenu DEVANT soi : grand, face bien visible, à peine raccourci en hauteur (vue plongeante), légèrement tourné."""
    t=flat(n,face,metal);w0,h0=t.size;t=t.resize((w,max(1,round(h0*w/w0*tilt))),Image.LANCZOS)
    return t.rotate(rot,Image.BICUBIC,expand=True)
# Réglages validés du bouclier tenu devant : largeur, raccourci en hauteur, rotation, décalage par rapport au centre de l'avant-bras
FRONT={'heater':dict(w=182,tilt=0.86,rot=18,off=(-30,62)),'round':dict(w=172,tilt=0.86,rot=18,off=(-30,62)),'pavise':dict(w=176,tilt=1.04,rot=18,off=(-26,84))}   # 'pavise' = le pavois, plus long que les autres
def put(canvas,sh,center):
    canvas.alpha_composite(sh,(round(center[0]-sh.size[0]/2),round(center[1]-sh.size[1]/2)));return canvas
def arm_anchor(lab,side=1):
    """Centre de l'avant-bras (brassard + gantelet) du côté voulu, en pixels du personnage."""
    H,W=lab.shape;yy,xx=np.mgrid[:H,:W];m=(lab==4)&((xx-627)*side>330)&(yy>600)
    cy,cx=ndi.center_of_mass(m);return (256+(cx-625)*.29,229+(cy-360)*.29)
if __name__=='__main__':
    O=Image.new('RGBA',(900,340),(140,105,70,255))
    for i,(n,c) in enumerate((('heater','#7a2a26'),('round','#2d4a7a'),('pavise','#2f6a34'))):
        t=flat(n,c);t.thumbnail((300,300),Image.LANCZOS);O.alpha_composite(t,(i*300+(300-t.size[0])//2,20))
    O.save('../obj/boucliers_plat.png')

# Garde : plaques de métal (4), tabard (5), bordure du tabard (9), cotte de mailles (15), ceinture (6), intérieur du col (7).
# Aucune peau. La cotte de mailles se reconnaît à sa texture d'anneaux, mesurée à l'intérieur des régions (loin des traits de contour).
import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import norm,bodyseg,full,kit,legs
def prep(src,tag,like='../adv/src3.png',dbg=False):
    norm.normalize_like(src,like,f'../grd/n_{tag}.png')
    a=np.array(Image.open(f'../grd/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1);H,W=al.shape
    line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
    inner=ndi.binary_erosion(comp>0,iterations=5)&~ndi.binary_dilation(line,iterations=4)
    hp=lum-ndi.gaussian_filter(lum,1.6);e=hp**2
    ml=ndi.mean(lum,comp,idx);ar=ndi.sum(al,comp,idx);cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T
    ni=ndi.sum(inner,comp,idx);tx=np.sqrt(ndi.sum(e*inner,comp,idx)/np.maximum(ni,1))
    kind=np.where(ml>132,4,np.where(ml>105,5,np.where(ml<66,6,np.where(tx>7.5,15,np.where(np.abs(cx-627)<80,9,16)))))        # 9 = bordure (encolure et bas, centrées) ; 16 = vêtement sombre sous le tabard, sur les côtés
    kind[(kind==5)&(np.abs(cx-627)>400)]=4                                    # doigts des gantelets
    kind[(ar>40000)&(np.abs(cx-627)<60)&(cy<600)&(ml<90)]=7                     # le trou du col
    if dbg:
        for i in np.argsort(-ar)[:36]: print(int(ar[i]),round(float(ml[i])),round(float(tx[i]),1),int(cx[i]),int(cy[i]),kind[i])
    lab=np.zeros((H,W),int);lab[comp>0]=kind[comp[comp>0]-1]
    m15=ndi.binary_closing(lab==15,iterations=9);lab[m15&np.isin(lab,(9,16,0))&~line]=15           # petites mailles isolées
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    return a,lab
G={4:.95,5:.8,9:.8,15:.75,16:.7,6:.7,7:.6}
def char(a,lab,tab,bord,sk='#c98f6a',hr='#8a4a22',metal='#aeb4bc',mail='#6a6e76',under='#3e3a3a',belt='#3a2a1c',pants='#4a4a52',ph=0):
    full.G.update(G);cols={1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512));c.alpha_composite(legs.legs(pants,'#3a2a1c',ph))
    t=full.tint(a,lab,{4:metal,5:tab,9:bord,15:mail,16:under,6:belt,7:'#2a2622'});c.alpha_composite(full.place(t,0.29,(625,360)));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols));return c
if __name__=='__main__':
    a,lab=prep('../grd/relaxed.png','relaxed',dbg=True)
    t=full.tint(a,lab,{4:'#aeb4bc',5:'#7a2a26',9:'#c9a23a',15:'#6a6e76',16:'#3e3a3a',6:'#3a2a1c',7:'#2a2622'}) if not full.G.update(G) else None
    bg=Image.new('RGBA',t.size,(140,105,70,255));bg.alpha_composite(t);bg.crop((0,100,1254,1250)).resize((900,825),Image.LANCZOS).save('../grd/z_relaxed.png')

# Masques précis : graines sûres par matière, puis ligne de partage des eaux qui cale les frontières sur les traits sombres du dessin
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
from scipy import ndimage as ndi
from skimage.segmentation import watershed,find_boundaries
import sys
sys.path.insert(0,'../v3k');import mk
def poly(pts,sh=(512,512)):
    m=Image.new('L',sh,0);ImageDraw.Draw(m).polygon(pts,fill=255);return np.array(m)>0
mir=lambda pts:[(512-x,y) for x,y in pts]
def segment_head(src='assets/head_dwarf_braided_90.png'):
    im=np.array(Image.open(src).convert('RGBA')).astype(float);al=im[...,3]>40
    lum=ndi.gaussian_filter(im[...,:3].mean(-1),0.8)
    elev=255-lum                                  # traits sombres = crêtes
    old=mk.head_masks()
    # métal : bandes au centre de chaque anneau
    rings=[[(215,121),(238,121),(238,130),(215,130)],[(246,105),(270,105),(270,126),(246,126)],[(283,121),(305,121),(305,130),(283,130)],[(248,352),(266,352),(266,360),(248,360)],[(253,374),(260,374),(259,377),(254,377)]]
    metal=np.zeros((512,512),bool)
    for r in rings: metal|=poly(r)
    near=ndi.binary_dilation(metal,iterations=5)
    ear=[(170,206),(176,195),(181,199),(179,214),(175,228),(171,224)]
    ears=poly(ear)|poly(mir(ear))
    earzone=ndi.binary_dilation(poly([(160,184),(187,184),(187,240),(160,240)])|poly(mir([(160,184),(187,184),(187,240),(160,240)])),iterations=1)
    mk_=np.zeros((512,512),int)
    mk_[ndi.binary_erosion(old['hair'],iterations=5)&~near&~earzone]=2
    mk_[ndi.binary_erosion(old['beard'],iterations=5)&~near&~earzone]=3
    mk_[ndi.binary_erosion(old['skin']&~earzone,iterations=3)]=1
    # mèches autour des oreilles : graines cheveux/barbe à la main
    XX=np.arange(512)[None,:]
    mk_[(mk_==1)&((XX<206)|(XX>306))]=0          # les favoris ne sont pas de la peau
    for pts,l in [([(186,186),(196,186),(196,225),(188,225)],2),([(180,243),(186,241),(186,250),(181,250)],3),([(189,237),(200,241),(201,270),(192,264)],3)]:
        for p in (pts,mir(pts)): mk_[poly(p)]=l
    mk_[ears]=1;mk_[metal]=4;mk_[~al]=0
    lab=watershed(elev,mk_,mask=al)
    # sourcils : poils, tracés à la main (pas de trait net autour)
    xs=np.arange(512);pts=[(192,235),(200,246),(208,251),(215,254),(232,258),(246,261),(256,262),(266,261),(280,258),(297,254),(304,251),(312,246),(320,235)]
    eye=np.interp(xs,[p[0] for p in pts],[p[1] for p in pts]);Y=np.arange(512)[:,None];X=xs[None,:]
    lab[(lab==1)&(Y<eye[None,:])&(X>192)&(X<320)]=3
    return im,al,lab,mk_
if __name__=='__main__':
    im,al,lab,seeds=segment_head()
    np.save('head_lab.npy',lab)
    C={1:(255,150,0),2:(0,110,255),3:(0,210,70),4:(255,0,200)}
    o=im[...,:3].copy()
    for l,c in C.items():
        m=lab==l
        for j in range(3): o[...,j][m]=o[...,j][m]*0.55+c[j]*0.45
    b=find_boundaries(lab,mode='inner')&al;o[b]=(255,255,255)
    bg=np.zeros((512,512,3))+np.array((60,60,60));bg[al]=o[al]
    Image.fromarray(bg.astype('uint8')).crop((150,70,362,390)).resize((848,1280),Image.LANCZOS).save('../seg_head.png')

# Oreilles repeintes proprement (forme nette, ourlet clair, creux sombre, trait de contour), glissées sous les mèches
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
from scipy import ndimage as ndi
import seg
S=8;X0,Y0,W,H=150,182,48,64
def ear_left():
    pts=[(194,196),(185,194),(177,196),(171,202),(168,212),(170,222),(175,230),(183,235),(194,237)]
    m=Image.new('L',(W*S,H*S),0);ImageDraw.Draw(m).polygon([((x-X0)*S,(y-Y0)*S) for x,y in pts],fill=255)
    m=np.array(m.filter(ImageFilter.GaussianBlur(1.6*S)))>127
    d=ndi.distance_transform_edt(m)/S
    yy,xx=np.mgrid[0:H*S,0:W*S];x=xx/S+X0;y=yy/S+Y0
    g=np.full(m.shape,128.0)+(214-y)*1.0+np.clip(d,0,5)*5            # volume : bombé, éclairé par le haut
    helix=np.exp(-((d-2.3)/1.1)**2)*np.clip((185-x)/5,0,1);g+=helix*45   # ourlet clair, seulement côté extérieur
    con=np.exp(-(((x-181.5)/3.6)**2+((y-215)/8.5)**2));g-=con*85          # creux sombre
    anti=np.exp(-((np.hypot((x-181.5)/5.2,(y-215)/11)-1)/0.16)**2)*np.clip((183-x)/4,0,1);g+=anti*28   # repli intérieur
    g-=np.clip((x-185)/6,0,1)*55                                          # ombre contre le crâne
    g=ndi.gaussian_filter(g,0.45*S)
    line=np.clip(1.6-(d/0.9),0,1);g=g*(1-line)+38*line                    # trait de contour
    a=ndi.gaussian_filter(m.astype(float),0.3*S)*255
    im=np.dstack([np.clip(g,0,255)]*3+[a]).astype('uint8')
    return Image.fromarray(im,'RGBA').resize((W,H),Image.LANCZOS)
def build():
    im,al,lab,_=seg.segment_head()
    src=Image.open('assets/head_dwarf_braided_90.png').convert('RGBA');a=np.array(src)
    X=np.arange(512)[None,:];old=(lab==1)&((X<189)|(X>323))&(np.arange(512)[:,None]<241)|(~al&(a[...,3]>0)&((X<189)|(X>323)))
    top=a.copy();top[old]=0;top[~( (lab>=2)|((lab==1)&~old) )]=0     # ce qui reste devant : cheveux, barbe, métal, visage
    e=ear_left();base=Image.new('RGBA',(512,512));base.alpha_composite(e,(X0,Y0));base.alpha_composite(e.transpose(Image.FLIP_LEFT_RIGHT),(512-X0-W,Y0))
    earA=np.array(base)[...,3]>100
    keep=top[...,3]>0;soft=ndi.gaussian_filter(keep.astype(float),0.7);nearold=ndi.binary_dilation(old,iterations=2)
    t2=a.copy();t2[...,3]=np.where(nearold,np.clip(soft*1.15,0,1)*a[...,3],top[...,3]).astype('uint8');t2[(~nearold)&~keep]=0
    t2[~al|(lab==0)]=0
    base.alpha_composite(Image.fromarray(t2))
    lab2=lab.copy();lab2[old]=0;lab2[earA&(lab2==0)]=1
    base.save('assets/head_fix.png');np.save('head_fix_lab.npy',lab2)
if __name__=='__main__': build()

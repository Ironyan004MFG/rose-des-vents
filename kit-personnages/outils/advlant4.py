# Lanterne au bout du bras tendu (pose « reach ») : le poing + lanterne dessiné seul par GPT (obj/hand_lantern.png) remplace la main ouverte.
# L'ancienne main est retirée d'après ses matières ; le haut du poing est glissé SOUS le bracelet.
import numpy as np,math
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
from bodyseg import poly
import norm,advp,full,kit,advlant
def prep(tag='reach_lantern4',sc=0.56,rot=-4,src=(640,150),dst_raw=(214,738),H=1700):
    a0,base0=advp.prep('../adv/reach2.png','reach2');top,l,r=norm.collar('../adv/reach2.png');s=(norm.REF[2]-norm.REF[1])/(r-l);cx=(l+r)/2;rcx=(norm.REF[1]+norm.REF[2])/2
    W=base0.shape[1];a=np.zeros((H,W,4));a[:a0.shape[0]]=a0;base=np.zeros((H,W),int);base[:base0.shape[0]]=base0;yy,xx=np.mgrid[:H,:W]
    dst=(rcx+s*(dst_raw[0]-cx),norm.REF[0]+s*(dst_raw[1]-top))
    L=np.array(Image.open('../obj/hand_lantern.png').convert('RGBA')).astype(float);ly,lx=np.mgrid[:L.shape[0],:L.shape[1]];al=L[...,3]>60;lum=L[...,:3].mean(-1)
    sk,k=ndi.label((lum>120)&al&(ly<420));hand=ndi.binary_dilation(ndi.binary_fill_holes(sk==sk[200,640]),iterations=6)&al&(ly<430)
    glass=poly([(452,775),(795,775),(795,1050),(452,1050)],al.shape)&al&(lum>150)
    X=np.zeros(al.shape,np.uint8);X[al]=4;X[glass]=30;X[hand]=1
    t=math.radians(rot);co,si=math.cos(t)/sc,math.sin(t)/sc;A=(co,-si,src[0]-co*dst[0]+si*dst[1], si,co,src[1]-si*dst[0]-co*dst[1])
    C=np.array(Image.fromarray(L.round().astype('uint8')).transform((W,H),Image.AFFINE,A,Image.BICUBIC)).astype(float);CX=np.array(Image.fromarray(X).transform((W,H),Image.AFFINE,A,Image.NEAREST))
    old=(base==1)&(xx<627);rm=ndi.binary_dilation(old,iterations=2)&~ndi.binary_dilation((base!=1)&(base>0)&(a[...,3]>60),iterations=1);rm|=ndi.binary_dilation(old,iterations=9)&(base==0)
    B=a.copy();B[rm,3]=0;B[ndi.binary_dilation(old,iterations=12)&(base==9)&(yy<norm.REF[0]+s*(900-top)),3]=0
    lc,lk=ndi.label((base==6)&(xx<627));touch=np.unique(lc[ndi.binary_dilation(old,iterations=10)&(lc>0)])          # ombre brune de l'ancienne main, sous le bracelet
    for i in touch:
        if (lc==i).sum()<7000: B[ndi.binary_dilation(lc==i,iterations=2)&(base!=4)&(base!=9),3]=0
    near=ndi.binary_dilation(old,iterations=14);thin=(B[...,3]>20)&near&~ndi.binary_opening(B[...,3]>20,iterations=4);B[thin,3]=0
    cc,kk=ndi.label(B[...,3]>20);big=np.argmax(ndi.sum(B[...,3]>20,cc,range(1,kk+1)))+1;B[cc!=big,3]=0
    # sous le bord du bracelet, le poing et la lanterne sont au PREMIER PLAN (bras tendu vers l'avant) ; au-dessus, le bracelet les recouvre
    xr=cx+(xx-rcx)/s;yr=top+(yy-norm.REF[0])/s;front=(yr>717+(xr-110)*0.27+8)&(C[...,3]>0)
    Cf=C.copy();Cf[~front,3]=0;Cb=C.copy();Cb[front,3]=0
    def over(T,U):
        t=T[...,3:]/255;u=U[...,3:]/255;oa=t+u*(1-t);o=np.zeros_like(T);o[...,:3]=(T[...,:3]*t+U[...,:3]*u*(1-t))/np.maximum(oa,1e-6);o[...,3:]=oa*255;return o
    o=over(Cf,over(B,Cb));lab=np.where(Cf[...,3]>128,CX,np.where(B[...,3]>60,base,CX));lab[o[...,3]<=60]=0;Image.fromarray(o.round().astype('uint8')).save(f'../adv/n_{tag}.png');return o,lab
def char(a,lab,cl,sk,hr,inn,metal='#9aa0a8',glow='#ffd98a',H=700):
    hh=1400;c=advp.char(a[:hh],lab[:hh],cl,sk,hr,inn);full.G.update({6:.8,4:.9,9:.95,30:1.0,1:.8});t=np.array(full.tint(a,lab,{**advp.COL(cl,sk,inn),4:metal,30:glow})).astype(float)
    yy,xx=np.mgrid[:lab.shape[0],:lab.shape[1]];m=(lab>0)&(xx<400)&(yy>900)&ndi.binary_dilation(np.isin(lab,(30,)),iterations=160)&np.isin(lab,(4,30,1))
    w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.0))).astype(float)/255;t[...,3]*=w
    c2=Image.new('RGBA',(512,H));c2.alpha_composite(c);c2.alpha_composite(advlant.tall(Image.fromarray(t.astype('uint8')),H));full.G[6]=.7;full.G[4]=1.0;return c2
if __name__=='__main__':
    a,lab=prep();sk='#c98f6a';O=Image.new('RGBA',(1024,700),(140,105,70,255))
    kit.HEAD=('hood',{8:'#2a3042'});O.alpha_composite(char(a,lab,'#343a50','#8a5a3c','#2a2422','#22242e'),(0,0))
    kit.HEAD=('hood',{8:'#6a4a3a'});O.alpha_composite(char(a,lab,'#7a4a3a',sk,'#b9b3aa','#3a2e26'),(512,0))
    O.crop((0,20,1024,660)).convert('RGB').save('../adv/cmp_rl4.png');O.crop((562,270,762,470)).resize((1000,1000),Image.LANCZOS).convert('RGB').save('../adv/z_rl6.png')

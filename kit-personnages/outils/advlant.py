# Aventurier tenant une lanterne à bout de bras : la main fermée sur l'anneau (dessin GPT, adv/lantern.png) est greffée au bout du bras tendu
# de la pose « reach » validée, à la place de la main ouverte. Paume vers le bas, la lanterne pend sous le poing.
import numpy as np,math
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import norm,advp,full,kit
def build(out='../adv/reach_lantern.png',sc=1.12,rot=-6,src_w=(133,757),dst_w=(202,716),H=1400):
    R=np.array(Image.open('../adv/reach2.png').convert('RGBA')).astype(float);L=np.array(Image.open('../adv/lantern.png').convert('RGBA')).astype(float)
    yy,xx=np.mgrid[:1254,:1254]
    # 1) la main fermée, l'anneau et la lanterne, sans le bracelet ni le manteau (contour tracé à la main sur adv/lantern.png)
    from bodyseg import poly
    al=L[...,3]>60;lum=L[...,:3].mean(-1);M=poly([(0,746),(226,750),(229,800),(230,1254),(0,1254)],(1254,1254))&al
    light,k=ndi.label((lum>112)&al&M&(yy>752)&(yy<885));hand=ndi.binary_dilation(ndi.binary_fill_holes(light==light[805,130]),iterations=5)
    ch=L.copy();ch[...,3]=np.where(M,ch[...,3],0)
    ext=ch.copy();ext[:-26]=ch[26:];ext[...,3]=np.where((yy<775)&(yy>728),ext[...,3],0)              # un peu de peau en plus, glissée sous le bracelet
    base=ch
    lant=M&(yy>838)&~hand;glass=ndi.binary_dilation(ndi.binary_opening((lum>205)&lant&(yy>1000),iterations=4),iterations=4)&(lum>195)&(yy>1000)
    lab=np.zeros((1254,1254),np.uint8);lab[base[...,3]>60]=1;lab[lant]=4;lab[glass]=30
    # 2) transformation vers le bout du bras tendu
    t=math.radians(rot);co,si=math.cos(t)/sc,math.sin(t)/sc;sx,sy=src_w;dx,dy=dst_w
    A=(co,-si,sx-co*dx+si*dy, si,co,sy-si*dx-co*dy)
    C=np.array(Image.fromarray(base.round().astype('uint8')).transform((1254,H),Image.AFFINE,A,Image.BICUBIC)).astype(float);CL=np.array(Image.fromarray(lab).transform((1254,H),Image.AFFINE,A,Image.NEAREST))
    Image.fromarray(C.round().astype('uint8')).save(out.replace('.png','_chunk.png'));Image.fromarray(CL).save(out.replace('.png','_lab.png'));return out
def prep(src='../adv/reach_lantern.png',tag='reach_lantern'):
    """Composition dans l'image normalisée : la main ouverte de « reach » est retirée d'après ses matières (peau, côté gauche), exactement ;
    la main à la lanterne est glissée dessous, donc sous le bracelet."""
    a,base=advp.prep('../adv/reach2.png','reach2');top,l,r=norm.collar('../adv/reach2.png');s=(norm.REF[2]-norm.REF[1])/(r-l);cx=(l+r)/2;rcx=(norm.REF[1]+norm.REF[2])/2
    A=(1/s,0,cx-rcx/s,0,1/s,top-norm.REF[0]/s);H,W=base.shape;yy,xx=np.mgrid[:H,:W]
    C=np.array(Image.open(src.replace('.png','_chunk.png')).transform((W,H),Image.AFFINE,A,Image.BICUBIC)).astype(float);X=np.array(Image.open(src.replace('.png','_lab.png')).transform((W,H),Image.AFFINE,A,Image.NEAREST))
    rm=ndi.binary_dilation((base==1)&(xx<627),iterations=2)&~ndi.binary_dilation((base!=1)&(base>0)&(a[...,3]>60),iterations=1);rm|=ndi.binary_dilation((base==1)&(xx<627),iterations=9)&(base==0);B=a.copy();B[rm,3]=0;near=ndi.binary_dilation((base==1)&(xx<627),iterations=14);thin=(B[...,3]>20)&near&~ndi.binary_opening(B[...,3]>20,iterations=4);B[thin,3]=0
    B[ndi.binary_dilation((base==1)&(xx<627),iterations=12)&(base==9)&(yy<900),3]=0                                       # éclats clairs laissés par le contour de l'ancienne main
    cc,kk=ndi.label(B[...,3]>20);big=np.argmax(ndi.sum(B[...,3]>20,cc,range(1,kk+1)))+1;B[(cc!=big),3]=0                     # restes détachés de l'ancien contour
    ba=B[...,3:]/255;c=C[...,3:]/255;o=np.zeros_like(B);oa=ba+c*(1-ba);o[...,:3]=(B[...,:3]*ba+C[...,:3]*c*(1-ba))/np.maximum(oa,1e-6);o[...,3:]=oa*255
    lab=np.where(B[...,3]>60,base,X);al=o[...,3]>60;lab[~al]=0;hole=al&(lab==0);_,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab[hole]=lab[ix[0],ix[1]][hole]
    Image.fromarray(o.round().astype('uint8')).save(f'../adv/n_{tag}.png');return o,lab
def tall(img,H=640):
    w,h=img.size;im=img.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(im,(round(256-625*.29),round(229-360*.29)));return o
def char(a,lab,cl,sk,hr,inn,metal='#aeb4bc',glow='#ffd98a',H=640):
    """Toile plus haute (640) : la lanterne descend sous le cadre habituel de 512."""
    c=advp.char(a,lab,cl,sk,hr,inn);full.G.update({6:.8,4:.95,9:.95,30:1.05,1:.8});t=np.array(full.tint(a,lab,{**advp.COL(cl,sk,inn),4:metal,30:glow})).astype(float)
    hh,ww=lab.shape;yy,xx=np.mgrid[:hh,:ww];m=np.isin(lab,(4,30))&(xx<330)&(yy>830)|((yy>880)&(xx<330)&(lab>0))
    w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.0))).astype(float)/255;t[...,3]*=w
    c2=Image.new('RGBA',(512,H));c2.alpha_composite(c);c2.alpha_composite(tall(Image.fromarray(t.astype('uint8')),H));full.G[6]=.7;return c2
if __name__=='__main__':
    build();a,lab=prep();im=Image.open('../adv/n_reach_lantern.png');bg=Image.new('RGBA',im.size,(150,40,40,255));bg.alpha_composite(im);bg.crop((20,640,420,1000)).resize((1000,900),Image.LANCZOS).save('../adv/z_rl.png')

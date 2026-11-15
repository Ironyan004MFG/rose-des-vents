import numpy as np,sys
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import full,norm,bodyseg,r2,kit,legs
def prep(src,tag,carry=False):
    print(tag,norm.normalize(src,f'../adv/n_{tag}.png'))
    bodyseg.HML=128;a,lab=bodyseg.auto_seg(f'../adv/n_{tag}.png');bodyseg.HML=100
    if carry: lab=r2.held(a,lab)
    al=a[...,3]>60;lum=a[...,:3].mean(-1);line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
    ml=ndi.mean(lum,comp,idx);area=ndi.sum(al,comp,idx)
    for i in range(k):
        if area[i]<120: continue
        m=comp==i+1;maj=np.bincount(lab[m],minlength=14).argmax()
        if maj in(5,9) and ml[i]<80: lab[m]=6
        elif maj in(5,6,9) and ml[i]>150 and area[i]<2500: lab[m]=4          # rivets
    _,ix=ndi.distance_transform_edt(~((lab>0)&~line),return_indices=True);l2=lab[ix[0],ix[1]];l2[~al]=0
    return a,l2
COL=lambda cl,sk,inn,lea='#5a3a22':{5:cl,1:sk,7:inn,9:'#d8d2c4',6:lea,10:'#c98f4a',11:'#e8c84a',12:'#6a3a7a'}
def char(a,lab,cl,sk,hr,inn,carry=False):
    full.G.update({6:.8,10:.9,11:.95,12:.85,4:1.0,9:.95})
    cols={5:cl,1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512));c.alpha_composite(legs.legs('#4a3a2a','#3a2a1c'))
    t=full.tint(a,lab,COL(cl,sk,inn));c.alpha_composite(full.place(t,0.29,(625,360)));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols))
    if carry:
        ta=np.array(t).astype(float);m=np.isin(lab,(1,4,10,11,12));w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5))).astype(float)/255;ta[...,3]*=w
        c.alpha_composite(full.place(Image.fromarray(ta.astype('uint8')),0.29,(625,360)))
    full.G[6]=.7;return c
if __name__=='__main__':
    a,lab=prep('../adv/plate.png','plate',True);b,lb=prep('../adv/src3.png','rel')
    C={1:(255,150,0),4:(255,0,200),5:(255,40,50),7:(0,200,255),9:(255,255,0),6:(120,70,20),10:(0,255,0),11:(255,255,255),12:(150,0,255)}
    o=np.zeros(a.shape[:2]+(3,))+40
    for l,c in C.items(): m=lab==l;o[m]=np.array(c)*0.55+a[...,:3][m]*0.45
    Image.fromarray(o.astype('uint8')).resize((627,700)).save('../advp_lab.png')
    V=r2.V;O=Image.new('RGBA',(512*3,512),(140,105,70,255))
    O.alpha_composite(char(b,lb,*V[0]),(0,0));O.alpha_composite(char(a,lab,*V[0],carry=True),(512,0));O.alpha_composite(char(a,lab,*V[1],carry=True),(1024,0))
    O.crop((0,40,1536,512)).resize((1920,590),Image.LANCZOS).save('../advp_cmp.png')

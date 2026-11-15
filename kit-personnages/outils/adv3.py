import numpy as np,math
from PIL import Image
from scipy import ndimage as ndi
import full,norm,bodyseg,r2,kit,legs
print('col',norm.collar('../adv/src3.png'),'ref',norm.REF)
print(norm.normalize('../adv/src3.png','../adv/n3.png'))
bodyseg.HML=128
a,lab=bodyseg.auto_seg('../adv/n3.png');bodyseg.HML=100
al=a[...,3]>60;lum=a[...,:3].mean(-1);line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
ml=ndi.mean(lum,comp,idx);area=ndi.sum(al,comp,idx);maj=np.array([np.bincount(lab[comp==i],minlength=14).argmax() for i in idx])
cl=np.median(lum[lab==5]);print('tissu',cl,[(int(m),int(s)) for m,s in zip(ml,area) if s>3000])
for i in range(k):
    if maj[i] in(5,9) and area[i]>300:
        if ml[i]<80: lab[(comp==i+1)]=6
        elif ml[i]>145 and area[i]<12000: lab[(comp==i+1)]=4
_,ix=ndi.distance_transform_edt(~((lab>0)&~line),return_indices=True);l2=lab[ix[0],ix[1]];l2[~al]=0;lab=l2
np.save('../adv/lab3.npy',lab)
C={1:(255,150,0),4:(255,0,200),5:(255,40,50),7:(0,200,255),9:(255,255,0),6:(120,70,20)}
o=np.zeros(a.shape[:2]+(3,))+40
for l,c in C.items(): m=lab==l;o[m]=np.array(c)*0.55+a[...,:3][m]*0.45
Image.fromarray(o.astype('uint8')).resize((627,700)).save('../adv3_lab.png')
def body(cl,sk,inn,trim='#b9b3aa',lea='#5a3a22'): return full.place(full.tint(a,lab,{5:cl,1:sk,7:inn,9:trim,6:lea}),0.29,(625,360))
V=r2.V;O=Image.new('RGBA',(512*4,512),(140,105,70,255))
for i in range(2):
    cl_,sk,hr,inn=V[i*2];cols={5:cl_,1:sk,2:hr,3:hr,6:'#3a2a1c'}
    c=Image.new('RGBA',(512,512));c.alpha_composite(legs.legs('#4a3a2a','#3a2a1c'));c.alpha_composite(body(cl_,sk,inn));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols));O.alpha_composite(c,(i*1024,0))
    O.alpha_composite(r2.char('robe_relaxed',*V[i*2]),(i*1024+512,0))
O.crop((0,40,2048,512)).save('../adv3_cmp.png')

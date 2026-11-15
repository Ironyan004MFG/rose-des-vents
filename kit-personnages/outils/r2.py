import numpy as np,math,os,glob,sys
from PIL import Image,ImageFilter
import full,kit,bodyseg
full.G.update({4:1.0,9:.95,10:.9,11:.95,12:.85})
D='../r2/n/';N=['robe_relaxed','robe_reach','robe_carry_plate','robe_walk_1','robe_walk_2','robe_walk_3','robe_walk_4','coat_relaxed']
RAW={}
def raw(n):
    if n not in RAW:
        p=D+f'lab_{n}.npy';a,lab=bodyseg.auto_seg(D+f'body_dwarf_{n}.png')
        if 'carry' in n: lab=held(a,lab)
        if 'reach' in n: lab[(lab==4)&(ndi.distance_transform_edt(lab!=1)>75)]=9
        RAW[n]=(a,lab)
    return RAW[n]
from scipy import ndimage as ndi
def held(a,lab):
    """objet tenu à deux mains : régions fermées par le trait situées entre les mains. 4 = plat, 10 pain, 11 fromage, 12 raisins"""
    al=a[...,3]>60;lum=a[...,:3].mean(-1);line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
    hm=lab==1;hc,hn=ndi.label(hm);sz=ndi.sum(hm,hc,np.arange(1,hn+1));two=np.argsort(-sz)[:2]+1
    (y0,x0),(y1,x1)=[ndi.center_of_mass(hc==t) for t in two];xl,xr=sorted((x0,x1));ym=(y0+y1)/2;xm=(xl+xr)/2
    cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T;area=ndi.sum(al,comp,idx);ml=ndi.mean(lum,comp,idx)
    out=lab.copy()
    for i in range(k):
        if area[i]<150 or area[i]>90000: continue
        e=((cx[i]-xm)/((xr-xl)/2+5))**2+((cy[i]-(ym-25))/135)**2
        if e>1: continue
        m=(comp==i+1)&(lab!=1)
        if (lab[comp==i+1]==7).mean()>0.5 or (cy[i]<ym-150): continue
        if cy[i]>ym+35 and area[i]>6000: out[m]=4                       # le plat
        elif cx[i]>xm+45: out[m]=12                                      # raisins
        elif abs(cx[i]-(xm+10))<75 and cy[i]>ym-35: out[m]=11            # fromage
        else: out[m]=10                                                  # pain
    _,ix=ndi.distance_transform_edt((out==5)&ndi.binary_dilation(np.isin(out,(4,10,11,12)),iterations=4)|(~al&False),return_indices=True)
    return out
TRIM=['#c9a23a'];BDY=60
def tinted(n,cl,sk,inn): a,lab=raw(n);return full.tint(a,lab,{5:cl,1:sk,7:inn,9:TRIM[0],10:'#c98f4a',11:'#e8c84a',12:'#6a3a7a'})
def body(n,cl,sk,inn): return full.place(tinted(n,cl,sk,inn),0.29,(625,360))
def front(n,cl,sk,inn):
    a,lab=raw(n);t=np.array(tinted(n,cl,sk,inn)).astype(float);m=np.isin(lab,(1,4,10,11,12))
    w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5))).astype(float)/255;t[...,3]*=w
    return full.place(Image.fromarray(t.astype('uint8')),0.29,(625,360))
def boots(cols,ph,dy=None):
    b=kit.tint('boots_dwarf_90',cols);o=Image.new('RGBA',(512,512));dy=BDY if dy is None else dy
    for x0,x1,s in ((0,256,1),(256,512,-1)): o.paste(b.crop((x0,0,x1,512)),(x0,dy+int(round(9*s*math.sin(ph)))))
    return o
def char(n,cl,sk,hr,inn,ph=0):
    cols={5:cl,1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512))
    c.alpha_composite(boots(cols,ph,26 if n.startswith('coat') else None));c.alpha_composite(body(n,cl,sk,inn));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols))
    if 'carry' in n: c.alpha_composite(front(n,cl,sk,inn))
    return c
V=[('#2f6a34','#c98f6a','#8a4a22','#3a2e26'),('#2d4a7a','#8a5a3c','#b9b3aa','#5a4632'),('#7a2a26','#e2b592','#2a2422','#2a2622'),('#5a4a6e','#d9a47e','#c9a23a','#3a3048')]
if __name__=='__main__':
    C={1:(255,150,0),4:(255,0,200),5:(255,40,50),7:(0,200,255),9:(255,255,0),10:(0,255,0),11:(255,255,255),12:(150,0,255)}
    W=np.zeros((1400*2,1254*4,3))+40
    for i,n in enumerate(N):
        a,lab=raw(n);o=np.zeros(a.shape[:2]+(3,))+40
        for l,c in C.items(): m=lab==l;o[m]=np.array(c)*0.55+a[...,:3][m]*0.45
        W[(i//4)*1400:(i//4+1)*1400,(i%4)*1254:(i%4+1)*1254]=o
    Image.fromarray(W.astype('uint8')).resize((1672,933),Image.LANCZOS).save('../r2_lab.png')
    O=Image.new('RGBA',(512*4,512*2),(140,105,70,255))
    for i,n in enumerate(N): O.alpha_composite(char(n,*V[i%4]),((i%4)*512,(i//4)*512))
    O.crop((0,40,2048,1024)).resize((1536,738),Image.LANCZOS).save('../r2_tinted.png')
    Z=Image.new('RGBA',(1024,512),(140,105,70,255));Z.alpha_composite(char('robe_carry_plate',*V[2]),(0,0));Z.alpha_composite(char('coat_relaxed',*V[0]),(512,0));Z.crop((40,50,984,500)).resize((1888,900),Image.LANCZOS).save('../r2_zoom.png')

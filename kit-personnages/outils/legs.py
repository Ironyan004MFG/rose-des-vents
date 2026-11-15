import numpy as np,math,glob
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import full,norm,r2,kit
full.G.update({13:.75,6:.7})
SRC=glob.glob('../lg2/**/legs_dwarf_pants.png',recursive=True)[0]
COAT=glob.glob('../r2/*/body_dwarf_coat_relaxed.png')[0]
def load():
    top,l,r=norm.collar(COAT);s=(norm.REF[2]-norm.REF[1])/(r-l);cx=(l+r)/2;rcx=(norm.REF[1]+norm.REF[2])/2
    im=Image.open(SRC).convert('RGBA').transform((1254,1400),Image.AFFINE,(1/s,0,cx-rcx/s,0,1/s,top-norm.REF[0]/s),Image.BICUBIC)
    a=np.array(im).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1);ls=ndi.gaussian_filter(lum,1.0)
    line=(ls<48)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1);area=ndi.sum(al,comp,idx);cy,cx_=np.array(ndi.center_of_mass(al,comp,idx)).T;ml=ndi.mean(lum,comp,idx)
    ys=np.where(al.any(1))[0];y0,y1=ys.min(),ys.max();H=y1-y0
    kind=np.full(k,13)
    kind[cy>y0+H*0.52]=6                                   # bottes et leurs sangles
    kind[(ml>112)&(area<9000)]=4                           # boucles, rivets
    lab=np.zeros(al.shape,int);lab[comp>0]=kind[comp[comp>0]-1]
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    return a,lab,(y0,y1)
A,LAB,(Y0,Y1)=load()
def legs(pants,leather,ph=0,amp=22):
    t=full.tint(A,LAB,{13:pants,6:leather});o=Image.new('RGBA',t.size);ysplit=int(Y0+(Y1-Y0)*0.30)
    o.paste(t.crop((0,0,1254,ysplit)),(0,0))                # bassin fixe
    for x0,x1,s in ((0,627,1),(627,1254,-1)):
        part=t.crop((x0,ysplit,x1,1400));dy=int(round(amp*s*math.sin(ph)));tmp=Image.new('RGBA',t.size);tmp.paste(part,(x0,ysplit+dy));o.alpha_composite(tmp)
    k=LEGW;kv=LEGH;o=o.transform(o.size,Image.AFFINE,(1/k,0,627-627/k,0,1/kv,Y0-(Y0-LEGUP)/kv),Image.BICUBIC)      # jambes élargies pour la carrure du nain
    return full.place(o,0.29,(625,360))
LEGW=1.0;LEGH=1.0;LEGUP=0
def char(n,cl,sk,hr,inn,pants='#4a3a2a',ph=0):
    cols={5:cl,1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512))
    c.alpha_composite(legs(pants,'#3a2a1c',ph));c.alpha_composite(r2.body(n,cl,sk,inn));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols));return c
if __name__=='__main__':
    V=r2.V;P=['#4a3a2a','#3a3f4a','#5a4a32','#2a2a2a']
    O=Image.new('RGBA',(512*4,512),(140,105,70,255))
    for i in range(4): O.alpha_composite(char('coat_relaxed',*V[i],pants=P[i]),(i*512,0))
    O.crop((0,40,2048,512)).resize((1792,413),Image.LANCZOS).save('../lg_tinted.png')
    Z=Image.new('RGBA',(512,512),(140,105,70,255));Z.alpha_composite(char('coat_relaxed',*V[0],pants=P[0]));Z.crop((70,50,442,512)).resize((992,1232),Image.LANCZOS).save('../lg_zoom.png')
    import os,glob as gl;os.makedirs('../lgf',exist_ok=True);[os.remove(f) for f in gl.glob('../lgf/*.png')]
    cols={5:V[0][0],1:V[0][1],2:V[0][2],3:V[0][2],6:'#3a2a1c'};head=kit.tint('head_dwarf_braided_90',cols);bd=r2.body('coat_relaxed',V[0][0],V[0][1],V[0][3])
    for f in range(72):
        t=f/24;ph=t*1.1*2*math.pi;c=Image.new('RGBA',(512,512),(140,105,70,255));c.alpha_composite(legs(P[0],'#3a2a1c',ph))
        b2=bd.rotate(1.5*math.sin(ph),resample=Image.BICUBIC,center=(256,260));c.alpha_composite(b2);c.alpha_composite(head.rotate(3*math.sin(t*1.3),resample=Image.BICUBIC,center=(256,229)));c.convert('RGB').save(f'../lgf/f{f:03d}.png')
    L=Image.new('RGBA',(512,512),(140,105,70,255));L.alpha_composite(legs(P[0],'#3a2a1c'));L.crop((120,280,392,500)).resize((816,660),Image.LANCZOS).save('../lg_legs.png')

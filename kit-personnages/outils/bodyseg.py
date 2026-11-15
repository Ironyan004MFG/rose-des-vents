# Masques automatiques d'un corps complet (1254 px) : 1 peau, 4 métal, 5 tissu, 7 chemise
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage as ndi
from skimage.segmentation import watershed
SHO=[(250,430),(1000,430)]
LT=52
HML=100
def poly(pts,sh):
    m=Image.new('L',(sh[1],sh[0]),0);ImageDraw.Draw(m).polygon(pts,fill=255);return np.array(m)>0
def auto_seg(path):
    """Régions fermées par le trait noir, classées par forme et position."""
    a=np.array(Image.open(path).convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1);ls=ndi.gaussian_filter(lum,1.0)
    H,W=al.shape;line=(ls<LT)&al;comp,n=ndi.label(al&~line);idx=np.arange(1,n+1)
    area=ndi.sum(al,comp,idx);cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T;ml=ndi.mean(lum,comp,idx)
    edt=ndi.distance_transform_edt(comp>0);fat=ndi.maximum(ndi.distance_transform_edt(al&~line),comp,idx)
    shirt=poly([(520,300),(730,300),(625,950)],(H,W))|poly([(545,215),(705,215),(705,300),(545,300)],(H,W))
    fs=ndi.mean(shirt.astype(float),comp,idx)
    ds=np.minimum(np.hypot(cx-SHO[0][0],cy-SHO[0][1]),np.hypot(cx-SHO[1][0],cy-SHO[1][1]))
    kind=np.full(n,5)
    kind[fs>0.5]=7
    hand=(fat>28)&(fat/np.sqrt(area)>0.24)&(area>2500)&(area<48000)&(np.abs(cx-627)>190)&(cy>520)&(ds>215)&(ml>HML)&(fs<0.2)
    kind[hand]=1
    # un bracelet large et clair peut passer pour une main : de deux « mains » voisines du même côté, celle qui est vers l'épaule est le bracelet
    hi=np.where(hand)[0]
    for p in hi:
        for q in hi:
            if p>=q or (cx[p]-627)*(cx[q]-627)<0 or np.hypot(cx[p]-cx[q],cy[p]-cy[q])>230: continue
            S=min(SHO,key=lambda t:(t[0]-cx[p])**2+(t[1]-cy[p])**2);dp=np.hypot(cx[p]-S[0],cy[p]-S[1]);dq=np.hypot(cx[q]-S[0],cy[q]-S[1])
            kind[p if dp<dq else q]=4
    lab=np.zeros((H,W),int);lab[comp>0]=kind[comp[comp>0]-1];hm=lab==1
    if hm.any():
        dh=ndi.distance_transform_edt(~hm);near=ndi.minimum(dh,comp,idx)
        hc,hn=ndi.label(hm);hcy,hcx=np.array(ndi.center_of_mass(hm,hc,np.arange(1,hn+1))).T
        def side(k):       # cosinus entre (main -> région) et (main -> épaule) : > 0 = côté bras
            h=np.argmin((hcx-cx[k])**2+(hcy-cy[k])**2);S=min(SHO,key=lambda q:(q[0]-hcx[h])**2+(q[1]-hcy[h])**2)
            u=np.array([cx[k]-hcx[h],cy[k]-hcy[h]]);v=np.array([S[0]-hcx[h],S[1]-hcy[h]]);return float(u@v/(np.linalg.norm(u)*np.linalg.norm(v)+1e-6))
        # objet tenu à deux mains : régions situées entre les deux mains
        if hn==2 and max(abs(hcx-627))<300:
            x0,x1=sorted(hcx);ym=hcy.mean()
            for k in range(n):
                if kind[k] in(5,7) and x0+25<cx[k]<x1-25 and abs(cy[k]-ym)<95 and area[k]>1200 and area[k]<150000 and fs[k]<0.6: kind[k]=4
        for k in range(n):
            if kind[k]!=5 or near[k]>14 or area[k]>16000: continue
            if side(k)>0.3 and ml[k]>105: kind[k]=4      # bracelet (jamais une pièce sombre : cuir, sacoche)
            elif ml[k]>98: kind[k]=1                     # doigt, pouce
        lab[comp>0]=kind[comp[comp>0]-1]
        for _ in range(2):                               # rivets et deuxième bande, collés au bracelet
            mm=lab==4;nm=ndi.minimum(ndi.distance_transform_edt(~mm),comp,idx)
            for k in range(n):
                if kind[k]==5 and nm[k]<10 and area[k]<16000 and near[k]<120 and side(k)>0.2 and ml[k]>105: kind[k]=4
            lab[comp>0]=kind[comp[comp>0]-1]
    kind[(kind==5)&(ml>112)&(fat<20)&(area>600)]=9          # liseré : bandes claires et minces du vêtement
    lab[comp>0]=kind[comp[comp>0]-1]
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    # rattrapages quand le trait ne ferme pas complètement une pièce
    hm=lab==1
    if hm.any():
        yy,xx=np.mgrid[0:H,0:W];l2=ndi.gaussian_filter(lum,2.5);hc,hn=ndi.label(hm);cms=ndi.center_of_mass(hm,hc,np.arange(1,hn+1))
        big=[(c,i+1) for i,c in enumerate(cms) if (hc==i+1).sum()>2500]
        for (hy,hx),i in big:
            m=hc==i;dh=ndi.distance_transform_edt(~m)
            if ((lab==4)&(dh<40)).sum()>400: continue                      # bracelet déjà trouvé
            S=min(SHO,key=lambda q:(q[0]-hx)**2+(q[1]-hy)**2);ux,uy=S[0]-hx,S[1]-hy;un=np.hypot(ux,uy)
            cosv=((xx-hx)*ux+(yy-hy)*uy)/(np.hypot(xx-hx,yy-hy)*un+1e-6)
            br=np.isin(lab,(5,9))&(dh<62)&(cosv>0.25)&(l2>112)
            br=ndi.binary_closing(br,iterations=6)&np.isin(lab,(5,9))&(dh<70);lab[br]=4
        if len(big)==2 and max(abs(c[1]-627) for c,_ in big)<300 and not((lab==4)&(np.abs(xx-627)<120)&(np.abs(yy-np.mean([c[0] for c,_ in big]))<80)).sum()>3000:
            x0,x1=sorted(c[1] for c,_ in big);ym=np.mean([c[0] for c,_ in big])
            ob=(lab!=1)&al&(xx>x0-40)&(xx<x1+40)&(np.abs(yy-ym)<120)&(l2>112)
            ob=ndi.binary_opening(ob,iterations=8);oc,on=ndi.label(ob)
            if on:
                ob=oc==(1+np.argmax(ndi.sum(ob,oc,np.arange(1,on+1))));ob=ndi.binary_fill_holes(ndi.binary_closing(ob,iterations=10));lab[ob&(lab!=1)]=4
    # liseré : bandes claires du vêtement (le trait ne les ferme pas toujours, donc on les prend par leur clarté)
    tr=(lab==5)&(ndi.gaussian_filter(lum,1.5)>140);tc,tn=ndi.label(tr)
    if tn:
        sz=ndi.sum(tr,tc,np.arange(1,tn+1));keep=np.isin(tc,1+np.where(sz>5000)[0]);lab[keep]=9
    return a,lab
if __name__=='__main__':
    N=['relaxed','reach','carry_plate','walk_1','walk_2','walk_3','walk_4'];C={1:(255,150,0),4:(255,0,200),5:(255,40,50),7:(0,200,255),9:(255,255,0)}
    W=np.zeros((1254*2,1254*4,3))+40
    for i,n in enumerate(N):
        a,lab=auto_seg(f'../c7/originaux_1254/body_dwarf_coat_{n}.png');np.save(f'../c7/lab_{n}.npy',lab)
        o=np.zeros((1254,1254,3))+40
        for l,c in C.items(): m=lab==l;o[m]=np.array(c)*0.55+a[...,:3][m]*0.45
        W[(i//4)*1254:(i//4+1)*1254,(i%4)*1254:(i%4+1)*1254]=o
    Image.fromarray(W.astype('uint8')).resize((1672,836),Image.LANCZOS).save('../c7_lab.png')

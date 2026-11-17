"""Queues du tieffelin : planche de GPT dessinée sur nos silhouettes, recalée par les croix rouges.
build() -> assets/tail_k.png (toile 512x660, croix = (256,387)) + tail_k_lab.npy (1 peau, 4 métal/bijoux, 2 poils)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ANCHOR=(256,387);G={1:.95,4:1.0,2:.9}
def build(src='../tq/q2_gris.png',mp='../tq/q2_map.png',n=8):
    calq=calque(mp,n)
    a=np.array(Image.open(src).convert('RGB')).astype(float);H,W=a.shape[:2];r,g,b=a[...,0],a[...,1],a[...,2];red=(r>170)&(g<90)&(b<90);c,k=ndi.label(ndi.binary_dilation(red,iterations=3))
    cen=sorted([ndi.center_of_mass(c==i) for i in range(1,k+1) if (c==i).sum()>60],key=lambda p:(round(p[0]/(H/2)),p[1]));assert len(cen)==n,len(cen)
    dx=np.median(np.diff([p[1] for p in cen[:4]]));s=(570/1.5)/dx;lum=a.mean(-1)      # 570 px par case sur notre planche, dessinée à 1,5x la toile
    # la croix : remplacée par le gris voisin
    rd=ndi.binary_dilation(red,iterations=2);_,ix=ndi.distance_transform_edt(rd,return_indices=True);a2=a.copy();a2[rd]=a[ix[0][rd],ix[1][rd]];lum2=a2.mean(-1)
    dark=ndi.binary_fill_holes(ndi.binary_closing(lum2<218,iterations=2));cc,kk=ndi.label(dark);out=[]
    for i,(cy,cx) in enumerate(cen,1):
        ids=np.unique(cc[int(cy)-12:int(cy)+13,int(cx)-12:int(cx)+13]);ids=ids[ids>0];m=np.isin(cc,ids)
        # chaînettes et pendeloques détachées : composantes proches
        near=ndi.binary_dilation(m,iterations=14)
        for j in np.unique(cc[near]):
            if j and j not in ids and (cc==j).sum()<2500: m|=cc==j
        ys,xs=np.where(m);y0,y1,x0,x1=ys.min()-3,ys.max()+4,xs.min()-3,xs.max()+4;sub=a2[y0:y1,x0:x1];mm=m[y0:y1,x0:x1];g_=sub.mean(-1)
        L=labels_from_calque(calq,i-1,mm)
        rgba=np.dstack([sub,np.where(mm,255,0)]).astype('uint8');t=Image.fromarray(rgba);nw,nh=round(t.size[0]*s),round(t.size[1]*s);t=t.resize((nw,nh),Image.LANCZOS);Ls=Image.fromarray(L.astype('uint8')).resize((nw,nh),Image.NEAREST)
        o=Image.new('RGBA',(512,660));lo=Image.new('L',(512,660));off=(round(ANCHOR[0]-(cx-x0)*s),round(ANCHOR[1]-(cy-y0)*s));o.paste(t,off);lo.paste(Ls,off);o.save(f'assets/tail_{i}.png');np.save(f'assets/tail_{i}_lab.npy',np.array(lo));out.append((i,off,(nw,nh),[int((L==q).sum()) for q in (1,2,4)]))
    return s,out
def calque(mp,n=8):
    """Calque de GPT (autre format que le gris) : pour chaque queue, (couleurs, masque) recadrés sur la queue."""
    a=np.array(Image.open(mp).convert('RGB')).astype(int);H,W=a.shape[:2];r,g,b=a[...,0],a[...,1],a[...,2];red=(r>190)&(g<90)&(b<90);c,k=ndi.label(ndi.binary_dilation(red,iterations=3))
    cen=sorted([ndi.center_of_mass(c==i) for i in range(1,k+1) if (c==i).sum()>50],key=lambda p:(round(p[0]/(H/2)),p[1]));assert len(cen)==n,len(cen)
    col=((a.max(-1)-a.min(-1))>90)|(a.mean(-1)<80);col=ndi.binary_closing(col|ndi.binary_dilation(red,iterations=2),iterations=2);cc,kk=ndi.label(col);out=[]
    for cy,cx in cen:
        ids=np.unique(cc[int(cy)-10:int(cy)+11,int(cx)-10:int(cx)+11]);ids=ids[ids>0];m=np.isin(cc,ids);near=ndi.binary_dilation(m,iterations=14)
        for j in np.unique(cc[near]):
            if j and j not in ids and (cc==j).sum()<2500: m|=cc==j
        ys,xs=np.where(m);out.append((a[ys.min():ys.max()+1,xs.min():xs.max()+1],m[ys.min():ys.max()+1,xs.min():xs.max()+1]))
    return out
def labels_from_calque(calq,i,mm):
    """Matières d'une queue : le calque est étiré sur la boîte de la queue grise. BLEU = poils (2), VERT = métal (4) ; les bijoux que GPT a
    laissés en jaune sont reconnus à leurs nombreux traits noirs intérieurs (la peau est un aplat sans trait)."""
    a,m=calq[i];h,w=mm.shape;r,g,b=a[...,0],a[...,1],a[...,2];dark=(a.mean(-1)<80)&m;L=np.where(m,1,0)
    L[(b>150)&(r<110)&(g<110)]=2;L[(g>150)&(r<120)&(b<120)]=4;L[(r>170)&(b>170)&(g<110)]=1
    inner=ndi.binary_erosion(m,iterations=6);dens=ndi.uniform_filter((dark&inner).astype(float),17);jw=ndi.binary_closing(ndi.binary_opening(dens>.13,iterations=3),iterations=6)&m;jw=ndi.binary_dilation(jw,iterations=5)&m;L[jw&(L==1)]=4
    L[dark]=0;_,ix=ndi.distance_transform_edt(L==0,return_indices=True);L=L[ix[0],ix[1]];L[~m]=0
    Ls=np.array(Image.fromarray(L.astype('uint8')).resize((w,h),Image.NEAREST)).astype(int);_,ix=ndi.distance_transform_edt(Ls==0,return_indices=True);Ls=Ls[ix[0],ix[1]];Ls[~mm]=0;return Ls
def build_old(ks=(1,2,7),first=9,s=.48):
    """Les trois queues de la première planche, validées par Yannick : retournées de 180°, glissées derrière la hanche."""
    for n,k in enumerate(ks):
        t=Image.open(f'../tq/t{k}.png').convert('RGBA').rotate(180);t=t.resize((round(t.size[0]*s),round(t.size[1]*s)),Image.LANCZOS);o=Image.new('RGBA',(512,660));o.alpha_composite(t,(228-t.size[0],385-t.size[1]))
        o.save(f'assets/tail_{first+n}.png');np.save(f'assets/tail_{first+n}_lab.npy',(np.array(o)[...,3]>40).astype('uint8'))
def tint(k,skin,metal='#d8c070',hair='#2a2420',mirror=False):
    a=np.array(Image.open(f'assets/tail_{k}.png').convert('RGBA')).astype(float);lab=np.load(f'assets/tail_{k}_lab.npy');lum=a[...,:3].mean(-1)/255;out=a.copy()
    for l,col in ((1,skin),(4,metal),(2,hair)):
        m=lab==l
        if not m.any(): continue
        f=np.clip(lum/lum[m].mean()*G[l],0,1.4);C=[int(col[j:j+2],16) for j in (1,3,5)]
        for j in range(3): out[...,j]=np.where(m,np.clip(C[j]*f,0,255),out[...,j])
    im=Image.fromarray(out.astype('uint8'))
    if mirror: im=im.transpose(Image.FLIP_LEFT_RIGHT)      # la toile fait 512 de large et l'attache est à x=256 : le miroir garde l'attache en place
    return im

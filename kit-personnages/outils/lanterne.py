# Poing à la lanterne (obj/hand_lantern.png, main NUE dessinée seule) posé au bout d'un bras tendu, pour n'importe quelle tenue à poignet de métal.
# Méthode validée sur l'aventurier (advlant4.py), rendue générique : la main ouverte est retirée d'après ses matières ; le poing est calé sur le
# bord bas du poignet (bracelet), dont il prend la largeur ; il glisse SOUS le bracelet et passe DEVANT tout le reste.
import numpy as np,math
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
from bodyseg import poly
SRC={}
PIV=(640,290)                                                                # centre du poing dans le dessin d'origine
def source(ang=0.0):
    """Poing + lanterne. ang (degrés, sens horaire) : le poing seul pivote autour de son centre pour suivre l'axe du bras ; la lanterne reste d'aplomb."""
    ang=round(float(ang),1)
    if ang not in SRC:
        L=np.array(Image.open('../obj/hand_lantern.png').convert('RGBA')).astype(float);ly,lx=np.mgrid[:L.shape[0],:L.shape[1]];al=L[...,3]>60;lum=L[...,:3].mean(-1)
        sk,k=ndi.label((lum>120)&al&(ly<420));hand=ndi.binary_dilation(ndi.binary_fill_holes(sk==sk[200,640]),iterations=6)&al&(ly<430)
        glass=poly([(452,775),(795,775),(795,1050),(452,1050)],al.shape)&al&(lum>150);X=np.zeros(al.shape,np.uint8);X[al]=4;X[glass]=30;X[hand]=1
        if ang:
            Hd=L.copy();Hd[~hand,3]=0;Ln=L.copy();Ln[hand,3]=0
            grow=ndi.binary_dilation(~hand&al,iterations=26)&hand;_,ix=ndi.distance_transform_edt(hand|~al,return_indices=True);Ln[grow]=L[ix[0],ix[1]][grow]      # l'anse continue sous les doigts
            Hr=np.array(Image.fromarray(Hd.round().astype('uint8')).rotate(-ang,Image.BICUBIC,center=PIV)).astype(float);hm=Hr[...,3:]/255
            L=Hr*hm+Ln*(1-hm);L[...,3]=np.maximum(Hr[...,3],Ln[...,3]);X=np.zeros(al.shape,np.uint8);X[L[...,3]>60]=4;X[glass]=30;X[Hr[...,3]>128]=1
        SRC[ang]=(L,X)
    return SRC[ang]
def graft(a0,lab0,rot=0,fit=1.06,up=7,H=1700,cuff=(4,9),dx=0,tilt=1.0,mend=False,follow=True):
    """a0, lab0 : image normalisée et matières d'une pose à main tendue (main ouverte à gauche). Renvoie (image, matières) sur une toile de hauteur H."""
    W=lab0.shape[1];a=np.zeros((H,W,4));a[:a0.shape[0]]=a0;base=np.zeros((H,W),int);base[:lab0.shape[0]]=lab0;yy,xx=np.mgrid[:H,:W]
    old=(base==1)&(xx<627);ys,xs=np.where(old);x0,x1=xs.min(),xs.max()
    cf=np.isin(base,cuff)&ndi.binary_dilation(old,iterations=45)&(xx<627)&(yy<ys.mean());cl,k=ndi.label(cf);cf=cl==(np.argmax(ndi.sum(cf,cl,range(1,k+1)))+1)
    cols=np.where(cf.any(0))[0];edge=np.full(W,np.nan);edge[cols]=[np.where(cf[:,c])[0].max() for c in cols];edge=np.interp(np.arange(W),cols,ndi.median_filter(edge[cols],9))
    py,px=np.where(cf);cv=np.cov(np.c_[px,py].T);ev,evec=np.linalg.eigh(cv);v=evec[:,1]*(1 if evec[0,1]>0 else -1);phi=math.degrees(math.atan2(v[1],v[0]))*tilt if follow else 0.0;print('axe du poignet',round(phi,1))
    cxc=(cols.min()+cols.max())/2+dx;wc=cols.max()-cols.min();sc=wc*fit/390;dst=(cxc,edge[int(cxc)]-up);L,X=source(phi);p=math.radians(round(phi,1))
    src=(PIV[0]+140*math.sin(p),PIV[1]-140*math.cos(p))                         # le haut du poignet, après pivot du poing
    t=math.radians(rot);co,si=math.cos(t)/sc,math.sin(t)/sc;A=(co,-si,src[0]-co*dst[0]+si*dst[1], si,co,src[1]-si*dst[0]-co*dst[1])
    C=np.array(Image.fromarray(L.round().astype('uint8')).transform((W,H),Image.AFFINE,A,Image.BICUBIC)).astype(float);CX=np.array(Image.fromarray(X).transform((W,H),Image.AFFINE,A,Image.NEAREST))
    rm=ndi.binary_dilation(old,iterations=2)&~ndi.binary_dilation((base!=1)&(base>0)&(a[...,3]>60),iterations=1);rm|=ndi.binary_dilation(old,iterations=9)&(base==0);B=a.copy();B[rm,3]=0
    lc,lk=ndi.label((base==6)&(xx<627))
    for i in np.unique(lc[ndi.binary_dilation(old,iterations=10)&(lc>0)]):
        if (lc==i).sum()<7000: B[ndi.binary_dilation(lc==i,iterations=2)&~np.isin(base,cuff),3]=0
    near=ndi.binary_dilation(old,iterations=14);thin=(B[...,3]>20)&near&~ndi.binary_opening(B[...,3]>20,iterations=4);B[thin,3]=0
    cc,kk=ndi.label(B[...,3]>20);B[cc!=np.argmax(ndi.sum(B[...,3]>20,cc,range(1,kk+1)))+1,3]=0
    if mend:                                                                  # l'ancienne main (pouce) cachait un bout du vêtement : on rebouche l'encoche
        sil=B[...,3]>60;lumB=B[...,:3].mean(-1);hole=ndi.binary_closing(sil,structure=np.ones((3,3)),iterations=60)&~sil&ndi.binary_dilation(old,iterations=30)&(yy>edge[None,:]+10)
        hole=ndi.binary_opening(hole,iterations=2);_,ix=ndi.distance_transform_edt(~(sil&(lumB>70)&~np.isin(base,cuff)&(base!=1)),return_indices=True)
        B[hole]=B[ix[0],ix[1]][hole];B[hole,3]=255;base=base.copy();base[hole]=base[ix[0],ix[1]][hole]
        rim=hole&(ndi.distance_transform_edt(sil|hole)<4.5);B[rim,:3]=28
    front=(yy>edge[None,:]+8)&(C[...,3]>0);Cf=C.copy();Cf[~front,3]=0;Cb=C.copy();Cb[front,3]=0
    Cb[...,3]=np.where(ndi.binary_erosion(B[...,3]>60,iterations=2),Cb[...,3],0)            # au-dessus du bord du bracelet, rien ne dépasse de la manche
    def over(T,U):
        t=T[...,3:]/255;u=U[...,3:]/255;oa=t+u*(1-t);o=np.zeros_like(T);o[...,:3]=(T[...,:3]*t+U[...,:3]*u*(1-t))/np.maximum(oa,1e-6);o[...,3:]=oa*255;return o
    o=over(Cf,over(B,Cb));lab=np.where(Cf[...,3]>128,CX,np.where(B[...,3]>60,base,CX));lab[o[...,3]<=60]=0;return o,lab,sc

def graft2(a0,lab0,cuff=(4,),inset=7,core=0.86,H=1700):
    """Pose du poing à la lanterne, refaite d'après la géométrie réelle du bracelet :
    - le poing (droit, jamais pivoté) prend exactement la largeur du bracelet et se centre dessus ;
    - il est remonté jusqu'à remplir toute l'ouverture du bracelet (aucun tissu visible entre les deux) ;
    - ordre des couches : vêtement < poing et lanterne < bracelet. Le poing sort donc DE SOUS le bracelet et passe devant tout le reste ;
    - l'ancienne main ouverte est retirée avec son trait de contour, et le vêtement qu'elle cachait est rebouché."""
    W=lab0.shape[1];a=np.zeros((H,W,4));a[:a0.shape[0]]=a0;base=np.zeros((H,W),int);base[:lab0.shape[0]]=lab0;yy,xx=np.mgrid[:H,:W];lum=a[...,:3].mean(-1);al=a[...,3]>60
    old=(base==1)&(xx<627);oy,ox=np.where(old)
    cf=np.isin(base,cuff)&(xx<627)&ndi.binary_dilation(old,iterations=110);cl,k=ndi.label(cf);cf=cl==(np.argmax(ndi.sum(cf,cl,range(1,k+1)))+1)
    cols=np.where(cf.any(0))[0];x0,x1=cols.min(),cols.max();e=np.array([np.where(cf[:,c])[0].max() for c in range(x0,x1+1)],float);e=ndi.grey_closing(ndi.median_filter(e,7),size=61)           # on ignore les encoches étroites du bord (la main ne doit pas y remonter)
    edge=np.interp(np.arange(W),np.arange(x0,x1+1),e)                                   # bord bas du bracelet, colonne par colonne (prolongé à plat de chaque côté)
    L,X=source(0);hm=X==1;hc=np.where(hm.any(0))[0];hx0,hx1=hc.min(),hc.max();htop=np.full(L.shape[1],np.nan);htop[hc]=[np.where(hm[:,c])[0].min() for c in hc]
    sc=(x1-x0-2*inset)/(hx1-hx0);cxs=(hx0+hx1)/2;cxd=(x0+x1)/2
    xs=np.arange(int(cxd-(hx1-hx0)*sc*core/2),int(cxd+(hx1-hx0)*sc*core/2)+1);sx=np.clip(np.round(cxs+(xs-cxd)/sc).astype(int),0,L.shape[1]-1)
    y0=np.nanmin(edge[xs]-htop[sx]*sc)-3                                                # position verticale : le poing remplit l'ouverture du bracelet
    A=(1/sc,0,cxs-cxd/sc,0,1/sc,-y0/sc);C=np.array(Image.fromarray(L.round().astype('uint8')).transform((W,H),Image.AFFINE,A,Image.BICUBIC)).astype(float);CX=np.array(Image.fromarray(X).transform((W,H),Image.AFFINE,A,Image.NEAREST))
    C[...,3]=np.where(yy>edge[None,:]-3,C[...,3],0)                                     # rien du poing au-dessus du bord du bracelet
    notch=ndi.binary_closing(cf,iterations=14)&~cf&al&(yy<=edge[None,:]+1);a[notch,:3]=np.minimum(a[notch,:3],34);lum=a[...,:3].mean(-1)      # encoches du bracelet : bouchées en sombre
    cf=cf|notch
    K=(ndi.binary_dilation(cf,iterations=4)&al&((lum<95)|cf))&~(old&(lum>=95))           # le bracelet et son trait : au-dessus de tout
    rm=(old|(ndi.binary_dilation(old,iterations=10)&(lum<110)&al))&~K                       # l'ancienne main et son trait
    B=a.copy();B[rm,3]=0;B[K,3]=0
    ly=min(int(oy.max())+8,H-1);row=np.where(al[ly]&~rm[ly])[0];p1=(x0+6.0,edge[x0]);p2=(float(row.min()) if len(row) else p1[0],float(ly))
    inside=(xx-p1[0])*(p2[1]-p1[1])-(yy-p1[1])*(p2[0]-p1[0])>0                          # à droite de la ligne bracelet → bord de la robe : c'est du vêtement
    fill=rm&inside&(yy>edge[None,:]);good=al&~rm&~K&np.isin(base,(5,))&(lum>80);_,ix=ndi.distance_transform_edt(~good,return_indices=True)
    B[fill]=a[ix[0],ix[1]][fill];B[fill,3]=255;base=base.copy();base[fill]=5
    sm=ndi.gaussian_filter(B[...,:3],(2.5,2.5,0));B[fill,:3]=sm[fill]
    cc,kk=ndi.label(B[...,3]>20);B[cc!=np.argmax(ndi.sum(B[...,3]>20,cc,range(1,kk+1)))+1,3]=0          # miettes détachées de l'ancien contour
    thin=(B[...,3]>20)&ndi.binary_dilation(old,iterations=14)&~ndi.binary_opening(B[...,3]>20,iterations=3);B[thin,3]=0
    rim=fill&(B[...,3]>20)&(ndi.distance_transform_edt(B[...,3]>20)<4.2);B[rim,:3]=26                        # trait de contour du bord rebouché
    def over(T,U):
        t=T[...,3:]/255;u=U[...,3:]/255;oa=t+u*(1-t);o=np.zeros_like(T);o[...,:3]=(T[...,:3]*t+U[...,:3]*u*(1-t))/np.maximum(oa,1e-6);o[...,3:]=oa*255;return o
    Kl=a.copy();Kl[~K,3]=0;o=over(Kl,over(C,B));lab=np.where(K,base,np.where(C[...,3]>128,CX,base));lab[o[...,3]<=60]=0
    return o,lab,dict(sc=sc,x0=x0,x1=x1,y0=y0)
def tall(img,H):
    w,h=img.size;im=img.resize((round(w*.29),round(h*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(im,(round(256-625*.29),round(229-360*.29)));return o
def veilleur(cl,sk,hr,inn,trim='#c9a23a',metal='#9aa0a8',glow='#ffd98a',H=700):
    """Mage, bras tendu, lanterne en main nue."""
    import r2,full,kit
    a0,l0=r2.raw('robe_reach');a,lab,info=graft2(a0,l0);cols={5:cl,1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,H));c.alpha_composite(r2.boots(cols,0))
    full.G.update({4:.9,30:1.0});c.alpha_composite(tall(full.tint(a,lab,{5:cl,1:sk,7:inn,9:trim,4:metal,30:glow}),H));full.G[4]=1.0;hd=Image.new('RGBA',(512,H));hd.alpha_composite(kit.tint('head_dwarf_braided_90',cols));c.alpha_composite(hd);return c,info

GR={}
def garde_reach(tab,bord,metal='#aeb4bc',glow='#ffd98a',emb=None,H=700,**kw):
    """Garde, bras tendu, lanterne tenue par le gantelet : pose COMPLÈTE dessinée par GPT (grd/rl_pad.png), sans aucune greffe.
    Ici : seulement les matières (vitres de la lanterne) et une toile plus haute."""
    import grd,full
    if 'p' not in GR:
        a,lab=grd.prep('../grd/rl_pad.png','rl',like='../grd/rl_pad.png',H=1900);yy,xx=np.mgrid[:lab.shape[0],:lab.shape[1]];lum=a[...,:3].mean(-1)
        g=ndi.binary_opening((lum>212)&(a[...,3]>60)&(xx<420)&(yy>1150),iterations=3);gc,gk=ndi.label(g);g=np.isin(gc,[i+1 for i,v in enumerate(ndi.sum(g,gc,range(1,gk+1))) if v>420]);lab[ndi.binary_dilation(g,iterations=3)&(lum>190)&(xx<420)&(yy>1150)]=30      # seulement les vitres, pas les rivets
        gy,gx=np.where(lab==30);box=(xx<gx.max()+75)&(yy>gy.min()-330);lab[box&np.isin(lab,(6,15,16,9))&(lum>120)]=4          # la lanterne et le gantelet : métal
        lab[np.isin(lab,(6,16))&(yy>1090)&~box]=9;GR['p']=(a,lab);GR['box']=box                                                  # la bordure du bas du tabard
    a,lab=GR['p'];grd.G[30]=1.0;c=grd.char(a[:1400],lab[:1400],tab,bord,metal=metal,emb=emb,**kw)
    full.G.update(grd.G);full.G.update({30:1.0});t=np.array(full.tint(a,lab,{4:metal,30:glow,5:tab,9:bord,15:'#6a6e76',16:'#3e3a3a',6:'#3a2a1c',7:'#2a2622'})).astype(float)
    yy,xx=np.mgrid[:lab.shape[0],:lab.shape[1]];m=GR['box']&(lab>0)&~np.isin(lab,(5,9))
    w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float)/255;t[...,3]*=w
    c2=Image.new('RGBA',(512,H));c2.alpha_composite(c);c2.alpha_composite(tall(Image.fromarray(t.astype('uint8')),H));return c2

def garde_reach2(tab,bord,metal='#aeb4bc',glow='#ffd98a',emb=None,H=700,**kw):
    """Patrouille de nuit : le garde VALIDÉ (tabard, bordure, gorgerin, épaulières, bras droit) + seulement le bras tendu et la lanterne dessinés par GPT,
    glissés sous l'épaulière validée. Là où l'ancien bras relâché laisse un vide, on voit le torse de GPT, qui se superpose au validé."""
    import grd,full
    if 'q' not in GR:
        garde_reach(tab,bord);an,ln=GR['p'];Hh,W=ln.shape;a0,l0=grd.prep('../grd/relaxed.png','relaxed');av=np.zeros((Hh,W,4));av[:a0.shape[0]]=a0;lv=np.zeros((Hh,W),int);lv[:l0.shape[0]]=l0
        yy,xx=np.mgrid[:Hh,:W];left=xx<627
        def comps(lab,img):
            m=(lab==4)&left;cl,k=ndi.label(m);cy=np.array(ndi.center_of_mass(m,cl,range(1,k+1)))[:,0];sz=ndi.sum(m,cl,range(1,k+1));return cl,cy,sz
        cl,cy,sz=comps(lv,av);paul=np.isin(cl,[i+1 for i in range(len(cy)) if cy[i]<610 and sz[i]>400]);lumv=av[...,:3].mean(-1)
        K=ndi.binary_dilation(paul,iterations=5)&(av[...,3]>60)&((lumv<58)|paul);K=ndi.median_filter(K.astype(np.uint8),size=9)>0                                  # épaulière validée et son trait : au-dessus
        armv=left&(yy>540)&(np.isin(lv,(15,))&(xx<345)|((lv==4)&~paul&(xx<345)));armv=(ndi.binary_dilation(armv,iterations=6)&(av[...,3]>60)&((lumv<95)|armv))&~K   # l'ancien bras relâché
        cn,cyn,szn=comps(ln,an);pauln=np.isin(cn,[i+1 for i in range(len(cyn)) if cyn[i]<610 and szn[i]>400]);lumn=an[...,:3].mean(-1)
        armn=left&(yy>540)&(xx<345)&(np.isin(ln,(15,))|((ln==4)&~pauln));lb=GR['box']&np.isin(ln,(4,30));cb,kb=ndi.label(ndi.binary_dilation(lb,iterations=4));gy0,gx0=np.where(ln==30);lb=ndi.binary_fill_holes(cb==cb[gy0[0],gx0[0]])&GR['box'];GR['lant']=lb;armn|=lb;armn=ndi.binary_dilation(armn,iterations=5)&(an[...,3]>60)&((lumn<95)|armn)&~ndi.binary_dilation(pauln,iterations=2)
        V=av.copy();V[armv,3]=0;V[K,3]=0;A=an.copy();A[~armn,3]=0;Kl=av.copy();Kl[~K,3]=0
        def over(T,U):
            t=T[...,3:]/255;u=U[...,3:]/255;oa=t+u*(1-t);o=np.zeros_like(T);o[...,:3]=(T[...,:3]*t+U[...,:3]*u*(1-t))/np.maximum(oa,1e-6);o[...,3:]=oa*255;return o
        sil=(V[...,3]>60)|(A[...,3]>60)|K;hole=ndi.binary_fill_holes(ndi.binary_closing(sil,iterations=12))&~sil&armv&(xx>150)      # vide laissé par l'ancien bras, contre le tabard
        good=(V[...,3]>60)&np.isin(lv,(16,))&(lumv>62);_,ix=ndi.distance_transform_edt(~good,return_indices=True);V[hole]=av[ix[0],ix[1]][hole];V[hole,3]=255;lv=lv.copy();lv[hole]=16
        o=over(Kl,over(A,V));lab=np.where(K,lv,np.where(armn,ln,lv));lab[o[...,3]<=60]=0
        gy,gx=np.where(lab==30);piv=GR['lant']&(lab>0)&~np.isin(lab,(4,30));lab[piv&(o[...,:3].mean(-1)>110)]=4;lab[piv&(o[...,:3].mean(-1)<=110)]=6
        GR['q']=(o,lab);Image.fromarray(o.round().astype('uint8')).save('../grd/n_guard_reach_lantern.png')
    a,lab=GR['q'];grd.G[30]=1.0;c=grd.char(a[:1400],lab[:1400],tab,bord,metal=metal,emb=emb,**kw)
    full.G.update(grd.G);full.G.update({30:1.0});t=np.array(full.tint(a,lab,{4:metal,30:glow,5:tab,9:bord,15:'#6a6e76',16:'#3e3a3a',6:'#3a2a1c',7:'#2a2622'})).astype(float)
    m=ndi.binary_dilation(GR['lant'],iterations=4)&(lab>0)&np.isin(lab,(4,30,6));w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float)/255;t[...,3]*=w
    c2=Image.new('RGBA',(512,H));c2.alpha_composite(c);c2.alpha_composite(tall(Image.fromarray(t.astype('uint8')),H));return c2
def overlay(c,a,lab,tint_cols,H):
    """Repose le poing et la lanterne par-dessus le personnage monté (bottes, tête) : ils sont au premier plan."""
    import full
    full.G.update({4:.9,30:1.0,1:.8});t=np.array(full.tint(a,lab,tint_cols)).astype(float);yy,xx=np.mgrid[:lab.shape[0],:lab.shape[1]]
    ys=np.where((lab==30).any(1))[0];m=np.isin(lab,(4,30,1))&(xx<450)&(yy>ys.min()-260)&ndi.binary_dilation(lab==30,iterations=170)
    cc,k=ndi.label(m);m=cc==cc[int(ys.mean()),int(np.where((lab==30).any(0))[0].mean())]
    w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.0))).astype(float)/255;t[...,3]*=w
    im=Image.fromarray(t.astype('uint8'));w0,h0=im.size;im=im.resize((round(w0*.29),round(h0*.29)),Image.LANCZOS);o=Image.new('RGBA',(512,H));o.paste(im,(round(256-625*.29),round(229-360*.29)))
    c2=Image.new('RGBA',(512,H));c2.alpha_composite(c);c2.alpha_composite(o);full.G[4]=1.0;return c2
def mage(cl,sk,hr,inn,trim='#c9a23a',metal='#9aa0a8',glow='#ffd98a',H=700,tilt=-0.6,dx=14):
    import r2,full,kit
    a0,l0=r2.raw('robe_reach');a,lab,sc=graft(a0,l0,mend=True,fit=0.98,dx=dx,tilt=tilt);cols={5:cl,1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512));c.alpha_composite(r2.boots(cols,0))
    tc={5:cl,1:sk,7:inn,9:trim,4:metal,30:glow};full.G.update({4:.9,30:1.0});c.alpha_composite(full.place(full.tint(a[:1400],lab[:1400],tc),0.29,(625,360)));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols))
    return overlay(c,a,lab,tc,H)

def garde(P,tab,bord,metal='#aeb4bc',glow='#ffd98a',emb=None,H=700,sc=0.46,rot=-3,dst=(139,852),edge=852,**kw):
    """Garde (pose relâchée) portant la lanterne : le gantelet à la lanterne (obj/gauntlet_lantern.png, dont on retire le bracelet du haut) remplace
    le poing ganté de gauche ; son haut glisse sous le bracelet du garde, le reste est au premier plan."""
    import grd,full
    a0,l0=P;Hh=1700;W=l0.shape[1];a=np.zeros((Hh,W,4));a[:a0.shape[0]]=a0;base=np.zeros((Hh,W),int);base[:l0.shape[0]]=l0;yy,xx=np.mgrid[:Hh,:W]
    L=np.array(Image.open('../obj/gauntlet_lantern.png').convert('RGBA')).astype(float);ly,lx=np.mgrid[:L.shape[0],:L.shape[1]];al=L[...,3]>60;lum=L[...,:3].mean(-1)
    L[(ly<118-(np.abs(lx-640)/160.0)**2*22),3]=0                                                    # le bracelet riveté du haut
    glass=poly([(452,775),(795,775),(795,1050),(452,1050)],al.shape)&al&(lum>150);X=np.zeros(al.shape,np.uint8);X[L[...,3]>60]=4;X[glass]=30
    t=math.radians(rot);co,si=math.cos(t)/sc,math.sin(t)/sc;src=(632,150);A=(co,-si,src[0]-co*dst[0]+si*dst[1], si,co,src[1]-si*dst[0]-co*dst[1])
    C=np.array(Image.fromarray(L.round().astype('uint8')).transform((W,Hh),Image.AFFINE,A,Image.BICUBIC)).astype(float);CX=np.array(Image.fromarray(X).transform((W,Hh),Image.AFFINE,A,Image.NEAREST))
    rm=poly([(40,edge-2),(206,edge-2),(236,872),(242,935),(205,1000),(40,1000)],(Hh,W))&(a[...,3]>0);B=a.copy();B[rm,3]=0
    front=(yy>edge+2)&(C[...,3]>0);Cf=C.copy();Cf[~front,3]=0;Cb=C.copy();Cb[front,3]=0
    def over(T,U):
        t=T[...,3:]/255;u=U[...,3:]/255;oa=t+u*(1-t);o=np.zeros_like(T);o[...,:3]=(T[...,:3]*t+U[...,:3]*u*(1-t))/np.maximum(oa,1e-6);o[...,3:]=oa*255;return o
    o=over(Cf,over(B,Cb));lab=np.where(Cf[...,3]>128,CX,np.where(B[...,3]>60,base,CX));lab[o[...,3]<=60]=0
    grd.G[30]=1.0;c=grd.char(o[:1400],lab[:1400],tab,bord,metal=metal,emb=emb,**kw)
    full.G.update({4:.95,30:1.0});tt=np.array(full.tint(o,lab,{4:metal,30:glow,5:tab,9:bord,15:'#6a6e76',16:'#3e3a3a',6:'#3a2a1c',7:'#2a2622'})).astype(float)
    m=(Cf[...,3]>30);w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float)/255;tt[...,3]*=w
    im=Image.fromarray(tt.astype('uint8'));w0,h0=im.size;im=im.resize((round(w0*.29),round(h0*.29)),Image.LANCZOS);ov=Image.new('RGBA',(512,H));ov.paste(im,(round(256-625*.29),round(229-360*.29)))
    c2=Image.new('RGBA',(512,H));c2.alpha_composite(c);c2.alpha_composite(ov);return c2
if __name__=='__main__':
    import kit
    O=Image.new('RGBA',(1024,700),(140,105,70,255))
    kit.HEAD=('hood',{8:'#2a3042'});O.alpha_composite(mage('#343a50','#8a5a3c','#2a2422','#22242e'),(0,0))
    kit.HEAD=('hood',{8:'#5a4a3a'});O.alpha_composite(mage('#6e5a40','#c98f6a','#b9b3aa','#3a2e26',trim='#8a744e'),(512,0))
    O.crop((0,20,1024,680)).convert('RGB').save('../r2/cmp_veilleur.png');O.crop((30,260,270,500)).resize((960,960),Image.LANCZOS).convert('RGB').save('../r2/z_veilleur.png')

# Fermier : matières classées par leur valeur de gris (règle donnée à GPT) — 1 peau, 14 chemise, 5 salopette, 6 corde/bretelles, 7 intérieur du col
import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import norm,bodyseg,full,kit,legs,r2
def prep(src,tag,like='../adv/src3.png'):
    norm.normalize_like(src,like,f'../far/n_{tag}.png') if like else norm.normalize(src,f'../far/n_{tag}.png')
    a=np.array(Image.open(f'../far/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1)
    line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
    area=ndi.sum(al,comp,idx);cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T;ml=ndi.mean(lum,comp,idx)
    H,W=al.shape;shirt=bodyseg.poly([(545,215),(705,215),(705,560),(545,560)],(H,W));fs=ndi.mean(shirt.astype(float),comp,idx)
    kind=np.where(ml>165,1,np.where(ml>125,14,np.where(ml>88,5,6)))
    kind[(fs>0.5)&(ml<100)]=7
    kind[(kind==1)&(np.abs(cx-627)<250)]=14                 # rien de clair au centre n'est de la peau
    lab=np.zeros((H,W),int);lab[comp>0]=kind[comp[comp>0]-1]
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    return a,lab
SC=0.29
def prep_pose(src,tag,base_src,base_tag):
    """Pose dérivée d'une image validée : on reprend les matières du torse validé partout où le dessin n'a pas changé
    (à un petit décalage près), et on ne classe que la zone des bras."""
    from skimage.segmentation import watershed
    b,lb=prep(base_src,base_tag);norm.normalize_like(src,'../adv/src3.png',f'../far/n_{tag}.png')
    a=np.array(Image.open(f'../far/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1)
    lb_=b[...,:3].mean(-1)*(b[...,3]>60);la_=lum*al;z=(slice(330,1150),slice(420,840));best=(1e9,0,0)
    for dy in range(-8,9,2):
        for dx in range(-8,9,2):
            e=np.abs(np.roll(np.roll(lb_,dy,0),dx,1)[z]-la_[z]).mean()
            if e<best[0]: best=(e,dy,dx)
    _,dy,dx=best;lbs=np.roll(np.roll(lb,dy,0),dx,1);bs=np.roll(np.roll(lb_,dy,0),dx,1)
    d=np.abs(ndi.gaussian_filter(bs,2.5)-ndi.gaussian_filter(la_,2.5))
    ch=ndi.binary_dilation(ndi.binary_opening(d>24,iterations=3),iterations=8)|(al&(lbs==0))
    ls=ndi.gaussian_filter(lum,1.0);l3=ndi.gaussian_filter(lum,2.5)
    tex=np.sqrt(ndi.gaussian_filter((lum-ndi.gaussian_filter(lum,5))**2,5))          # la chemise a des plis, la peau est lisse
    lab=np.where(ch,0,lbs);found=[]
    for LT2 in (95,75,bodyseg.LT):                                    # trait de plus en plus permissif : on ferme d'abord les contours faibles (bord de manche)
        free=al&ch&(ls>=LT2)&(lab==0)
        for c in found: free&=~c
        comp,k=ndi.label(free)
        if not k: continue
        idx=np.arange(1,k+1);ml=ndi.mean(lum,comp,idx);area=ndi.sum(al,comp,idx);sd=ndi.standard_deviation(l3,comp,idx);cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T
        for i in range(k):
            if area[i]<150: continue
            if LT2>bodyseg.LT and sd[i]>16 and area[i]>6000: continue     # encore deux matières mélangées : on réessaie avec un trait plus permissif
            m=comp==i+1
            if ml[i]>122: found.append(m)                                 # clair : manche ou peau, tranché plus bas selon la position le long du bras
            else: lab[m]=5 if ml[i]>88 else 6
    # le long de chaque bras, la manche est près de l'épaule et la peau (avant-bras, main) au bout
    for side,S in ((-1,bodyseg.SHO[0]),(1,bodyseg.SHO[1])):
        cs=[(m,np.hypot(*(np.array(ndi.center_of_mass(m))[::-1]-np.array(S)))) for m in found if (np.array(ndi.center_of_mass(m))[1]-627)*side>150]
        if not cs: continue
        dmax=max(d for _,d in cs)
        for m,d in cs: lab[m]=1 if d>0.62*dmax else 14
    for m in found:
        if abs(ndi.center_of_mass(m)[1]-627)<=150: lab[m]=14
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    print(tag,'décalage',dy,dx,'zone changée %',round(float((ch&al).mean()*100),1))
    return a,lab

# Panier de légumes (pose carry) : contours tracés à la main sur l'image normalisée — 26 osier, 20 tomate, 21 feuillage, 22 chou, 23 oignon, 27 ail, 24 patate, 25 carotte
def _el(cx,cy,rx,ry,n=40): return [(cx+rx*np.cos(t),cy+ry*np.sin(t)) for t in np.linspace(0,2*np.pi,n,endpoint=False)]
BASKET=[(26,[(300,920),(340,935),(450,975),(625,990),(800,975),(905,935),(945,920),(935,985),(880,1050),(790,1090),(625,1100),(460,1090),(370,1055),(310,990)]),
 (26,[(330,935),(340,830),(400,790),(520,790),(640,765),(760,790),(870,800),(910,850),(915,940),(800,980),(625,995),(450,980)]),
 (20,_el(396,848,52,52)),(20,_el(487,868,60,55)),(21,_el(395,812,40,20)),(21,_el(490,842,38,24)),
 (22,_el(637,852,113,88)),(22,_el(540,815,28,30)),
 (21,[(745,805),(790,798),(860,803),(885,840),(885,915),(840,905),(780,870),(750,870)]),
 (24,_el(577,915,60,38)),(24,_el(622,955,66,38)),
 (25,[(700,895),(760,883),(778,905),(722,988),(668,988)]),(25,[(778,905),(822,893),(832,930),(792,978),(722,988)]),
 (23,[(398,860),(422,860),(452,885),(490,915),(494,962),(470,978),(380,968),(366,930),(380,895)]),
 (27,[(494,908),(512,908),(546,940),(556,988),(454,988),(464,945)])]
VEG={26:'#a8763e',20:'#c23a2a',21:'#5f8a3a',22:'#a3c26c',23:'#d6a85a',27:'#ece4cf',24:'#b8925a',25:'#e07a2a'}
def basket(a,lab):
    al=a[...,3]>60;out=lab.copy();lum=a[...,:3].mean(-1);H,W=lab.shape;yy,xx=np.mgrid[:H,:W]
    out[(out==6)&(yy>760)&~((np.abs(xx-650)<60)&(yy>1085)&(yy<1130))]=5      # sous les mains, la salopette à l'ombre reste de la salopette (seul le noeud de corde dépasse)
    out[(out==5)&(yy<760)&((xx<325)|(xx>925))]=14                             # plis sombres des manches
    for i,(l,p) in enumerate(BASKET):
        m=bodyseg.poly(p,lab.shape)&al
        if l==26: m&=(lab!=1)
        if i==1: m&=(lum<80)&(yy>800)                                          # derrière les légumes : seulement l'ombre
        out[m]=l
    return out

# Fourche tenue à la verticale (poses fork_*) : 4 métal, 28 bois ; main tracée à la main, le reste du côté est reclassé sans peau
FORK=[(4,[(195,20),(400,20),(400,225),(345,240),(322,300),(255,292),(258,235),(200,225)]),
 (28,[(252,292),(322,300),(305,330),(285,420),(262,520),(255,580),(203,575),(212,520),(232,420)]),
 (28,[(168,742),(224,748),(192,930),(185,960),(150,975),(125,950),(128,915)]),
 (1,[(108,625),(150,598),(200,578),(250,570),(278,592),(292,625),(272,660),(265,700),(250,742),(200,755),(160,745),(125,720),(105,690)])]
HELD={4:'#9aa0a6',28:'#8a6a42'}
HAND=[(100,625),(150,592),(200,572),(255,565),(285,588),(300,625),(280,665),(272,705),(258,750),(200,762),(155,752),(118,725),(98,690)]
def fork(a,lab):
    al=a[...,3]>60;lum=a[...,:3].mean(-1);out=lab.copy();H,W=lab.shape;yy,xx=np.mgrid[:H,:W]
    out[(out==1)&(xx<627)]=0                                                    # aucune peau de ce côté hors de la main (retracée plus bas)
    zone=bodyseg.poly([(0,280),(300,280),(300,830),(235,905),(0,1010)],(H,W))&al
    line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
    ml=ndi.mean(lum,comp,idx);kind=np.where(ml>125,14,np.where(ml>88,5,6));m=zone&(comp>0);out[zone]=0;out[m]=kind[comp[m]-1]
    out[zone&(out==5)&(yy<840)]=14                                              # plis sombres de la chemise
    out[zone&(out==6)&(yy>875+(xx-215)*0.82)]=5                                 # sous la corde : salopette à l'ombre du manche
    low=(xx<330)&(yy>875+(xx-215)*0.82);out[low&np.isin(out,(6,14))]=5           # bas de la salopette, côté fourche
    for l,p in FORK[:3]: out[bodyseg.poly(p,(H,W))&al]=l
    hp=bodyseg.poly(HAND,(H,W));fr=ndi.mean(hp.astype(float),comp,idx);ar=ndi.sum(al,comp,idx)
    for i in range(k):
        if fr[i]>0.6 and ml[i]>140 and ar[i]>60: out[comp==i+1]=1               # la main : régions fermées par le trait
    _,ix=ndi.distance_transform_edt(out==0,return_indices=True);out=out[ix[0],ix[1]];out[~al]=0
    return out
def char(a,lab,shirt,over,sk,hr,rope='#6b5a3a',pants='#5a4a32',ph=0):
    full.G.update({14:.85,6:.85,5:.75,26:.8,20:.8,21:.8,22:.8,23:.8,27:.85,24:.8,25:.8,28:.8,4:.9});cols={1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512));c.alpha_composite(legs.legs(pants,'#3a2a1c',ph))
    t=full.tint(a,lab,{14:shirt,5:over,1:sk,6:rope,7:'#3a2e26',**VEG,**HELD})
    c.alpha_composite(full.place(t,SC,(625,360)));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols))
    held=np.isin(lab,list(VEG)+list(HELD))
    if held.any():                                                    # l'objet tenu repasse devant la barbe
        w=np.array(Image.fromarray((held*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5))).astype(float)/255
        h=np.array(t).astype(float);h[...,3]*=w;c.alpha_composite(full.place(Image.fromarray(h.astype('uint8')),SC,(625,360)))
    full.G[6]=.7;return c
if __name__=='__main__':
    import advp
    a,lab=prep('../far/relaxed2.png','relaxed2');b,lb=advp.prep('../adv/src3.png','rel')
    O=Image.new('RGBA',(512*4,512),(140,105,70,255))
    O.alpha_composite(char(a,lab,'#d8cdb0','#5a6f8a','#c98f6a','#8a4a22'),(0,0));O.alpha_composite(char(a,lab,'#b9a27a','#6a4a32','#8a5a3c','#2a2422'),(512,0));O.alpha_composite(char(a,lab,'#e6dfd0','#4a6a3a','#e2b592','#c9a23a'),(1024,0));O.alpha_composite(advp.char(b,lb,*r2.V[0]),(1536,0))
    O.crop((0,40,2048,512)).resize((1920,442),Image.LANCZOS).save('../far_cmp2.png')

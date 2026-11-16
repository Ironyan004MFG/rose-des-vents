# Fermier : matières classées par leur valeur de gris (règle donnée à GPT) — 1 peau, 14 chemise, 5 salopette, 6 corde/bretelles, 7 intérieur du col
import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import norm,bodyseg,full,kit,legs,r2
def prep(src,tag,like='../adv/src3.png'):
    if like!='DEJA': norm.normalize_like(src,like,f'../far/n_{tag}.png') if like else norm.normalize(src,f'../far/n_{tag}.png')      # 'DEJA' : ../far/n_<tag>.png est déjà normalisé
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

# Longe (poses lead_*) : le bras de droite tient un bout de corde ; la peau n'est admise que dans le contour de l'avant-bras et de la main
LSKIN=[(995,712),(1180,708),(1190,760),(1180,800),(1188,870),(1175,940),(1100,975),(1035,960),(992,900),(992,845),(1030,812),(1002,770)]
LROPE=[[(1196,703),(1230,712),(1218,780),(1195,822),(1188,852),(1158,848),(1165,818),(1180,770)],[(955,945),(1000,905),(1050,885),(1055,915),(1010,945),(975,975),(958,968)]]
def lead(src,tag,lab_left=None):
    a,lab=prep(src,tag,like='../adv/src3.png');al=a[...,3]>60;lum=a[...,:3].mean(-1);H,W=lab.shape;yy,xx=np.mgrid[:H,:W];out=lab.copy()
    line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1)
    sp=bodyseg.poly(LSKIN,(H,W));fr=ndi.mean(sp.astype(float),comp,idx);ml=ndi.mean(lum,comp,idx);ar=ndi.sum(al,comp,idx)
    right=xx>627;out[right&(out==1)]=14
    out[right&(out==14)&(yy>880+(xx-960)*0.3)&(xx<1000)]=5
    for i in range(k):
        if fr[i]>0.6 and ml[i]>140 and ar[i]>60: out[(comp==i+1)]=1
    for p in LROPE: out[bodyseg.poly(p,(H,W))&al&(out!=1)]=6
    _,lb=prep('../far/relaxed2.png','relaxed2');out[right&(xx<1000)&(lb==6)&(out==5)]=6      # bretelle et corde de taille : matières du fermier validé
    rp=ndi.binary_closing((out==6)&right&(yy>780)&(xx<1020),iterations=3);cc,kk=ndi.label((out==5)&right&(yy>800)&(xx>900)&(xx<1020))
    if lab_left is not None: out[:,:627]=lab_left[:,:627]
    out[~al]=0
    return a,out

# Travail aux champs (fork_work) : les deux mains sur la fourche, tenue en diagonale devant le ventre. Image remise à l'échelle avant (work_al.png).
WSKIN=[[(225,735),(330,720),(400,760),(420,830),(390,900),(330,905),(280,880),(245,820)],
       [(705,875),(760,860),(880,935),(860,990),(700,1090),(650,1150),(600,1200),(540,1195),(500,1150),(495,1095),(540,1060),(640,1040),(690,960)]]
WFORK=[(4,[(560,1285),(660,1275),(765,1330),(765,1560),(580,1560),(560,1400)]),
       (28,[(378,855),(418,845),(440,900),(495,1000),(545,1070),(505,1095),(455,1010),(400,910)]),(28,[(555,1190),(610,1180),(645,1290),(605,1300)])]
def work(src='../far/work_al.png',tag='work'):
    norm.normalize_like(src,'../adv/src3.png',f'../far/n_{tag}.png',H=1800)
    a=np.array(Image.open(f'../far/n_{tag}.png').convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1);H,W=al.shape
    line=(ndi.gaussian_filter(lum,1.0)<bodyseg.LT)&al;comp,k=ndi.label(al&~line);idx=np.arange(1,k+1);ml=ndi.mean(lum,comp,idx);ar=ndi.sum(al,comp,idx)
    cy,cx=np.array(ndi.center_of_mass(al,comp,idx)).T;shirt=bodyseg.poly([(545,215),(705,215),(705,560),(545,560)],(H,W));fs=ndi.mean(shirt.astype(float),comp,idx)
    kind=np.where(ml>125,14,np.where(ml>88,5,6));kind[(fs>0.5)&(ml<100)]=7
    sp=np.zeros((H,W),bool)
    for p in WSKIN: sp|=bodyseg.poly(p,(H,W))
    fr=ndi.mean(sp.astype(float),comp,idx);kind[(fr>0.6)&(ml>140)&(ar>60)]=1
    lab=np.zeros((H,W),int);lab[comp>0]=kind[comp[comp>0]-1]
    yy,xx=np.mgrid[:H,:W];lab[(lab==5)&(yy<695)]=6                                # bretelles et boucles
    kp=bodyseg.poly([(430,870),(700,860),(700,960),(690,1015),(540,1015),(520,930),(440,910)],(H,W));l0=lab.copy()
    lab[kp&(l0==5)]=6;lab[kp&(l0==6)]=5                                            # corde et noeud éclairés, salopette à l'ombre dessous
    lab[~kp&(lab==6)&(yy>700)&(np.abs(xx-627)<240)]=5
    for l,p in WFORK: lab[bodyseg.poly(p,(H,W))&al&(lab!=1)]=l
    _,ix=ndi.distance_transform_edt(lab==0,return_indices=True);lab=lab[ix[0],ix[1]];lab[~al]=0
    return a,lab

def staff(a,lab):
    """Bâton de marche tiré d'une pose à la fourche : on retire les dents et la douille, et on ferme le haut du manche par un bout arrondi."""
    from PIL import ImageDraw
    a=a.copy();lab=lab.copy();a[lab==4,3]=0;lab[lab==4]=0
    H,W=lab.shape;cap=Image.new('L',(W,H),0);d=ImageDraw.Draw(cap);d.ellipse([250,268,326,312],fill=255);cm=np.array(cap)>0
    edge=cm&~ndi.binary_erosion(cm,iterations=5);yy,xx=np.mgrid[:H,:W]
    g=150-35*((yy-290)/22.0)                                                       # bois : plus clair en haut du bout arrondi
    for j in range(3): a[...,j]=np.where(cm,np.where(edge,26,g),a[...,j])
    a[...,3]=np.where(cm,255,a[...,3]);lab[cm]=28
    return a,lab
def char(a,lab,shirt,over,sk,hr,rope='#6b5a3a',pants='#5a4a32',ph=0):
    full.G.update({14:.85,6:.85,5:.75,26:.8,20:.8,21:.8,22:.8,23:.8,27:.85,24:.8,25:.8,28:.8,4:.9});cols={1:sk,2:hr,3:hr,6:'#3a2a1c'};c=Image.new('RGBA',(512,512));c.alpha_composite(legs.legs(pants,'#3a2a1c',ph))
    t=full.tint(a,lab,{14:shirt,5:over,1:sk,6:rope,7:'#3a2e26',**VEG,**HELD})
    c.alpha_composite(full.place(t,SC,(625,360)));c.alpha_composite(kit.tint('head_dwarf_braided_90',cols))
    held=np.isin(lab,list(VEG)+([] if kit.HEAD and kit.HEAD[0]=='widehat' else list(HELD)))    # sous un grand chapeau, le manche reste sous le bord
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
# --- Pêcheur (far/fish.png) : les deux mains serrent la poignée d'une canne devant le ventre. GPT ne dessine que la poignée ;
# la canne, le fil et le bouchon sont dessinés en code (rod), ce qui permet de les animer (canne qui plie, bouchon qui danse).
def fisher(src='../far/fish.png'):
    a,lab=prep(src,'fish');sh=lab.shape;arm=bodyseg.poly([(250,800),(420,790),(690,810),(690,945),(480,970),(250,960)],sh)|bodyseg.poly([(560,950),(700,930),(850,790),(1045,770),(1045,930),(905,975),(760,1060),(560,1095)],sh)
    lab=lab.copy();lab[(lab==1)&~arm]=14;lab[arm&np.isin(lab,(14,1))]=1;      # seuls les avant-bras et les mains sont de la peau ; les manches claires sont de la chemise
    yy,xx=np.mgrid[:sh[0],:sh[1]];st=(lab>0)&(xx>595)&(xx<665)&(((yy>745)&(yy<818))|((yy>1088)&(yy<1206)));lab[st]=28;return a,lab
WATER=520                                         # ligne d'eau sur la toile 512 : juste devant les bottes
ROD=(257.5,346)                                   # haut de la poignée sur la toile 512 : il tient la canne PAR LE BAS, elle monte de là
def rod(c,dy=0,length=520,bend=0.0,bob=0.0,wood='#8a6a42',line=70,tilt=0.0):
    """c : toile, personnage décalé de dy (dy >= length+line-240). bend : flexion de la canne (-1..1), bob : enfoncement du bouchon (0..1)."""
    from PIL import ImageDraw
    S=3;o=Image.new('RGBA',(c.size[0]*S,c.size[1]*S));d=ImageDraw.Draw(o);import math;x0,y0=ROD[0],ROD[1]+dy+(22 if tilt else 0);n=24;pts=[];sn,cs=math.sin(math.radians(tilt)),math.cos(math.radians(tilt))      # inclinée : elle sort du poing (départ caché sous la main)
    for i in range(n+1):
        u=i/n;pts.append((x0-sn*length*u+bend*40*u*u*cs,y0-cs*length*u,7.5*(1-u)+1.6*u))
    for col,g in (('#2a1c12',1.4),(wood,0)):
        L=[((x-w-g)*S,y*S) for x,y,w in pts];R=[((x+w+g)*S,y*S) for x,y,w in pts][::-1];d.polygon(L+R,fill=col)
    for k in (0.6,0.8,1.0):                           # anneaux
        x,y,w=pts[int(n*k)];d.ellipse([(x-w-2.2)*S,(y-2)*S,(x+w+2.2)*S,(y+2)*S],outline='#9aa0a6',width=S)
    tx,ty,_=pts[-1];bx,by=tx+bend*10,dy+WATER+line      # l'eau est DEVANT lui (bas de l'image) : le fil retombe du bout de la canne jusqu'au bouchon, devant ses pieds
    d.line([(tx*S,ty*S),(bx*S,by*S)],fill=(235,235,225,220),width=S)
    r=6-2*bob;d.ellipse([(bx-r)*S,(by-r)*S,(bx+r)*S,(by+r)*S],fill='#f2eee4',outline='#2a1c12',width=S);d.pieslice([(bx-r)*S,(by-r)*S,(bx+r)*S,(by+r)*S],180,360,fill='#c23a2a',outline='#2a1c12',width=S)
    c.alpha_composite(o.resize(c.size,Image.LANCZOS));return c
def fisherman(P,shirt,over,sk,hr,dy=360,**kw):
    """Ordre : corps < tête < canne < mains et poignée. La canne est tenue DEVANT lui : avec la perspective, elle passe devant la barbe et la tête."""
    a,lab=P;c=Image.new('RGBA',(512,512+dy+140));rk={k:kw.pop(k) for k in ('length','bend','bob','line','tilt') if k in kw}
    if rk.get('tilt'): a=a.copy();a[(lab==28)&(np.mgrid[:lab.shape[0],:lab.shape[1]][0]<830),3]=0      # canne inclinée : le bout de poignée du haut (vertical) est retiré
    orig=kit.tint;kit.tint=lambda n,cols:Image.new('RGBA',(512,512)) if n.startswith('head') else orig(n,cols)
    try: body=char(a,lab,shirt,over,sk,hr,**kw)
    finally: kit.tint=orig
    c.alpha_composite(body,(0,dy));c.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}),(0,dy));rod(c,dy,**rk)
    full.G.update({14:.85,5:.75,28:.8});t=np.array(full.tint(a,lab,{1:sk,28:HELD[28]})).astype(float);m=np.isin(lab,(1,28))&(np.abs(np.mgrid[:lab.shape[0],:lab.shape[1]][1]-627)<140)
    t[...,3]*=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255;c.alpha_composite(full.place(Image.fromarray(t.astype('uint8')),SC,(625,360)),(0,dy));return c

# --- Pêcheur, pose inclinée (far/fish2.png) : GPT a dessiné la canne entière, en biais, tenue à deux mains. Elle dépasse au-dessus du cadre :
# la toile normalisée a OFF lignes de plus en haut. La canne (28) et les mains repassent devant la tête ; le fil et le bouchon restent en code.
OFF=300;F2=dict(s=1.219,cx=622,top=266,rod=((222,12),(722,1000)),tip=(226,14),
 arms=[[(400,730),(560,720),(660,740),(660,850),(560,860),(420,840)],[(600,830),(700,800),(770,790),(800,840),(720,940),(610,950)]])
def _f2(p): return 623+F2['s']*(p[0]-F2['cx']),165+OFF+F2['s']*(p[1]-F2['top'])
def fisher2(src='../far/fish2.png'):
    s=F2['s'];Image.open(src).convert('RGBA').transform((1254,1400+OFF),Image.AFFINE,(1/s,0,F2['cx']-623/s,0,1/s,F2['top']-(165+OFF)/s),Image.BICUBIC).save('../far/n_fish2.png')
    a,lab=prep(src,'fish2',like='DEJA');sh=lab.shape;yy,xx=np.mgrid[:sh[0],:sh[1]];lum=a[...,:3].mean(-1);(x0,y0),(x1,y1)=_f2(F2['rod'][0]),_f2(F2['rod'][1])
    d=np.abs((xx-x0)*(y1-y0)-(yy-y0)*(x1-x0))/np.hypot(x1-x0,y1-y0);rodm=(lab>0)&(d<20*s)&(ndi.gaussian_filter(lum,1.5)<178)&(yy<y1+10)
    arm=np.zeros(sh,bool)
    for pl in F2['arms']: arm|=bodyseg.poly([_f2(p) for p in pl],sh)
    lab=lab.copy();lab[(lab==1)&~arm]=14;lab[arm&np.isin(lab,(14,1))&~rodm]=1;rodm=ndi.binary_opening(rodm&(lab!=1),iterations=2);lab[rodm]=28;return a,lab
def fisherman2(P,shirt,over,sk,hr,rope='#6b5a3a',pants='#5a4a32',wood='#8a6a42',ph=0,bob=0.0,line=60,top=140):
    """Toile 512 x (512+top). Ordre : jambes < corps < tête < canne et mains."""
    from PIL import ImageDraw
    a,lab=P;dy=top;c=Image.new('RGBA',(512,512+top));c.alpha_composite(legs.legs(pants,'#3a2a1c',ph),(0,dy));full.G.update({14:.85,6:.85,5:.75,28:.8,1:.8,7:.6})
    t=full.tint(a,lab,{14:shirt,5:over,1:sk,6:rope,7:'#3a2e26',28:wood});pl=lambda im:full.place(im,SC,(625,360+OFF))
    def put(im):
        p=pl(im);o=Image.new('RGBA',c.size);o.alpha_composite(p,(0,dy)) if p.size[1]<=512 else o.alpha_composite(p.crop((0,0,512,min(p.size[1],512+top))),(0,dy));return o
    body=put(t);c.alpha_composite(body);c.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}),(0,dy))
    m=(lab==28)|((lab==1)&(np.abs(np.mgrid[:lab.shape[0],:lab.shape[1]][1]-_f2((650,0))[0])<95));h=np.array(t).astype(float);h[...,3]*=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255;c.alpha_composite(put(Image.fromarray(h.astype('uint8'))))
    tx,ty=_f2(F2['tip']);tx,ty=256+(tx-625)*.29,229+(ty-360-OFF)*.29+dy;d=ImageDraw.Draw(c);bx,by=tx-10,ty-line*0+line*0;bx,by=tx-18,ty+line
    d.line([(tx,ty),(bx,by)],fill=(235,235,225,220),width=1);r=5-1.5*bob;d.ellipse([bx-r,by-r,bx+r,by+r],fill='#f2eee4',outline='#2a1c12');d.pieslice([bx-r,by-r,bx+r,by+r],180,360,fill='#c23a2a',outline='#2a1c12');return c

# --- Pêcheur (pose retenue, far/fish3.png) : GPT dessine le corps du fermier à l'identique et, dans les deux mains, un court manche EN BIAIS.
# Le code prolonge ce manche en canne (même direction), puis le fil retombe du bout jusqu'au bouchon dans l'eau, DEVANT lui (bas de l'image).
F3=dict(rod=((165,160),(675,1045)),arms=[[(225,740),(300,690),(470,650),(600,700),(600,840),(480,865),(300,870),(225,850)],[(540,830),(700,790),(830,740),(940,720),(1030,740),(1030,900),(830,965),(720,1010),(560,990)]])
def _tr3():
    top,l,r=norm.collar('../adv/src3.png');s=(norm.REF[2]-norm.REF[1])/(r-l);cx=(l+r)/2;rcx=(norm.REF[1]+norm.REF[2])/2;return lambda p:(rcx+s*(p[0]-cx),norm.REF[0]+s*(p[1]-top)),s
def fisher3(src='../far/fish3.png'):
    a,lab=prep(src,'fish3');tr,s=_tr3();sh=lab.shape;yy,xx=np.mgrid[:sh[0],:sh[1]];lum=ndi.gaussian_filter(a[...,:3].mean(-1),1.5);(x0,y0),(x1,y1)=tr(F3['rod'][0]),tr(F3['rod'][1]);L=np.hypot(x1-x0,y1-y0)
    d=np.abs((xx-x0)*(y1-y0)-(yy-y0)*(x1-x0))/L;u=((xx-x0)*(x1-x0)+(yy-y0)*(y1-y0))/L**2;rodm=(lab>0)&(d<34*s)&(lum<172)&(u>-.03)&(u<1.03)
    arm=np.zeros(sh,bool)
    for pl in F3['arms']: arm|=bodyseg.poly([tr(p) for p in pl],sh)
    lab=lab.copy();lab[(lab==1)&~arm]=14;lab[arm&np.isin(lab,(14,1))&~rodm]=1;rodm=ndi.binary_opening(rodm&(lab!=1),iterations=2);lab[rodm]=28;lab[(lab==28)&arm&(lum<108)]=1;return a,lab      # les plis sombres des doigts restent de la peau
def fisherman3(P,shirt,over,sk,hr,rope='#6b5a3a',pants='#5a4a32',wood='#8a6a42',ph=0,length=430,bend=0.0,bob=0.0,mx=170,dy=300,below=110):
    """Toile (512+mx) x (512+dy+below), personnage décalé de (mx, dy). Ordre : jambes < corps < tête < canne (manche de GPT + prolongement en code) < mains."""
    from PIL import ImageDraw
    a,lab=P;tr,s=_tr3();W,H=512+mx,512+dy+below;c=Image.new('RGBA',(W,H));c.alpha_composite(legs.legs(pants,'#3a2a1c',ph),(mx,dy));full.G.update({14:.85,6:.85,5:.75,28:.8,1:.8,7:.6})
    t=full.tint(a,lab,{14:shirt,5:over,1:sk,6:rope,7:'#3a2e26',28:wood});c.alpha_composite(full.place(t,SC,(625,360)),(mx,dy));c.alpha_composite(kit.tint('head_dwarf_braided_90',{1:sk,2:hr,3:hr,6:'#3a2a1c'}),(mx,dy))
    part=lambda m:full.place(Image.fromarray(np.dstack([np.array(t)[...,:3],np.array(t)[...,3]*np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255]).astype('uint8')),SC,(625,360))
    c.alpha_composite(part(lab==28),(mx,dy))
    cv=lambda p:(mx+256+(p[0]-625)*.29,dy+229+(p[1]-360)*.29);(x0,y0),(x1,y1)=cv(tr(F3['rod'][0])),cv(tr(F3['rod'][1]));L=np.hypot(x0-x1,y0-y1);ux,uy=(x0-x1)/L,(y0-y1)/L;px,py=-uy,ux
    if px<0: px,py=-px,-py                                         # perpendiculaire tournée vers l'avant (le bas de l'image)
    if py<0: px,py=-px,-py
    S=3;o=Image.new('RGBA',(W*S,H*S));d=ImageDraw.Draw(o);n=24;w0=7.0;pts=[]
    for i in range(n+1):
        v=i/n;k=bend*70*v*v;pts.append((x0-ux*10+ux*length*v+px*k,y0-uy*10+uy*length*v+py*k,w0*(1-v)+1.5*v))
    for col,g in (('#2a1c12',1.3),(wood,0)):
        A=[((x+px*(w+g))*S,(y+py*(w+g))*S) for x,y,w in pts];B=[((x-px*(w+g))*S,(y-py*(w+g))*S) for x,y,w in pts][::-1];d.polygon(A+B,fill=col)
    for k in (0.5,0.75,1.0):
        x,y,w=pts[int(n*k)];d.ellipse([(x-w-2)*S,(y-w-2)*S,(x+w+2)*S,(y+w+2)*S],outline='#9aa0a6',width=S)
    tx,ty,_=pts[-1];bx,by=tx,dy+WATER+60;d.line([(tx*S,ty*S),(bx*S,by*S)],fill=(235,235,225,220),width=S)
    r=6-2*bob;d.ellipse([(bx-r)*S,(by-r)*S,(bx+r)*S,(by+r)*S],fill='#f2eee4',outline='#2a1c12',width=S);d.pieslice([(bx-r)*S,(by-r)*S,(bx+r)*S,(by+r)*S],180,360,fill='#c23a2a',outline='#2a1c12',width=S)
    c.alpha_composite(o.resize((W,H),Image.LANCZOS));c.alpha_composite(part((lab==1)&(np.abs(np.mgrid[:lab.shape[0],:lab.shape[1]][1]-627)<160)),(mx,dy));return c

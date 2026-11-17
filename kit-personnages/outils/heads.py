# Têtes supplémentaires : dessin GPT remis à l'échelle de la tête validée (repère : bout du nez), matières par ligne de partage des eaux à partir de graines.
# Matières : 1 peau, 2 cheveux/sourcils, 3 barbe, 4 métal, 8 tissu de coiffe (capuche, chapeau)
import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
from skimage.segmentation import watershed
NOSE=(262,285)                                    # bout du nez de la tête validée, sur la toile 512
G={1:.8,2:.75,3:.75,4:.9,8:.72,6:.7}
def build(name,src,s,nose,seeds,er=0):
    im=Image.open(src).convert('RGBA');a=np.array(im).astype(float);al=a[...,3]>40;lum=ndi.gaussian_filter(a[...,:3].mean(-1),1.2)
    mk=np.zeros(al.shape,int)
    for l,pts in seeds.items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=watershed(255-lum,mk,mask=al)
    w,h=im.size;sm=im.resize((round(w*s),round(h*s)),Image.LANCZOS);o=Image.new('RGBA',(512,512));off=(round(NOSE[0]-nose[0]*s),round(NOSE[1]-nose[1]*s));o.paste(sm,off)
    L=Image.fromarray(lab.astype('uint8')).resize(sm.size,Image.NEAREST);lo=Image.new('L',(512,512));lo.paste(L,off)
    o.save(f'assets/head_{name}.png');np.save(f'assets/head_{name}_lab.npy',np.array(lo));return o,np.array(lo)
# Têtes d'avant les lots : remontées pour suivre la règle de hauteur (sourcils sur la ligne des épaules, y = EYE_Y). Valeur = décalage vers le haut, en pixels.
RAISE={'fix':38,'hood':38,'widehat':45,'helm':40,'greathelm':24,'greathelm_nobeard':25,'greathelm_camail':24,'barbute':36,'barbute_shaved':35,'barbute_nobeard':36,
       'coif':43,'coif_shaved':45,'coif_f':35,'toque':48,'naine':25,'dame':22,'dame2':22,'dame3':25}
DX=-6                                            # anciennes têtes : construites sur NOSE x=262, donc 6 px à droite de l'axe des corps (256) ; recentrées ici
def raise_(im,dy,dx=DX):
    if not dy: return im
    o=Image.new('RGBA',im.size);o.alpha_composite(im.crop((-dx,dy,im.size[0],im.size[1])),(0,0));return o
def tint(name,cols):
    a=np.array(Image.open(f'assets/head_{name}.png').convert('RGBA')).astype(float);lab=np.load(f'assets/head_{name}_lab.npy')
    lum=(a[...,0]*.3+a[...,1]*.59+a[...,2]*.11)/255;out=a.copy()
    for l,col in cols.items():
        m=lab==l
        if not m.any(): continue
        w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float)/255
        f=np.clip(lum/lum[m].mean()*G[l],0,1.35);C=np.array([int(col[j:j+2],16) for j in (1,3,5)],float)
        for j in range(3): out[...,j]=out[...,j]*(1-w)+np.clip(C[j]*f,0,255)*w
    o=Image.fromarray(out.astype('uint8'))
    return raise_(o,RAISE.get(name,0))
HOOD=dict(src='../far/hood.png',s=0.38,nose=(628,700),seeds={
 8:[(650,220),(628,300),(550,400),(700,400),(628,480),(470,500),(790,500),(450,600),(805,600),(628,540),(520,540),(740,540),(455,660),(803,660),(470,720),(790,720)],
 1:[(628,670),(628,640),(628,612),(565,640),(695,640),(600,690),(658,690),(540,645),(718,645),(575,655),(685,655),(590,583),(668,583),(628,588),(530,580),(728,580)]+[(x,573) for x in range(545,720,15)],
 2:[(545,597),(715,597),(580,603),(680,603)],
 3:[(560,705),(700,705),(628,760),(540,760),(720,760),(628,830),(580,800),(680,800),(505,690),(755,690),(628,790),(600,850),(655,850)],
 4:[(628,872),(628,926)]})
WIDEHAT=dict(src='../far/widehat.png',s=0.38,nose=(628,695),seeds={       # calé sur le bout de la barbe (même barbe que la capuche)
 8:[(628,300),(628,400),(350,400),(900,400),(450,250),(800,250),(628,180),(400,550),(860,550),(628,600),(520,600),(740,600),(300,450),(950,450),(628,220),(540,330),(720,330),(628,625),(480,610),(780,610)],
 6:[(628,545),(540,527),(720,527),(470,470),(790,470),(450,420),(805,420)],
 1:[(628,690),(628,665),(610,700),(648,700),(565,668),(692,668)],
 3:[(560,715),(700,715),(628,770),(540,770),(720,770),(628,840),(580,810),(680,810),(490,700),(770,700),(628,800),(470,665),(790,665)],
 4:[(628,878),(628,925)]})
HELM=dict(src='../far/helm.png',s=0.38,nose=(628,695),seeds={                 # calé sur le bout de la barbe
 4:[(530,380),(720,380),(628,300),(628,450),(628,540),(470,500),(800,510),(540,545),(720,548),(628,618),(628,640),(500,430),(760,430),(628,250),(628,565),(520,548),(730,548),(462,518),(795,518),(628,878),(612,878),(644,878),(628,928),(580,330),(680,330)],
 1:[(608,690),(650,690),(628,702),(545,645),(712,645),(565,662),(695,662),(590,670),(668,670)],
 2:[(535,612),(722,612),(570,618),(688,618)],
 3:[(560,722),(700,722),(628,770),(540,770),(720,770),(628,840),(580,810),(680,810),(480,645),(780,645),(470,700),(790,700),(628,800),(600,850),(655,850),(458,595),(800,595),(628,902),(588,882),(668,882),(606,907),(650,907),(596,862),(660,862)]})
GREATHELM=dict(src='../far/greathelm.png',s=0.38,nose=(628,697),seeds={             # grand heaume fermé (paladin) ; calé sur le bout de la barbe
 4:[(540,300),(700,300),(628,250),(628,400),(540,420),(710,420),(540,560),(710,560),(628,520),(628,640),(500,600),(760,600),(628,320),(470,330),(790,330),(560,530),(700,530),(628,600),(480,450),(780,450),(628,902),(628,925)],
 3:[(560,705),(700,705),(628,760),(540,760),(720,760),(628,840),(580,810),(680,810),(480,650),(780,650),(470,700),(790,700),(628,800),(600,865),(655,865),(520,690),(740,690)]})
BARBUTE=dict(src='../far/barbute.png',s=0.38,nose=(628,697),seeds={                 # barbute ouverte en T (guerrier) ; calée sur le bout de la barbe
 4:[(540,330),(710,330),(628,260),(628,420),(520,450),(740,450),(480,560),(780,560),(540,610),(715,610),(628,480),(600,300),(660,300),(500,520),(760,520),(628,855),(628,868)],
 1:[(628,585),(628,600),(622,570),(636,570)],
 3:[(560,700),(700,700),(628,760),(540,760),(720,760),(628,820),(580,800),(680,800),(470,640),(790,640),(470,700),(790,700),(628,790),(628,905),(610,895),(646,895),(628,650),(600,655),(656,655)]})
BARBUTE_SHAVED=dict(src='../far/barbute_shaved.png',s=0.38,nose=(628,697),seeds={          # même barbute, bas de visage rasé : pour les races sans barbe
 4:[(540,330),(710,330),(628,260),(628,420),(520,450),(740,450),(480,560),(780,560),(540,610),(715,610),(628,480),(600,300),(660,300),(500,520),(760,520)],
 1:[(628,585),(628,605),(628,650),(628,700),(590,700),(668,700),(628,725),(610,670),(646,670),(560,690),(696,690)]})
COIF=dict(src='../far/coif.png',s=0.38,nose=(628,697),seeds={                      # cervelière sur camail de mailles (clerc en armure) ; 15 = mailles
 4:[(628,300),(560,330),(700,330),(628,360),(520,385),(740,385),(628,395),(628,872),(628,924)],
 15:[(628,470),(500,480),(760,480),(448,600),(805,600),(628,540),(452,650),(802,650),(540,440),(720,440),(560,520),(700,520),(455,540),(800,540)],
 1:[(628,690),(560,645),(695,645),(628,640),(628,605),(530,630),(725,630),(628,665)],
 2:[(560,607),(695,607),(530,612),(725,612)],
 3:[(628,760),(560,735),(700,735),(628,820),(520,725),(740,725),(580,800),(680,800),(600,855),(655,855),(570,712),(690,712),(628,900),(490,680),(770,680),(500,740),(755,740),(520,780),(735,780),(482,655),(775,655),(545,820),(710,820)]})
COIF_SHAVED=dict(src='../far/coif_shaved.png',s=0.38,nose=(628,703),seeds={        # même coiffe, visage rasé : pour les autres races
 4:[(628,300),(560,330),(700,330),(628,360),(500,360),(760,360),(628,400)],
 15:[(628,470),(500,480),(760,480),(455,600),(800,600),(628,540),(468,700),(788,700),(540,440),(720,440),(628,842),(590,828),(665,828),(560,520),(700,520),(628,563),(530,566),(725,566),(470,620),(788,620),(488,690),(770,690),(532,765),(725,765),(628,814)],
 1:[(628,592),(550,592),(710,592),(505,625),(760,620),(628,620),(560,665),(700,665),(520,665),(740,665),(628,700),(540,720),(720,720),(628,790),(628,760),(580,780),(680,780),(500,690),(760,690),(628,660)],
 2:[(530,612),(555,622),(578,632),(670,632),(695,620),(722,608)]})
COIF_F=dict(src='../far/coif_f.png',s=0.38,nose=(628,723),seeds={                  # cervelière, visage féminin (le nez est volontairement décalé : c'est la calotte qu'on aligne)
 4:[(628,300),(560,300),(700,300),(628,250),(628,390),(500,380),(760,380),(628,425),(520,410),(740,410)],
 15:[(628,490),(540,480),(720,480),(460,520),(800,520),(470,600),(790,600),(500,660),(765,660),(560,710),(700,710),(628,740),(628,715),(450,460),(810,460)],
 1:[(630,560),(560,580),(700,580),(630,610),(630,680),(570,640),(690,640),(630,530),(540,555),(720,555),(600,690),(660,690),(630,585)],
 2:[(530,530),(560,540),(700,540),(730,530)]})
TOQUE=dict(src='../far/toque.png',s=0.36,nose=(625,660),seeds={                    # toque de cuisinier (8), sur la tête du nain barbu
 8:[(625,500),(500,500),(750,500),(470,470),(790,470),(628,300),(450,330),(800,330),(628,200),(380,350),(880,350),(540,400),(720,400),(628,420),(400,420),(850,420)],
 1:[(420,500),(850,500),(415,530),(855,530),(625,630),(625,655),(590,625),(660,625),(625,575),(490,610),(760,610),(520,625),(735,625),(470,560),(790,560)],
 2:[(520,572),(570,580),(680,580),(730,572)],
 3:[(430,590),(820,590),(440,650),(810,650),(540,650),(710,650),(500,640),(750,640),(625,720),(520,720),(730,720),(560,770),(690,770),(625,790),(480,690),(770,690),(580,860),(670,860),(625,872)],
 4:[(625,815),(625,835),(625,899)]})
NAINE=dict(src='../far/naine.png',s=0.27,nose=(628,945),seeds={                   # naine sans barbe : tresse en couronne (2), fichu (8). Le repère est volontairement sous le menton :
 8:[(628,420),(520,470),(740,470),(628,560),(560,400),(700,400),(628,360),(500,520),(760,520),(628,445),(540,500),(720,500)],          # la tête est posée plus haut que les têtes barbues, sinon elle a « la tête dans le cou »
 2:[(628,250),(420,330),(840,330),(360,480),(900,480),(400,600),(860,600),(520,640),(740,640),(628,640),(628,690),(520,690),(740,690),(450,690),(810,690),(410,700),(850,700),(420,740),(840,740),
    (480,738),(530,755),(575,770),(680,770),(725,755),(775,738)],
 1:[(628,755),(560,735),(690,735),(500,800),(760,800),(628,820),(628,900),(560,870),(700,870),(378,680),(880,680),(455,790),(800,790),(520,785),(735,785),(628,790)]})
DAME=dict(src='../far/dame.png',s=0.27,nose=(628,950),seeds={                     # dame noble : chignon tressé sous résille de perles, diadème à pierre (52). Posée haut comme la naine.
 2:[(628,500),(450,560),(800,560),(400,640),(860,640),(520,520),(740,520),(628,300),(450,300),(800,300),(500,420),(760,420),(628,400),(400,380),(860,380),(420,700),(840,700),(628,230)],
 1:[(628,850),(540,820),(720,820),(628,900),(378,680),(880,680),(480,800),(780,800),(560,880),(700,880),(628,700),(520,690),(740,690),(628,670),(628,790),(540,788),(715,788),(505,778),(752,778),(580,795),(675,795),(470,740),(790,740),(600,740),(655,740),(540,715),(715,715)],
 52:[(628,605),(628,590),(628,620)]})
def _brows(lab,lum):
    """Sourcils des têtes de dame : tout le visage est d'abord de la peau, puis seuls les poils sombres de la bande des sourcils deviennent des cheveux.
    (Avec des graines, l'ombre des paupières se confondait avec les sourcils : gros pâtés carrés.)"""
    yy,xx=np.mgrid[:512,:512];f=lambda y:NOSE[1]+(y-950)*.27;g=lambda x:NOSE[0]+(x-628)*.27;lab=lab.copy()
    face=(lab==1)
    band=face&(yy>f(722))&(yy<f(766))&(np.abs(xx-g(628))>(602-628)*-.27)&(xx>g(476))&(xx<g(780));ref=ndi.maximum_filter(ndi.gaussian_filter(lum,1.5),9)
    br=band&(lum<ref*0.80);br=ndi.binary_opening(br,iterations=1);lab[br]=2;return lab
def build_dame():
    """Comme build, puis le métal (diadème, résille, perles) est repéré par sa clarté dans les cheveux : trop fin pour des graines."""
    o,lab=build('dame',**DAME)   # pas de graines sur les sourcils : _brows s'en charge
    a=np.array(o).astype(float);lum=a[...,:3].mean(-1);yy=np.mgrid[:512,:512][0];dy=NOSE[1]+(612-950)*.27;m=(lab==2)&(lum>ndi.gaussian_filter(lum,4)+34)&(lum>150)&(yy<dy-24);band=(lab>0)&(lum>150)&(np.abs(yy-dy)<5)&(lab!=52)
    lab=lab.copy();lab[m|band]=4;xx=np.mgrid[:512,:512][1];f=lambda y:NOSE[1]+(y-950)*.27;g=lambda x:NOSE[0]+(x-628)*.27
    lab=_brows(lab,lum)
    np.save('assets/head_dame_lab.npy',lab);return o,lab
# --- Dames : même visage que DAME (GPT n'a changé que la coiffure), donc mêmes graines de peau et de sourcils ; seuls les cheveux changent.
BROWS=[(500,742),(545,748),(585,758),(672,758),(712,748),(757,742)]
LADY={'dame2':[(560,560),(700,560),(500,560),(760,560),(420,620),(840,620),(400,700),(860,700),(450,480),(800,480),(628,300),(500,300),(760,300),(400,400),(860,400),(628,480),(380,520),(880,520),(520,440),(740,440),(450,250),(800,250),(628,350)],
      'dame3':[(560,560),(700,560),(450,600),(800,600),(400,700),(860,700),(420,450),(830,450),(500,300),(760,300),(628,200),(380,560),(880,560),(628,420),(450,330),(800,330),(560,480),(700,480),(350,480),(900,480)]}
def build_lady(name):
    """Tête de dame : bijoux et perles (4) repérés par leur clarté dans les cheveux ; sourcils limités à leur bande."""
    o,lab=build(name,src=f'../far/{name}.png',s=0.27,nose=(628,950),seeds={2:LADY[name],1:DAME['seeds'][1]});a=np.array(o).astype(float);lum=a[...,:3].mean(-1);yy,xx=np.mgrid[:512,:512];f=lambda y:NOSE[1]+(y-950)*.27;g=lambda x:NOSE[0]+(x-628)*.27
    lab=lab.copy();lab[(lab==2)&(lum>ndi.gaussian_filter(lum,4)+34)&(lum>150)&(yy<f(640))]=4
    lab=_brows(lab,lum);np.save(f'assets/head_{name}_lab.npy',lab);return o,lab
# --- Lots de têtes (planche de GPT découpée en ../lot<N>/t<k>.png) : pas de graines. Les cheveux, la barbe et les sourcils sont repérés par leur
# TEXTURE (mèches peintes), la peau par son aspect lisse ; les anneaux de métal sont les petites zones lisses et claires hors du visage.
LOT1={1:(135,240),2:(135,262),3:(135,335),4:(165,250),5:(140,265),6:(133,328),7:(137,250),8:(133,325)}        # bout du nez de chaque tête (dans son image découpée)
SKIN1={3:[(92,345,180,400)]}
RINGS1={3:[(105,58,165,80)],4:[(92,362,138,388),(182,362,228,388)],8:[(100,76,170,100),(115,343,152,364),(115,378,152,412)]}        # anneaux de métal : boîtes (x0,y0,x1,y1)
UP1={1:-16,2:-18,3:-28,4:-16,5:-34,6:-18,7:-34,8:-18}                          # têtes sans barbe : posées plus haut (menton au bord de l'encolure)
def build_auto(name,src,nose,s=0.62,thr=4.6,rings=(),up=0,skin=()):
    im=Image.open(src).convert('RGBA');a=np.array(im).astype(float);al=a[...,3]>40;lum=a[...,:3].mean(-1);hp=lum-ndi.gaussian_filter(lum,1.0);e=np.sqrt(ndi.gaussian_filter(hp*hp,4.0))      # échelle fine : les mèches (traits fins) comptent, pas les rides ni les ombres douces
    hair=(e>thr)&al;smooth=ndi.binary_opening(al&~hair,iterations=2);c,k=ndi.label(smooth);lab=np.where(al,2,0);W=al.shape[1]
    if k:
        idx=range(1,k+1);sz=ndi.sum(smooth,c,idx);cy,cx=np.array(ndi.center_of_mass(smooth,c,idx)).T;face=int(np.argmax(sz))
        for i in range(k):
            if sz[i]>=120 and (i==face or abs(cx[i]-nose[0])>0.3*W or (abs(cx[i]-nose[0])<0.25*W and abs(cy[i]-nose[1])<0.3*W)): lab[c==i+1]=1        # visage, crâne, oreilles
        sk=ndi.binary_closing(lab==1,iterations=3)&al&(e<thr*1.25);lab[sk&(lab==2)]=1
        # le trait de contour autour d'une zone de peau (crâne chauve, oreilles) n'est pas des cheveux
        rim=(lab==2)&(ndi.distance_transform_edt(al)<7)&(ndi.distance_transform_edt(lab!=1)<8);lab[rim]=1
    yy,xx=np.mgrid[:al.shape[0],:W];e2=np.sqrt(ndi.gaussian_filter(hp*hp,1.6));sl=ndi.gaussian_filter(lum,1.2)
    # oreilles : zones lisses et claires sur les côtés, à la hauteur des yeux (la texture y est mesurée de près : le contour épais des oreilles déborde sinon)
    side=al&(np.abs(xx-nose[0])>88)&(yy>nose[1]-135)&(yy<nose[1]+15)&(e2<thr*2.4)&(sl>88);side=ndi.binary_opening(side,iterations=1);c2,k2=ndi.label(side)
    for i in range(1,k2+1):
        m=c2==i
        if m.sum()>=70: lab[ndi.binary_dilation(m,iterations=5)&al&(sl>70)&(np.abs(xx-nose[0])>80)]=1
    for x0,y0,x1,y1 in skin: lab[al&(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)&(e2<thr*1.6)]=1                                   # peau isolée du visage (menton sous une moustache)
    for x0,y0,x1,y1 in rings: lab[al&(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)&(ndi.gaussian_filter(lum,1.2)>112)]=4
    w,h=im.size;sm=im.resize((round(w*s),round(h*s)),Image.LANCZOS);o=Image.new('RGBA',(512,512));off=(round(NOSE[0]-nose[0]*s),round(NOSE[1]-nose[1]*s)+up);o.paste(sm,off)
    L=Image.fromarray(lab.astype('uint8')).resize(sm.size,Image.NEAREST);lo=Image.new('L',(512,512));lo.paste(L,off);o.save(f'assets/head_{name}.png');np.save(f'assets/head_{name}_lab.npy',np.array(lo));return o,np.array(lo)
# La séparation par la texture seule laisse des artefacts (joues et oreilles couleur cheveux, crâne rasé couleur cheveux). Méthode retenue :
# un POLYGONE de peau par tête (visage, crâne chauve ou rasé) + des boîtes d'oreilles. Hors du polygone : cheveux. Dans le polygone : peau,
# sauf ce qui est nettement texturé (sourcils, moustache, barbe qui déborde). Le crâne rasé est donc toujours couleur peau.
FACE1={1:[(40,150),(33,85),(60,25),(135,1),(210,25),(238,85),(232,150),(215,200),(185,215),(165,250),(105,250),(85,215),(55,200)],
 2:[(62,150),(80,140),(135,150),(190,140),(208,150),(212,215),(190,250),(165,275),(105,275),(80,250),(58,215)],
 3:[(50,240),(135,255),(220,240),(232,290),(215,345),(190,385),(135,395),(80,385),(55,345),(38,290)],
 4:[(100,165),(165,150),(230,165),(240,215),(225,250),(165,268),(105,250),(90,215)],
 5:[(60,190),(100,170),(150,185),(200,170),(232,190),(235,240),(215,285),(175,308),(125,308),(85,285),(58,240)],
 6:[(8,215),(10,165),(42,105),(88,84),(80,160),(105,220),(133,250),(160,220),(185,160),(178,84),(224,105),(256,165),(258,215),(240,265),(200,290),(165,330),(100,330),(65,290),(32,265)],
 7:[(75,110),(70,60),(100,15),(140,5),(180,15),(210,60),(205,110),(225,170),(228,215),(205,255),(170,285),(105,285),(70,255),(48,215),(52,170)],
 8:[(45,240),(135,255),(225,240),(238,290),(222,330),(185,345),(165,330),(105,330),(85,345),(48,330),(32,290)]}
EARS1={1:[(0,95,42,168),(230,95,270,168)],2:[(0,135,48,208),(222,135,267,208)],3:[(0,212,42,288),(230,212,269,288)],4:[],5:[(3,168,48,228),(238,168,284,228)],
 6:[(0,198,38,268),(232,198,266,268)],7:[(8,112,50,190),(228,112,270,190)],8:[(0,212,38,283),(232,212,267,283)]}
THR1={6:9.5,7:9.0}
BEARD1={1:True,2:True,3:False,4:True,5:False,6:True,7:False,8:True}
SKULL1={1:165,6:255,7:185}                       # au-dessus de cette ligne (image découpée), tout le polygone est de la peau                               # seuil de texture dans le visage (plus haut : repousse du crâne rasé, rides du front)
def build_poly(name,src,nose,face,ears=(),rings=(),up=0,s=0.62,thr=7.0,beard=True,skull=None):
    from PIL import ImageDraw
    im=Image.open(src).convert('RGBA');a=np.array(im).astype(float);al=a[...,3]>40;lum=a[...,:3].mean(-1);hp=lum-ndi.gaussian_filter(lum,1.0);e=np.sqrt(ndi.gaussian_filter(hp*hp,3.0));sl=ndi.gaussian_filter(lum,1.2)
    pm=Image.new('L',im.size,0);ImageDraw.Draw(pm).polygon([tuple(p) for p in face],fill=255);pm=np.array(pm)>0;yy,xx=np.mgrid[:al.shape[0],:al.shape[1]]
    lab=np.where(al,2,0);tex=ndi.binary_opening((e>thr)&pm,iterations=1);tex=ndi.binary_closing(tex,iterations=2);c,k=ndi.label(tex);sz=ndi.sum(tex,c,range(1,k+1));tex=np.isin(c,[i+1 for i in range(k) if sz[i]>=90])
    eye=(np.abs(xx-nose[0])<78)&(yy>nose[1]-80)&(yy<nose[1]-8)                       # orbites : sombres mais c'est de la peau
    dark=(sl<=108)&~eye&(yy>nose[1]-15) if beard else np.zeros(al.shape,bool)        # tête barbue : sous le nez, ce qui est sombre et lisse est de la barbe ; sans barbe, c'est l'ombre du menton
    lab[pm&al&~tex&~dark]=1
    if skull is not None: lab[pm&al&(yy<skull)]=1                                    # crâne chauve ou rasé : toujours couleur peau, jamais couleur cheveux
    for x0,y0,x1,y1 in ears: lab[al&(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)&(e<11)]=1
    # le trait de contour d'une zone de peau au bord de la silhouette (crâne chauve ou rasé, oreilles) n'est pas des cheveux
    lab[(lab==2)&(ndi.distance_transform_edt(al)<9)&(ndi.distance_transform_edt(lab!=1)<11)&(e<14)]=1
    for v,mn in ((1,70),(2,45)):                                                     # miettes : petits îlots de peau dans les cheveux, et l'inverse
        c,k=ndi.label(lab==v);sz=ndi.sum(lab==v,c,range(1,k+1));lab[np.isin(c,[i+1 for i in range(k) if sz[i]<mn])]=3-v
    for x0,y0,x1,y1 in rings: lab[al&(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)&(sl>112)]=4
    w,h=im.size;sm=im.resize((round(w*s),round(h*s)),Image.LANCZOS);o=Image.new('RGBA',(512,512));off=(round(NOSE[0]-nose[0]*s),round(NOSE[1]-nose[1]*s)+up);o.paste(sm,off)
    L=Image.fromarray(lab.astype('uint8')).resize(sm.size,Image.NEAREST);lo=Image.new('L',(512,512));lo.paste(L,off);o.save(f'assets/head_{name}.png');np.save(f'assets/head_{name}_lab.npy',np.array(lo));return o,np.array(lo)
# --- Calque de matières (méthode retenue pour les lots) : GPT repeint la planche en aplats (peau ROUGE, poils BLEU, métal VERT).
# Chaque tête du calque est recalée sur sa tête grise (boîte sur boîte), puis sert d'étiquettes. Plus rien n'est deviné.
def split_map(path,n=8,rows=2):
    m=np.array(Image.open(path).convert('RGB')).astype(int);fg=(m.max(-1)-m.min(-1)>60);fg=ndi.binary_fill_holes(ndi.binary_closing(fg,iterations=2));c,k=ndi.label(fg);sz=ndi.sum(fg,c,range(1,k+1));ids=[i+1 for i in np.argsort(sz)[::-1][:n]]
    obs=ndi.find_objects(c);mid=m.shape[0]/rows;cells=sorted([(obs[i-1],i) for i in ids],key=lambda t:(int(((t[0][0].start+t[0][0].stop)/2)//mid),t[0][1].start));out=[]
    for sl,i in cells:
        p=m[sl];r,g,b=p[...,0],p[...,1],p[...,2];lab=np.zeros(r.shape,np.uint8);lab[(r>150)&(g<110)&(b<110)]=1;lab[(b>150)&(r<110)&(g<110)]=2;lab[(g>150)&(r<130)&(b<130)]=4;lab[(r>150)&(g>150)&(b<110)]=8;lab[(r>150)&(b>150)&(g<120)]=31;lab[(g>150)&(b>150)&(r<120)]=6;lab[(r>200)&(g>80)&(g<=170)&(b<90)]=60;lab[c[sl]!=i]=0;out.append(lab)      # jaune = tissu de coiffe (8), magenta = plume (31), cyan = cuir (6)
    return out
EYE_Y=200;BROW_DY=14                             # RÈGLE DE HAUTEUR (nain) : les SOURCILS arrivent au niveau du haut des épaules (y = 200 sur la toile 512, mesuré sur tous les corps).
#                                                  BROW_DY : les sourcils sont environ 14 px au-dessus des yeux dans les images découpées (EYE1..4 donnent le y des yeux).
#                                                  Plus bas, le personnage a « la tête entre les épaules ». Ne plus caler sur le nez de la tête barbue.
# Ce qui arrive sur la ligne du haut des épaules dépend de la morphologie (règle donnée par Yannick) :
LIGNE={'nain':'sourcils','halfelin':'sourcils','humain':'yeux','elfe':'yeux','tieffelin':'yeux','demi-orc':'nez'}
AXIS=256                                         # axe de TOUS les corps sur la toile (col et épaules mesurés à 256). NOSE[0]=262 décalait les têtes de 6 px vers la droite.
def build_map(name,src,nose,mlab,up=0,s=0.62,eye=None):
    if eye is not None: up=round(EYE_Y-(NOSE[1]+(eye-BROW_DY-nose[1])*s))
    im=Image.open(src).convert('RGBA');a=np.array(im);al=a[...,3]>40;w,h=im.size;L=np.array(Image.fromarray(mlab).resize((w,h),Image.NEAREST))
    _,ix=ndi.distance_transform_edt(L==0,return_indices=True);L=L[ix[0],ix[1]];L[~al]=0                     # bords mal recouverts : matière la plus proche
    sm=im.resize((round(w*s),round(h*s)),Image.LANCZOS);o=Image.new('RGBA',(512,512));off=(round(AXIS-nose[0]*s),round(NOSE[1]-nose[1]*s)+up);o.paste(sm,off)
    Ls=Image.fromarray(L.astype('uint8')).resize(sm.size,Image.NEAREST);lo=Image.new('L',(512,512));lo.paste(Ls,off);o.save(f'assets/head_{name}.png');np.save(f'assets/head_{name}_lab.npy',np.array(lo));return L
def split_sheet(path,out,n=8,rows=2):
    """Découpe une planche grise en n têtes (out % k), rangées par ligne puis par colonne."""
    im=np.array(Image.open(path).convert('RGB')).astype(float);lum=im.mean(-1);c,k=ndi.label(lum>236);edge=np.unique(np.r_[c[0],c[-1],c[:,0],c[:,-1]]);bg=ndi.binary_dilation(np.isin(c,edge[edge>0]),iterations=3)
    fig=ndi.binary_fill_holes(~bg);cc,kk=ndi.label(fig);sz=ndi.sum(fig,cc,range(1,kk+1));ids=[i+1 for i in np.argsort(sz)[::-1][:n]];obs=ndi.find_objects(cc);mid=im.shape[0]/rows
    cells=sorted([(obs[i-1],i) for i in ids],key=lambda t:(int(((t[0][0].start+t[0][0].stop)/2)//mid),t[0][1].start))
    for q,(sl,i) in enumerate(cells):
        m=cc[sl]==i;al=ndi.gaussian_filter(m.astype(float),0.7)*m*255;Image.fromarray(np.dstack([im[sl],al]).round().astype('uint8')).save(out%(q+1))
G.update({31:.9,6:.75,8:.8,60:.85})      # 60 = paille (ORANGE dans le calque)
def build_lot1(mp='../lot1/map.png'):
    M=split_map(mp)
    for k,n in LOT1.items(): build_map(f'l1_{k}',f'../lot1/t{k}.png',n,M[k-1],eye=EYE1[k])
LOT2={1:(127,240),2:(150,268),3:(125,262),4:(175,268),5:(132,268),6:(132,262),7:(132,308),8:(165,318)}      # lot 2 : moine, noble à toque, noble au cercle, noble au chapeau, marin, érudit, forgeron, barde
UP2={1:-28,2:-22,3:-22,4:-28,5:-20,6:-22,7:-30,8:-34}      # toutes remontées : calées sur le nez, elles couvraient la poitrine
def build_lot2(mp='../lot2/map.png'):
    M=split_map(mp)
    for k,n in LOT2.items(): build_map(f'l2_{k}',f'../lot2/t{k}.png',n,M[k-1],s=0.66,eye=EYE2[k])
# lot 3 (femmes) : nattes, chignon, âgée au bonnet de laine, érudite, marchande au turban, barde, capuchonnée, fermière au chapeau de paille.
# Têtes sans barbe : le repère est le MENTON (x du nez, y du bas du visage), posé sur NOSE comme la naine. Dans ce calque, CYAN (6) = paille.
LOT3={1:(155,322),2:(157,402),3:(170,388),4:(155,366),5:(170,337),6:(188,381),7:(170,354),8:(216,327)}
UP3={1:-10,2:-10,3:-14,4:-18,5:-22,6:-22,7:-16,8:-8}      # remontées : avec une coiffe volumineuse, le menton au bord de l'encolure fait encore trop bas
def build_lot3(mp='../lot3/map.png'):
    M=split_map(mp)
    for k,n in LOT3.items(): build_map(f'l3_{k}',f'../lot3/t{k}.png',n,M[k-1],s=0.52,eye=EYE3[k])
# lot 4 (hommes, oublis) : rôdeur à capuche, roublard à capuche et foulard, fermier au chapeau de paille, druide à couronne de feuilles (31), mineur à calotte de cuir, mendiant.
LOT4={1:(155,290),2:(160,270),3:(210,285),4:(170,258),5:(130,245),6:(165,255)}
UP4={1:-14,2:-28,3:-6,4:-20,5:-32,6:-10}      # coiffes volumineuses (capuche, calotte, grande chevelure) : remontées, sinon la tête couvre le torse jusqu'à la ceinture
def build_lot4(mp='../lot4/map.png'):
    M=split_map(mp,n=6)
    for k,n in LOT4.items():
        m=M[k-1].copy()
        if k!=3: m[m==60]=0                      # l'orange (paille) n'existe que sur le fermier : ailleurs ce sont des traits de bouche rouge-orangé
        build_map(f'l4_{k}',f'../lot4/t{k}.png',n,m,s=0.70,eye=EYE4[k])
EYE1={1:197,2:217,3:290,4:207,5:226,6:283,7:210,8:280}      # y des yeux dans chaque image découpée (lots 1 à 4)
EYE2={1:203,2:228,3:222,4:228,5:232,6:243,7:270,8:278}
EYE3={1:238,2:320,3:300,4:285,5:262,6:305,7:268,8:250}
EYE4={1:255,2:245,3:250,4:222,5:212,6:220}
# --- HALFELIN. Les sourcils sont lus dans le calque (les deux petites bandes bleues isolées dans le rouge) : plus de repère à poser à la main.
# HA[k] = (x du milieu du visage, y des sourcils) dans l'image découpée. Échelle 0,54 : tête à 0,92 de celle du nain (morpho.RACES).
HA={1:(162,246),2:(147,225),3:(154,230),4:(146,232),5:(176,258),6:(151,225),7:(163,211),8:(162,247)}
HB={1:(155,255),2:(168,238),3:(190,230),4:(170,300),5:(155,188),6:(175,272),7:(170,215),8:(175,238)}      # halfelin lot B : chignon, capuche, grand chapeau, toque, moine, noble toque, noble cercle, noble chapeau
HC={1:(155,232),2:(160,215),3:(150,222),4:(180,252),5:(170,245),6:(155,220),7:(195,208),8:(175,215)}      # halfelin lot C : marin, érudit, forgeron, barde, rôdeur, roublard, fermier, druide
def brows_from_map(m):
    c,k=ndi.label(m==2);idx=range(1,k+1);sz=ndi.sum(m==2,c,idx);cm=ndi.center_of_mass(m==2,c,idx);b=sorted([(cm[i],sz[i]) for i in range(k) if 60<sz[i]<2500],key=lambda t:-t[1])[:2]
    return (round((b[0][0][1]+b[1][0][1])/2),round((b[0][0][0]+b[1][0][0])/2)) if len(b)==2 else None
def build_lotH(lot,tab,s=0.54):
    M=split_map(f'../{lot}/map.png',n=len(tab))
    for k,(cx,by) in tab.items(): build_map(f'{lot}_{k}',f'../{lot}/t{k}.png',(cx,by),M[k-1],s=s,eye=by+BROW_DY)
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='helm':
        o,lab=build('helm',**HELM);t=tint('helm',{1:'#c98f6a',2:'#8a4a22',3:'#8a4a22',4:'#aeb4bc'});bg=Image.new('RGBA',(512,512),(140,105,70,255));bg.alpha_composite(t)
        bg.crop((150,60,370,400)).resize((660,1020),Image.LANCZOS).save('../far/z_helm.png');sys.exit()
    if len(sys.argv)>1 and sys.argv[1]=='widehat':
        o,lab=build('widehat',**WIDEHAT);t=tint('widehat',{1:'#c98f6a',2:'#8a4a22',3:'#8a4a22',4:'#9aa0a6',8:'#8a7a5a',6:'#3a2a1c'});bg=Image.new('RGBA',(512,512),(140,105,70,255));bg.alpha_composite(t)
        bg.crop((110,60,414,400)).resize((912,1020),Image.LANCZOS).save('../far/z_widehat.png');sys.exit()
    o,lab=build('hood',**HOOD)
    t=tint('hood',{1:'#c98f6a',2:'#8a4a22',3:'#8a4a22',4:'#9aa0a6',8:'#4a5a32'});bg=Image.new('RGBA',(512,512),(140,105,70,255));bg.alpha_composite(t)
    bg.crop((150,60,370,400)).resize((660,1020),Image.LANCZOS).save('../far/z_hood.png')

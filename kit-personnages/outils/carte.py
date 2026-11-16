# Personnages de la carte montés avec leurs objets. Règle : un objet tenu passe SOUS les doigts (ou derrière le poing), jamais posé par-dessus la main.
import numpy as np,math
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
import items,far,advp,r2,grd,kit,full
def cv(p): return (256+(p[0]-625)*.29,229+(p[1]-360)*.29)                 # image normalisée -> toile 512
def fist_of(lab,labels,side=-1,rows=70):
    """Centre du poing (bas du bras) du côté voulu, en pixels de la toile, et son masque."""
    H,W=lab.shape;yy,xx=np.mgrid[:H,:W];m=np.isin(lab,labels)&((xx-627)*side>250);ys=np.where(m.any(1))[0];m&=yy>ys.max()-rows
    cy,cx=ndi.center_of_mass(m);return cv((cx,cy)),m
def patch(c,src,mask):
    """Repose par-dessus c les pixels de src situés dans le masque (image normalisée) : les doigts repassent devant l'objet."""
    w=full.place(Image.fromarray((mask*255).astype('uint8')).convert('RGBA'),0.29,(625,360)).split()[0].filter(ImageFilter.GaussianBlur(0.8))
    s=np.array(src).astype(float);s[...,3]*=np.array(w)/255;c.alpha_composite(Image.fromarray(s.astype('uint8')));return c
def lantern_under(char,fist,h=100,up=5,mask=None):
    """Lanterne pendue au poing par son anneau (celui du dessin, attaché à la lanterne) : le haut de l'anneau est DANS le poing, sous les doigts ;
    le bas de l'anneau en ressort. Dessinée par-dessus le vêtement, mais sous le poing."""
    t=items.layer('lantern',h);c=Image.new('RGBA',char.size);c.alpha_composite(t,(round(fist[0]-t.size[0]/2),round(fist[1]-up)))
    if mask is None: c.alpha_composite(char);return c
    o=char.copy();o.alpha_composite(c);return patch(o,char,mask)
def axe_farmer():
    """Bûcheron : dans la pose à la fourche, tout l'outil est remplacé par la hache (manche plus épais), glissée sous les doigts."""
    a,lab=far.prep_pose('../far/fork_relaxed.png','fork_relaxed','../far/relaxed2.png','relaxed2');lab=far.fork(a,lab);H,W=lab.shape
    hand=ndi.binary_dilation(far.bodyseg.poly(far.HAND,(H,W)),iterations=6);tool=np.isin(lab,(4,28))&~hand
    ys,xs=np.where(lab==28);P=np.c_[xs,ys].astype(float);m=P.mean(0);u=np.linalg.svd(P-m,full_matrices=False)[2][0]
    if u[1]>0: u=-u                                                          # du bas vers le haut
    t=(P-m)@u;b=m+u*t.min();s=0.66;ai,li,_=items.prep('woodaxe');ix,iy=650,1195;co,si=-u[1],u[0]
    M=(co/s,si/s,ix-(co*b[0]+si*b[1])/s,-si/s,co/s,iy-(-si*b[0]+co*b[1])/s)
    A=np.array(Image.fromarray(ai.astype('uint8')).transform((W,H),Image.AFFINE,M,Image.BICUBIC)).astype(float);L=np.array(Image.fromarray(li.astype('uint8')).transform((W,H),Image.AFFINE,M,Image.NEAREST))
    a=a.copy();lab=lab.copy();a[tool,3]=0;lab[tool]=0;put=(A[...,3]>60)&~((lab==1)&hand)&~(hand&(lab>0)&(a[...,3]>60)&~np.isin(lab,(28,)))
    put=(A[...,3]>60)&~(hand&(lab==1));a[put]=A[put];lab[put]=L[put];return a,lab
def bow_in_hand(char,fist,mask,h=175,rot=45):
    """Arc tenu par sa poignée dans le poing relâché : bois du côté du corps, corde vers l'extérieur, en diagonale ; passe sous les doigts."""
    a,lab,bb=items.prep('bow');t=items.layer('bow',h,flip=True);k=h/(bb[3]-bb[1]);gy,gx=ndi.center_of_mass(lab==6)
    gx=t.size[0]-(gx-bb[0])*k;gy=(gy-bb[1])*k;R=int(h*1.2);sq=Image.new('RGBA',(2*R,2*R));sq.alpha_composite(t,(round(R-gx),round(R-gy)))
    sq=sq.rotate(rot,Image.BICUBIC);o=char.copy();o.alpha_composite(sq,(round(fist[0]-R),round(fist[1]-R)));return patch(o,char,mask)
def chasseur(char):
    """Réglage VALIDÉ : arc en travers du dos (poignée au milieu du dos, une pointe au-dessus d'une épaule) et carquois derrière l'autre épaule,
    tous deux dessinés SOUS le personnage. Les deux mains restent libres : toutes les poses et marches existantes fonctionnent."""
    al=np.array(char)[...,3];yr=int(np.argmax(al[:,320:345].max(1)>60));c=Image.new('RGBA',char.size)
    items.put(c,items.layer('bow',400,rot=30),(246,280));items.put(c,items.layer('quiver',215,rot=-16),(338,yr+62));c.alpha_composite(char);return c
def colporteur(char):
    """Réglage VALIDÉ : ballot dans le dos (hauteur 150, centré en (256,150)), dessiné SOUS le personnage. Cette grandeur vaut pour toutes les têtes ;
    sous le grand chapeau, seule la couverture roulée dépasse."""
    c=Image.new('RGBA',char.size);items.put(c,items.layer('bundle',150),(256,150));c.alpha_composite(char);return c

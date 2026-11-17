# Morphologies des autres races, fabriquées à partir du corps du NAIN (aucun dessin de corps à redemander) :
#  - tronc : on allonge seulement la bande aisselle → poignet (épaules, mains, bas du vêtement, bottes intacts) ;
#  - larg  : largeur globale ;
#  - centre: on resserre seulement la bande centrale (entre les épaulettes), qui garde donc sa forme aux épaulettes et aux bras.
from PIL import Image
Y0,Y1=292,372;X0,X1=188,324                       # sur la toile 512 du personnage
RACES={'nain':dict(tronc=0,larg=1.0,centre=1.0,tete=1.0),'halfelin':dict(tronc=0,larg=.8,centre=1.0,tete=.92),
       'humain':dict(tronc=42,larg=.82,centre=1.0,tete=1.0),'elfe':dict(tronc=50,larg=.82,centre=.66,tete=.96),
       'demi-orc':dict(tronc=72,larg=1.08,centre=1.0,tete=1.08)}
def body(im,tronc=0,larg=1.0,centre=1.0,**k):
    w,h=im.size
    if tronc:
        o=Image.new('RGBA',(w,h+tronc));o.paste(im.crop((0,0,w,Y0)),(0,0));o.paste(im.crop((0,Y0,w,Y1)).resize((w,Y1-Y0+tronc),Image.LANCZOS),(0,Y0));o.paste(im.crop((0,Y1,w,h)),(0,Y1+tronc));im=o;h+=tronc
    if centre!=1.0:
        cw=round((X1-X0)*centre);d=(X1-X0)-cw;o=Image.new('RGBA',(w,h));o.paste(im.crop((0,0,X0,h)),(d//2,0));o.paste(im.crop((X0,0,X1,h)).resize((cw,h),Image.LANCZOS),(X0+d//2,0));o.paste(im.crop((X1,0,w,h)),(X1-d+d//2,0));im=o
    if larg!=1.0: im=im.resize((round(w*larg),h),Image.LANCZOS)
    return im

def pt(x,y,tronc=0,larg=1.0,centre=1.0,**k):
    """Où tombe un point (x,y) de la toile 512 du nain après déformation (repère de l'image renvoyée par body)."""
    if tronc: y=y+(tronc if y>=Y1 else (y-Y0)*tronc/(Y1-Y0) if y>Y0 else 0)
    if centre!=1.0:
        cw=round((X1-X0)*centre);d=(X1-X0)-cw;x=x+d//2 if x<X0 else (X0+d//2+(x-X0)*centre if x<X1 else x-d+d//2)
    return x*larg,y
def emblem_on(bd,emb_fn,mask,chest=(257,358),size=84,**p):
    """Pose l'emblème de faction APRÈS la déformation, à ses vraies proportions (jamais écrasé) : il est recentré sur la poitrine déformée
    et réduit seulement s'il dépasse la largeur du tabard. mask : image L du tabard (toile 512), déformée ici comme le corps."""
    b=body(bd,**p);m=body(mask.convert('RGBA'),**p).split()[0];cx,cy=pt(chest[0],chest[1],**p);cy+=p.get('tronc',0)*0.25
    row=[x for x in range(m.size[0]) if m.getpixel((x,min(int(cy),m.size[1]-1)))>128];w=(max(row)-min(row)) if row else size
    s=int(min(size*(1.12 if p.get('tronc',0) else 1.0),w*0.86));e=emb_fn(s);lay=Image.new('RGBA',b.size);lay.alpha_composite(e,(round(cx-s/2),round(cy-s/2)))
    import numpy as np
    lay.putalpha(Image.fromarray(np.minimum(np.array(lay.split()[3]),np.array(m))));b.alpha_composite(lay);return b

def neck(c,sk,cx=256,y0=176,y1=300,w=96,dark=100):
    """Cou : comble l'encolure sous une tête SANS BARBE (sinon on voit un trou sombre sous le menton). À poser sur le corps, AVANT la tête.
    Seuls les pixels SOMBRES de l'encolure (l'intérieur du col) deviennent de la peau : cols, boutons et bretelles restent intacts."""
    from PIL import ImageDraw,ImageFilter
    import numpy as np
    from scipy import ndimage as ndi
    r,g,b=[int(sk[i:i+2],16) for i in (1,3,5)];S=3;m=Image.new('L',(c.size[0]*S,c.size[1]*S),0);ImageDraw.Draw(m).ellipse([(cx-w/2)*S,y0*S,(cx+w/2)*S,y1*S],fill=255);m=np.array(m.resize(c.size,Image.LANCZOS))>128
    a=np.array(c).astype(float);lum=a[...,:3].mean(-1);hole=m&(a[...,3]>60)&(lum<dark);hole=ndi.binary_opening(hole,iterations=2);lab,k=ndi.label(hole)
    if k: hole=lab==(np.argmax(ndi.sum(hole,lab,range(1,k+1)))+1);hole=ndi.binary_dilation(ndi.binary_fill_holes(hole),iterations=2)&m
    al=np.array(Image.fromarray((hole*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)));yy=np.mgrid[:c.size[1],:c.size[0]][0];sh=np.clip(.86-(yy-y0)/(y1-y0)*.16,.6,1)
    lay=np.dstack([r*sh*.98,g*sh*.94,b*sh*.92,al]).astype('uint8');c.alpha_composite(Image.fromarray(lay));return c

def mail_neck(a,lab,hole=7,mail=15,dark=.72):
    """Garde et plates sous une tête sans barbe (autres morphologies que le nain) : le trou de l'encolure est rempli de COTTE DE MAILLES
    (demande de Yannick). On prélève un carré de mailles sur le corps, on le répète en miroir dans le trou, un peu assombri (ombre du menton)."""
    import numpy as np
    from scipy import ndimage as ndi
    a=a.copy();lab=lab.copy();m=lab==mail;c,k=ndi.label(m);big=c==(np.argmax(ndi.sum(m,c,range(1,k+1)))+1);d=ndi.distance_transform_edt(big);y,x=np.unravel_index(np.argmax(d),d.shape);r=int(d[y,x]*.68)
    t=a[y-r:y+r,x-r:x+r,:3];t=np.concatenate([t,t[:,::-1]],1);t=np.concatenate([t,t[::-1]],0);h=lab==hole;ys,xs=np.where(h)
    if not len(ys): return a,lab
    y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1;T=np.tile(t,((y1-y0)//t.shape[0]+1,(x1-x0)//t.shape[1]+1,1))[:y1-y0,:x1-x0]
    sub=a[y0:y1,x0:x1];hm=h[y0:y1,x0:x1];sub[hm,:3]=T[hm]*dark;lab[h]=mail;return a,lab

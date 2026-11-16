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

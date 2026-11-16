# Emblèmes de faction simplifiés, dessinés en code (lisibles à la taille de la carte). emblem(nom, taille) -> image RGBA carrée.
# Les gardes appartiennent aux factions de la région (Poing Enflammé à Baldur's Gate, Grands Capitaines à Luskan…), jamais à la Guilde.
import math
from PIL import Image,ImageDraw
SS=8
def _c(d,cx,cy,r,f): d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=f)
def _flame(d,f,k=1.0,dy=0):
    P=[(50,4),(60,22),(72,14),(74,34),(88,30),(84,56),(78,76),(64,92),(50,96),(36,92),(22,76),(16,56),(12,30),(26,36),(28,16),(40,24)]
    d.polygon([((50+(x-50)*k)*SS,(52+(y-52)*k+dy)*SS) for x,y in P],fill=f)
def poing(d):                                    # Poing Enflammé : un poing ganté dans les flammes
    _flame(d,(226,120,30,255));_flame(d,(246,196,60,255),.62,8)
    g=(205,208,214,255);k=(60,62,70,255)
    d.rounded_rectangle([34*SS,40*SS,66*SS,74*SS],radius=6*SS,fill=k);d.rounded_rectangle([36*SS,42*SS,64*SS,72*SS],radius=5*SS,fill=g)
    for x in (43,50,57): d.line([(x*SS,42*SS),(x*SS,58*SS)],fill=k,width=int(1.6*SS))
    d.line([(36*SS,58*SS),(64*SS,58*SS)],fill=k,width=int(1.6*SS));d.rounded_rectangle([40*SS,72*SS,60*SS,86*SS],radius=2*SS,fill=k);d.rounded_rectangle([42*SS,72*SS,58*SS,84*SS],radius=2*SS,fill=(170,174,182,255))
def capitaines(d):                               # Grands Capitaines de Luskan : une ancre
    w=(236,232,220,255);t=int(9*SS)
    d.ellipse([40*SS,4*SS,60*SS,24*SS],outline=w,width=int(6*SS));d.line([(50*SS,22*SS),(50*SS,90*SS)],fill=w,width=t);d.line([(30*SS,36*SS),(70*SS,36*SS)],fill=w,width=t)
    d.arc([14*SS,34*SS,86*SS,94*SS],20,160,fill=w,width=t)
    d.polygon([(8*SS,56*SS),(26*SS,60*SS),(14*SS,76*SS)],fill=w);d.polygon([(92*SS,56*SS),(74*SS,60*SS),(86*SS,76*SS)],fill=w)
def lathandre(d):                                # Église de Lathandre : le soleil levant
    g=(240,196,70,255)
    for i in range(9):
        a=math.pi+math.pi*i/8;x,y=50+46*math.cos(a),72+46*math.sin(a);px,py=-math.sin(a)*5,math.cos(a)*5
        d.polygon([((50+24*math.cos(a)+px)*SS,(72+24*math.sin(a)+py)*SS),(x*SS,y*SS),((50+24*math.cos(a)-px)*SS,(72+24*math.sin(a)-py)*SS)],fill=g)
    d.pieslice([24*SS,46*SS,76*SS,98*SS],180,360,fill=g);d.line([(8*SS,74*SS),(92*SS,74*SS)],fill=g,width=int(6*SS))
E_={'poing':poing,'capitaines':capitaines,'lathandre':lathandre}
# couleurs de la tenue : tabard, bordure, métal
COL={'poing':('#a3231d','#8a8f96','#aeb4bc'),'capitaines':('#27445f','#d8d2c4','#9aa0a6'),'lathandre':('#c98a93','#e2c15a','#d9c9a0')}
def emblem(n,size):
    im=Image.new('RGBA',(100*SS,100*SS));E_[n](ImageDraw.Draw(im));return im.resize((size,size),Image.LANCZOS)

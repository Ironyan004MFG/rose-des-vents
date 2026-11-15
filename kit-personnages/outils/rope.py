# Corde torsadée dessinée en code le long d'un chemin (longe, laisse…) : même largeur et mêmes torons que les bouts de corde dessinés
import math,numpy as np
from PIL import Image,ImageDraw
def rope(size,pts,w=10.0,col=(152,128,86),SS=4):
    """size (L,H) de la toile ; pts : points du chemin (pixels) ; w : largeur de la corde en pixels. Rend un calque RGBA."""
    L=Image.new('RGBA',(size[0]*SS,size[1]*SS));d=ImageDraw.Draw(L);P=np.array(pts,float)*SS;W=w*SS
    seg=np.hypot(*np.diff(P,axis=0).T);cum=np.r_[0,np.cumsum(seg)];step=W*0.72;n=max(2,int(cum[-1]/step))
    S=np.linspace(0,cum[-1],n);X=np.interp(S,cum,P[:,0]);Y=np.interp(S,cum,P[:,1])
    dark=(34,26,18,255);d.line(list(zip(X,Y)),fill=dark,width=int(W+SS*2.4),joint='curve')
    for r,(x,y) in zip((W/2+SS*1.2,)*2,((X[0],Y[0]),(X[-1],Y[-1]))): d.ellipse([x-r,y-r,x+r,y+r],fill=dark)
    lo=tuple(int(c*0.72) for c in col);hi=tuple(min(255,int(c*1.18)) for c in col)
    for i in range(n):
        j=min(i+1,n-1);k=max(i-1,0);a=math.atan2(Y[j]-Y[k],X[j]-X[k])+math.radians(36)      # torons en biais
        ca,sa=math.cos(a),math.sin(a);hl,hw=W*0.80,W*0.36
        def quad(sx,sy,off=0):                                                              # toron arrondi
            return [(X[i]+ca*hl*sx*math.cos(t)-sa*(hw*sy*math.sin(t)+off),Y[i]+sa*hl*sx*math.cos(t)+ca*(hw*sy*math.sin(t)+off)) for t in np.linspace(0,2*math.pi,18,endpoint=False)]
        d.polygon(quad(1.08,1.12),fill=dark);d.polygon(quad(1,1),fill=lo+(255,));d.polygon(quad(.9,.72,-hw*.12),fill=col+(255,));d.polygon(quad(.6,.3,-hw*.36),fill=hi+(255,))
    # on rogne ce qui dépasse de la largeur de la corde
    M=Image.new('L',L.size,0);ImageDraw.Draw(M).line(list(zip(X,Y)),fill=255,width=int(W+SS*2.4),joint='curve')
    md=ImageDraw.Draw(M)
    for x,y in ((X[0],Y[0]),(X[-1],Y[-1])): r=W/2+SS*1.2;md.ellipse([x-r,y-r,x+r,y+r],fill=255)
    L.putalpha(Image.fromarray(np.minimum(np.array(L.split()[3]),np.array(M))))
    return L.resize(size,Image.LANCZOS)

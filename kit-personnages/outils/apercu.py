"""Aperçus des grandes races : chaque tête sur un corps permis par assoc.py, torse allongé, cou caché derrière le col."""
import numpy as np, heads, std, morpho, prp, cui, frg, brb, srv, rob
from PIL import Image
SK='#d9a988'
heads.G.update({6:.8,31:.9,8:.8,60:.85,15:.8,52:.95,69:1.0})
_P={}
def P(n):
    if n not in _P:
        _P[n]={'aventurier':std.adventurer,'mage':std.mage,'fermier':std.farmer,'garde':std.guard,'plates':std.plates,'barbare_f':lambda:std.prep('../std/brbf_relaxed.png','../std/brbf_relaxed_map.png'),
               'pourpoint':lambda:prp.prep('../prp/relaxed.png','relaxed'),'cuisinier':lambda:cui.prep('../cui/relaxed.png','relaxed'),'forgeron':lambda:frg.prep('../frg/relaxed.png','relaxed'),
               'barbare':lambda:brb.prep('../brb/relaxed.png','relaxed'),'serveuse':lambda:srv.prep('../srv/relaxed.png','relaxed'),'robe':lambda:rob.prep('../rob/relaxed.png','relaxed')}[n]()
    return _P[n]
STD={'aventurier':{5:'#3a5a3a',14:'#d8cdb0',6:'#5a3e28',4:'#aeb4bc',33:'#8a6a4a'},'mage':{5:'#3a3a6a',14:'#c9a23a',33:'#7a2e2e',6:'#5a3e28',4:'#c8ccd2'},'fermier':{5:'#5a6f8a',14:'#d8cdb0',33:'#8a5a3a',6:'#b9a27a',4:'#aeb4bc'},
     'garde':{4:'#b4bac2',15:'#7a7e86',6:'#3a2a1c',5:'#7a2e2e',14:'#d8c070'},'plates':{4:'#b4bac2',15:'#7a7e86',6:'#3a2a1c',14:'#d8c070'},'barbare_f':{5:'#6a5a48',6:'#3a2a1c',4:'#aeb4bc'}}
def body(n,sk=SK,tronc=42,fem=False,larg=1.0,**kw):
    # larg : carrure de la race (elfe .92, demi-orc 1.12) ; tronc : allongement du torse
    """-> (image 512x660, masque de l'ouverture du col). kw : couleurs (corps standard : {matière: couleur} dans cols=...)."""
    p=P(n)
    if n in STD:
        if n in ('garde','plates'): std.guard() if n=='garde' else std.plates()
        if n=='barbare_f': std.G.update({5:.8})
        c=std.char(p,{1:sk,**STD[n],**kw.get('cols',{})},H=600);l=(.9 if fem else 1)*larg
        h=std.hole(std.prep('../std/grd_relaxed.png','../std/grd_relaxed_map.png') if n in ('garde','plates') else p,512).convert('RGBA')      # garde, plates : l'encolure est remplie de mailles, on reprend son contour dans le calque du garde
    else:
        f={'pourpoint':lambda:prp.char(p,head=None,sk=sk,**kw),'cuisinier':lambda:cui.char(p,head=False,sk=sk,**kw),'forgeron':lambda:frg.char(p,head=False,sk=sk,**kw),'barbare':lambda:brb.char(p,head=False,sk=sk,**kw),
           'serveuse':lambda:srv.char(p,head=None,sk=sk,**kw),'robe':lambda:rob.char(p,head=None,sk=sk,**kw)}[n]
        with morpho.skin_neck(): c=f()
        h=std.hole(p[:2],512).convert('RGBA');l=.8*larg
    c=morpho.body(c,larg=l,tronc=tronc);o=Image.new('RGBA',(512,660));o.alpha_composite(c.crop((0,0,c.size[0],min(660,c.size[1]))),((512-c.size[0])//2,0))
    hb=morpho.body(h,larg=l).split()[0];hm=Image.new('L',(512,512));hm.paste(hb,((512-hb.size[0])//2,0));return o,hm
def put(c,hm,name,cols,sk=SK,mail=False):
    """Pose la tête ; le cou (71) n'est visible que dans l'ouverture du col. mail=True : cou en cotte de mailles (têtes casquées)."""
    t=heads.tint(name,{heads.COU:('#5e6168' if mail else std.shade(sk)),1:sk,**cols});lab=np.load(f'assets/head_{name}_lab.npy');a=np.array(t).astype(float)
    a[...,3]=np.where(lab==heads.COU,a[...,3]*np.array(hm).astype(float)/255,a[...,3]);c.alpha_composite(Image.fromarray(a.astype('uint8')));return c
def sheet(items,out,cols=4,w=1536,sk=SK,**race):
    """items : [(corps, kwargs corps, tête, couleurs tête), ...]"""
    rows=-(-len(items)//cols);O=Image.new('RGBA',(512*cols,660*rows),(140,105,70,255))
    for i,(b,kw,h,hc) in enumerate(items):
        c,hm=body(b,**{'sk':sk,**race,**kw});put(c,hm,h,hc,sk=sk,mail=kw.get('mail',False) if False else hc.pop('mail',False));O.alpha_composite(c,(512*(i%cols),660*(i//cols)))
    O.convert('RGB').resize((w,round(w*O.size[1]/O.size[0])),Image.LANCZOS).save(out);return O

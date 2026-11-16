# Emblèmes de faction simplifiés, dessinés en code (lisibles à la taille de la carte). emblem(nom, taille) -> image RGBA carrée.
# Les gardes appartiennent aux forces de la région (lore des Royaumes Oubliés), jamais à la Guilde. Une région peut avoir plusieurs gardes.
# Emblèmes tirés du lore : Poing Enflammé, Neverwinter (flocons), Triboar (sanglier), Mirabar (hache), Silverymoon (lune et étoile), Daggerford (dague).
# Emblèmes inventés (rien dans le lore) : Guet et Garde de Waterdeep, Guet de Baldur's Gate, ancre de Luskan, flocon de Wintershield.
import math
from PIL import Image,ImageDraw
SS=8
OR=(226,186,74,255);ARGENT=(226,230,236,255);BLANC=(240,240,236,255);NOIR=(26,24,26,255);VIDE=(0,0,0,0)
def P(d,pts,f): d.polygon([(x*SS,y*SS) for x,y in pts],fill=f)
def C(d,cx,cy,r,f): d.ellipse([(cx-r)*SS,(cy-r)*SS,(cx+r)*SS,(cy+r)*SS],fill=f)
def R(d,x0,y0,x1,y1,f,rad=0): d.rounded_rectangle([x0*SS,y0*SS,x1*SS,y1*SS],radius=rad*SS,fill=f)
def L(d,pts,f,w): d.line([(x*SS,y*SS) for x,y in pts],fill=f,width=int(w*SS),joint='curve')
def _flame(d,f,k=1.0,dy=0):
    pts=[(50,4),(60,22),(72,14),(74,34),(88,30),(84,56),(78,76),(64,92),(50,96),(36,92),(22,76),(16,56),(12,30),(26,36),(28,16),(40,24)]
    P(d,[(50+(x-50)*k,52+(y-52)*k+dy) for x,y in pts],f)
def poing(d):                                    # Poing Enflammé : un poing ganté dans les flammes
    _flame(d,(226,120,30,255));_flame(d,(246,196,60,255),.62,8);g=(205,208,214,255);k=(60,62,70,255)
    R(d,34,40,66,74,k,6);R(d,36,42,64,72,g,5)
    for x in (43,50,57): L(d,[(x,42),(x,58)],k,1.6)
    L(d,[(36,58),(64,58)],k,1.6);R(d,40,72,60,86,k,2);R(d,42,72,58,84,(170,174,182,255),2)
def guet_bg(d):                                  # Guet de Baldur's Gate (Haute-Ville) : la porte et sa herse
    R(d,14,40,86,94,OR);d.pieslice([14*SS,4*SS,86*SS,76*SS],180,360,fill=OR)
    R(d,28,48,72,94,VIDE);d.pieslice([28*SS,22*SS,72*SS,74*SS],180,360,fill=VIDE)
    for x in (39,50,61): L(d,[(x,26),(x,94)],OR,4.5)
    for y in (46,62,78): L(d,[(28,y),(72,y)],OR,4.5)
def ancre(d):                                    # Grands Capitaines de Luskan : une ancre
    w=BLANC;d.ellipse([40*SS,4*SS,60*SS,24*SS],outline=w,width=int(6*SS));L(d,[(50,22),(50,90)],w,9);L(d,[(30,36),(70,36)],w,9)
    d.arc([14*SS,34*SS,86*SS,94*SS],20,160,fill=w,width=int(9*SS));P(d,[(8,56),(26,60),(14,76)],w);P(d,[(92,56),(74,60),(86,76)],w)
def _flocon(d,cx,cy,r,f,w):
    for i in range(6):
        a=math.pi/2+i*math.pi/3;x,y=cx+r*math.cos(a),cy+r*math.sin(a);L(d,[(cx,cy),(x,y)],f,w)
        for s in (-1,1):
            b=a+s*math.pi/4;mx,my=cx+r*.58*math.cos(a),cy+r*.58*math.sin(a);L(d,[(mx,my),(mx+r*.36*math.cos(b),my+r*.36*math.sin(b))],f,w*.8)
    C(d,cx,cy,w*.9,f)
def neverwinter(d):                              # Garde de Neverwinter : trois flocons reliés par une volute
    L(d,[(30+16*math.sin(t*4.2)+t*22,10+t*82) for t in [i/30 for i in range(31)]],(170,196,226,255),4)
    _flocon(d,34,22,17,BLANC,4.2);_flocon(d,62,50,19,BLANC,4.6);_flocon(d,40,80,16,BLANC,4.0)
def wintershield(d): _flocon(d,50,50,42,BLANC,7)  # Veilleurs de Wintershield : un seul grand flocon
def guet_wd(d):                                  # Guet de Waterdeep : le croissant de lune sur l'eau
    C(d,50,42,36,OR);C(d,64,36,31,VIDE)
    for y,x0,x1 in ((84,22,78),(94,32,68)): L(d,[(x0+(x1-x0)*i/12,y+2.2*math.sin(i*1.6)) for i in range(13)],OR,4.5)
def garde_wd(d):                                 # Garde de Waterdeep : la tour crénelée
    P(d,[(30,96),(34,34),(66,34),(70,96)],OR);R(d,22,18,78,36,OR)
    for x in (22,43,64): R(d,x,6,x+14,22,OR)
    R(d,42,66,58,96,VIDE);d.pieslice([42*SS,56*SS,58*SS,76*SS],180,360,fill=VIDE);R(d,46,42,54,54,VIDE)
def sanglier(d):                                 # Les Douze de Triboar : une hure de sanglier, de face
    k=NOIR;P(d,[(16,8),(38,26),(22,40)],k);P(d,[(84,8),(62,26),(78,40)],k)
    d.ellipse([18*SS,18*SS,82*SS,84*SS],fill=k);d.ellipse([30*SS,58*SS,70*SS,98*SS],fill=k)
    i=(236,226,200,255);P(d,[(28,80),(20,54),(36,72)],i);P(d,[(72,80),(80,54),(64,72)],i)
    C(d,37,44,4,(210,60,40,255));C(d,63,44,4,(210,60,40,255));C(d,43,80,3.4,(90,30,30,255));C(d,57,80,3.4,(90,30,30,255))
def hache(d):                                    # La Hache de Mirabar : hache à double tranchant, dressée
    r=(176,84,48,255);R(d,46,10,54,84,r);P(d,[(50,2),(57,12),(43,12)],r);P(d,[(38,96),(44,82),(56,82),(62,96)],r)
    for s in (-1,1): P(d,[(50+s*4,22),(50+s*22,12),(50+s*40,20),(50+s*46,40),(50+s*40,60),(50+s*22,68),(50+s*4,56),(50+s*14,40)],r)
def lune_etoile(d):                              # Chevaliers d'Argent de Silverymoon : croissant de lune abritant une étoile
    C(d,46,50,42,ARGENT);C(d,62,50,36,VIDE)
    P(d,[(66+r*math.cos(a),50+r*math.sin(a)) for a,r in [(i*math.pi/4-math.pi/2,(17 if i%2==0 else 5.5)) for i in range(8)]],ARGENT)
def dague(d):                                    # Milice de Daggerford : la dague ensanglantée
    P(d,[(42,34),(58,34),(55,78),(50,92),(45,78)],ARGENT);L(d,[(50,38),(50,84)],(150,156,166,255),1.6)
    R(d,26,28,74,36,OR,3);R(d,44,6,56,30,(92,60,36,255),2);C(d,50,6,6,OR)
    s=(190,28,30,255);P(d,[(45,78),(55,78),(50,92)],s);C(d,50,97,3.2,s);C(d,60,90,2.4,s)
E_={'poing':poing,'guet_bg':guet_bg,'ancre':ancre,'neverwinter':neverwinter,'wintershield':wintershield,'guet_wd':guet_wd,'garde_wd':garde_wd,'sanglier':sanglier,'hache':hache,'lune_etoile':lune_etoile,'dague':dague}
# Gardes : (identifiant, région, nom, emblème, tabard, bordure, métal)
GARDES=[
 ('poing',"Baldur's Gate",'Poing Enflammé','poing','#a3231d','#8a8f96','#aeb4bc'),
 ('guet_bg',"Baldur's Gate",'Guet de la Haute-Ville','guet_bg','#26324a','#c9a23a','#aeb4bc'),
 ('garde_nw','Neverwinter','Garde de Neverwinter','neverwinter','#2f5d94','#c8ced6','#b4bac2'),
 ('wintershield','Neverwinter','Veilleurs de Wintershield','wintershield','#7ea3c4','#eef0f0','#b4bac2'),
 ('guet_wd','Waterdeep','Guet de la Cité','guet_wd','#2c6a3c','#c9a23a','#aeb4bc'),
 ('garde_wd','Waterdeep','Garde de la Cité','garde_wd','#232328','#c9a23a','#9a9ea6'),
 ('douze','Triboar','Les Douze','sanglier','#8a1a1c','#1e1c1e','#8a8478'),
 ('hache','Mirabar','La Hache de Mirabar','hache','#222024','#a8502c','#7a7e86'),
 ('argent','Silverymoon',"Chevaliers d'Argent",'lune_etoile','#27409a','#d4d8e0','#d6dae2'),
 ('daggerford','Daggerford','Milice de Daggerford','dague','#1f3566','#c8ced6','#aeb4bc'),
 ('kurth','Luskan','Nef Kurth','ancre','#27445f','#d8d2c4','#9aa0a6'),
 ('baram','Luskan','Nef Baram','ancre','#6e2630','#d8d2c4','#9aa0a6'),
 ('suljack','Luskan','Nef Suljack','ancre','#2f5a46','#d8d2c4','#9aa0a6'),
 ('taerl','Luskan','Nef Taerl','ancre','#4a5560','#d8d2c4','#9aa0a6'),
 ('rethnor','Luskan','Nef Rethnor','ancre','#23232a','#d8d2c4','#9aa0a6')]
def emblem(n,size):
    im=Image.new('RGBA',(100*SS,100*SS));E_[n](ImageDraw.Draw(im));return im.resize((size,size),Image.LANCZOS)

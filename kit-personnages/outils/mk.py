from PIL import Image,ImageDraw,ImageFilter
import numpy as np
D='/tmp/claude-0/-home-claude/07f1d72c-91b3-5b0d-bd68-356d5399ab1b/scratchpad/v3k/'
A=D+'RDV_Nain_Corrections_v3/'
def L(p): return Image.open(p).convert('RGBA')
def poly(pts):
    m=Image.new('L',(512,512),0);ImageDraw.Draw(m).polygon(pts,fill=255);return np.array(m)>0
mir=lambda pts:[(512-x,y) for x,y in pts]
def head_masks():
    al=np.array(L(A+'assets/head_dwarf_braided_90.png'))[...,3]>30
    face=[(189,232),(200,240),(215,247),(232,252),(246,257),(256,259),(266,257),(280,252),(297,247),(311,240),(322,232),(325,245),(323,262),(312,271),(300,277),(285,275),(273,271),(274,280),(268,290),(256,293),(244,290),(238,280),(239,271),(227,275),(212,277),(200,271),(189,262),(187,245)]
    ear=[(161,180),(178,183),(188,200),(190,232),(186,246),(170,236),(162,215)]
    skin=(poly(face)|poly(ear)|poly(mir(ear)))&al
    hl=[(150,246),(187,245),(189,232),(200,240),(215,247),(232,252),(246,257),(256,259),(266,257),(280,252),(297,247),(311,240),(322,232),(325,245),(362,246)]
    xs=np.arange(512);yh=np.interp(xs,[p[0] for p in hl],[p[1] for p in hl]);Y=np.arange(512)[:,None]
    hair=al&~skin&(Y<=yh[None,:]);beard=al&~skin&~hair
    return {'skin':skin,'hair':hair,'beard':beard}
def save(name,ms):
    for k,m in ms.items():
        g=Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))
        o=Image.merge('RGBA',(g,g,g,g));o.save(D+f'mymasks/{k}_{name}.png')
if __name__=='__main__':
    save('head_dwarf_braided_90',head_masks())

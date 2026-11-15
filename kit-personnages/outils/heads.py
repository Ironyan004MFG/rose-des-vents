# Têtes supplémentaires : dessin GPT remis à l'échelle de la tête validée (repère : bout du nez), matières par ligne de partage des eaux à partir de graines.
# Matières : 1 peau, 2 cheveux/sourcils, 3 barbe, 4 métal, 8 tissu de coiffe (capuche, chapeau)
import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage as ndi
from skimage.segmentation import watershed
NOSE=(262,285)                                    # bout du nez de la tête validée, sur la toile 512
G={1:.8,2:.75,3:.75,4:.9,8:.72}
def build(name,src,s,nose,seeds,er=0):
    im=Image.open(src).convert('RGBA');a=np.array(im).astype(float);al=a[...,3]>40;lum=ndi.gaussian_filter(a[...,:3].mean(-1),1.2)
    mk=np.zeros(al.shape,int)
    for l,pts in seeds.items():
        for x,y in pts: mk[y-3:y+4,x-3:x+4]=l
    lab=watershed(255-lum,mk,mask=al)
    w,h=im.size;sm=im.resize((round(w*s),round(h*s)),Image.LANCZOS);o=Image.new('RGBA',(512,512));off=(round(NOSE[0]-nose[0]*s),round(NOSE[1]-nose[1]*s));o.paste(sm,off)
    L=Image.fromarray(lab.astype('uint8')).resize(sm.size,Image.NEAREST);lo=Image.new('L',(512,512));lo.paste(L,off)
    o.save(f'assets/head_{name}.png');np.save(f'assets/head_{name}_lab.npy',np.array(lo));return o,np.array(lo)
def tint(name,cols):
    a=np.array(Image.open(f'assets/head_{name}.png').convert('RGBA')).astype(float);lab=np.load(f'assets/head_{name}_lab.npy')
    lum=(a[...,0]*.3+a[...,1]*.59+a[...,2]*.11)/255;out=a.copy()
    for l,col in cols.items():
        m=lab==l
        if not m.any(): continue
        w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))).astype(float)/255
        f=np.clip(lum/lum[m].mean()*G[l],0,1.35);C=np.array([int(col[j:j+2],16) for j in (1,3,5)],float)
        for j in range(3): out[...,j]=out[...,j]*(1-w)+np.clip(C[j]*f,0,255)*w
    return Image.fromarray(out.astype('uint8'))
HOOD=dict(src='../far/hood.png',s=0.38,nose=(628,700),seeds={
 8:[(650,220),(628,300),(550,400),(700,400),(628,480),(470,500),(790,500),(450,600),(805,600),(628,540),(520,540),(740,540),(455,660),(803,660),(470,720),(790,720)],
 1:[(628,670),(628,640),(628,612),(565,640),(695,640),(600,690),(658,690),(540,645),(718,645),(575,655),(685,655),(590,583),(668,583),(628,588),(530,580),(728,580)]+[(x,573) for x in range(545,720,15)],
 2:[(545,597),(715,597),(580,603),(680,603)],
 3:[(560,705),(700,705),(628,760),(540,760),(720,760),(628,830),(580,800),(680,800),(505,690),(755,690),(628,790),(600,850),(655,850)],
 4:[(628,872),(628,926)]})
if __name__=='__main__':
    o,lab=build('hood',**HOOD)
    t=tint('hood',{1:'#c98f6a',2:'#8a4a22',3:'#8a4a22',4:'#9aa0a6',8:'#4a5a32'});bg=Image.new('RGBA',(512,512),(140,105,70,255));bg.alpha_composite(t)
    bg.crop((150,60,370,400)).resize((660,1020),Image.LANCZOS).save('../far/z_hood.png')

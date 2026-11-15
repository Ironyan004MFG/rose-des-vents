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

import sys
from PIL import Image,ImageFilter
import numpy as np
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import kit
def seg(path,seeds,r=9):
    a=np.array(Image.open(path).convert('RGBA')).astype(float);al=a[...,3]>60;lum=a[...,:3].mean(-1)
    mk=np.zeros(al.shape,int);yy,xx=np.mgrid[0:al.shape[0],0:al.shape[1]]
    for l,pts in seeds.items():
        for x,y in pts: mk[(xx-x)**2+(yy-y)**2<r*r]=l
    mk[~al]=0;return a,watershed(255-ndi.gaussian_filter(lum,1.2),mk,mask=al)
G={1:.8,5:.72,7:.6}
def tint(a,lab,cols):
    lum=(a[...,0]*.3+a[...,1]*.59+a[...,2]*.11)/255;out=a.copy()
    for l,col in cols.items():
        m=lab==l
        if not m.any(): continue
        w=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255
        f=np.clip(lum/lum[m].mean()*G[l],0,1.4);C=np.array([int(col[j:j+2],16) for j in (1,3,5)],float)
        for j in range(3): out[...,j]=out[...,j]*(1-w)+np.clip(C[j]*f,0,255)*w
    return Image.fromarray(out.astype('uint8'))
SEED1={1:[(215,840),(1040,840),(180,860),(1075,860)],
 4:[(180,750),(1075,760),(130,740),(1120,745),(230,765),(1020,770),(622,925),(622,960),(622,1030)],
 5:[(300,600),(950,600),(450,500),(800,500),(400,900),(850,900),(350,1000),(900,1000),(450,300),(800,300),(620,1165),(250,500),(1000,500),(500,1100),(750,1100),(420,620),(830,620),(620,210)],
 7:[(620,500),(620,700),(560,330),(690,330),(600,820),(650,820),(620,1100)]}
def place(img,s,neck,tgt=(256,229)):
    w,h=img.size;im=img.resize((round(w*s),round(h*s)),Image.LANCZOS);o=Image.new('RGBA',(512,512));o.paste(im,(round(tgt[0]-neck[0]*s),round(tgt[1]-neck[1]*s)));return o
def char(body,cols,bdy=0):
    c=Image.new('RGBA',(512,512));b=kit.tint('boots_dwarf_90',cols);t=Image.new('RGBA',(512,512));t.paste(b,(0,bdy));c.alpha_composite(t)
    c.alpha_composite(body);c.alpha_composite(kit.tint('head_dwarf_braided_90',cols));return c
if __name__=='__main__':
    a,lab=seg('../cc/body1.png',SEED1)
    V=[('#2f6a34','#c98f6a','#8a4a22','#3a2e26'),('#2d4a7a','#8a5a3c','#b9b3aa','#5a4632')]
    O=Image.new('RGBA',(512*4,512),(140,105,70,255))
    for i,(s,ny,bd) in enumerate([(0.25,330,0),(0.27,330,10),(0.27,360,0),(0.29,360,14)]):
        cl,sk,hr,inn=V[i%2];cols={5:cl,1:sk,2:hr,3:hr,6:'#3a2a1c'}
        body=place(tint(a,lab,{5:cl,1:sk,7:inn}),s,(625,ny));O.alpha_composite(char(body,cols,bd),(i*512,0))
    O.crop((0,40,2048,500)).resize((1792,402),Image.LANCZOS).save('../cc_test.png')
    Image.fromarray(np.array(tint(a,lab,{5:V[0][0],1:V[0][1],7:V[0][3]}))).resize((627,627),Image.LANCZOS).save('../cc_body.png')

import numpy as np,glob,os,sys
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
K='/home/claude/rose-des-vents/kit-personnages'
def contour(lab):
    sk=(lab==1)|(lab==71);sk=ndi.binary_fill_holes(sk);return sk^ndi.binary_erosion(sk,iterations=2)
ref=np.load(f'{K}/elfe/tete/lotA/head_m_v_02_matieres.npy')
ref2=np.load(f'{K}/elfe/tete/lotE/head_f_v_chignon_matieres.npy')
def sheet(files,out,cols=8):
    rows=-(-len(files)//cols);S=Image.new('RGB',(cols*220,rows*240),(140,105,70));d=ImageDraw.Draw(S)
    for i,f in enumerate(files):
        im=Image.open(f.replace('_matieres.npy','.png')).convert('RGBA');c=Image.new('RGBA',(512,512),(140,105,70,255));c.alpha_composite(im)
        a=np.array(c);r=ref2 if '/head_f_' in f else ref;m=contour(r);a[m]=(0,255,255,255)
        a[200,:]=(255,0,0,255);a[:,256]=(255,255,0,255)
        t=Image.fromarray(a).crop((146,90,366,330));S.paste(t.convert('RGB'),((i%cols)*220,(i//cols)*240))
        d.text(((i%cols)*220+4,(i//cols)*240+2),os.path.basename(f)[5:-13][:22]+' '+f.split('/')[-2][-1],fill=(255,255,255))
    S.save(out)
if __name__=='__main__':
    r=sys.argv[1];fs=sorted(glob.glob(f'{K}/{r}/tete/lot*/head_*_matieres.npy'));sheet(fs,sys.argv[2])


import heads,prp,frg,brb,srv,rob,far,advp,r2,kit
from PIL import Image,ImageDraw
def run(line=False):
    heads.build_lot1();heads.build_lot2();heads.build_lot3();heads.build_lot4()
    R=prp.prep('../prp/relaxed.png','relaxed');L=prp.lute();Bk=prp.book();F=frg.prep('../frg/relaxed.png','relaxed');B=brb.prep('../brb/relaxed.png','relaxed');P=srv.prep('../srv/relaxed.png','relaxed');G=rob.prep('../rob/relaxed.png','relaxed');fa,fl=far.prep('../far/relaxed2.png','relaxed2');b,lb=advp.prep('../adv/src3.png','rel')
    orig=kit.tint;NOHEAD=lambda n,c:Image.new('RGBA',(512,512)) if n.startswith('head') else orig(n,c)
    def pad(f):
        kit.tint=NOHEAD
        try: c=f()
        finally: kit.tint=orig
        o=Image.new('RGBA',(512,560));o.alpha_composite(c.crop((0,0,512,min(c.size[1],560))));return o
    def sheet(n,bodies,tint,out,cols):
        O=Image.new('RGBA',(512*cols,560*((n+cols-1)//cols)),(140,105,70,255))
        for k in range(1,n+1):
            c=bodies[k-1]();c.alpha_composite(tint(k))
            if line: ImageDraw.Draw(c).line([(150,heads.EYE_Y),(362,heads.EYE_Y)],fill=(255,0,0,255),width=2)
            O.alpha_composite(c,(((k-1)%cols)*512,((k-1)//cols)*560))
        O.convert('RGB').resize((O.size[0]*3//4,O.size[1]*3//4),Image.LANCZOS).save(out)
    def T(lot,V):
        def f(k): v=V[k-1];return heads.tint(f'l{lot}_{k}',{1:'#c98f6a',2:v['hr'],4:v.get('me','#aeb4bc'),8:v.get('cl','#6a5a48'),31:v.get('pl','#f2eee4'),6:v.get('cu','#3a2a1c'),60:'#d8c28a'})
        return f
    V1=[dict(hr=h) for h in ['#8a4a22','#2a2420','#c9a24a','#b9b3aa','#5a3a22','#a83a22','#8a8a8a','#3a2a20']]
    sheet(8,[lambda:prp.char(R,head=None,cloth='#2e5a3a',trim='#c9a23a'),lambda:prp.char(R,head=None,cloth='#1f3a5a',trim='#c8ccd2',metal='#c8ccd2'),lambda:prp.bard(L,head=None),lambda:prp.char(R,head=None,cloth='#3a3440',trim='#8a8470'),lambda:prp.char(R,head=None,cloth='#7a2e2e',trim='#e8dcc0'),lambda:brb.char(B,head=False),lambda:prp.char(R,head=None,cloth='#5a2a4a'),lambda:brb.char(B,head=False,fur='#d8d2c4')],T(1,V1),'../lot1/corps.png',4)
    V2=[dict(hr='#6b4a2b',cl='#6a5a48'),dict(hr='#3a2a20',cl='#5a2a4a',pl='#f2eee4'),dict(hr='#8a4a22',me='#d8c070'),dict(hr='#2a2420',cl='#1f3a5a',me='#d8c070'),dict(hr='#b9b3aa',cl='#2e4a6a'),dict(hr='#d8d2c4',cl='#3a3440',me='#c9a23a'),dict(hr='#a83a22',cu='#3a2a1c',cl='#6a5a48'),dict(hr='#c9a24a',cl='#7a2e2e',pl='#e8c44a')]
    sheet(8,[lambda:prp.char(R,head=None,cloth='#5a4a32',trim='#5a4a32',metal='#5a4a32',belt='#c9b98a'),lambda:prp.char(R,head=None,cloth='#5a2a4a'),lambda:prp.char(R,head=None,cloth='#7a2e2e',trim='#d8c070'),lambda:prp.char(R,head=None,cloth='#1f3a5a',trim='#d8c070'),lambda:prp.char(R,head=None,cloth='#2e4a6a',trim='#2e4a6a',metal='#8a8470'),lambda:prp.scholar(Bk,head=None,cloth='#3a3440',trim='#8a8470'),lambda:frg.char(F,head=False),lambda:prp.bard(L,head=None,cloth='#7a2e2e',trim='#e8c44a')],T(2,V2),'../lot2/corps.png',4)
    V3=[dict(hr='#8a4a22'),dict(hr='#c9a24a'),dict(hr='#b9b3aa',cl='#7a5a6a'),dict(hr='#3a2a20',cl='#3a3440',me='#c9a23a'),dict(hr='#2a2420',cl='#b0626e',me='#d8c070'),dict(hr='#a83a22',cl='#2e5a3a',pl='#f2eee4'),dict(hr='#5a3a22',cl='#4a5a3a'),dict(hr='#c9a24a',cu='#d8c28a')]
    sheet(8,[lambda:srv.char(P,head=None),lambda:srv.char(P,head=None,bodice='#2e5a3a',skirt='#6a4a2e',ribbon='#b0626e'),lambda:srv.char(P,head=None,bodice='#4a4038',skirt='#3a3440',ribbon='#8a8470'),lambda:rob.char(G,head=None,cloth='#3a3440',trim='#8a8470',front='#d8d2c4',metal='#8a8470'),lambda:rob.char(G,head=None,cloth='#7a2e4a',trim='#d8c070'),lambda:rob.char(G,head=None,cloth='#2e5a3a',trim='#e8c44a',front='#e8dcc0'),lambda:srv.char(P,head=None,bodice='#3a4a32',skirt='#4a4038',apron='#6a5a48',ribbon='#3a2a1c',shirt='#b9a27a'),lambda:srv.char(P,head=None,bodice='#5a6f8a',skirt='#6a4a2e',shirt='#e6dfd0')],T(3,V3),'../lot3/corps.png',4)
    V4=[dict(hr='#6b4a2b',cl='#3a4a32'),dict(hr='#2a2420',cl='#2a2a30'),dict(hr='#8a4a22'),dict(hr='#b9b3aa',pl='#4f8a3a'),dict(hr='#3a2a20',cu='#5a3e28'),dict(hr='#8a8a8a',cl='#6a5a48')]
    sheet(6,[lambda:pad(lambda:advp.char(b,lb,*r2.V[0])),lambda:pad(lambda:advp.char(b,lb,*r2.V[1])),lambda:pad(lambda:far.char(fa,fl,'#d8cdb0','#5a6f8a','#c98f6a','#8a4a22')),lambda:prp.char(R,head=None,cloth='#3a4a32',trim='#3a4a32',metal='#5a4a32',belt='#5a3e28'),lambda:frg.char(F,head=False,apron='#4a4438'),lambda:pad(lambda:far.char(fa,fl,'#8a7a5c','#5a4a3a','#c98f6a','#8a8a8a'))],T(4,V4),'../lot4/corps.png',3)
if __name__=='__main__':
    import sys;run(line='ligne' in sys.argv)

import sys; sys.path.insert(0,'tools')
from proof import Renderer, sheet
R=Renderer('build/quick/R.ttf'); B=Renderer('build/quick/B.ttf')
U="ABCDEFGHIJKLMNOPQRSTUVWXYZ"; L="abcdefghijklmnopqrstuvwxyz"; D="0123456789 .,:;!?-_+=/\\|()[]{}'\"*#$%&@^~<>"
sheet([(R,U,72),(R,L,72),(R,D[:24],72),(R,D[24:],72)],'proofs/p1.png')
sheet([(B,U,72),(B,L,72),(B,D[:24],72),(B,D[24:],72)],'proofs/p2.png')

from pathlib import Path
from PIL import Image,ImageDraw
root=Path('work/verification/video-reference');out=Image.new('RGB',(1080,720),'#0b0b0d');d=ImageDraw.Draw(out)
for i,n in enumerate(['Neon-Emerald','Lime-Drop','Amber-Script','Scarlet-Punch']):
 im=Image.open(root/(n+'-2.png')).convert('RGBA');im.thumbnail((510,310));x=(i%2)*540+(540-im.width)//2;y=(i//2)*360;out.paste(im,(x,y),im);d.text(((i%2)*540+18,y+330),n.replace('-',' '),fill='#ffffff')
out.save(root/'styles-preview.png')

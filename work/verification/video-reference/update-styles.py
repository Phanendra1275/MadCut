from pathlib import Path
p=Path('outputs/chatcut/lib/templates.ts');s=p.read_text(encoding='utf-8');s=s.replace("'Rock Solidance'] as const", "'Rock Solidance','Neon Emerald','Lime Drop','Amber Script','Scarlet Punch'] as const")
s=s.replace("const existingCatalog:","const existingCatalog:")
marker=" {name:'Minimal',label:'Simple word reveal'"
pos=s.index(marker)
s=s[:pos]+""" {name:'Neon Emerald',label:'Video reference · neon two-line reveal',sample:'NUVVU EM CHESTHUNNAV',accent:'#69ff35'},
 {name:'Lime Drop',label:'Video reference · spring word drop',sample:'NUVVU EM CHESTHUNNAV',accent:'#c4ff39'},
 {name:'Amber Script',label:'Video reference · warm bold & script',sample:'Nuvvu em chesthunnav',accent:'#ffb43c'},
 {name:'Scarlet Punch',label:'Video reference · red & white punch',sample:'NUVVU EM CHESTHUNNAV',accent:'#ff3038'},

"""+s[pos:]
s=s.replace("Pop Tag':'Highlight'", "Pop Tag':'Highlight'") # category uses unquoted key below
s=s.replace("Pop Tag':'Highlight'", "Pop Tag':'Highlight'")
s=s.replace("'Pop Tag':'Highlight'", "'Pop Tag':'Highlight','Neon Emerald':'Highlight','Lime Drop':'Dynamic','Amber Script':'Cinematic','Scarlet Punch':'Bold'")
p.write_text(s,encoding='utf-8')
p=Path('outputs/chatcut/app/page.tsx');s=p.read_text(encoding='utf-8');s=s.replace('15 studio','19 studio');p.write_text(s,encoding='utf-8')
p=Path('outputs/chatcut/lib/render-caption.ts');s=p.read_text(encoding='utf-8')
s=s.replace("const base=look.size", "const reference=['Neon Emerald','Lime Drop','Amber Script','Scarlet Punch'].includes(style);\n const base=look.size")
s=s.replace("||(style==='Butter Up')", "||(style==='Butter Up')||(style==='Amber Script'&&index>=Math.ceil(raw.length/2))")
s=s.replace("'Rock Solidance'].includes(style)||(style==='Trio Lockup'", "'Rock Solidance','Neon Emerald','Lime Drop','Scarlet Punch'].includes(style)||(style==='Trio Lockup'")
s=s.replace("'Spinning Butter','Coovetica Waving of'].includes(style)", "'Spinning Butter','Coovetica Waving of','Neon Emerald','Lime Drop','Amber Script','Scarlet Punch'].includes(style)")
s=s.replace("if(style==='Butter Up')ctx.translate", "if(style==='Lime Drop'){const spring=1-Math.exp(-elapsed*18)*Math.cos(elapsed*25);ctx.translate(0,(1-spring)*g.size*.55);const scale=.85+.15*spring;ctx.scale(scale,scale);}if(['Neon Emerald','Amber Script','Scarlet Punch'].includes(style)){ctx.translate(0,(1-progress)*g.size*.25);const scale=.94+.06*progress;ctx.scale(scale,scale);}if(style==='Butter Up')ctx.translate")
s=s.replace("if(style==='Rock Solidance'&&g.script)color='#63ce08';", "if(style==='Rock Solidance'&&g.script)color='#63ce08';if(reference){color=g.index<Math.ceil(raw.length/2)?accent:look.color;if(style==='Lime Drop')color=g.index<Math.ceil(raw.length/2)?look.color:accent;}")
s=s.replace("if(['Glow Script','Hyper Clean'", "if(reference){ctx.strokeStyle='rgba(0,0,0,.85)';ctx.lineWidth=g.size*.075;ctx.strokeText(g.text,-g.width/2,0);ctx.shadowColor=color;ctx.shadowBlur=g.size*(isActive?.18:.07);}\n    if(['Glow Script','Hyper Clean'")
p.write_text(s,encoding='utf-8')
p=Path('outputs/chatcut/local/speech_engine.py');s=p.read_text(encoding='utf-8')
s=s.replace("if probability<.55 or language not in {'te','hi','en'}:raise ValueError('Spoken language is uncertain. Choose Telugu, Hindi, or English and generate again.')", """if probability<.55:raise ValueError('Spoken language is uncertain. Choose the actual spoken language: Telugu, Hindi, or English, and generate again.')
        if language not in {'te','hi','en'}:
            name={'ta':'Tamil','ml':'Malayalam','kn':'Kannada','bn':'Bengali','mr':'Marathi'}.get(language,language)
            raise ValueError(f'Detected {name} speech ({probability:.0%} confidence). MadCut currently supports Telugu, Hindi and English. This video can be used for visual styling, but do not force it into Telugu captions.')""")
p.write_text(s,encoding='utf-8')

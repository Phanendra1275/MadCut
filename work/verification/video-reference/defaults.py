from pathlib import Path
p=Path('outputs/chatcut/lib/templates.ts');s=p.read_text(encoding='utf-8');s=s.replace('sample:string;accent:string}[]=[','sample:string;accent:string;defaults?:{entry:string;motion:boolean;color:string}}[]=[')
for name,color in [('Neon Emerald','#69ff35'),('Lime Drop','#c4ff39'),('Amber Script','#ffb43c'),('Scarlet Punch','#ff3038')]:
 s=s.replace("accent:'"+color+"'},", "accent:'"+color+"',defaults:{entry:'Auto',motion:true,color:'#ffffff'}},")
p.write_text(s,encoding='utf-8')

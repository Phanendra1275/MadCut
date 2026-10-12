"""Regressions for real spelling failures, beyond memorized caption examples."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from natural_tenglish import generate
from timed_subtitles import fast_tenglish
from caption_timing import faithful

cases={
 'ఉంటేనే చుట్టుపక్కల పెట్టి':'untene chuttupakkala petti',
 'మాట్లాడేటప్పుడు':'maatlaadetappudu',
 'మంచి ఆట':'manchi aata',
 'తాత తోట':'thaatha thota',
 'గుంటూరు':'guntooru',
 'ఫస్ట్ వీడియో కెమెరా ఫేస్ ఛానల్ సపోర్ట్ స్టార్ట్':'first video camera face channel support start',
 'అసిస్టెంట్ ప్రొఫెసర్ స్టూడెంట్స్ లైఫ్ ట్రై':'assistant professor students life try',
 'ఫ్రాన్స్ బీచ్ రిసార్ట్స్':'France beach resorts',
 'ఈ కెమెరాలో వీడియోకి ఫస్ట్ సపోర్ట్ ఉంది':'ee camera lo video ki first support undi',
}
results=[]
for source,expected in cases.items():
 value=generate(source);assert value==expected,(source,value,expected)
 assert faithful(source,value),(source,value,'meaning guard')
 parts=source.split();cue={'id':'r','text':source,'start':0,'end':len(parts),'words':[{'word':w,'start':i,'end':i+1,'confidence':.92} for i,w in enumerate(parts)]}
 output=fast_tenglish([cue])[0]
 assert output.get('words'),('lost mapped speech anchors',source)
 assert (output['start'],output['end'])==(cue['start'],cue['end'])
 assert all(cue['start']<=w['start']<w['end']<=cue['end'] for w in output['words'])
 results.append({'source':source,'natural':value,'mappedWords':len(output['words'])})
assert generate('టానా','Natural',glossary={'టానా':'TANA'})=='TANA'
assert generate('Phanendra Vasthunnanu GMRIT 2026')=='Phanendra Vasthunnanu GMRIT 2026'
Path('work/verification/caption-foundation/roman-fallback-results.json').write_text(json.dumps({'passed':len(cases)+2,'cases':results,'guards':['approved Telugu proper noun','Latin names and numbers unchanged']},ensure_ascii=False,indent=2),encoding='utf-8')
print('Passed',len(cases)+2,'retroflex/dental, English loanword, protected name and mapped timing checks.')

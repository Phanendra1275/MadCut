import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from timed_subtitles import fast_tenglish
from transcript_correction import correct
from caption_timing import faithful
cases={'నువ్వు ఎక్కడికి వెళ్తున్నావు?':'Nuvvu ekkadiki velthunnav?','ఏం చేస్తున్నావు?':'Em chesthunnav?','నేను కూడా వస్తాను.':'Nenu kuda vastha.','చాలా బాగుంది.':'Chala bagundi.','నాకు అర్థం కాలేదు.':'Naaku artham kaaledu.','వస్తున్నావు':'Vasthunnav','వెళ్లావు':'Vellav','చేశావు':'Chesav','చెప్పావు':'Cheppav','వెళ్తాను':'Veltha','చేస్తాను':'Chestha','ఉన్నాను':'Unna','ఉన్నావు':'Unnav','ఉంటుంది':'Untundi','ఉన్నాడు':'Unnadu','ఈ వీడియోని edit చేసి నాకు పంపు.':'Ee video ni edit chesi naaku pampu.','రేపు మీటింగ్ ఉంది.':'Repu meeting undi.','వీడియో upload చేశావా?':'Video upload chesava?','బ్రో, ఈ డిజైన్ చాలా బాగుంది.':'Bro, ee design chala bagundi.','వెబ్‌సైట్ రెడీ అయ్యిందా?':'Website ready ayyinda?','ఫైల్ send చెయ్యి.':'File send cheyyi.'}
results=[]
for source,expected in cases.items():
 parts=source.split();c={'id':'test','start':0,'end':len(parts),'text':source,'confidence':.99,'words':[{'word':w,'start':i,'end':i+1} for i,w in enumerate(parts)]}
 t=fast_tenglish([c])[0];assert t['text']==expected,(source,t['text'],expected);assert (t['start'],t['end'])==(c['start'],c['end']);assert t.get('words'),(source,'lost anchors');assert fast_tenglish([c],'WhatsApp')[0]['text']==expected;results.append({'source':source,'natural':t['text'],'speechAnchors':len(t['words'])})
 assert faithful(source,t['text'])
original={'id':'typo','start':0,'end':3,'text':'నువ్వు ఎక్కడికి వెళ్తునావ్','confidence':.99};fixed=correct([original],model_enabled=False)[0];assert 'వెళ్తున్నావు' in fixed['text'];assert fast_tenglish([fixed])[0]['text']=='Nuvvu ekkadiki velthunnav?'
assert correct([{'id':'meaning','start':0,'end':3,'text':'నాకు అర్ధం కాలేదు'}],model_enabled=False)[0]['text']=='నాకు అర్థం కాలేదు'
assert correct([{'id':'half','start':0,'end':3,'text':'అర్ధం గంట వేచి ఉండు'}],model_enabled=False)[0]['text']=='అర్ధం గంట వేచి ఉండు'
assert fast_tenglish([{'id':'names','start':0,'end':3,'text':'Phanendra GMRIT Instagram YouTube ChatGPT Vasthunnanu 123'}])[0]['text']=='Phanendra GMRIT Instagram YouTube ChatGPT Vasthunnanu 123'
assert fast_tenglish([{'id':'formal','start':0,'end':3,'text':'నువ్వు ఎక్కడికి వెళ్తున్నావు?'}],'Formal')[0]['text']=='Nuvvu ekkadiki veltunnavu?'
Path('work/verification/natural-tenglish-v2-results.json').write_text(json.dumps({'cases':results,'additionalGuards':['proper nouns','contextual artham versus half','high-confidence obvious typo','formal mode','no invented bro/emoji']},ensure_ascii=False,indent=2),encoding='utf-8');print('Passed',len(cases),'natural/mixed-language examples, exact speech anchors, semantic guards and modes.')

import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from transcript_correction import correct,acceptable
from timed_subtitles import fast_tenglish
cases={'నువ్వు ఎక్కడికి వెళ్తున్నావు?':'Nuvvu ekkadiki velthunnav?','ఏం చేస్తున్నావు?':'Em chesthunnav?','రేపు కాలేజీలో మీటింగ్ ఉంది':'Repu college lo meeting undi','ఈ వీడియోని edit చేసి నాకు పంపు':'Ee video ni edit chesi naaku pampu'}
for text,expected in cases.items():
 c={'id':'x','start':0,'end':3.2,'text':text}
 assert fast_tenglish([c])[0]['text']==expected
 assert fast_tenglish([c],'WhatsApp')[0]['text']==expected
 assert fast_tenglish([c])[0]['end']==3.2
c={'id':'formal','start':0,'end':3.2,'text':'నువ్వు ఎక్కడికి వెళ్తున్నావు?'}
assert fast_tenglish([c],'Formal')[0]['text']=='Nuvvu ekkadiki veltunnavu?'
names='Phanendra GMRIT Instagram YouTube ChatGPT 123';assert fast_tenglish([{**c,'text':names}])[0]['text']==names
assert not acceptable('Phanendra 10 రాలేదు','Fanendra 4 వచ్చాడు')
assert not acceptable('నాకు తెలియదు','నాకు తెలుసు')
c={'id':'typo','start':0,'end':3.2,'text':'నువ్వు ఎక్కడికి వెళ్తునావ్','confidence':.4,'words':[{'word':w,'start':i,'end':i+1,'confidence':.4} for i,w in enumerate('నువ్వు ఎక్కడికి వెళ్తునావ్'.split())]}
d=correct([c],model_enabled=False)[0];assert d['text']=='నువ్వు ఎక్కడికి వెళ్తున్నావు?' and [(w['start'],w['end']) for w in d['words']]==[(w['start'],w['end']) for w in c['words']]
assert correct([{**c,'text':'నాకు తెలియదు','words':[],'confidence':.98}],model_enabled=False)[0]['correction']=='preserved'
print('Passed natural/formal/WhatsApp, mixed speech, proper nouns, no default emoji, unchanged correction anchors and protected meaning.')

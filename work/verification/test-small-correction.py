import sys,json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from transcript_correction import correct,acceptable,stop
samples=[{'id':'typo','start':0,'end':3.2,'text':'నువ్వు ఎక్కడికి వెళ్తునావ్','confidence':.4},{'id':'context','start':3.2,'end':6,'text':'ఏం చేస్తున్నావు','confidence':.4},{'id':'protected','start':6,'end':9,'text':'Phanendra GMRIT Instagram YouTube ChatGPT 123','confidence':.4}]
result=correct(samples)
Path('work/verification/small-correction-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False),flush=True)
for a,b in zip(samples,result):assert (a['start'],a['end'])==(b['start'],b['end'])
assert result[0]['text']=='నువ్వు ఎక్కడికి వెళ్తున్నావు'
assert result[2]['text']==samples[2]['text']
assert not acceptable('Phanendra 10 రాలేదు','Fanendra 4 వచ్చాడు')
stop()

import httpx,time,json
from pathlib import Path
text='కొన్ని క్రియలు ఆబ్జెక్టుల మధ్య తేడాను గుర్తించడానికి ఇది ఒక ముఖ్యమైన మార్గం.'
cues=[{'id':'corrected','start':0,'end':6.72,'text':text}]
def wait(client,jid):
 for _ in range(600):
  job=client.get('/api/jobs/'+jid).json()
  if job['status']=='failed':raise RuntimeError(job['error'])
  if job['status']=='complete':return job['result']
  time.sleep(1)
 raise TimeoutError('Local model took too long')
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as client:
 with Path('work/verification/telugu-delayed.wav').open('rb') as f:
  r=client.post('/api/align',files={'file':('audio.wav',f,'audio/wav')},data={'language':'te','captions':json.dumps(cues,ensure_ascii=False)});r.raise_for_status();aligned=wait(client,r.json()['jobId'])
 print('Aligned:',json.dumps(aligned,ensure_ascii=False),flush=True)
 cue=aligned['cues'][0];assert cue['text']==text and cue['start']>1.8 and 7.5<cue['end']<9
 assert len(cue['words'])==len(text.split())
 r=client.post('/api/translate',json={'cues':aligned['cues'],'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'});r.raise_for_status();tenglish=wait(client,r.json()['jobId'])
 print('Tenglish:',json.dumps(tenglish,ensure_ascii=False),flush=True)
 latin=tenglish['cues'][0];assert latin['timing']=='mapped' and latin['words'] and latin['start']==cue['start'] and latin['end']==cue['end']
 assert any(w['start']>3 for w in latin['words'])
 Path('work/verification/madcut-speech-sync-results.json').write_text(json.dumps({'leadingSilence':2,'trailingSilence':3,'originalIncorrectTimes':cues,'aligned':aligned,'tenglish':tenglish},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Passed: wrong early timing corrected from speech; spelling preserved; Tenglish retained real word anchors.')

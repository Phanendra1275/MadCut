import httpx,time,json
from pathlib import Path
native=json.loads(Path('work/verification/prasad-caption-debug-recognition.json').read_text(encoding='utf-8'))['cues'][:1]
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 r=c.post('/api/translate',json={'cues':native,'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'});r.raise_for_status()
 for _ in range(300):
  job=c.get('/api/jobs/'+r.json()['jobId']).json()
  if job['status']=='failed':raise RuntimeError(job['error'])
  if job['status']=='complete':break
  time.sleep(1)
 cue=job['result']['cues'][0];assert cue['text'].lower()=='mobiles unboxings';assert cue['words'][1]['start']==.94 and cue['words'][1]['end']==2.1,cue
 Path('work/verification/caption-debug-live-final.json').write_text(json.dumps(job['result'],ensure_ascii=False,indent=2),encoding='utf-8');print('Final restarted API passed canonical spelling and native compound-word anchors.')

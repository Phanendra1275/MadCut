import httpx,time,json
from pathlib import Path
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 with Path('work/verification/prasad-problem.wav').open('rb') as f:r=c.post('/api/transcribe',data={'language':'te'},files={'file':('prasad.wav',f,'audio/wav')})
 r.raise_for_status();print('Recognition job',r.json(),flush=True)
 for i in range(600):
  job=c.get('/api/jobs/'+r.json()['jobId']).json()
  if job['status']=='failed':raise RuntimeError(job['error'])
  if job['status']=='complete':break
  time.sleep(1)
 result=job['result'];assert all(len(v['text'].split())<=3 for v in result['cues']);assert 'మొబైల్స్' in ' '.join(v['text'] for v in result['cues']);Path('work/verification/prasad-caption-debug-recognition.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('Recognition passed',len(result['cues']),'short speech groups',flush=True)
 r=c.post('/api/translate',json={'cues':result['cues'],'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'});r.raise_for_status()
 for i in range(600):
  job=c.get('/api/jobs/'+r.json()['jobId']).json()
  if job['status']=='failed':raise RuntimeError(job['error'])
  if job['status']=='complete':break
  time.sleep(1)
 translated=job['result'];Path('work/verification/prasad-caption-debug-tenglish.json').write_text(json.dumps(translated,ensure_ascii=False,indent=2),encoding='utf-8');text=' '.join(v['text'] for v in translated['cues']);assert 'unboxings' in text and 'ivanni' in text,text
 p=json.loads(Path('work/verification/prasad-fixed-project.json').read_text(encoding='utf-8'));p.update(original=result['cues'],tracks={'Telugu':result['cues'],'Tenglish':translated['cues']});p['look']['template']='Left Blur Slide';Path('work/verification/prasad-debug-project.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');print('Tenglish passed:',text,flush=True)

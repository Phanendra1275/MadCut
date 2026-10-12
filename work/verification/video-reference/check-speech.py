import httpx,time,json
from pathlib import Path
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=90) as c:
 with Path('work/verification/video-reference/audio.wav').open('rb') as f:r=c.post('/api/transcribe',data={'language':'auto'},files={'file':('reference.wav',f,'audio/wav')})
 r.raise_for_status();jid=r.json()['jobId'];print('Reference speech check started',flush=True)
 for i in range(500):
  job=c.get('/api/jobs/'+jid).json()
  if job['status']=='failed':
   Path('work/verification/video-reference/recognition.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
   print(job['error'],flush=True);break
  if job['status']=='complete':break
  time.sleep(1)
 Path('work/verification/video-reference/recognition.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(job.get('result',job),ensure_ascii=False),flush=True)

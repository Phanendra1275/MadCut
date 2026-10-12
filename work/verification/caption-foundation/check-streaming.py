import httpx,time,json
from pathlib import Path
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 events=[];start=time.monotonic()
 with Path('work/verification/caption-foundation/streaming-input.mp4').open('rb') as f:r=c.post('/api/transcribe',files={'file':('stream.mp4',f,'video/mp4')},data={'language':'te'})
 r.raise_for_status();jid=r.json()['jobId'];previous=None
 while time.monotonic()-start<1000:
  j=c.get('/api/jobs/'+jid).json();key=(j['status'],j.get('partialRevision'))
  if key!=previous:
   previous=key;e={'seconds':round(time.monotonic()-start,3),'status':j['status'],'progress':j.get('progress'),'partial':len(j.get('partial',{}).get('cues',[])),'preliminary':j.get('partial',{}).get('preliminary')};events.append(e);print(e,flush=True)
  if j['status']=='failed':raise RuntimeError(j['error'])
  if j['status']=='complete':break
  time.sleep(.15)
 else:raise TimeoutError('stream test')
 assert not j['result']['cacheHit'];assert any(e['partial']>0 and e['status']=='running' for e in events)
 Path('work/verification/caption-foundation/streaming-result.json').write_text(json.dumps({'seconds':round(time.monotonic()-start,3),'events':events,'result':j['result']},ensure_ascii=False,indent=2),encoding='utf-8');print('Streaming verified.',flush=True)

import httpx,time,json
from pathlib import Path
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 print(c.get('/api/health').json(),flush=True)
 for label,path in [('delayed','work/verification/telugu-delayed.wav'),('full','C:/Users/HP/Downloads/Prasad Tech.mp4')]:
  start=time.monotonic();events=[];last=-1
  with Path(path).open('rb') as f:r=c.post('/api/transcribe',files={'file':('sample.mp4',f,'video/mp4')},data={'language':'te','tenglishMode':'Natural'})
  r.raise_for_status();jid=r.json()['jobId']
  for _ in range(1600):
   j=c.get('/api/jobs/'+jid).json()
   if j.get('progress',-1)!=last:
    last=j.get('progress',-1);events.append({'seconds':round(time.monotonic()-start,3),'progress':last,'cues':len(j.get('partial',{}).get('cues',[])),'status':j['status']});print(label,events[-1],flush=True)
   if j['status']=='failed':raise RuntimeError(j['error'])
   if j['status']=='complete':break
   time.sleep(.25)
  else:raise TimeoutError('recognition')
  result=j['result'];elapsed=round(time.monotonic()-start,3)
  assert result['cues'] and result['language']=='te'
  for source,target in zip(result['cues'],result['versions']['Tenglish']):
   assert (source['start'],source['end'])==(target['start'],target['end'])
   assert all(source['start']-.001<=w['start']<w['end']<=source['end']+.001 for w in source.get('words',[]))
  if label=='full':assert any(e['status']=='running' and e['cues']>0 and 0<e['progress']<95 for e in events)
  Path('work/verification/quality-live-'+label+'.json').write_text(json.dumps({'elapsedSeconds':elapsed,'events':events,'result':result},ensure_ascii=False,indent=2),encoding='utf-8')
  print(label,'complete',elapsed,'seconds',len(result['cues']),'cues',flush=True)

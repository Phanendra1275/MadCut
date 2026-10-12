import httpx,time,json,sys
from pathlib import Path
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from transcription_scoring import normalize as norm, distance as edit, POLICY
refs=json.loads(Path('work/verification/telugu-heldout-references.json').read_text(encoding='utf-8'))
cases=[(f'reference-{i+1}',r['audio'],r['reference']) for i,r in enumerate(refs)]+[('creator-video','C:/Users/HP/Downloads/Prasad Tech.mp4',None)]
results=[]
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as client:
 print('Health:',client.get('/api/health').json(),flush=True)
 for label,path,reference in cases:
  began=time.monotonic();events=[];first=None;last=None
  with Path(path).open('rb') as f:request=client.post('/api/transcribe',files={'file':(Path(path).name,f,'video/mp4')},data={'language':'te','tenglishMode':'Natural'})
  request.raise_for_status();jid=request.json()['jobId']
  while time.monotonic()-began<1000:
   job=client.get('/api/jobs/'+jid).json()
   state=(job.get('progress'),job.get('partialRevision'),job['status'])
   if state!=last:
    last=state;event={'seconds':round(time.monotonic()-began,3),'progress':job.get('progress'), 'revision':job.get('partialRevision'),'status':job['status'],'partialCues':len(job.get('partial',{}).get('cues',[])),'preliminary':job.get('partial',{}).get('preliminary')};events.append(event);print(label,event,flush=True)
   if first is None and job.get('partial',{}).get('cues'):first=round(time.monotonic()-began,3)
   if job['status']=='failed':raise RuntimeError(job['error'])
   if job['status']=='complete':break
   time.sleep(.2)
  else:raise TimeoutError(label)
  result=job['result'];cues=result['cues'];roman=result['versions']['Tenglish'];assert cues and len(cues)==len(roman)
  for native,latin in zip(cues,roman):
   assert (native['start'],native['end'])==(latin['start'],latin['end']);assert native.get('flow')==latin.get('flow')
   if native.get('words'):assert all(native['start']-.001<=w['start']<w['end']<=native['end']+.001 for w in native['words'])
  assert all(a['end']<=b['start']+.001 for a,b in zip(cues,cues[1:]));assert result['timelineQuality']['wordCount']==len(result['rawTranscript'].split())
  seconds=round(time.monotonic()-began,3);entry={'label':label,'seconds':seconds,'firstPartialSeconds':first,'events':events,'result':result,'accuracyGroundTruth':reference is not None,'scoringPolicy':POLICY}
  if reference:
   source=norm(reference).split();predicted=norm(' '.join(c['text'] for c in cues)).split();entry.update(reference=reference,wordErrors=edit(source,predicted),referenceWords=len(source),WER=round(edit(source,predicted)/len(source)*100,2))
  results.append(entry);Path('work/verification/caption-foundation/live-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print(label,'complete',seconds,'captions',len(cues),'coverage alerts',len(result['timelineQuality']['uncoveredSpeech']),flush=True)
 # Verify repeated upload reuses acoustic work rather than rerunning the model.
 with Path(refs[0]['audio']).open('rb') as f:request=client.post('/api/transcribe',files={'file':('cached.wav',f,'audio/wav')},data={'language':'te'})
 jid=request.json()['jobId'];start=time.monotonic()
 while True:
  j=client.get('/api/jobs/'+jid).json()
  if j['status']=='failed':raise RuntimeError(j['error'])
  if j['status']=='complete':break
  time.sleep(.1)
 assert j['result']['cacheHit'];Path('work/verification/caption-foundation/cache-result.json').write_text(json.dumps({'seconds':round(time.monotonic()-start,3),'result':j['result']},ensure_ascii=False,indent=2),encoding='utf-8');print('Cache verified',flush=True)

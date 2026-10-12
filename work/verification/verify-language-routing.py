import httpx,time,json,sys
from pathlib import Path
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=30) as client:
 results=[]
 for name,language in ([('spoken-english.wav','en')] if len(sys.argv)>1 else [('telugu-heldout-3.wav','auto'),('spoken-english.wav','en')]):
  with Path('work/verification',name).open('rb') as f:
   response=client.post('/api/transcribe',files={'file':(name,f,'audio/wav')},data={'language':language});response.raise_for_status();jid=response.json()['jobId']
  deadline=time.time()+600
  while time.time()<deadline:
   job=client.get('/api/jobs/'+jid).json()
   if job['status']=='failed':raise RuntimeError(job['error'])
   if job['status']=='complete':break
   time.sleep(1)
  else:raise TimeoutError('Speech test timed out')
  result=job['result'];results.append({'requested':language,**result});print(json.dumps(result,ensure_ascii=False),flush=True)
  if language=='auto':assert result['language']=='te' and result['speechEngine']=='Telugu-trained Whisper medium'
  else:
   text=' '.join(c['text'].lower() for c in result['cues']);assert result['language']=='en' and 'college' in text and '10' in text
 Path('work/verification/language-routing-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Passed speech routing checks:',', '.join(r['requested'] for r in results))

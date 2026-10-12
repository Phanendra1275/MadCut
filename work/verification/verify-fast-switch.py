import httpx,time,json
from pathlib import Path
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 with Path('work/verification/telugu-heldout-2.wav').open('rb') as f:
  r=c.post('/api/transcribe',data={'language':'te'},files={'file':('heldout.wav',f,'audio/wav')});r.raise_for_status();jid=r.json()['jobId']
 for _ in range(180):
  j=c.get('/api/jobs/'+jid).json()
  if j['status']=='failed':raise RuntimeError(j['error'])
  if j['status']=='complete':break
  time.sleep(.2)
 else:raise TimeoutError('recognition timed out')
 d=j['result'];assert d['speechDevice']=='cuda' and d['cues']
 for cue in d['cues']:
  assert cue['end']>cue['start'] and all(cue['start']<=w['start']<w['end']<=cue['end']+.001 for w in cue['words'])
 pids=json.loads(Path('outputs/chatcut/.local/runtime-pids.json').read_text());assert not pids['language'] and not pids['translation'] and pids['speech']
 Path('work/verification/fast-heldout-recognition.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Passed switching from optional translation back to GPU speech; native and Tenglish word intervals valid.',flush=True)

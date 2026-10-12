import json,time,httpx
from pathlib import Path
cues=json.loads(Path('work/verification/prasad-recognition-comparison.json').read_text(encoding='utf-8'))['specialized']['cues']
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as client:
 for _ in range(180):
  if client.get('/api/health').json()['configured']:break
  time.sleep(1)
 r=client.post('/api/translate',json={'cues':cues,'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'});r.raise_for_status();jid=r.json()['jobId']
 for _ in range(600):
  job=client.get('/api/jobs/'+jid).json()
  if job['status']=='failed':raise RuntimeError(job['error'])
  if job['status']=='complete':break
  time.sleep(1)
 out=job['result'];print(json.dumps(out,ensure_ascii=False),flush=True)
 first=out['cues'][0];assert 'unboxings' in first['text'].lower() and 'ivanni' in first['text'].lower() and 'ante' in first['text'].lower() and first['timing']=='mapped'
 Path('work/verification/prasad-tenglish-fixed.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 p=json.loads(Path('work/verification/madcut-verified.json').read_text(encoding='utf-8'));p.update(name='Prasad Tech spelling check',language='Tenglish',duration=12,projectId='prasad-verified',original=cues,tracks={'Telugu':cues,'Tenglish':out['cues']});p['look']['template']='Karaoke';p['aspect']='9:16';p['frame']={'scale':100,'width':100,'height':100,'x':0,'y':0,'rotation':0,'background':'#0b0b0d'}
 Path('work/verification/prasad-fixed-project.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Passed actual clip Tenglish generation: conventional spellings and mapped timings.')

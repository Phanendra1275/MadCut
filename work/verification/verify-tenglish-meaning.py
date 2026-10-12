import httpx,time,json
texts=['అతను రాలేదు. నేను 10 నిమిషాల్లో వస్తాను.','నువ్వు ఈరోజు college కి వస్తున్నావా?','ఏంటి బ్రో నువ్వు ఇంకా రాలేదు?','నాకు ఈ వీడియో నచ్చలేదు.']
cues=[{'id':str(i),'start':i*4,'end':i*4+3,'text':t} for i,t in enumerate(texts)]
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=30) as client:
 response=client.post('/api/translate',json={'cues':cues,'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'});response.raise_for_status();job_id=response.json()['jobId']
 deadline=time.time()+300
 while time.time()<deadline:
  job=client.get('/api/jobs/'+job_id).json()
  if job['status']=='failed':raise RuntimeError(job['error'])
  if job['status']=='complete':break
  time.sleep(1)
 else:raise TimeoutError('Local writer timed out')
 result=job['result'];print(json.dumps(result,ensure_ascii=False),flush=True)
 from pathlib import Path
 Path('work/verification/tenglish-meaning-results.json').write_text(json.dumps({'source':texts,**result},ensure_ascii=False,indent=2),encoding='utf-8')
 values=[c['text'].lower() for c in result['cues']]
 assert '10' in values[0] and 'college' in values[1] and 'bro' in values[2]
 assert all('?' in values[i] for i in [1,2])
 assert any(t in values[0] for t in ['raledu','raaledu','raledhu','raaledhu'])
 assert any(t in values[3] for t in ['nachaledu','nacchaledu','nachaledhu','nacchaledhu','nachchaledu','nachchaledhu'])
 print('Passed: negation, numbers, English code-switching and questions.')

import httpx,time,json
from pathlib import Path
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 r=c.post('/api/translate',json={'cues':[{'id':'optional','start':0,'end':3,'text':'నువ్వు ఈరోజు కాలేజీకి వస్తున్నావా?'}],'sourceLanguage':'te','language':'English','tone':'Accurate'});r.raise_for_status();jid=r.json()['jobId']
 for _ in range(180):
  j=c.get('/api/jobs/'+jid).json()
  if j['status']=='failed':raise RuntimeError(j['error'])
  if j['status']=='complete':break
  time.sleep(1)
 else:raise TimeoutError('Optional translation did not finish')
 result=j['result'];assert result['cues'][0]['start']==0 and result['cues'][0]['end']==3
 Path('work/verification/fast-optional-translation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Optional translation passed:',result['cues'][0]['text'])

import httpx,time,json
from pathlib import Path
c=httpx.Client(timeout=30);base='http://127.0.0.1:5173'
for _ in range(90):
 if c.get(base+'/api/health').json()['configured']:break
 time.sleep(1)
def wait(body):
 r=c.post(base+'/api/translate',json=body);r.raise_for_status();jid=r.json()['jobId']
 for _ in range(500):
  j=c.get(base+'/api/jobs/'+jid).json()
  if j['status']=='complete':return j['result']
  if j['status']=='failed':raise RuntimeError(j['error'])
  time.sleep(1)
 raise TimeoutError()
speech=json.loads(Path('work/verification/free-ai-results.json').read_text(encoding='utf-8'))['speech']['cues']
results={}
for lang in ['Hinglish','Tenglish']:
 results[lang]=wait({'cues':speech,'sourceLanguage':'en','language':lang,'tone':'Accurate'})
 print(lang,json.dumps(results[lang],ensure_ascii=False),flush=True)
novel=[{'id':'a','start':0,'end':3,'text':'Please wait 25 minutes. I cannot come tomorrow.'},{'id':'b','start':3,'end':6,'text':'This video is not good. Why are you late?'}]
results['NovelTenglish']=wait({'cues':novel,'sourceLanguage':'en','language':'Tenglish','tone':'Accurate'});print(json.dumps(results['NovelTenglish'],ensure_ascii=False),flush=True)
results['WhatsApp']=wait({'cues':[{'id':'x','start':0,'end':3,'text':'నాకు ఈ వీడియో అస్సలు నచ్చలేదు.'}],'sourceLanguage':'te','language':'Tenglish','tone':'WhatsApp'});print(json.dumps(results['WhatsApp'],ensure_ascii=False),flush=True)
Path('work/verification/final-chat-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

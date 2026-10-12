import httpx,time,json
from pathlib import Path
c=httpx.Client(timeout=30);base='http://127.0.0.1:5173'
def wait(r):
 r.raise_for_status();j=r.json()['jobId']
 for _ in range(600):
  v=c.get(base+'/api/jobs/'+j).json()
  if v['status']=='complete':return v['result']
  if v['status']=='failed':raise RuntimeError(v['error'])
  time.sleep(1)
 raise TimeoutError()
original=[{'id':'a','start':0,'end':3,'text':'Please wait 25 minutes. I cannot come tomorrow.'},{'id':'b','start':3,'end':6,'text':'This video is not good. Why are you late?'}]
results={}
for lang in ['Tenglish','Telugu']:
 results[lang]=wait(c.post(base+'/api/translate',json={'cues':original,'sourceLanguage':'en','language':lang,'tone':'Accurate'}))
 print(json.dumps(results[lang],ensure_ascii=False),flush=True)
with Path('work/verification/spoken-telugu.wav').open('rb') as f:
 result=wait(c.post(base+'/api/transcribe',files={'file':('test.wav',f,'audio/wav')},data={'language':'te'}))
results['TeluguSpeech']=result;print(json.dumps(result,ensure_ascii=False),flush=True)
results['TeluguSpeechTenglish']=wait(c.post(base+'/api/translate',json={'cues':result['cues'],'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'}))
print(json.dumps(results['TeluguSpeechTenglish'],ensure_ascii=False),flush=True)
Path('work/verification/free-novel-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

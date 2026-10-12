import json,time,httpx
from pathlib import Path
base='http://127.0.0.1:5173'
client=httpx.Client(timeout=30)
def wait_job(result):
    jid=result['jobId'];end=time.time()+600;last=''
    while time.time()<end:
        job=client.get(base+'/api/jobs/'+jid).json()
        if job['message']!=last:print(job['message'],flush=True);last=job['message']
        if job['status']=='complete':return job['result']
        if job['status']=='failed':raise RuntimeError(job['error'])
        time.sleep(1)
    raise TimeoutError('Local model test timed out')
with Path('work/verification/spoken-english.wav').open('rb') as f:
    r=client.post(base+'/api/transcribe',files={'file':('speech.wav',f,'audio/wav')},data={'language':'en'})
r.raise_for_status();spoken=wait_job(r.json());print(json.dumps({'transcription':spoken},ensure_ascii=False),flush=True)
results={}
for language in ['Tenglish','Telugu','English','Hindi','Hinglish']:
    r=client.post(base+'/api/translate',json={'cues':spoken['cues'],'sourceLanguage':'en','language':language,'tone':'Accurate'});r.raise_for_status();results[language]=wait_job(r.json())
    print(json.dumps({'language':language,'captions':[c['text'] for c in results[language]['cues']]},ensure_ascii=False),flush=True)
telugu=[{'id':'1','start':0,'end':3,'text':'నువ్వు ఈరోజు కాలేజీకి వస్తున్నావా?'},{'id':'2','start':3,'end':6,'text':'అతను రాలేదు.'},{'id':'3','start':6,'end':9,'text':'రేపు మనం సినిమాకి వెళ్దామా?'}]
r=client.post(base+'/api/translate',json={'cues':telugu,'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'});r.raise_for_status();results['TeluguToTenglish']=wait_job(r.json());print(json.dumps(results['TeluguToTenglish'],ensure_ascii=False),flush=True)
Path('work/verification/free-ai-results.json').write_text(json.dumps({'speech':spoken,'versions':results},ensure_ascii=False,indent=2),encoding='utf-8')


import httpx,time,json
from pathlib import Path
c=httpx.Client(timeout=30)
with Path('work/verification/spoken-telugu.wav').open('rb') as f:
    r=c.post('http://127.0.0.1:8765/api/transcribe',files={'file':('telugu.wav',f,'audio/wav')},data={'language':'te'})
r.raise_for_status();jid=r.json()['jobId'];print('Telugu speech check started',flush=True)
while True:
    job=c.get('http://127.0.0.1:8765/api/jobs/'+jid).json()
    if job['status'] in ['complete','failed']:break
    time.sleep(1)
Path('work/verification/telugu-recognition.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(job,ensure_ascii=False),flush=True)

import httpx,time,json
from pathlib import Path
out={}
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 def job(path,**kwargs):
  started=time.perf_counter();r=c.post(path,**kwargs);r.raise_for_status();jid=r.json()['jobId']
  for _ in range(1800):
   d=c.get('/api/jobs/'+jid).json()
   if d['status']=='failed':raise RuntimeError(d['error'])
   if d['status']=='complete':return d['result'],round(time.perf_counter()-started,3)
   time.sleep(.2)
  raise RuntimeError('timeout')
 print('Ready:',c.get('/api/health').json(),flush=True)
 for label,path in [('first','work/verification/prasad-problem.mp4'),('repeat','work/verification/prasad-problem.mp4'),('warm_new','work/verification/prasad-frame-test.mp4')]:
  with Path(path).open('rb') as f:result,elapsed=job('/api/transcribe',data={'language':'te'},files={'file':(Path(path).name,f,'video/mp4')})
  assert 'srt' in result and 'Tenglish' in result['versions'];assert result['cacheHit']==(label=='repeat'),result['cacheHit']
  assert all(cue['start']==source['start'] and cue['end']==source['end'] for cue,source in zip(result['versions']['Tenglish'],result['cues']))
  if label!='warm_new':assert 'unboxings' in ' '.join(v['text'] for v in result['versions']['Tenglish'])
  out[label]={'elapsedSeconds':elapsed,'processingSeconds':result['processingSeconds'],'cacheHit':result['cacheHit'],'device':result['speechDevice'],'cues':result['cues'],'tenglish':result['versions']['Tenglish']}
  Path('work/verification/fast-pipeline-final-benchmark.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(label,elapsed,'seconds',len(result['cues']),'cues',flush=True)
  if label=='first':Path('work/verification/fast-source.srt').write_text(result['srt'],encoding='utf-8')
 result,elapsed=job('/api/translate',json={'cues':out['first']['cues'],'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'})
 out['tenglishConversionSeconds']=elapsed;assert result['pipeline']=='timed-subtitles-to-tenglish'
 pids=json.loads(Path('outputs/chatcut/.local/runtime-pids.json').read_text());assert pids['language'] is None and pids['translation'] is None and pids['speech']
 out['residentSpeechPid']=pids['speech'];out['languageModelsLoaded']=False
 Path('work/verification/fast-pipeline-final-benchmark.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('Tenglish conversion',elapsed,'seconds, no language models loaded.',flush=True)

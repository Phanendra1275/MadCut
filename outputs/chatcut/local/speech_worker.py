import json,sys,gc
import speech_engine as engine
from pathlib import Path
from speech_engine import recognize,align_transcript

def run(request):
 evidence={}
 def progress(cues,processed,duration,detected):
  print(json.dumps({'event':'progress','cues':cues,'processedSeconds':round(processed,3),'duration':round(duration,3),'language':detected,**evidence},ensure_ascii=False),flush=True)
 def operation():
  if request.get('alignment') is not None:return align_transcript(Path(request['path']),request['alignment'],request['language'])
  return recognize(Path(request['path']),request['language'],request.get('terms',''),apply_spellings=False,on_progress=progress if request.get('stream') else None,on_evidence=evidence.update)
 try:return operation()
 except RuntimeError as exc:
  if engine._warm_device!='cuda' or not any(word in str(exc).lower() for word in ['cuda','cublas','cudnn','out of memory','allocation']):raise
  engine.CONFIG['speech_device']='cpu';engine._warm_model=None;gc.collect()
  return operation()

if sys.argv[1]=='--serve':
 for line in sys.stdin:
  try:response={'result':run(json.loads(line))}
  except Exception as exc:response={'error':str(exc) or 'Speech recognition failed.'}
  print(json.dumps(response,ensure_ascii=False),flush=True)
else:
 try:
  if sys.argv[1]=='--align':result=align_transcript(Path(sys.argv[2]),json.loads(Path(sys.argv[3]).read_text(encoding='utf-8')),sys.argv[4])
  else:result=recognize(Path(sys.argv[1]),sys.argv[2],sys.argv[3] if len(sys.argv)>3 else '')
  print(json.dumps(result,ensure_ascii=False))
 except ValueError as exc:
  print(json.dumps({'error':str(exc)},ensure_ascii=False));raise SystemExit(1)

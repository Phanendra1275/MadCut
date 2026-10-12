import sys,json,gc
from pathlib import Path
sys.path.insert(0,'outputs/chatcut/local')
import speech_engine as s
out={}
for engine in ['specialized','multilingual']:
 if engine=='multilingual':s.CONFIG['telugu_speech_model']=None
 out[engine]=s.recognize(Path('work/verification/prasad-problem.wav'),'te')
 Path('work/verification/prasad-recognition-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(engine,json.dumps(out[engine],ensure_ascii=False),flush=True);gc.collect()

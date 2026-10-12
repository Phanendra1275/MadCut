import gc,json,time,os
from pathlib import Path
from faster_whisper import WhisperModel
os.environ['HF_HUB_OFFLINE']='1'
h=Path.home()/'.cache/huggingface/hub';out={}
for name in ['medium','large-v3']:
 p=next(p.parent for p in h.glob('models--Systran--faster-whisper-'+name+'/snapshots/*/model.bin'))
 started=time.monotonic();print('Checking Whisper '+name,flush=True)
 model=WhisperModel(str(p),device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
 segments,info=model.transcribe('work/verification/spoken-telugu.wav',language='te',beam_size=5,word_timestamps=True,vad_filter=True,condition_on_previous_text=False)
 text=' '.join(s.text.strip() for s in segments)
 out[name]={'text':text,'seconds':round(time.monotonic()-started,2)}
 print(json.dumps({name:out[name]},ensure_ascii=False),flush=True)
 del model;gc.collect()
Path('work/verification/speech-model-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')

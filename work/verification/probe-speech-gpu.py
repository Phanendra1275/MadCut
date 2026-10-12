import os,json,time,sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
root=Path('outputs/chatcut').resolve();dll=root/'.local/runtime/cuda-python/nvidia/cublas/bin';os.environ['PATH']=str(dll)+os.pathsep+os.environ['PATH'];handle=os.add_dll_directory(str(dll))
from faster_whisper import WhisperModel
started=time.perf_counter();m=WhisperModel(str(root/'.local/models/whisper-telugu-medium'),device='cuda',compute_type='int8_float16',local_files_only=True,cpu_threads=6);print('CUDA model loaded',time.perf_counter()-started,flush=True)
segments,_=m.transcribe('work/verification/prasad-frame-test.mp4',language='te',beam_size=5,word_timestamps=False,without_timestamps=True,condition_on_previous_text=False)
print('CUDA result',[(s.text,len(s.tokens)) for s in segments],time.perf_counter()-started,flush=True)

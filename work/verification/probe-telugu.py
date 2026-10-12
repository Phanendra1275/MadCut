import os,time
os.environ['HF_HUB_OFFLINE']='1'
from faster_whisper import WhisperModel
p='outputs/chatcut/.local/models/whisper-telugu-medium';t=time.time();print('Loading Telugu model',flush=True)
m=WhisperModel(p,device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True);print('Loaded',round(time.time()-t,2),flush=True)
segments,info=m.transcribe('work/verification/telugu-heldout-2.wav',language='te',task='transcribe',beam_size=1,without_timestamps=True,word_timestamps=False,vad_filter=True,temperature=0.0,condition_on_previous_text=False)
for s in segments:print('TEXT',s.text,'Seconds',round(time.time()-t,2),flush=True)

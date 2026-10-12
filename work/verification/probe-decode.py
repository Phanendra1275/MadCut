import os,json,time
os.environ['HF_HUB_OFFLINE']='1'
from faster_whisper import WhisperModel
class InspectModel(WhisperModel):
 def generate_with_fallback(self,encoder,prompt,tokenizer,options):
  result=super().generate_with_fallback(encoder,prompt,tokenizer,options)
  tokens=result[0].sequences_ids[0]
  print(json.dumps({'maxLength':self.max_length,'promptLength':len(prompt),'tokenCount':len(tokens),'special':[t for t in tokens if t>=tokenizer.eot],'tail':tokens[-20:],'text':tokenizer.decode(tokens)},ensure_ascii=False),flush=True)
  return result
m=InspectModel('outputs/chatcut/.local/models/whisper-telugu-medium',device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
segments,info=m.transcribe('work/verification/telugu-heldout-1.wav',language='te',task='transcribe',beam_size=1,without_timestamps=True,word_timestamps=False,vad_filter=False,temperature=0.0,condition_on_previous_text=False)
for s in segments:print(s.text,flush=True)

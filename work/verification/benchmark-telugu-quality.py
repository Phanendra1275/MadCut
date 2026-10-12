import json,os,sys,time
from pathlib import Path
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from speech_engine import load_model,caption_segments,telugu_segments
from transcription_scoring import normalize, distance, POLICY
from faster_whisper.audio import decode_audio
mode=sys.argv[1];config=json.loads(Path('outputs/chatcut/.local/config.json').read_text(encoding='utf-8-sig'))
path=Path('outputs/chatcut/.local/models/whisper-telugu-medium') if mode!='baseline' else Path(config['whisper_model'])
refs=json.loads(Path('work/verification/telugu-heldout-references.json').read_text(encoding='utf-8'))
print('Testing',mode,flush=True);model=load_model(path);results=[];word_errors=words=char_errors=chars=0
for sample in refs:
 start=time.monotonic();audio=decode_audio(sample['audio'],sampling_rate=16000)
 if mode=='fixed':segments=telugu_segments(model,audio)
 else:segments,info=model.transcribe(audio,language='te',task='transcribe',beam_size=5,temperature=0.0,word_timestamps=True,without_timestamps=mode=='tuned',vad_filter=True,condition_on_previous_text=mode=='tuned')
 segments=list(segments);cues=caption_segments(segments,len(audio)/16000) if mode!='baseline' else None
 text=' '.join(c['text'] for c in cues) if cues is not None else ' '.join(s.text.strip() for s in segments)
 ref=normalize(sample['reference']);prediction=normalize(text)
 we=distance(ref.split(),prediction.split());ce=distance(ref.replace(' ',''),prediction.replace(' ',''));word_errors+=we;words+=len(ref.split());char_errors+=ce;chars+=len(ref.replace(' ',''))
 r={'id':sample['id'],'audio':sample['audio'],'reference':sample['reference'],'text':text,'wordErrors':we,'referenceWords':len(ref.split()),'characterErrors':ce,'referenceCharacters':len(ref.replace(' ','')),'seconds':round(time.monotonic()-start,2),'cues':cues}
 results.append(r);print(json.dumps(r,ensure_ascii=False),flush=True)
summary={'mode':mode,'scoringPolicy':POLICY,'wordErrors':word_errors,'referenceWords':words,'WER':round(word_errors/words*100,2),'CER':round(char_errors/chars*100,2),'samples':results}
Path(f'work/verification/telugu-quality-benchmark-{mode}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='samples'}),flush=True)

"""Local speech recognition with Telugu-specific weights and faithful text alignment."""
from __future__ import annotations
import gc
import os
import sys
import json
import re
import unicodedata
import uuid
import numpy as np
from spelling_profile import correct_native
from speech_quality import quality,decode_reasons,retry_better,audit
from transcription_scoring import normalize as scoring_normalize
from types import SimpleNamespace
from pathlib import Path
_cuda_handles=[]
_cuda_runtime=Path(__file__).resolve().parent.parent/'.local/runtime/cuda-python/nvidia/cublas/bin'
if _cuda_runtime.is_dir():
    os.environ['PATH']=str(_cuda_runtime)+os.pathsep+os.environ.get('PATH','')
    if hasattr(os,'add_dll_directory'):_cuda_handles.append(os.add_dll_directory(str(_cuda_runtime)))
import ctranslate2
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from faster_whisper.audio import pad_or_trim
from faster_whisper.tokenizer import Tokenizer
from faster_whisper.vad import get_speech_timestamps, VadOptions

ROOT=Path(__file__).resolve().parent.parent
CONFIG=json.loads((ROOT/'.local/config.json').read_text(encoding='utf-8-sig'))

def clean(text):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFC',text)).strip()

def compact(text):
    return re.sub(r'\s+','',unicodedata.normalize('NFC',text))

def speech_onset(audio):
    """Find a conservative first phoneme, rather than highlighting leading silence.

    VAD locates speech; energy before its onset retains quiet consonants that
    VAD alone can miss. This changes timing only, never trims recognition audio.
    """
    spans=get_speech_timestamps(audio,VadOptions(min_silence_duration_ms=200,speech_pad_ms=0,threshold=.35))
    if not spans:return None
    detected=spans[0]['start']/16000
    begin=max(0,int((detected-.8)*16000));end=min(len(audio),int((detected+.2)*16000))
    samples=audio[begin:end];frames=len(samples)//320
    if frames<3:return None
    rms=np.sqrt(np.mean(samples[:frames*320].reshape(-1,320)**2,axis=1))
    floor=float(np.percentile(rms,20));peak=float(rms.max())
    if peak<max(.006,floor*6):return None
    threshold=max(.003,floor*4,peak*.04)
    for i in range(len(rms)-1):
        if rms[i]>=threshold and rms[i+1]>=threshold:
            return max(0,begin/16000+i*.02-.04)
    return None

def speech_offset(audio):
    """Retain quiet final consonants, but avoid holding text through trailing silence."""
    spans=get_speech_timestamps(audio,VadOptions(min_silence_duration_ms=200,speech_pad_ms=0,threshold=.35))
    if not spans:return None
    detected=spans[-1]['end']/16000
    begin=max(0,int((detected-.2)*16000));end=min(len(audio),int((detected+.8)*16000))
    samples=audio[begin:end];frames=len(samples)//320
    if frames<3:return None
    rms=np.sqrt(np.mean(samples[:frames*320].reshape(-1,320)**2,axis=1))
    floor=float(np.percentile(rms,20));peak=float(rms.max())
    if peak<max(.006,floor*6):return None
    threshold=max(.003,floor*4,peak*.04)
    for i in range(len(rms)-1,0,-1):
        if rms[i]>=threshold and rms[i-1]>=threshold:return min(len(audio)/16000,begin/16000+(i+1)*.02+.06)
    return None

def refine_last_offset(audio,cues,offset=0):
    if not cues or not cues[-1].get('words'):return
    last=cues[-1]['words'][-1]
    begin=max(0,round((last['start']-offset-.4)*16000));finish=min(len(audio),round((last['end']-offset+.2)*16000))
    ending=speech_offset(audio[begin:finish])
    if ending is None:return
    ending=round(offset+begin/16000+ending,3)
    if last['start']<ending<last['end']-.25:
        last['end']=ending;cues[-1]['end']=ending
        cues[-1]['boundaryRefinement']='trailing-silence'

def refine_first_onset(audio,cues,offset=0):
    if not cues or not cues[0].get('words'):return
    onset=speech_onset(audio)
    if onset is None:return
    first=cues[0]['words'][0];onset=round(offset+onset,3)
    if first['start']<onset<first['end']:
        first['start']=onset;cues[0]['start']=onset

def aligned_written_words(segment):
    """Keep written word boundaries even when alignment tokens split a Telugu word."""
    text=clean(segment.text)
    raw=list(segment.words or [])
    if not raw or compact(''.join(w.word for w in raw))!=compact(text):return None
    spans=[];cursor=0
    for w in raw:
        length=len(compact(w.word))
        if length:spans.append((cursor,cursor+length,w.start,w.end));cursor+=length
    result=[];cursor=0
    for word in text.split():
        end=cursor+len(compact(word))
        parts=[p for p in spans if p[0]<end and p[1]>cursor]
        if not parts:return None
        first,last=parts[0],parts[-1]
        start_time=first[2]+(first[3]-first[2])*(cursor-first[0])/(first[1]-first[0])
        end_time=last[2]+(last[3]-last[2])*(end-last[0])/(last[1]-last[0])
        if end_time<=start_time:return None
        contributing=[w for w in raw if compact(w.word) and w.start<end_time-1e-6 and w.end>start_time+1e-6]
        scores=[getattr(w,'probability',getattr(w,'confidence',None)) for w in contributing]
        evidence={'confidence':round(min(scores),3)} if scores and all(isinstance(v,(int,float)) and np.isfinite(v) for v in scores) else {}
        if cursor!=first[0] or end!=last[1]:evidence['timing']='estimated'
        result.append({'word':word,'start':max(0,round(start_time,3)),'end':round(end_time,3),**evidence})
        cursor=end
    return result

def caption_segments(segments,duration,on_progress=None):
    """Retain each decoded utterance and its real word anchors for later grouping."""
    cues=[]
    for segment in segments:
        text=clean(segment.text)
        if not text:continue
        words=aligned_written_words(segment)
        start=max(0,words[0]['start'] if words else segment.start,cues[-1]['end'] if cues else 0)
        end=min(duration,words[-1]['end'] if words else segment.end)
        if end<=start:
            if cues:
                cues[-1]['text']+=' '+text;cues[-1].pop('words',None)
                cues[-1].update(needsReview=True,reviewReasons=['unresolved-word-timing'])
            continue
        cue={'id':str(uuid.uuid4()),'start':round(start,3),'end':round(end,3),'text':text,'segment':{'start':round(segment.start,3),'end':round(segment.end,3)},'recognitionQuality':quality(segment),'reviewReasons':decode_reasons(segment),'acousticRetry':getattr(segment,'acoustic_retry','not-needed')}
        cue['alignmentWords']=[{'word':w.word,'start':w.start,'end':w.end,
                                **({'confidence':getattr(w,'probability',getattr(w,'confidence',None))} if isinstance(getattr(w,'probability',getattr(w,'confidence',None)),(int,float)) else {})}
                               for w in (segment.words or [])]
        if words:
            bounded=[{**w,'start':max(start,w['start']),'end':min(end,w['end'])} for w in words]
            valid=all(w['end']>w['start'] and (not i or w['start']>=bounded[i-1]['end']-.001) for i,w in enumerate(bounded))
            if valid:
                cue['words']=bounded
                if bounded!=words:cue.update(rawWords=words,alignmentRepair='segment-overlap-clamp',needsReview=True)
                if any(w.get('timing')=='estimated' for w in bounded):
                    cue.update(timing='estimated',needsReview=True)
                    cue['reviewReasons'].append('interpolated-asr-word-boundary')
                if all('confidence' in w for w in bounded):cue['confidence']=round(sum(w['confidence'] for w in bounded)/len(bounded),3)
        audit(cue);cues.append(cue)
        if on_progress:on_progress(cues,min(duration,max(segment.end,end)),duration)
        if len(cues)>500:raise ValueError('Use a shorter video: up to 500 speech segments.')
    return cues

_warm_model=None
_warm_path=None
_warm_device=None

def load_model(path):
    global _warm_model,_warm_path,_warm_device
    path=str(path)
    if _warm_model is None or _warm_path!=path:
        _warm_model=None;gc.collect()
        device='cuda' if CONFIG.get('speech_device','auto')!='cpu' and _cuda_runtime.is_dir() and ctranslate2.get_cuda_device_count()>0 else 'cpu'
        try:_warm_model=WhisperModel(path,device=device,compute_type='int8_float16' if device=='cuda' else 'int8',cpu_threads=6,num_workers=1,local_files_only=True)
        except RuntimeError:
            if device!='cuda':raise
            device='cpu';_warm_model=WhisperModel(path,device='cpu',compute_type='int8',cpu_threads=6,num_workers=1,local_files_only=True)
        _warm_device=device
        _warm_path=path
    return _warm_model


def join_recovery_windows(left,right):
    # Identical adjacent words can be an intentional spoken repetition.
    # Only collapse a duplicate whose measured intervals substantially overlap.
    if left and right and left[-1].words and right[0].words:
        a=left[-1].words[-1];b=right[0].words[0]
        key=lambda t:scoring_normalize(t)
        overlap=min(a.end,b.end)-max(a.start,b.start)
        shorter=min(a.end-a.start,b.end-b.start)
        if key(a.word)==key(b.word) and shorter>0 and overlap/shorter>=.5:
            right[0].words=right[0].words[1:]
            right[0].text=' '.join(w.word for w in right[0].words)
            if not right[0].words:right=right[1:]
    return left+right

def telugu_segments(model,audio,terms='',stats=None,speech_spans=None):
    """Decode each speech window once, then align its fixed text separately.

    This model was trained without timestamp tokens. Letting word alignment
    control decoding's next seek re-recognizes trailing silence as extra words.
    Alignment must never decide which audio is recognized a second time.
    """
    chunks=get_speech_timestamps(audio,VadOptions(min_silence_duration_ms=400,speech_pad_ms=500,max_speech_duration_s=10)) if speech_spans is None else [{'start':max(0,round(s['start']*16000)-8000),'end':min(len(audio),round(s['end']*16000)+8000)} for s in speech_spans]
    # A quiet final syllable can fall below VAD's threshold. For short clips,
    # speech detection is a silence gate, not permission to trim the utterance.
    if chunks and len(audio)<=14*16000:chunks=[{'start':0,'end':len(audio)}]
    windows=[]
    for chunk in chunks:
        if windows and (chunk['start']<=windows[-1]['end'] or ((chunk['end']-windows[-1]['start'])/16000<=12 and (chunk['start']-windows[-1]['end'])/16000<=2)):
            windows[-1]['end']=chunk['end']
        else:windows.append(dict(chunk))
    def inference_windows(start,end,keep_start,keep_end):
        """Plan bounded acoustic work before decoding, so long speech streams.

        These are inference windows, not caption boundaries. Context overlaps
        are assigned to one side by measured word centers after alignment.
        """
        while end-start>12*16000:
            a=start+8*16000;b=min(end-16000,start+11*16000)
            samples=audio[a:b];n=len(samples)//1600
            energy=np.mean(samples[:n*1600].reshape(n,1600)**2,axis=1) if n else []
            boundary=a+(int(np.argmin(energy))*1600+800 if n else 0)
            yield start,boundary+4000,keep_start,min(keep_end,boundary/16000)
            start=boundary-4000;keep_start=max(keep_start,boundary/16000)
        yield start,end,keep_start,keep_end
    tokenizer=Tokenizer(model.hf_tokenizer,model.model.is_multilingual,task='transcribe',language='te')
    retry_budget=2
    if stats is None:stats={}
    stats.update(decodedWindows=0,acousticRetries=0,recoverySplits=0)
    def decode_window(start,end,keep_start,keep_end,depth=0):
        nonlocal retry_budget
        if end-start>12*16000:
            # Bound acoustic inference, not caption display duration. Pick the
            # quietest 100 ms near the end of the window, then retain padding.
            a=start+8*16000;b=min(end-16000,start+11*16000)
            samples=audio[a:b];n=len(samples)//1600
            energy=np.mean(samples[:n*1600].reshape(n,1600)**2,axis=1) if n else []
            boundary=a+(int(np.argmin(energy))*1600+800 if n else 0)
            left=decode_window(start,boundary+4000,keep_start,min(keep_end,boundary/16000),depth)
            right=decode_window(boundary-4000,end,max(keep_start,boundary/16000),keep_end,depth)
            return join_recovery_windows(left,right)
        stats['decodedWindows']+=1
        offset=start/16000
        speech=audio[start:end]
        # Reuse the exact acoustic encoding used for decoding. Re-encoding the
        # same window for word alignment adds latency without new evidence.
        encoded=[];original_encode=model.encode
        def capture(features):
            value=original_encode(features);encoded.append(value);return value
        model.encode=capture
        try:
            decoded,_=model.transcribe(speech,language='te',task='transcribe',beam_size=5,temperature=0.0,word_timestamps=False,without_timestamps=True,vad_filter=False,condition_on_previous_text=False,initial_prompt=terms.strip() or None)
            decoded=list(decoded)
        finally:model.encode=original_encode
        if not decoded:return []
        capped=any(len([t for t in s.tokens if t<tokenizer.eot])>=220 or '\ufffd' in s.text for s in decoded)
        retry_status='not-needed'
        if not capped and any(decode_reasons(s) for s in decoded) and retry_budget>0:
            retry_budget-=1;stats['acousticRetries']+=1;retry_status='original-preserved'
            # Reuse the same encoder state; retry only the decoder, twice at most
            # per upload. Never replace healthy speech or trust a score alone.
            original_encode=model.encode
            if len(encoded)==1:model.encode=lambda features:encoded[0]
            try:
                retry,_=model.transcribe(speech,language='te',task='transcribe',beam_size=8,temperature=0.0,word_timestamps=False,without_timestamps=True,vad_filter=False,condition_on_previous_text=False,initial_prompt=terms.strip() or None)
                retry=list(retry)
                if retry_better(decoded,retry,terms):decoded=retry;retry_status='accepted'
            finally:model.encode=original_encode
        # CT2 reserves half of Whisper's 448 positions, even without timestamps.
        # Telugu byte tokens can hit this ceiling in less than ten seconds.
        # Recognize smaller overlapping windows instead of saving a cut sentence.
        capped=any(len([t for t in s.tokens if t<tokenizer.eot])>=220 or '\ufffd' in s.text for s in decoded)
        # Keep authoritative decoded text; reuse those exact tokens for timing.
        aligned=[{'seek':0,'start':s.start,'end':s.end,'tokens':s.tokens} for s in decoded]
        features=model.feature_extractor(speech)
        encoder=encoded[0] if len(encoded)==1 else model.encode(pad_or_trim(features))
        model.add_word_timestamps([aligned],tokenizer,encoder,min(features.shape[-1]-1,model.feature_extractor.nb_max_frames),"\"'“¿([{-","\"'.。,，!！?？:：”)]}、",0)
        if capped:
            stats['recoverySplits']+=1
            if depth>=5 or end-start<16000:raise ValueError('Speech is too dense to decode fully. Split the video into shorter clips and generate again.')
            midpoint=(start+end)/2
            # Prefer a recognized word boundary so neither half cuts a syllable.
            candidates=[offset+w['end'] for s in aligned for w in s.get('words',[]) if .25*(end-start)/16000<w['end']<.75*(end-start)/16000]
            boundary=round((min(candidates,key=lambda t:abs(t-midpoint/16000)) if candidates else midpoint/16000)*16000)
            overlap=4000
            left=decode_window(start,min(end,boundary+overlap),keep_start,min(keep_end,boundary/16000),depth+1)
            right=decode_window(max(start,boundary-overlap),end,max(keep_start,boundary/16000),keep_end,depth+1)
            # Adjacent window alignment can place the same boundary word on both
            # sides. Collapse only the identical word at this known seam.
            return join_recovery_windows(left,right)
        result=[]
        for original,timed in zip(decoded,aligned):
            words=[SimpleNamespace(**{**w,'start':offset+w['start'],'end':offset+w['end']}) for w in timed.get('words',[])]
            segment=SimpleNamespace(text=original.text,start=offset+original.start,end=min(end/16000,offset+original.end),words=words,avg_logprob=original.avg_logprob,compression_ratio=original.compression_ratio,no_speech_prob=original.no_speech_prob,acoustic_retry=retry_status)
            # At a recovery seam, retain complete written words by their aligned
            # center. Text outside a seam is always kept verbatim.
            if keep_start>offset or keep_end<end/16000:
                written=aligned_written_words(segment)
                if not written:
                    # Bad overlap alignment must not abort the whole video. Decode
                    # this retained interval without padding so authoritative text
                    # survives; caption_segments flags absent word timing.
                    a=max(start,round(keep_start*16000));b=min(end,round(keep_end*16000))
                    if a>=b:return []
                    return decode_window(a,b,a/16000,b/16000,depth+1)
                selected=[w for w in written if keep_start<=(w['start']+w['end'])/2<keep_end]
                if not selected:continue
                segment=SimpleNamespace(text=' '.join(w['word'] for w in selected),start=max(keep_start,selected[0]['start']),end=min(keep_end,selected[-1]['end']),words=[SimpleNamespace(**w) for w in selected],avg_logprob=original.avg_logprob,compression_ratio=original.compression_ratio,no_speech_prob=original.no_speech_prob,acoustic_retry=retry_status)
            result.append(segment)
        if result and result[0].words:
            written=aligned_written_words(result[0]);onset=speech_onset(speech)
            if written and onset is not None and written[0]['start']<offset+onset<written[0]['end']:
                written[0]['start']=round(offset+onset,3)
                result[0].start=written[0]['start'];result[0].words=[SimpleNamespace(**w) for w in written]
        return result
    for window in windows:
        for start,end,keep_start,keep_end in inference_windows(window['start'],window['end'],window['start']/16000,window['end']/16000):
            yield from decode_window(start,end,keep_start,keep_end)

def recognize(path,language,terms='',apply_spellings=True,on_progress=None,on_evidence=None):
    audio=decode_audio(str(path),sampling_rate=16000)
    # Preserve the original waveform except invalid samples, clipping and DC.
    audio=np.clip(np.nan_to_num(audio,nan=0,posinf=1,neginf=-1),-1,1).astype(np.float32)
    dc=float(audio.mean()) if len(audio) else 0
    if abs(dc)>.005:audio=np.clip(audio-dc,-1,1).astype(np.float32)
    spans=get_speech_timestamps(audio,VadOptions(min_silence_duration_ms=400,speech_pad_ms=0,threshold=.35))
    speech_spans=[{'start':round(s['start']/16000,3),'end':round(s['end']/16000,3)} for s in spans]
    evidence={'duration':round(len(audio)/16000,3),'speechSpans':speech_spans,'preprocessing':{'sampleRate':16000,'channels':1,'dcOffsetRemoved':round(dc,6) if abs(dc)>.005 else 0}}
    if on_evidence:on_evidence(evidence)
    model=None;probability=None
    if language=='auto':
        detector_path=CONFIG.get('speech_detector_model',CONFIG['whisper_model'])
        detector=load_model(detector_path)
        language,probability,_=detector.detect_language(audio,vad_filter=True,language_detection_segments=3,language_detection_threshold=.65)
        del detector;gc.collect()
        if probability<.55 or language not in {'te','hi','en'}:
            # Regional speech can be ambiguous to the lightweight detector.
            # Use the already installed multilingual model for a second opinion.
            detector=load_model(CONFIG['whisper_model'])
            language,probability,_=detector.detect_language(audio,vad_filter=True,language_detection_segments=3,language_detection_threshold=.65)
            del detector;gc.collect()
        if probability<.55:raise ValueError('Spoken language is uncertain. Choose the actual spoken language: Telugu, Hindi, or English, and generate again.')
        if language not in {'te','hi','en'}:
            name={'ta':'Tamil','ml':'Malayalam','kn':'Kannada','bn':'Bengali','mr':'Marathi'}.get(language,language)
            raise ValueError(f'Detected {name} speech ({probability:.0%} confidence). MadCut currently supports Telugu, Hindi and English. This video can be used for visual styling, but do not force it into Telugu captions.')
    specialized=language=='te' and CONFIG.get('telugu_speech_model')
    model_path=CONFIG['telugu_speech_model'] if specialized else CONFIG['whisper_model']
    model=load_model(model_path)
    stats={}
    if specialized:
        segments=telugu_segments(model,audio,terms,stats,speech_spans)
        detected='te'
    else:
        segments,info=model.transcribe(audio,language=language,task='transcribe',beam_size=5,temperature=0.0,word_timestamps=True,vad_filter=True,vad_parameters={'min_silence_duration_ms':400,'speech_pad_ms':200},condition_on_previous_text=True,initial_prompt=terms.strip() or None)
        detected=info.language
    cues=caption_segments(segments,len(audio)/16000,(lambda c,t,d:on_progress(c,t,d,detected)) if on_progress else None)
    refine_first_onset(audio,cues)
    refine_last_offset(audio,cues)
    if detected=='te' and apply_spellings:correct_native(cues)
    return {'language':detected,'cues':cues,'speechEngine':'Telugu-trained Whisper medium' if specialized else 'Whisper large-v3','languageProbability':probability,'speechDevice':_warm_device,'recognitionStats':stats,**evidence,'rawTranscript':' '.join(c['text'] for c in cues)}

def align_transcript(path,cues,language):
    """Align corrected native text to audio without re-recognizing or rewriting it."""
    audio=decode_audio(str(path),sampling_rate=16000);duration=len(audio)/16000
    model=load_model(CONFIG['whisper_model'])
    tokenizer=Tokenizer(model.hf_tokenizer,model.model.is_multilingual,task='transcribe',language=language)
    groups=[];group=[];count=0
    for cue in cues:
        tokens=tokenizer.encode(' '+cue['text'].strip())
        if len(tokens)>400:raise ValueError('Split very long captions before syncing speech timing.')
        if group and (cue['end']-group[0][0]['start']>26 or count+len(tokens)>400):groups.append(group);group=[];count=0
        group.append((cue,tokens));count+=len(tokens)
    if group:groups.append(group)
    output=[]
    for group in groups:
        group_start=len(output)
        begin=max(0,group[0][0]['start']-.6);end=min(duration,group[-1][0]['end']+.6)
        if len(groups)==1 and duration<=28:begin=0;end=duration
        if end<=begin:raise ValueError('Caption times must fall within the video.')
        speech=audio[round(begin*16000):round(end*16000)]
        features=model.feature_extractor(speech);encoder=model.encode(pad_or_trim(features))
        timed=[{'seek':0,'start':c['start']-begin,'end':c['end']-begin,'tokens':t} for c,t in group]
        model.add_word_timestamps([timed],tokenizer,encoder,min(features.shape[-1]-1,model.feature_extractor.nb_max_frames),"\"'“¿([{-","\"'.。,，!！?？:：”)]}、",0)
        for (original,_),aligned in zip(group,timed):
            raw=[SimpleNamespace(**{**w,'start':begin+w['start'],'end':begin+w['end']}) for w in aligned.get('words',[])]
            words=aligned_written_words(SimpleNamespace(text=original['text'],words=raw))
            if not words:raise ValueError('Could not reliably align this caption. Check that the text matches the spoken language and wording.')
            start=max(0,output[-1]['end'] if output else 0,words[0]['start']);finish=min(duration,words[-1]['end'])
            if finish<=start:raise ValueError('Could not reliably align this caption. Check the spoken wording.')
            output.append({'id':original['id'],'text':original['text'],'start':round(start,3),'end':round(finish,3),'words':words})
        refine_first_onset(speech,output[group_start:],begin)
        refine_last_offset(speech,output[group_start:],begin)
    return {'language':language,'cues':output,'speechEngine':'Whisper large-v3 forced alignment','speechDevice':_warm_device}

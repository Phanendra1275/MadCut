"""Timed STT subtitles are the source of truth; Latin spelling reuses anchors."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import re,json
from chat_spelling import hint
from spelling_profile import roman_words

from natural_tenglish import generate
@lru_cache(maxsize=2048)
def romanize(text,mode,context,glossary):
    return generate(text,mode,context,json.loads(glossary))

from caption_timing import safe_tenglish, speech_words

def timestamp(value):
    ms=max(0,round(value*1000));hours,ms=divmod(ms,3600000);minutes,ms=divmod(ms,60000);seconds,ms=divmod(ms,1000)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}'

def srt(cues):
    return '\n'.join(f"{i+1}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues))

def fast_tenglish(cues,mode='Natural',emojis=False):
    if mode not in {'Natural','WhatsApp','Formal'}:raise ValueError('Choose Natural, WhatsApp or Formal Tenglish.')
    glossary=json.dumps(roman_words(),ensure_ascii=False,sort_keys=True)
    def convert(item):
        i,original=item;context=' '.join(c['text'] for c in cues[max(0,i-1):i+2])
        text=romanize(original['text'],mode,context,glossary)
        sentence_start=i==0 or bool(re.search(r'[.!?]\s*$',cues[i-1]['text'])) or original['start']-cues[i-1]['end']>.7
        if sentence_start and re.match(r'^[\u0c00-\u0c7f]',original['text']):text=text[:1].upper()+text[1:]
        cue={k:original[k] for k in ['id','start','end']};cue['text']=text
        words=speech_words(original,text)
        if words:cue.update(words=words,timing='mapped')
        for key in ['confidence','needsReview','correction','rawText','segment','recognitionQuality','reviewReasons','acousticRetry','flow','speechEnd','gapRepair','qualityScores','sourceSegmentIds','sourceWords','sourceTiming','recoveryAttemptId']:
            if key in original:cue[key]=deepcopy(original[key])
        if words and len(words)!=len(original.get('words',[])):
            cue['timing']='estimated'
            cue['needsReview']=True
            cue['reviewReasons']=list(dict.fromkeys([*cue.get('reviewReasons',[]),'estimated-roman-word-timing']))
        # Emoji mode never invents spoken 'bro'. It decorates explicit emotion only.
        if mode=='WhatsApp' and emojis and re.search(r'నవ్వు|హాహా|haha|lol',original['text'],re.I):cue['text']+=' 😂';cue.pop('words',None)
        if not cue.get('words'):
            cue['needsReview']=True
            cue['reviewReasons']=list(dict.fromkeys([*cue.get('reviewReasons',[]),'estimated-roman-word-timing']))
        return cue
    with ThreadPoolExecutor(max_workers=4) as pool:return list(pool.map(convert,enumerate(cues)))

def subtitle_result(raw,mode='Natural',emojis=False):
    result=deepcopy(raw);cues=result['cues'];language=result['language'];versions={}
    for cue in cues:
        cue['qualityScores']={'transcriptionConfidence':cue.get('confidence'),'languageConfidence':raw.get('languageProbability'),'correctionConfidence':None,'tenglishConfidence':None}
    # Correction/romanization have no calibrated probability; never invent one.
    name={'te':'Telugu','hi':'Hindi','en':'English'}.get(language)
    if name:versions[name]=cues
    if language=='te':versions['Tenglish']=fast_tenglish(cues,mode,emojis)
    result.update(srt=srt(cues),versions=versions,pipeline='speech-to-timed-subtitles')
    return result

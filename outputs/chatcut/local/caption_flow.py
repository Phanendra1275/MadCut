"""Word-driven segmentation and conservative, VAD-backed presentation timing.

This layer never recognizes, corrects or invents text. Acoustic word anchors
remain unchanged; only caption grouping and short presentation holds change.
"""
from copy import deepcopy
import math,re

DEFAULTS={'maxWords':6,'maxCharsPerLine':36,'maxLines':2,'maxDuration':4.,'minDuration':.6,'maxGapMs':250,'pauseMs':600}

def options(value=None):
 result={**DEFAULTS,**(value or {})}
 bounds={'maxWords':(1,12),'maxCharsPerLine':(20,48),'maxLines':(1,2),'maxDuration':(1,6),'minDuration':(.2,1.5),'maxGapMs':(0,250),'pauseMs':(400,1500)}
 for k,(a,b) in bounds.items():
  v=result[k]
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not a<=v<=b:raise ValueError('Invalid caption timing setting: '+k)
 if result['minDuration']>=result['maxDuration']:raise ValueError('Minimum caption duration must be shorter than maximum.')
 return result

def speech_between(start,end,spans):
 return any(s['start']<=start+.02 and s['end']>=end-.02 for s in spans)

def valid_words(cue):
 words=cue.get('words',[]);previous=cue['start']
 if len(words)!=len(cue['text'].split()):return False
 for word in words:
  if not all(isinstance(word.get(k),(int,float)) and math.isfinite(word[k]) for k in ('start','end')):return False
  if word['start']<previous-.001 or word['end']<=word['start'] or word['start']<cue['start']-.001 or word['end']>cue['end']+.001:return False
  previous=word['end']
 return bool(words)

def natural_break(word):
 # Endings and punctuation are hints, never a translation or text rewrite.
 return bool(re.search(r'[.!?।,;:]$',word) or re.search(r'(?:ఉంది|ఉన్నాను|వస్తాను|వెళ్తున్నావు|చేస్తున్నావు|కాలేదు|లేదు|కాదు|అన్నమాట)[.!?]*$',word))

def split_words(words,settings):
 groups=[];i=0
 while i<len(words):
  end=i+1;last_boundary=None
  while end<len(words):
   candidate=words[i:end+1];text=' '.join(w['word'] for w in candidate)
   gap=words[end]['start']-words[end-1]['end']
   if gap>=settings['pauseMs']/1000:break
   if len(candidate)>settings['maxWords'] or len(text)>settings['maxCharsPerLine']*settings['maxLines'] or words[end]['end']-words[i]['start']>settings['maxDuration']:
    if last_boundary and words[last_boundary-1]['end']-words[i]['start']>=settings['minDuration']:end=last_boundary
    break
   if natural_break(words[end-1]['word']):
    last_boundary=end
    if words[end-1]['end']-words[i]['start']>=settings['minDuration'] and re.search(r'[.!?।]$',words[end-1]['word']):break
   end+=1
  groups.append(words[i:end]);i=end
 return groups

def prepare(cues,duration,spans=(),settings=None):
 cfg=options(settings);result=[];issues=[];preserved=[]
 for original in cues:
  cue=deepcopy(original)
  if not 0<=cue['start']<cue['end']<=duration+.001:raise ValueError('Caption outside audio duration.')
  if result and cue['start']<result[-1]['end']-.001:raise ValueError('Overlapping source captions; alignment needs review.')
  preserved.extend(cue['text'].split())
  if valid_words(cue):
   word_offset=0
   for group in split_words(cue['words'],cfg):
    start,end=group[0]['start'],group[-1]['end']
    part={**cue,'sourceSegmentIds':cue.get('sourceSegmentIds',[cue['id']]),'id':cue['id']+'-w'+str(word_offset),'start':start,'end':end,'speechEnd':end,'text':' '.join(w['word'] for w in group),'words':group,'flow':'vad'}
    word_offset+=len(group)
    if all(isinstance(w.get('confidence'),(int,float)) and not isinstance(w['confidence'],bool) and math.isfinite(w['confidence']) for w in group):part['confidence']=round(sum(w['confidence'] for w in group)/len(group),3)
    else:part.pop('confidence',None)
    result.append(part)
  else:
   # Retain authoritative content and the segment interval. Do not manufacture
   # a word alignment or subdivide a segment into equal-time pseudo words.
   cue.pop('words',None);cue['needsReview']=True
   cue['reviewReasons']=list(dict.fromkeys([*cue.get('reviewReasons',[]),'unresolved-word-timing']))
   result.append(cue)
 for a,b in zip(result,result[1:]):
  gap=b['start']-a['end']
  if 0<gap<=cfg['maxGapMs']/1000+.0001 and speech_between(a['end'],b['start'],spans):
   a.setdefault('speechEnd',a['end']);a['end']=b['start'];a['gapRepair']='vad-short-hold';a['flow']='vad'
 if preserved!=[w for c in result for w in c['text'].split()]:raise ValueError('Caption segmentation changed spoken words.')
 for i,c in enumerate(result):
  reasons=list(c.get('reviewReasons',[]))
  if c['end']-c['start']<cfg['minDuration']:reasons.append('short-caption')
  if c['end']-c['start']>cfg['maxDuration']:reasons.append('long-caption')
  if c.get('words') and not valid_words(c):raise ValueError('Word anchors outside caption or overlapping.')
  if i and c['start']<result[i-1]['end']-.001:raise ValueError('Overlapping captions after segmentation.')
  if reasons:c.update(needsReview=True,reviewReasons=list(dict.fromkeys(reasons)))
 # Compare speech coverage with recognized word coverage. Silence outside VAD
 # is deliberately ignored. Uncovered speech is exposed, never filled with text.
 intervals=[(w['start'],w['end']) for c in result for w in c.get('words',[])]
 for span in spans:
  cursor=span['start']
  for start,end in intervals:
   if end<=span['start'] or start>=span['end']:continue
   if start-cursor>.6:issues.append({'start':round(cursor,3),'end':round(min(start,span['end']),3),'reason':'speech-without-word-alignment'})
   cursor=max(cursor,min(end,span['end']))
  if span['end']-cursor>.6:issues.append({'start':round(cursor,3),'end':round(span['end'],3),'reason':'speech-without-word-alignment'})
 return result,{'wordCount':len(preserved),'captionCount':len(result),'uncoveredSpeech':issues,'gapRepairs':sum(c.get('gapRepair')=='vad-short-hold' for c in result),'settings':cfg}

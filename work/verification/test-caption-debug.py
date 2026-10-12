import sys,json
from pathlib import Path
from types import SimpleNamespace as NS
sys.path.insert(0,'outputs/chatcut/local')
from caption_timing import canonical_tenglish,faithful,speech_words
from speech_engine import caption_segments
source='మొబైల్స్ అన్ బాక్సింగ్స్ ఇవన్నీ అంటే అసలు ఏదో వింతగా చూసేవారు అన్నమాట'
value=canonical_tenglish(source,'mobiles anbaaksings ivannee ante asalu edo vinthagaa choosevaaru annamaata')
assert value=='mobiles unboxings ivanni ante asalu edo vinthaga choosevaru annamata',value
assert not faithful('నువ్వు రాలేదు','nuvvu ravali')
assert canonical_tenglish('అంటే అంతే','anthe ante')=='ante anthe' # preserve the native distinction
words=[NS(word=w,start=a,end=b) for w,a,b in [('నువ్వు',0,.3),('ఈరోజు',.4,.8),('రాలేదు',2,2.5),('కాదు',2.6,3),('బ్రో',3.1,3.5)]]
cues=caption_segments([NS(text=' '.join(w.word for w in words),words=words,start=0,end=3.5)],4)
assert len(cues)==2 and cues[0]['end']==.8 and cues[1]['start']==2,cues
assert ' '.join(c['text'] for c in cues)==' '.join(w.word for w in words)
Path('work/verification/caption-debug-unit.json').write_text(json.dumps({'canonicalTenglish':value,'pauseGroups':cues},ensure_ascii=False,indent=2),encoding='utf-8')
print('Passed loanword/chat spelling, negation, distinct-word preservation, pause splitting and text preservation.')

import sys
from pathlib import Path
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from timed_subtitles import fast_tenglish
from caption_timing import speech_words
for native,expected in [('ఆబ్జెక్ట్‌ల మధ్య','Object la madhya'),('ఈ ఫైల్‌ని edit చేసి పంపు','Ee file ni edit chesi pampu'),('ప్రాజెక్ట్‌లో ChatGPT 123','Project lo ChatGPT 123'),('ఆబ్జెక్ట్‌లు','Objects')]:
 cue={'id':'x','start':0,'end':4,'text':native,'words':[{'word':w,'start':i,'end':i+.5} for i,w in enumerate(native.split())]}
 value=fast_tenglish([cue])[0]
 assert value['text']==expected,(value['text'],expected)
 assert '\u200c' not in value['text'] and '\u200d' not in value['text']
 assert (value['start'],value['end'])==(0,4)
 print(value['text'])
print('Passed real loanword/joiner regression, productive suffixes, names/numbers and unchanged cue times.')

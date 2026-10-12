import sys,json
from pathlib import Path
sys.path.insert(0,'outputs/chatcut/local')
from caption_timing import faithful,safe_tenglish,speech_words
from chat_spelling import hint
c=json.loads(Path('work/verification/prasad-recognition-comparison.json').read_text(encoding='utf-8'))['specialized']['cues'][0]
correct='mobiles unboxings ivanni ante asalu edo vinthaga choosevaru annamata'
assert faithful(c['text'],correct)
assert not faithful(c['text'],'anbaaksings ivannee anthe asalu edo vinthagaa choosevaaru annamaatha')
v=safe_tenglish(c['text']);assert 'unboxings' in v and 'ivanni ante' in v and 'annamata' in v
words=speech_words(c,correct);assert words and len(words)==9 and words[1]['start']==c['words'][1]['start'] and words[1]['end']==c['words'][2]['end']
print('Actual clip native:',c['text']);print('Preferred Tenglish:',v);print('Passed: genuine loanword, natural chat spellings, combined unboxings speech anchor, wrong screenshot spelling rejected.')

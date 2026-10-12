import sys,json
from pathlib import Path
from types import SimpleNamespace as S
from unittest.mock import patch
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from speech_quality import quality,decode_reasons,retry_better,audit
from transcript_correction import correct
bad=S(text='నువ్వు ఎక్కడికి వెళ్తునావ్',avg_logprob=-1.4,compression_ratio=1.1,no_speech_prob=.1)
good=S(text='నువ్వు ఎక్కడికి వెళ్తున్నావు',avg_logprob=-.6,compression_ratio=1.1,no_speech_prob=.1)
assert retry_better([bad],[good])
assert not retry_better([good],[bad])
assert not retry_better([S(text='నాకు తెలియదు',avg_logprob=-1.5)],[S(text='నాకు తెలుసు',avg_logprob=-.2)])
assert not retry_better([S(text='Phanendra 123',avg_logprob=-1.5)],[S(text='Fanendra 123',avg_logprob=-.2)])
assert not decode_reasons(good)
assert 'uncertain-recognition' in decode_reasons(bad)
assert audit({'text':'సరే','start':0,'end':3})['reviewReasons']==['estimated-word-timing']
assert 'long-word-alignment' in audit({'words':[{'word':'సరే','start':0,'end':3}]})['reviewReasons']
c={'id':'x','text':'నువ్వు ఎక్కడికి వెళ్తునావ్','start':0,'end':3,'confidence':.3,'words':[{'word':w,'start':i,'end':i+1} for i,w in enumerate(bad.text.split())]}
memo={};first=correct([c],model_enabled=False,memo=memo)
with patch('transcript_correction.acceptable',side_effect=AssertionError('Repeated correction')):
 second=correct([c],model_enabled=False,memo=memo)
assert first==second and len(memo)==1
assert [(w['start'],w['end']) for w in first[0]['words']]==[(w['start'],w['end']) for w in c['words']]
Path('work/verification/acoustic-quality-tests.json').write_text(json.dumps({'passed':['confidence gate','improved-score guard','negation guard','name guard','missing timing flag','long alignment flag','incremental memo','unchanged correction timing']},indent=2),encoding='utf-8')
print('Passed acoustic retry guards, timing warnings, incremental correction reuse and unchanged anchors.')

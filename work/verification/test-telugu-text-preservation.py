import sys
from types import SimpleNamespace as NS
from pathlib import Path
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from speech_engine import caption_segments,compact
cases=[
 NS(text='నువ్వు వస్తున్నావా?',start=0,end=3,words=[NS(word=' నువ్వు',start=0,end=1),NS(word=' వస్తు',start=1,end=2),NS(word='న్నావా?',start=2,end=3)]),
 NS(text='అవకాశాలను మెరుగుపరుచుకోవచ్చు.',start=0,end=3,words=[NS(word=' అవకాసాలన�',start=0,end=1.5),NS(word=' మెరుగుపరుచుకోవచ్చు.',start=1.5,end=3)]),
 NS(text='నువ్వు రాలేదు.',start=0,end=3,words=[NS(word=' నువ్వు',start=0,end=0),NS(word=' రాలేదు.',start=0,end=3)])]
for case in cases:
 cues=caption_segments([case],3)
 assert compact(' '.join(c['text'] for c in cues))==compact(case.text)
 assert '�' not in ' '.join(c['text'] for c in cues)
 assert all(0<=c['start']<c['end']<=3 for c in cues)
print('Passed: Telugu word splits, corrupt alignment text, zero-duration spoken words.')

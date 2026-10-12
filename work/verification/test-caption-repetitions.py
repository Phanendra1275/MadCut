import sys
from types import SimpleNamespace as NS
sys.path.insert(0,'outputs/chatcut/local')
from speech_engine import join_recovery_windows
from caption_timing import faithful

def seg(start,end):
 return NS(text='రా',words=[NS(word='రా',start=start,end=end)])
repeated=join_recovery_windows([seg(1,1.2)],[seg(1.25,1.5)])
assert ' '.join(s.text for s in repeated)=='రా రా'
duplicate=join_recovery_windows([seg(1,1.4)],[seg(1.05,1.45)])
assert len(duplicate)==1
assert not faithful('నువ్వు ఈరోజు college కి వస్తున్నావా?','Nuvvu eeroju college vasthunnava?')
print('Passed: deliberate repeated words retained, overlapping recovery duplicate removed, omitted spoken word rejected.')

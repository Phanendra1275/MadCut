import sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path('outputs/chatcut/local').resolve()))
from caption_flow import prepare,options
from transcript_correction import correct
from timed_subtitles import fast_tenglish,subtitle_result
checks=[]
def cue(text,start=0,gap=.1):
 words=[{'word':w,'start':round(start+i*(.4+gap),3),'end':round(start+i*(.4+gap)+.4,3),'confidence':.94} for i,w in enumerate(text.split())]
 return {'id':'c','text':text,'start':words[0]['start'],'end':words[-1]['end'],'words':words}
def record(name):checks.append(name)
a=cue('Bro nenu ivala college ki velthunna');before=copy.deepcopy(a)
out,q=prepare([a],a['end'],[{'start':0,'end':a['end']}]);assert len(out)==1 and out[0]['text']==a['text'] and a==before;record('six-word phrase retained, source untouched')
a=cue('నువ్వు ఎక్కడికి వెళ్తున్నావు?');out,_=prepare([a],a['end']);assert len(out)==1;record('question phrase not split at three words')
for gap in [.15,.2,.25,.251,.8]:
 a=cue('Bro');b=cue('nenu',a['end']+gap);b['id']='b';duration=b['end'];raw=[a,b]
 joined,q=prepare(raw,duration,[{'start':0,'end':duration}]);assert (joined[0]['end']==b['start'])==(gap<=.25);assert joined[0]['words']==a['words'];record('speech-backed gap '+str(gap))
 silent,_=prepare(raw,duration,[{'start':0,'end':a['end']},{'start':b['start'],'end':b['end']}]);assert silent[0]['end']==a['end'];record('actual silence '+str(gap)+' retained')
a=cue('అవును అవును bro');out,_=prepare([a],a['end']);assert ' '.join(c['text'] for c in out)==a['text'];record('intentional spoken repetition retained')
a=cue('నువ్వు ఎక్కడికి వెళ్తునావ్');out,_=prepare([a],a['end']);fixed=correct(out,model_enabled=False);roman=fast_tenglish(fixed);assert roman[0]['text']=='Nuvvu ekkadiki velthunnav?';assert [(w['start'],w['end']) for c in roman for w in c['words']]==[(w['start'],w['end']) for c in out for w in c['words']];record('correct Telugu before Roman output, exact anchors')
a=cue('నాకు అర్ధం కాలేదు');out,_=prepare([a],a['end']);fixed=correct(out,model_enabled=False);assert fast_tenglish(fixed)[0]['text']=='Naaku artham kaaledu';record('contextual Telugu spelling preserves negation')
a=cue('Phanendra GMRIT Instagram YouTube ChatGPT 123');fixed=correct([a],model_enabled=False);assert fast_tenglish(fixed)[0]['text']==a['text'];record('names and numbers preserved')
for invalid in [{'id':'x','text':'x','start':-1,'end':1},{'id':'x','text':'x','start':1,'end':.5},{'id':'x','text':'x','start':0,'end':10}]:
 try:prepare([invalid],3)
 except ValueError:record('invalid timeline rejected')
 else:raise AssertionError('invalid accepted')
a=cue('missing');a['words'][0]['end']=0;out,_=prepare([a],1);assert out[0]['text']=='missing' and not out[0].get('words') and out[0]['needsReview'];record('bad alignment retains content, no fake word times')
a=cue('one two three four five six seven eight nine ten');out,_=prepare([a],a['end'],settings={'maxWords':4});assert [w for c in out for w in c['text'].split()]==a['text'].split();assert [w for c in out for w in c['words']]==a['words'];record('segmentation no missing/reordered words')
_,q=prepare([cue('Bro')],3,[{'start':0,'end':3}]);assert q['uncoveredSpeech'];record('uncovered speech exposed without invented captions')
r=subtitle_result({'language':'te','cues':[cue('నువ్వు వస్తాను')]});assert r['cues'][0]['qualityScores']['correctionConfidence'] is None;record('no fabricated quality probabilities')
Path('work/verification/caption-foundation/unit-results.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2),encoding='utf-8');print('Passed',len(checks),'caption flow regression checks.')

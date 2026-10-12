import sys,tempfile
from pathlib import Path
sys.path.insert(0,'outputs/chatcut/local')
import spelling_profile as p
from chat_spelling import hint
with tempfile.TemporaryDirectory(dir='work/verification') as folder:
 p.PATH=Path(folder)/'profile.json'
 p.save('ప్రసాద','ప్రసాద్','Prasad')
 cues=[{'text':'ప్రసాద వచ్చారు.','words':[{'word':'ప్రసాద','start':0,'end':1},{'word':'వచ్చారు.','start':1,'end':2}]}]
 assert p.correct_native(cues)==1 and cues[0]['text']=='ప్రసాద్ వచ్చారు.' and cues[0]['words'][0]['word']=='ప్రసాద్'
 assert hint('ప్రసాద్','Tenglish')=='Prasad'
 assert p.entries()[0]['roman']=='Prasad'
 p.remove('ప్రసాద');assert not p.entries()
print('Passed: approved native correction, retained word timing, learned Roman spelling, persistence and deletion.')

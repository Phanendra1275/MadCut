import sys
sys.path.insert(0,'outputs/chatcut/local')
from caption_timing import speech_words,faithful
source={'text':'నువ్వు ఈరోజు college కి వస్తున్నావా?','start':0,'end':8,'words':[{'word':w,'start':a,'end':b} for w,a,b in [('నువ్వు',0,.6),('ఈరోజు',1,1.8),('college',3,4),('కి',4.2,4.5),('వస్తున్నావా?',6,8)]]}
words=speech_words(source,'Nuvvu eeroju college ki vasthunnava?')
assert [(w['start'],w['end']) for w in words]==[(0,.6),(1,1.8),(3,4),(4.2,4.5),(6,8)]
assert speech_words(source,'Are you coming to college today?') is None
assert not faithful('అతను రాలేదు. నేను 10 నిమిషాల్లో వస్తాను.','Athanu ravali. Nenu 10 nimishallo vasthanu.')
assert faithful('అతను రాలేదు.','Athanu raledu.')
assert not faithful(source['text'],'Nuvvu eeroju college ki vasthunnava.')
print('Passed: real pauses and word anchors retained; paraphrases, missing questions and changed negatives rejected.')

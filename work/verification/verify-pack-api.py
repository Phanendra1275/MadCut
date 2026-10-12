from zipfile import ZipFile
from pathlib import Path
import hashlib,json,time,sys,httpx
root=Path('outputs/chatcut');rows=json.loads((root/'public/templates/index.json').read_text(encoding='utf-8'));assert len(rows)==33
with ZipFile(r'C:\Users\HP\Documents\Text Templates.zip') as z:
 for row in rows:
  data=(root/'public'/row['file'].lstrip('/')).read_bytes();assert data==z.read(row['originalFile']);assert (root/'public'/row['preview'].lstrip('/')).is_file()
(root/'verification/default-library').mkdir(exist_ok=True,parents=True);(root/'verification/default-library/source-integrity.json').write_text(json.dumps({'templates':len(rows),'originalBytesPreserved':True,'previewCount':33,'sha256':[{'id':r['id'],'hash':hashlib.sha256((root/'public'/r['file'].lstrip('/')).read_bytes()).hexdigest()} for r in rows]},indent=2),encoding='utf-8')
sys.path.insert(0,str((root/'local').resolve()));from timed_subtitles import fast_tenglish
text='నేను కూడా వస్తాను.';cues=[{'id':str(i),'start':i*3,'end':(i+1)*3,'text':text,'confidence':.99,'words':[{'word':w,'start':i*3+j,'end':i*3+j+1} for j,w in enumerate(text.split())]} for i in range(100)]
start=time.perf_counter();out=fast_tenglish(cues);cold=time.perf_counter()-start;start=time.perf_counter();fast_tenglish(cues);warm=time.perf_counter()-start;assert all(c.get('words') for c in out)
with httpx.Client(base_url='http://127.0.0.1:5173',timeout=60) as c:
 for mode,expected in [('Natural','Nuvvu ekkadiki velthunnav?'),('WhatsApp','Nuvvu ekkadiki velthunnav?'),('Formal','Nuvvu ekkadiki veltunnavu?')]:
  cue={'id':'x','start':0,'end':3,'text':'నువ్వు ఎక్కడికి వెళ్తునావ్','confidence':.99,'words':[{'word':w,'start':i,'end':i+1} for i,w in enumerate('నువ్వు ఎక్కడికి వెళ్తునావ్'.split())]};r=c.post('/api/translate',json={'cues':[cue],'language':'Tenglish','tone':'Social Media','sourceLanguage':'te','tenglishMode':mode,'emojis':False});r.raise_for_status()
  for _ in range(300):
   job=c.get('/api/jobs/'+r.json()['jobId']).json()
   if job['status']=='failed':raise RuntimeError(job['error'])
   if job['status']=='complete':break
   time.sleep(.05)
  result=job['result'];assert result['cues'][0]['text']==expected,(mode,result);assert result['nativeCues'][0]['text']=='నువ్వు ఎక్కడికి వెళ్తున్నావు?';assert result['cues'][0]['words'];assert [(w['start'],w['end']) for w in result['cues'][0]['words']]==[(w['start'],w['end']) for w in cue['words']]
 print('Passed original MOGRT integrity, preview availability, real API modes and exact corrected word anchors.');print('100 captions text-only:',round(cold,3),'s cold;',round(warm,3),'s warm.')
(root/'verification/default-library/text-performance.json').write_text(json.dumps({'captionCount':100,'coldSeconds':cold,'warmSeconds':warm,'speechRecognitionIncluded':False,'apiModesPassed':['Natural','WhatsApp','Formal'],'socialToneDoesNotInventWords':True},indent=2),encoding='utf-8')

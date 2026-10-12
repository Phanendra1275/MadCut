"""Selective, bounded transcript-only correction with conservative acceptance."""
import json,re,os,time,secrets,subprocess,unicodedata,hashlib
from pathlib import Path
from copy import deepcopy
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import httpx
ROOT=Path(__file__).resolve().parent.parent
CACHE=ROOT/'.local/correction-cache.json'
LOCK=Lock();PROCESS=None;TOKEN=secrets.token_urlsafe(24);URL='http://127.0.0.1:8768';VERSION='guarded-v4-context-spelling'
SYSTEM='''You are a Telugu speech-to-caption correction engine.
Your job is to correct speech-to-text output from spoken Telugu while preserving the speaker's exact meaning, tone, and conversational style.
Correct Telugu spelling, obvious transcription mistakes, word boundaries, punctuation, and grammar where necessary.
Do not rewrite the sentence unnecessarily.
Do not make colloquial Telugu formal unless explicitly requested.
Do not translate Telugu into English.
Do not invent missing information.
Preserve names, brands, places, numbers, English technical words, and Telugu-English mixed speech.
When generating Tenglish, represent Telugu using Roman/English characters naturally, similar to how Telugu speakers type on WhatsApp.
Tenglish must be conversational and context-aware, not a literal English translation and not rigid character-by-character transliteration.
Prefer natural forms such as: 'చేస్తున్నావు' → 'chesthunnav'; 'వెళ్తున్నావు' → 'velthunnav'; 'వస్తున్నాను' → 'vasthunna'; 'చాలా బాగుంది' → 'chala bagundi'; 'ఏం చేస్తున్నావు' → 'em chesthunnav'.
Return only the requested caption text and never add explanations.'''
OBVIOUS={'వెళ్తునావ్':'వెళ్తున్నావు','వెళ్తునావు':'వెళ్తున్నావు','చేస్తునావు':'చేస్తున్నావు','వస్తునావు':'వస్తున్నావు'}
NEGATIVE=('లేదు','లేను','లేడు','లేవు','కాదు','వద్దు','కూడదు','కుదరదు')
def cache_read():
 try:return json.loads(CACHE.read_text(encoding='utf-8'))
 except (ValueError,OSError):return {}
def cached(key):
 with LOCK:return cache_read().get(key)
def remember(key,value):
 with LOCK:
  rows=cache_read();rows.pop(key,None);rows[key]=value;rows=dict(list(rows.items())[-1200:]);temp=CACHE.with_suffix('.tmp');temp.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8');os.replace(temp,CACHE)
def stop():
 global PROCESS
 if PROCESS and PROCESS.poll() is None:
  try:
   PROCESS.terminate()
   try:PROCESS.wait(timeout=5)
   except (subprocess.TimeoutExpired, OSError):
    try:PROCESS.kill();PROCESS.wait(timeout=3)
    except OSError:pass
  except OSError:pass
 PROCESS=None

def start():
 global PROCESS
 config=json.loads((ROOT/'.local/config.json').read_text(encoding='utf-8-sig'))
 model=config.get('correction_model')
 if not model or not Path(model).is_file():return False
 llama_exec=config.get('llama_executable')
 if not llama_exec or not Path(llama_exec).is_file():return False
 if PROCESS is None or PROCESS.poll() is not None:
  try:
   with (ROOT/'.local/logs/correction.log').open('a',encoding='utf-8') as log:
    PROCESS=subprocess.Popen([llama_exec,'-m',model,'--host','127.0.0.1','--port','8768','--device',config.get('device','Vulkan1'),'-ngl','99','--split-mode','none','-c','4096','-t','4','--parallel','2','--jinja','--reasoning','off','--no-webui'],stdout=log,stderr=log,cwd=str(ROOT),env={**os.environ,'LLAMA_API_KEY':TOKEN},creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  except OSError:return False
 deadline=time.monotonic()+20
 while time.monotonic()<deadline:
  if PROCESS.poll() is not None:return False
  try:
   if httpx.get(URL+'/health',timeout=.5).status_code==200:return True
  except httpx.HTTPError:pass
  time.sleep(.15)
 return False

def protected(text):return re.findall(r'[A-Za-z][A-Za-z0-9_-]*|\d+(?:[.,]\d+)*',text)
def tokens(text):return re.findall(r'[\u0c00-\u0c7f\u200c\u200d]+|[A-Za-z0-9_-]+',text)
def acceptable(original,proposed,names=()):
 if not proposed or len(proposed)>len(original)*1.25+3 or protected(original)!=protected(proposed):return False
 a,b=tokens(original),tokens(proposed)
 if len(a)!=len(b):return False
 for x,y in zip(a,b):
  if x==y:continue
  if any(x in n or x==n for n in names if n):return False
  if x.endswith(NEGATIVE) or y.endswith(NEGATIVE):return False
  if SequenceMatcher(None,x,y,autojunk=False).ratio()<.8:return False
 if '?' in original and '?' not in proposed:return False
 if SequenceMatcher(None,original,proposed,autojunk=False).ratio()<.88:return False
 return True

def correct(cues,terms='',model_enabled=True,memo=None):
 result=deepcopy(cues);memo_keys=[];names=[x.strip() for x in re.split(r'[,\n]',terms) if x.strip()];work=[]
 for i,c in enumerate(result):
  context=' '.join(x['text'] for x in cues[max(0,i-1):i+2])
  memo_key=hashlib.sha256(json.dumps([VERSION,c,context,names],ensure_ascii=False,sort_keys=True).encode()).hexdigest();memo_keys.append(memo_key)
  if memo is not None and memo_key in memo:result[i]=deepcopy(memo[memo_key]);continue
  words=c.get('words',[]);confidence=c.get('confidence');low=(isinstance(confidence,(int,float)) and confidence<.8) or any(isinstance(w.get('confidence'),(int,float)) and w['confidence']<.55 for w in words) or (c.get('recognitionQuality',{}).get('averageLogProbability') or 0)<-1
  contextual_typo=bool(re.search(r'(?:నాకు|నీకు|మీకు|మాకు)\s+అర్ధం\s+(?:కాలేదు|కావడం|అయ్యింది|అవ్వలేదు)',c['text']))
  suspicious=contextual_typo or any(w in c['text'] for w in OBVIOUS) or '\ufffd' in c['text']
  c['needsReview']=bool(c.get('needsReview') or low or suspicious)
  if not (low or suspicious):c['correction']='preserved';continue
  before=c['text'];after=re.sub(r'[\u0c00-\u0c7f]+',lambda m:OBVIOUS.get(m[0],m[0]) if m[0] not in names else m[0],before)
  if contextual_typo:after=re.sub(r'(?<=[\u0c00-\u0c7f])\s+అర్ధం(?=\s+(?:కాలేదు|కావడం|అయ్యింది|అవ్వలేదు))',' అర్థం',after)
  if after!=before and re.fullmatch(r'(?:నువ్వు\s+)?(?:ఎక్కడికి\s+వెళ్తున్నావు|ఏం\s+చేస్తున్నావు)',after.strip()) and not (i+1<len(cues) and cues[i+1]['text'].lstrip().startswith('అని')):after+='?'
  if after!=before and acceptable(before,after,names):apply(c,after,'spelling-rule');continue
  context=' '.join(x['text'] for x in cues[max(0,i-1):i+2]);key=hashlib.sha256(json.dumps([VERSION,before,context,names],ensure_ascii=False).encode()).hexdigest()
  found=cached(key)
  if found is not None:
   if acceptable(before,found,names):apply(c,found,'cache')
   else:c['correction']='preserved'
  else:work.append((i,key,context))
 deferred=set(i for i,_,_ in work[4:])
 def finish():
  if memo is not None:
   for i,(key,c) in enumerate(zip(memo_keys,result)):
    if i not in deferred:memo[key]=deepcopy(c)
  return result
 # Bound extra work per update; remaining uncertain text is kept for review.
 for i,_,_ in work[4:]:result[i]['correction']='uncertain-preserved'
 work=work[:4]
 if not work or not model_enabled:return finish()
 if not start():
  for i,_,_ in work:result[i]['correction']='uncertain-preserved'
  return finish()
 def task(item):
  i,key,context=item;c=result[i];text=c['text']
  try:
   with httpx.Client(timeout=8,headers={'Authorization':'Bearer '+TOKEN}) as client:
    r=client.post(URL+'/v1/chat/completions',json={'model':'local','temperature':0,'max_tokens':128,'messages':[{'role':'system','content':SYSTEM+'\nCorrect only the caption, using surrounding context. Preserve word count and uncertain words. /no_think'},{'role':'user','content':json.dumps({'context':context,'protectedTerms':names,'caption':text},ensure_ascii=False)}]});r.raise_for_status();value=r.json()['choices'][0]['message']['content'].strip()
   if not acceptable(text,value,names):value=text
  except (httpx.HTTPError,KeyError,ValueError):value=text
  remember(key,value);return i,value
 with ThreadPoolExecutor(max_workers=2) as pool:
  for i,value in pool.map(task,work):apply(result[i],value,'small-model' if value!=result[i]['text'] else 'uncertain-preserved')
 return finish()

def apply(c,value,kind):
 old=c['text'];c['correction']=kind
 if value==old:return
 c.setdefault('sourceWords',deepcopy(c.get('words',[])))
 c.setdefault('sourceTiming',{'start':c['start'],'end':c['end']})
 c.setdefault('correctionVersions',[]).append({'text':old,'words':deepcopy(c.get('words',[])),'kind':kind})
 c['rawText']=old;c['text']=unicodedata.normalize('NFC',value)
 replacement=c['text'].split()
 if len(replacement)==len(c.get('words',[])):
  c['words']=[{**{k:v for k,v in w.items() if k!='confidence'},'word':text} for w,text in zip(c['words'],replacement)]
 else:c.pop('words',None)
 c['timing']='estimated'

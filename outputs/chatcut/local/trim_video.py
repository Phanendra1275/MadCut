"""Reviewable audio-silence and explicit filler/repetition cuts."""
import subprocess,re,json,shutil,uuid
from pathlib import Path
from export_video import ROOT,EXPORTS

def ffmpeg():
 exe=json.loads((ROOT/'.local/config.json').read_text(encoding='utf-8-sig')).get('ffmpeg_executable')
 if exe and (Path(exe).is_file() or shutil.which(exe)):return exe
 return shutil.which('ffmpeg') or 'ffmpeg'
def ranges(cuts,duration):
 merged=[]
 for c in sorted(cuts,key=lambda c:c['start']):
  a=max(0,c['start']);b=min(duration,c['end'])
  if b<=a:continue
  if merged and a<=merged[-1]['end']:merged[-1]['end']=max(b,merged[-1]['end'])
  else:merged.append({'start':a,'end':b,'reason':c['reason']})
 keep=[];cursor=0
 for c in merged:
  if c['start']-cursor>.03:keep.append([cursor,c['start']])
  cursor=c['end']
 if duration-cursor>.03:keep.append([cursor,duration])
 return merged,keep

def analyze(path,settings,job):
 try:
  duration=float(settings['duration']);threshold=float(settings.get('threshold',.6))
  if not .05<duration<600 or threshold not in [.3,.35,.5,.6,.8,.9]:raise ValueError('Invalid trim settings.')
  cuts=[];job['message']='Listening for pauses…'
  if settings.get('silences',True):
   try:
    p=subprocess.run([ffmpeg(),'-v','info','-i',str(path),'-vn','-af',f'silencedetect=noise=-40dB:d={threshold}','-f','null','-'],capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   except OSError as exc:raise ValueError(f'Could not run silence detection: {exc}')
   if p.returncode:raise ValueError('Could not analyze this video audio.')
   start=None
   for line in p.stderr.splitlines():
    a=re.search(r'silence_start: ([0-9.]+)',line);b=re.search(r'silence_end: ([0-9.]+)',line)
    if a:start=float(a[1])
    if b and start is not None:
     end=min(duration,float(b[1]));cuts.append({'start':start if start<.1 else start+.12,'end':end if end>duration-.1 else end-.12,'reason':'Silence'});start=None
   if start is not None:cuts.append({'start':start+.12,'end':duration,'reason':'Silence'})
  words=[w for c in settings.get('cues',[]) for w in c.get('words',[])]
  for i,w in enumerate(words):
   normalized=re.sub(r'[^\w]','',w['word']).lower()
   if settings.get('fillers') and normalized in {'um','uh','హ్మ్'} and w.get('confidence',0)>=.8:cuts.append({'start':w['start'],'end':w['end'],'reason':'Filler'})
   if settings.get('repetitions') and i and normalized==re.sub(r'[^\w]','',words[i-1]['word']).lower() and w['start']-words[i-1]['end']<.3 and w.get('confidence',0)>=.9:cuts.append({'start':w['start'],'end':w['end'],'reason':'Repeated word'})
  cuts,keep=ranges(cuts,duration)
  if not keep:raise ValueError('No audible content to keep. Your source is unchanged.')
  return {'cuts':cuts,'keep':keep,'removedSeconds':round(sum(c['end']-c['start'] for c in cuts),3),'duration':sum(b-a for a,b in keep)}
 finally:path.unlink(missing_ok=True)

def apply(path,settings,job):
 try:
  keep=settings['keep'];duration=float(settings['duration']);last=0
  if not isinstance(keep,list) or not 1<=len(keep)<=100:raise ValueError('Use up to 100 kept ranges.')
  for a,b in keep:
   if not 0<=a<b<=duration+.1 or a<last:raise ValueError('Invalid cuts.')
   last=b
  job['message']='Creating the reviewed cut…';dest=EXPORTS/(str(uuid.uuid4())+'.mp4')
  try:
   probe=subprocess.run([ffmpeg(),'-i',str(path)],capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));audio='Audio:' in probe.stderr
  except OSError as exc:raise ValueError(f'Could not probe media: {exc}')
  filters=[]
  for i,(a,b) in enumerate(keep):
   filters.append(f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]')
   if audio:filters.append(f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]')
  sequence=''.join(f'[v{i}]'+(f'[a{i}]' if audio else '') for i in range(len(keep)));filters.append(sequence+f'concat=n={len(keep)}:v=1:a={1 if audio else 0}[v]'+('[a]' if audio else ''))
  args=[ffmpeg(),'-y','-v','error','-i',str(path),'-filter_complex',';'.join(filters),'-map','[v]']+(['-map','[a]'] if audio else [])+['-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-movflags','+faststart',str(dest)]
  try:
   p=subprocess.run(args,capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  except OSError as exc:dest.unlink(missing_ok=True);raise ValueError(f'The reviewed cut could not render: {exc}')
  if p.returncode:dest.unlink(missing_ok=True);raise ValueError('The reviewed cut could not render.')
  return {'url':'/api/exports/'+dest.name,'duration':sum(b-a for a,b in keep)}
 finally:path.unlink(missing_ok=True)

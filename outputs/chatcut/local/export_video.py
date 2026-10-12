"""Local FFmpeg exports of browser-rendered caption frames."""
import json,zipfile,re,subprocess,shutil,uuid,struct,time
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi import HTTPException
from fastapi.responses import FileResponse
ROOT=Path(__file__).resolve().parent.parent
EXPORTS=ROOT/'.local/exports';EXPORTS.mkdir(exist_ok=True)

def number(v,lo,hi):
 if not isinstance(v,(int,float)) or not lo<=v<=hi:raise ValueError('Invalid export settings.')
 return v

def encode(archive,media,job):
 try:
  config=json.loads((ROOT/'.local/config.json').read_text(encoding='utf-8-sig'))
  ffmpeg=config.get('ffmpeg_executable') or shutil.which('ffmpeg')
  if not ffmpeg:raise ValueError('Local FFmpeg is unavailable.')
  with TemporaryDirectory(dir=ROOT/'.local',prefix='render-') as folder:
   work=Path(folder)
   with zipfile.ZipFile(archive) as z:
    entries=z.infolist()
    if len(entries)>18002 or sum(i.file_size for i in entries)>500*1024*1024:raise ValueError('Use a shorter export or lower resolution.')
    m=json.loads(z.read('manifest.json'));width=int(number(m['width'],2,7680));height=int(number(m['height'],2,7680));duration=number(m['duration'],.05,600);fps=m['fps']
    if fps not in [30,60] or m['quality'] not in ['Low','Medium','High'] or m['type'] not in ['video','green','blue','transparent']:raise ValueError('Invalid export format.')
    frames=m['frames'];previous=0;concat=[]
    if not 1<=len(frames)<=18000:raise ValueError('No caption frames.')
    for i,f in enumerate(frames):
     name=f'caption-{i}.png';span=number(f['duration'],.000001,600)
     data=z.read(name)
     if data[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',data[16:24])!=(width,height):raise ValueError('Invalid caption frame.')
     (work/name).write_bytes(data);previous+=span;concat.append(f"file '{name}'\noption framerate {fps}\nduration {span:.9f}")
    if abs(previous-duration)>.05:raise ValueError('Caption frame timing does not match the video.')
    concat.append(f"file 'caption-{len(frames)-1}.png'\noption framerate {fps}")
    (work/'frames.txt').write_text('\n'.join(concat),encoding='utf-8')
   kind=m['type'];alpha=kind=='transparent';suffix='.mov' if alpha else '.mp4';dest=EXPORTS/(str(uuid.uuid4())+suffix)
   args=[ffmpeg,'-y','-v','error','-nostats','-progress','pipe:1']
   has_media=bool(media)
   if kind=='video' and not media:raise ValueError('Attach your video to export it.')
   if media:args+=['-i',str(media)]
   args+=['-f','concat','-safe','0','-i',str(work/'frames.txt')]
   overlay=1 if has_media else 0
   if kind=='video':
    source_width=number(m['sourceWidth'],1,16384);source_height=number(m['sourceHeight'],1,16384);f=m['frame']
    values={k:number(f[k],-180 if k in ['rotation','x','y'] else 10,300) for k in ['scale','width','height','x','y','rotation']}
    color=f['background']
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',color):raise ValueError('Invalid background.')
    fit=min(width/source_width,height/source_height);vw=max(2,round(source_width*fit*values['scale']*values['width']/10000/2)*2);vh=max(2,round(source_height*fit*values['scale']*values['height']/10000/2)*2);rotation=values['rotation']*3.14159265359/180
    filters=f"color=c={color}:s={width}x{height}:r={fps}:d={duration}[bg];[0:v]scale={vw}:{vh},setsar=1,format=rgba,rotate={rotation}:ow=rotw({rotation}):oh=roth({rotation}):c=none[media];[bg][media]overlay=(W-w)/2+{width*values['x']/100}:(H-h)/2+{height*values['y']/100}:shortest=1[base];[base][{overlay}:v]overlay=0:0:eof_action=repeat:format=auto[v]"
   elif alpha:filters=f'[{overlay}:v]format=yuva444p10le[v]'
   else:
    color='#00B140' if kind=='green' else '#0047BB';filters=f'color=c={color}:s={width}x{height}:r={fps}:d={duration}[bg];[bg][{overlay}:v]overlay=0:0:eof_action=repeat:format=auto[v]'
   args+=['-filter_complex',filters,'-map','[v]']
   if media and m.get('audio',True):args+=['-map','0:a?']
   args+=['-t',str(duration),'-r',str(fps)]
   if alpha:args+=['-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-alpha_bits','16','-c:a','pcm_s16le']
   else:args+=['-c:v','libx264','-preset','fast','-crf',str({'Low':28,'Medium':20,'High':16}[m['quality']]),'-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart']
   args+=[str(dest)];job['message']='Encoding your export locally…';job['progress']=20
   with (work/'error.log').open('w') as errors:
    process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=errors,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    for line in process.stdout:
     if line.startswith('out_time_us='):
      try:job['progress']=min(99,20+int(line.split('=')[1])/1000000/duration*80)
      except ValueError:pass
    if process.wait()!=0:
     dest.unlink(missing_ok=True);raise ValueError('FFmpeg could not encode the export. Try 720p.')
   job['progress']=100
   for old in EXPORTS.glob('*'):
    if old.is_file() and old.stat().st_mtime<time.time()-86400:old.unlink(missing_ok=True)
   return {'url':'/api/exports/'+dest.name,'format':'mov' if alpha else 'mp4','width':width,'height':height,'fps':fps,'size':dest.stat().st_size}
 finally:
  archive.unlink(missing_ok=True)
  if media:media.unlink(missing_ok=True)

def file_response(name):
 if not re.fullmatch(r'[0-9a-f-]{36}\.(mp4|mov)',name):raise HTTPException(404,'Export not found.')
 p=EXPORTS/name
 if not p.is_file():raise HTTPException(404,'Export expired. Render it again.')
 return FileResponse(p,media_type='video/quicktime' if p.suffix=='.mov' else 'video/mp4',filename='MadCut'+p.suffix)

import httpx,time,hashlib
from pathlib import Path
root=Path('outputs/chatcut/.local/models/telugu-source');root.mkdir(parents=True,exist_ok=True)
repo='vasista22/whisper-telugu-medium';rev='bc8626d162a43fd3c9febcc34c27e5780815014e'
with httpx.Client(follow_redirects=True,timeout=120) as c:
 info=c.get('https://huggingface.co/api/models/'+repo,params={'blobs':'true'}).json()
 for f in info['siblings']:
  name=f['rfilename']
  if name in ['training_args.bin','.gitattributes','README.md'] or 'flax' in name:continue
  dest=root/name;size=f['size']
  if dest.is_file() and dest.stat().st_size==size:continue
  if size<1024*1024:
   r=c.get(f'https://huggingface.co/{repo}/resolve/{rev}/{name}');r.raise_for_status();dest.write_bytes(r.content);continue
  while not dest.exists() or dest.stat().st_size<size:
   start=dest.stat().st_size if dest.exists() else 0;end=min(size-1,start+64*1024*1024-1)
   for attempt in range(4):
    try:
     with c.stream('GET',f'https://huggingface.co/{repo}/resolve/{rev}/{name}?chunk={start}',headers={'Range':f'bytes={start}-{end}'}) as r:
      r.raise_for_status()
      if r.status_code!=206 or not r.headers.get('content-range','').startswith(f'bytes {start}-'):raise RuntimeError('Invalid download range')
      with dest.open('ab') as out:
       for chunk in r.iter_bytes(1024*1024):out.write(chunk)
     break
    except httpx.HTTPError:
     if attempt==3:raise
     time.sleep(2);start=dest.stat().st_size if dest.exists() else 0;end=min(size-1,start+64*1024*1024-1)
   print(name,round(dest.stat().st_size/size*100),'%',flush=True)
  if f.get('lfs',{}).get('sha256'):
   with dest.open('rb') as inp:digest=hashlib.file_digest(inp,'sha256').hexdigest()
   if digest!=f['lfs']['sha256']:raise RuntimeError('Checksum failed')
 print('Telugu model downloaded and checked.',flush=True)

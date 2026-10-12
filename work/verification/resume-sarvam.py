import httpx,time,hashlib
from pathlib import Path
p=Path('outputs/chatcut/.local/models/sarvam/sarvam-translate-q4_k_m.gguf');total=2464497984
with httpx.Client(follow_redirects=True,timeout=60) as c:
 while p.stat().st_size<total:
  start=p.stat().st_size;end=min(total-1,start+64*1024*1024-1)
  url=f'https://huggingface.co/Mungert/sarvam-translate-GGUF/resolve/main/sarvam-translate-q4_k_m.gguf?download=true&chunk={start}'
  with c.stream('GET',url,headers={'Range':f'bytes={start}-{end}'}) as r:
   r.raise_for_status()
   if r.status_code!=206 or not r.headers.get('content-range','').startswith(f'bytes {start}-'):raise RuntimeError('Download did not honor resume offset')
   with p.open('ab') as f:
    for b in r.iter_bytes(1024*1024):f.write(b)
  print(round(p.stat().st_size/1e9,2),'GB',flush=True)
 digest=hashlib.file_digest(p.open('rb'),'sha256').hexdigest();print('SHA256',digest,flush=True)
 if digest!='2b61ebb739505d9884482170087949b3076e1c095b24bdab68f3d018ef1dab2d':raise RuntimeError('Model checksum failed')
 license=c.get('https://huggingface.co/sarvamai/sarvam-translate/resolve/main/LICENSE.txt');license.raise_for_status()
 out=Path('outputs/chatcut/licenses');out.mkdir(exist_ok=True);(out/'sarvam-translate-GPL-3.0.txt').write_bytes(license.content)

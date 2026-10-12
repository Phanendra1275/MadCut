import httpx,time
from pathlib import Path
p=Path('outputs/chatcut/.local/models/sarvam/sarvam-translate-q4_k_m.gguf');t=time.time();n=0;last=0
with httpx.Client(follow_redirects=True,timeout=120) as c:
 with c.stream('GET','https://huggingface.co/Mungert/sarvam-translate-GGUF/resolve/main/sarvam-translate-q4_k_m.gguf?download=true') as r:
  r.raise_for_status()
  with p.open('wb') as f:
   for b in r.iter_bytes(4*1024*1024):
    f.write(b);n+=len(b)
    if n-last>256*1024*1024:print(round(n/1e9,2),'GB',round(time.time()-t),'s',flush=True);last=n
if n!=2464497984:raise RuntimeError('Incomplete model download')
print('Complete',n,flush=True)

import httpx
from pathlib import Path
p=Path('work/verification/telugu-test.parquet');size=331720646
with httpx.Client(follow_redirects=True,timeout=90) as c:
 while not p.exists() or p.stat().st_size<size:
  start=p.stat().st_size if p.exists() else 0;end=min(size-1,start+64*1024*1024-1)
  url=f'https://huggingface.co/datasets/google/fleurs/resolve/refs%2Fconvert%2Fparquet/te_in/test/0000.parquet?chunk={start}'
  with c.stream('GET',url,headers={'Range':f'bytes={start}-{end}'}) as r:
   r.raise_for_status()
   if r.status_code!=206 or not r.headers.get('content-range','').startswith(f'bytes {start}-'):raise RuntimeError('Invalid range')
   with p.open('ab') as f:
    for b in r.iter_bytes(1024*1024):f.write(b)
  print('Telugu test recordings',round(p.stat().st_size/size*100),'%',flush=True)

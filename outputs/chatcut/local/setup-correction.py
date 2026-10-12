"""Download the free selective text-correction model into this project only."""
from pathlib import Path
import urllib.request,json,hashlib
root=Path(__file__).resolve().parent.parent;dest=root/'.local/models/correction';dest.mkdir(parents=True,exist_ok=True)
path=dest/'Qwen3-1.7B-Q8_0.gguf';url='https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/90862c4/Qwen3-1.7B-Q8_0.gguf?download=true'
if not path.exists():
 temp=path.with_suffix('.download')
 with urllib.request.urlopen(url,timeout=120) as r,temp.open('wb') as f:
  while chunk:=r.read(1024*1024):f.write(chunk)
 with temp.open('rb') as f:assert f.read(4)==b'GGUF'
 temp.replace(path)
print('Local correction model downloaded:',path.stat().st_size,flush=True)
c=root/'.local/config.json';config=json.loads(c.read_text(encoding='utf-8-sig'));config['correction_model']=str(path);c.write_text(json.dumps(config,indent=2),encoding='utf-8')

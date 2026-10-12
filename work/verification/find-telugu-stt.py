import httpx
for q in ['faster-whisper-telugu','vaani-telugu','whisper-telugu']:
 models=httpx.get('https://huggingface.co/api/models',params={'search':q,'limit':35},timeout=30).json()
 for m in models:
  d=httpx.get('https://huggingface.co/api/models/'+m['id'],timeout=30).json()
  if any(f['rfilename']=='model.bin' for f in d.get('siblings',[])):print(m['id'],flush=True)

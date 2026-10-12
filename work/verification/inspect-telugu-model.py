import httpx,json
for repo in ['vasista22/whisper-telugu-medium','vasista22/whisper-telugu-large-v2']:
 r=httpx.get('https://huggingface.co/api/models/'+repo,params={'blobs':'true'},timeout=30).json()
 print(json.dumps({'repo':repo,'sha':r.get('sha'),'files':[(f['rfilename'],f.get('size')) for f in r.get('siblings',[]) if 'flax' not in f['rfilename']]}))
r=httpx.get('https://datasets-server.huggingface.co/parquet',params={'dataset':'google/fleurs','config':'te_in','split':'test'},timeout=30)
print('PARQUET',r.status_code,r.text[:5000])

"""Reproduce the free Telugu-specific recognizer without changing global Python packages."""
import hashlib
import json
import os
import subprocess
import sys
import time
import venv
from pathlib import Path
import httpx

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'.local'
REPO='vasista22/whisper-telugu-medium'
REVISION='bc8626d162a43fd3c9febcc34c27e5780815014e'
HEADS=[[13,15],[15,4],[15,15],[16,1],[20,0],[23,4]]
FILES={'pytorch_model.bin','config.json','generation_config.json','preprocessor_config.json','tokenizer_config.json','special_tokens_map.json','added_tokens.json','vocab.json','merges.txt','normalizer.json'}

def source_download(source):
    source.mkdir(parents=True,exist_ok=True)
    with httpx.Client(follow_redirects=True,timeout=120) as client:
        response=client.get(f'https://huggingface.co/api/models/{REPO}/revision/{REVISION}',params={'blobs':'true'});response.raise_for_status()
        for item in response.json()['siblings']:
            name=item['rfilename']
            if name not in FILES:continue
            path=source/name;size=item['size']
            if path.exists() and path.stat().st_size>size:path.unlink()
            if not path.exists() or path.stat().st_size!=size:
                if size<1024*1024:
                    r=client.get(f'https://huggingface.co/{REPO}/resolve/{REVISION}/{name}');r.raise_for_status();path.write_bytes(r.content)
                else:
                    attempts=0
                    while not path.exists() or path.stat().st_size<size:
                        start=path.stat().st_size if path.exists() else 0;end=min(size-1,start+64*1024*1024-1)
                        try:
                            with client.stream('GET',f'https://huggingface.co/{REPO}/resolve/{REVISION}/{name}?chunk={start}',headers={'Range':f'bytes={start}-{end}'}) as r:
                                r.raise_for_status()
                                if r.status_code!=206 or not r.headers.get('content-range','').startswith(f'bytes {start}-'):raise RuntimeError('Invalid model download offset.')
                                with path.open('ab') as out:
                                    for part in r.iter_bytes(1024*1024):out.write(part)
                            attempts=0;print(f'Telugu model: {path.stat().st_size/size:.0%}',flush=True)
                        except httpx.HTTPError:
                            attempts+=1
                            if attempts>=4:raise
                            time.sleep(2)
            digest=item.get('lfs',{}).get('sha256')
            if digest:
                with path.open('rb') as f:
                    if hashlib.file_digest(f,'sha256').hexdigest()!=digest:raise RuntimeError('Telugu model checksum failed.')

def main():
    target=DATA/'models/whisper-telugu-medium'
    if not (target/'model.bin').is_file() or not (target/'tokenizer.json').is_file():
        tools=DATA/'accuracy-tools';python=tools/'Scripts/python.exe'
        if not python.is_file():venv.EnvBuilder(with_pip=True,system_site_packages=True).create(tools)
        if Path(sys.executable).resolve()!=python.resolve():
            subprocess.run([str(python),'-m','pip','install','--no-cache-dir','torch==2.8.0','--index-url','https://download.pytorch.org/whl/cpu'],check=True)
            subprocess.run([str(python),'-m','pip','install','--no-cache-dir','transformers==4.57.6','sentencepiece','ctranslate2'],check=True)
            subprocess.run([str(python),str(Path(__file__).resolve())],check=True)
            return
        source=DATA/'models/telugu-source';source_download(source)
        os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
        from transformers import AutoTokenizer
        from ctranslate2.converters import TransformersConverter
        AutoTokenizer.from_pretrained(str(source),local_files_only=True).save_pretrained(source)
        TransformersConverter(str(source),copy_files=['tokenizer.json','preprocessor_config.json'],low_cpu_mem_usage=True).convert(str(target),quantization='int8',force=True)
    # The converter cannot infer selected heads from a local fine-tuned model name.
    config=target/'config.json';values=json.loads(config.read_text(encoding='utf-8'));values['alignment_heads']=HEADS;config.write_text(json.dumps(values,indent=2),encoding='utf-8')
    (target/'provenance.json').write_text(json.dumps({'source':REPO,'revision':REVISION,'license':'Apache-2.0','quantization':'int8','word_alignment':'standard Whisper-medium heads'},indent=2),encoding='utf-8')
    print('Free Telugu recognizer is ready.',flush=True)

if __name__=='__main__':main()

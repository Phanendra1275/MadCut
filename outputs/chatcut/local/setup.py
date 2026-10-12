"""Install only free local dependencies; all project downloads stay in .local."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'.local'
TAG='b11474'
MODEL_REPO='Qwen/Qwen3-8B-GGUF'
MODEL_FILE='Qwen3-8B-Q4_K_M.gguf'

def download(url,dest):
    req=urllib.request.Request(url,headers={'User-Agent':'ChatCut-free-local'})
    with urllib.request.urlopen(req,timeout=60) as response,dest.open('wb') as output:
        while part:=response.read(1024*1024):output.write(part)

def regional_download(dest):
    import httpx
    size=2464497984
    expected='2b61ebb739505d9884482170087949b3076e1c095b24bdab68f3d018ef1dab2d'
    if dest.exists() and dest.stat().st_size>size:dest.unlink()
    with httpx.Client(follow_redirects=True,timeout=90) as client:
        while not dest.exists() or dest.stat().st_size<size:
            start=dest.stat().st_size if dest.exists() else 0
            end=min(size-1,start+64*1024*1024-1)
            url=f'https://huggingface.co/Mungert/sarvam-translate-GGUF/resolve/main/sarvam-translate-q4_k_m.gguf?download=true&chunk={start}'
            with client.stream('GET',url,headers={'Range':f'bytes={start}-{end}'}) as response:
                response.raise_for_status()
                if response.status_code!=206 or not response.headers.get('content-range','').startswith(f'bytes {start}-'):
                    raise RuntimeError('The download server did not honor the resume position.')
                with dest.open('ab') as output:
                    for part in response.iter_bytes(1024*1024):output.write(part)
            print(f'Translation model: {dest.stat().st_size/size:.0%}',flush=True)
    with dest.open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise RuntimeError('Translation model checksum failed. Remove the incomplete model and run setup again.')

def main():
    for name in ['logs','models/qwen','models/whisper','runtime/llama']:(DATA/name).mkdir(parents=True,exist_ok=True)
    needed=['faster_whisper','fastapi','uvicorn','multipart','httpx','huggingface_hub','indic_transliteration']
    missing=[name for name in needed if not importlib.util.find_spec(name)]
    python=sys.executable
    if missing:
        import venv
        target=DATA/'venv'
        if not (target/'Scripts/python.exe').is_file():venv.EnvBuilder(with_pip=True,system_site_packages=True).create(target)
        python=str(target/'Scripts/python.exe')
        if Path(sys.executable).resolve()!=Path(python).resolve():
            subprocess.run([python,'-m','pip','install','-r',str(ROOT/'local/requirements.txt')],check=True)
            subprocess.run([python,str(Path(__file__).resolve())],check=True)
            return
    os.environ['HF_HUB_CACHE']=str(DATA/'models/hub')
    os.environ['HF_XET_CACHE']=str(DATA/'models/xet')
    from huggingface_hub import hf_hub_download,snapshot_download
    executable=next((DATA/'runtime/llama').rglob('llama-server.exe'),None)
    if executable is None:
        print('Downloading the free GPU runtime...',flush=True)
        url=f'https://github.com/ggml-org/llama.cpp/releases/download/{TAG}/llama-{TAG}-bin-win-vulkan-x64.zip'
        archive=DATA/'runtime/llama-vulkan.zip'
        download(url,archive)
        destination=(DATA/'runtime/llama').resolve()
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                if not (destination/item.filename).resolve().is_relative_to(destination):raise RuntimeError('Unsafe archive path.')
            z.extractall(destination)
        executable=next(destination.rglob('llama-server.exe'))
    model=DATA/'models/qwen'/MODEL_FILE
    if not model.is_file():
        print('Downloading the free language model (about 5 GB)...',flush=True)
        hf_hub_download(MODEL_REPO,MODEL_FILE,local_dir=model.parent)
    with model.open('rb') as f:
        if f.read(4)!=b'GGUF':raise RuntimeError('The language model download is incomplete.')
    regional=DATA/'models/sarvam/sarvam-translate-q4_k_m.gguf'
    regional.parent.mkdir(parents=True,exist_ok=True)
    if not regional.is_file() or regional.stat().st_size!=2464497984:
        print('Downloading the free Indian-language translation model (about 2.5 GB)...',flush=True)
        regional_download(regional)
    with regional.open('rb') as f:
        if f.read(4)!=b'GGUF':raise RuntimeError('The translation model download is incomplete.')
    hub=Path.home()/'.cache/huggingface/hub'
    cached=[p.parent for p in hub.glob('models--Systran--faster-whisper-large-v3/snapshots/*/model.bin') if p.stat().st_size>3_000_000_000 and (p.parent/'tokenizer.json').is_file()]
    if cached:
        speech=cached[0]
        print('Reusing the complete cached Whisper model.',flush=True)
    else:
        speech=DATA/'models/whisper'
        if not (speech/'model.bin').is_file():
            print('Downloading the free speech model...',flush=True)
            snapshot_download('Systran/faster-whisper-large-v3',local_dir=speech)
    subprocess.run([python,str(ROOT/'local/setup-telugu.py')],check=True)
    detectors=[p.parent for p in hub.glob('models--Systran--faster-whisper-small/snapshots/*/model.bin') if p.stat().st_size>400_000_000 and (p.parent/'tokenizer.json').is_file()]
    if detectors:detector=detectors[0]
    else:
        detector=DATA/'models/detector'
        if not (detector/'model.bin').is_file():snapshot_download('Systran/faster-whisper-small',local_dir=detector)
    listed=subprocess.run([str(executable),'--list-devices'],capture_output=True,text=True,check=True).stdout
    devices=re.findall(r'(Vulkan\d+):\s*([^\n]+)',listed)
    preferred=next((name for name,desc in devices if 'NVIDIA' in desc),devices[0][0] if devices else 'none')
    config={'whisper_model':str(speech),'telugu_speech_model':str(DATA/'models/whisper-telugu-medium'),'speech_detector_model':str(detector),'qwen_model':str(model),'translation_model':str(regional),'llama_executable':str(executable),'python_executable':python,'device':preferred,'gpu_layers':20,'translation_gpu_layers':16,'model_name':'Qwen3-8B + Sarvam Translate','speech_name':'Telugu-trained Whisper medium + multilingual Whisper large-v3'}
    (DATA/'config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    print('Ready. Double-click Start-ChatCut.cmd. No paid API is configured.',flush=True)

if __name__=='__main__':main()

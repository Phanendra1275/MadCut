"""Enable free NVIDIA speech acceleration in this project's runtime only."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
if os.name!='nt':raise SystemExit('This installer is for the Windows MadCut runtime.')
import ctranslate2
if not ctranslate2.get_cuda_device_count():raise SystemExit('No supported NVIDIA GPU detected. CPU recognition remains available.')
target=ROOT/'.local/runtime/cuda-python'
if not (target/'nvidia/cublas/bin/cublas64_12.dll').is_file():
    subprocess.run([sys.executable,'-m','pip','install','--target',str(target),'--no-deps','--no-cache-dir','nvidia-cublas-cu12==12.9.2.10'],check=True)
print('NVIDIA speech runtime ready. Restart MadCut. CPU fallback remains available.')

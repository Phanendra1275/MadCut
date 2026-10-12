import os
from pathlib import Path
root=Path('outputs/chatcut/.local/models');os.environ['HF_HUB_CACHE']=str(root.resolve()/'hub');os.environ['HF_XET_CACHE']=str(root.resolve()/'xet')
from huggingface_hub import hf_hub_download
p=hf_hub_download('Mungert/sarvam-translate-GGUF','sarvam-translate-q4_k_m.gguf',local_dir=root/'sarvam')
print(p,flush=True)

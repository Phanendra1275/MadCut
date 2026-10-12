import os,json,time
from pathlib import Path
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
from transformers import AutoTokenizer
from ctranslate2.converters import TransformersConverter
root=Path('outputs/chatcut/.local/models');source=root/'telugu-source';target=root/'whisper-telugu-medium'
p=source/'generation_config.json';d=json.loads(p.read_text());d['alignment_heads']=[[13,15],[15,4],[15,15],[16,1],[20,0],[23,4]];p.write_text(json.dumps(d),encoding='utf-8')
print('Preparing the Telugu tokenizer',flush=True)
AutoTokenizer.from_pretrained(str(source.resolve()),local_files_only=True).save_pretrained(source)
print('Converting verified Telugu weights to the local recognition format',flush=True)
TransformersConverter(str(source.resolve()),copy_files=['tokenizer.json','preprocessor_config.json'],low_cpu_mem_usage=True).convert(str(target),quantization='int8',force=True)
print('Conversion complete',flush=True)

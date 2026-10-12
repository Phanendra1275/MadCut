import json
from pathlib import Path
import pyarrow.parquet as pq
rows=pq.read_table('work/verification/telugu-test.parquet').to_pylist()
chosen=[];ids=set();genders=set()
for index,r in enumerate(rows):
 seconds=r['num_samples']/16000
 if not 5<seconds<14 or r['id'] in ids:continue
 if len(chosen)==1 and r['gender'] in genders:continue
 if len(chosen)==2 and index<25:continue
 p=Path(f'work/verification/telugu-heldout-{len(chosen)+1}.wav');p.write_bytes(r['audio']['bytes'])
 chosen.append({'row':index,'id':r['id'],'seconds':seconds,'gender':r['gender'],'audio':str(p),'reference':r['raw_transcription']});ids.add(r['id']);genders.add(r['gender'])
 if len(chosen)==3:break
Path('work/verification/telugu-heldout-references.json').write_text(json.dumps(chosen,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(chosen,ensure_ascii=True),flush=True)

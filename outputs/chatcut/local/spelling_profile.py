"""User-approved local word spellings. This is a glossary, not model fine-tuning."""
import json,re,os
from pathlib import Path
from threading import Lock
PATH=Path(__file__).resolve().parent.parent/'.local/spelling-profile.json'
LOCK=Lock()
def entries():
    try:return json.loads(PATH.read_text(encoding='utf-8'))['entries']
    except (OSError,ValueError,KeyError):return []
def save(heard,native,roman):
    if not all(isinstance(v,str) and 0<len(v)<=80 for v in (heard,native,roman)):raise ValueError('Enter one word in each spelling field.')
    if not re.fullmatch(r'[\u0c00-\u0c7f\u200c\u200d]+',heard) or not re.fullmatch(r'[\u0c00-\u0c7f\u200c\u200d]+',native) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*',roman):raise ValueError('Use a Telugu word and its English-letter spelling, without spaces.')
    with LOCK:
        rows=[r for r in entries() if r['heard']!=heard];rows.append({'heard':heard,'native':native,'roman':roman})
        if len(rows)>200:raise ValueError('Use up to 200 learned spellings.')
        write(rows)
    return rows
def write(rows):
    tmp=PATH.with_suffix('.tmp');tmp.write_text(json.dumps({'version':1,'entries':rows},ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,PATH)
def remove(heard):
    with LOCK:write([r for r in entries() if r['heard']!=heard])
def roman_words():return {r['native']:r['roman'] for r in entries()}
def correct_native(cues):
    mapping={r['heard']:r['native'] for r in entries()};count=0
    def change(m):return mapping.get(m[0],m[0])
    for c in cues:
        value=re.sub(r'[\u0c00-\u0c7f\u200c\u200d]+',change,c['text'])
        if value!=c['text']:
            count+=1;c['text']=value
            for w in c.get('words',[]):w['word']=re.sub(r'[\u0c00-\u0c7f\u200c\u200d]+',change,w['word'])
    return count

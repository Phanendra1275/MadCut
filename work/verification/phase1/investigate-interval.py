"""Bounded re-recognition with the installed model; no accuracy ground truth."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path('outputs/chatcut/local').resolve()))
from speech_engine import recognize

root = Path('work/verification/phase1')
start = time.perf_counter()
result = recognize(root/'flagged-interval-context.wav', 'te', apply_spellings=False)
offset = 49.44
for cue in result['cues']:
    cue['start'] = round(cue['start'] + offset, 3)
    cue['end'] = round(cue['end'] + offset, 3)
    for word in cue.get('words', []):
        word['start'] = round(word['start'] + offset, 3)
        word['end'] = round(word['end'] + offset, 3)
report = {'source': 'C:/Users/HP/Downloads/Prasad Tech.mp4',
          'warning': {'start': 51.44, 'end': 52.19},
          'context': {'start': offset, 'end': 54.19},
          'humanVerified': False, 'seconds': round(time.perf_counter()-start, 3), 'result': result}
(root/'flagged-interval-recognition.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'seconds': report['seconds'], 'text': result['rawTranscript'],
                  'words': [w for c in result['cues'] for w in c.get('words', [])]}, ensure_ascii=False), flush=True)

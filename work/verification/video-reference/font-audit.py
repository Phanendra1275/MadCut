import json,collections
from pathlib import Path
items=json.loads(Path('outputs/chatcut/public/templates/index.json').read_text(encoding='utf-8'))
fonts=collections.defaultdict(list)
for t in items:
 for f in set(p.get('font') for p in t['properties'] if p.get('font')):fonts[f].append(t['name'])
print(json.dumps(fonts,indent=2))

from pathlib import Path
s=Path('outputs/chatcut/app/page.tsx').read_text(encoding='utf-8')
a=s.index('Apply \'');print(s[a-550:a+900])

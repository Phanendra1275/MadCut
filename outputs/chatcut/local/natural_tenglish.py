"""Spoken morphology over native tokens, with context and protected spellings."""
import re
from chat_spelling import hint
from spelling_profile import roman_words
SYSTEM="""You are an expert Telugu speech and Tenglish caption editor.
First understand the intended Telugu meaning from the speech-to-text output.
Correct obvious Telugu transcription and spelling errors without changing the speaker's meaning.
Then generate natural Tenglish using Roman/English characters.
Tenglish must resemble the way a Telugu speaker naturally types on WhatsApp and social media.
Do not perform literal English translation.
Do not use rigid character-by-character transliteration.
Do not unnecessarily use formal Telugu grammar.
Preserve commonly used English words inside Telugu sentences.
Preserve names, brands, places, numbers and technical terms.
Use conversational Telugu endings naturally, such as: velthunnav chesthunnav vasthunnav chesav vellav vastha veltha chestha unna unnav.
Never invent words that were not spoken.
When uncertain, preserve the original meaning rather than hallucinating.
Return only the corrected caption."""
from pathlib import Path
import json
_RULES=json.loads((Path(__file__).parent/'data/tenglish-normalization.json').read_text(encoding='utf-8'))
NATURAL=_RULES['natural'];FORMAL=_RULES['formal']

def generate(text,mode='Natural',context='',glossary=None):
    preferred=glossary if glossary is not None else roman_words()
    spans=list(re.finditer(r'[\u0c00-\u0c7f\u200c\u200d]+',text));out=[];position=0
    for index,match in enumerate(spans):
        out.append(text[position:match.start()]);native=match[0];word=native.replace('\u200c','').replace('\u200d','')
        # Approved names and brand spellings take precedence over contractions.
        if native in preferred:value=preferred[native]
        elif mode=='Formal' and word in FORMAL:value=FORMAL[word]
        else:
            value=hint(native,'Tenglish',preferred)
            if mode!='Formal':
                following=spans[index+1][0] if index+1<len(spans) else ''
                quoted_name=following in {'పేరు','అనే','అని'} and re.search(r'పేరు|పిలుస్తారు',context)
                if word in NATURAL:value=NATURAL[word]
                elif not quoted_name:
                    # Inflected Telugu verbs, never a regex over Latin names.
                    if word.endswith(('తున్నాను','టున్నాను','దున్నాను')):value=re.sub(r'(thunna|tunna|dhunna|dunna)a?nu$',r'\1',value)
                    elif word.endswith(('తున్నావు','టున్నావు','దున్నావు')):value=re.sub(r'(thunn|tunn|dhunn|dunn)aa?vu$',r'\1av',value)
                    elif word.endswith(('న్నావు','ప్పావు','ళ్లావు')):value=re.sub(r'aa?vu$','av',value)
        out.append(value);position=match.end()
    out.append(text[position:]);value=''.join(out).replace('\u200c','').replace('\u200d','').strip();return re.sub(r'\bun\s+boxings?\b',lambda m:m[0].replace(' ',''),value,flags=re.I)

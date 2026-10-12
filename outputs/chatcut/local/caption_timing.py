"""Keep faithful Tenglish connected to native speech, without timing paraphrases."""
import re,json
from functools import lru_cache
from difflib import SequenceMatcher
from chat_spelling import hint, TELUGU_CHAT
from spelling_profile import roman_words

def phonetic(text):
    text=re.sub(r'[^a-z0-9]','',text.lower())
    text=text.replace('x','ks').replace('sh','s').replace('ch','c').replace('th','t').replace('dh','d').replace('ph','f')
    return re.sub(r'(.)\1+',r'\1',text)

@lru_cache(maxsize=4096)
def variants(word,glossary):
    from natural_tenglish import generate
    preferred=json.loads(glossary)
    return [phonetic(hint(word,'Tenglish',preferred)),phonetic(generate(word,'Natural',glossary=preferred)),phonetic(generate(word,'Formal',glossary=preferred))]

def references(source,target):
    glossary=json.dumps(roman_words(),sort_keys=True,ensure_ascii=False)
    rows=[variants(w,glossary) for w in source.split()]
    b=''.join(phonetic(w) for w in target.split())
    candidates=[[w[i] for w in rows] for i in range(3)]
    return max(candidates,key=lambda words:SequenceMatcher(None,''.join(words),b,autojunk=False).ratio())

def faithful(source,target):
    expected_words=references(source,target)
    a=''.join(expected_words)
    b=''.join(phonetic(word) for word in target.split())
    if '?' in source and '?' not in target:return False
    for term in re.findall(r'[A-Za-z][A-Za-z0-9_-]*|\d+(?:[.,]\d+)*',source):
        if not re.search(r'(?<![A-Za-z0-9_-])'+re.escape(term)+r'(?![A-Za-z0-9_-])',target):return False
    negative_endings=('లేదు','లేను','లేడు','లేవు','కాదు','వద్దు','కూడదు','కుదరదు')
    target_words=[phonetic(w) for w in target.split()]
    for word in source.split():
        native=re.sub(r'[^\u0c00-\u0c7f]','',word)
        if native.endswith(negative_endings):
            expected=phonetic(hint(native,'Tenglish'))
            if not any(SequenceMatcher(None,expected,w,autojunk=False).ratio()>=.9 for w in target_words):return False
    match=SequenceMatcher(None,a,b,autojunk=False)
    if not a or not b or match.ratio()<.84:return False
    # A high whole-sentence score can hide a missing short spoken word.
    covered={start+i for start,_,size in match.get_matching_blocks() for i in range(size)}
    cursor=0
    for word,value in zip(source.split(),expected_words):
        if value and sum(i in covered for i in range(cursor,cursor+len(value)))/len(value)<.7:return False
        cursor+=len(value)
    target_covered={start+i for _,start,size in match.get_matching_blocks() for i in range(size)}
    cursor=0
    for word in target.split():
        value=phonetic(word)
        if value and sum(i in target_covered for i in range(cursor,cursor+len(value)))/len(value)<.6:return False
        cursor+=len(value)
    return True

def speech_words(original,text):
    """Map Latin spelling onto native word anchors only when phonetics agree.

    One-to-one words inherit the whole native interval. Compound word splits
    use positions within the native anchor; these are explicitly mapped times,
    not a claim of independent forced alignment of a translated language.
    """
    native=original.get('words') or []
    if not native or not faithful(original['text'],text):return None
    target_words=text.split()
    glossary=json.dumps(roman_words(),sort_keys=True,ensure_ascii=False)
    if len(native)==len(target_words) and all(max(SequenceMatcher(None,v,phonetic(t),autojunk=False).ratio() for v in variants(w['word'],glossary))>=.84 for w,t in zip(native,target_words)):
        return [{**w,'word':t} for w,t in zip(native,target_words)]
    source='';anchors=[]
    for word,value in zip(native,references(' '.join(w['word'] for w in native),text)):
        if not value:continue
        source+=value
        for i in range(len(value)):
            anchors.append((word['start']+(word['end']-word['start'])*i/len(value),word['start']+(word['end']-word['start'])*(i+1)/len(value)))
    target_words=text.split();target='';spans=[]
    for word in target_words:
        value=phonetic(word)
        if not value:return None
        a=len(target);target+=value;spans.append((a,len(target),word))
    match=SequenceMatcher(None,source,target,autojunk=False)
    if match.ratio()<.84:return None
    mapping={b+i:a+i for a,b,n in match.get_matching_blocks() for i in range(n)}
    result=[];previous=original['start']
    for a,b,word in spans:
        positions=[mapping[i] for i in range(a,b) if i in mapping]
        if len(positions)/(b-a)<.6:return None
        start=max(original['start'],previous,anchors[min(positions)][0]);end=min(original['end'],anchors[max(positions)][1])
        if end<=start:return None
        result.append({'word':word,'start':round(start,3),'end':round(end,3)});previous=end
    return result

def polish_tenglish(value):
    return re.sub(r'\bun\s+boxings?\b',lambda m:m[0].replace(' ',''),value,flags=re.I)

def safe_tenglish(text):
    """Use the native pronunciation if a writer replaces or omits dialogue."""
    value=hint(text,'Tenglish')
    value=polish_tenglish(value)
    for old,new in {'raaledu':'raledu','vasthunnaavaa':'vasthunnava','vasthunnaava':'vasthunnava','ekkadiki':'ekkadiki','velthunnaavu':'velthunnav','nimishaallo':'nimishallo'}.items():
        value=re.sub(r'\b'+re.escape(old)+r'\b',new,value,flags=re.I)
    return value

def canonical_tenglish(source,value):
    """Enforce known chat/loanword spellings without guessing unknown words."""
    lexicon={**TELUGU_CHAT,**roman_words()};expected_words=safe_tenglish(source).split();latin_words=value.split()
    if len(expected_words)!=len(latin_words):return polish_tenglish(value)
    known=set(lexicon.values())
    for i,(original,latin) in enumerate(zip(expected_words,latin_words)):
        expected=re.sub(r'[^A-Za-z0-9-]','',original)
        if expected not in known:continue
        if SequenceMatcher(None,phonetic(expected),phonetic(latin),autojunk=False).ratio()<.75:continue
        punctuation=re.search(r'[^A-Za-z0-9]+$',latin)
        latin_words[i]=expected+(punctuation[0] if punctuation else '')
    return polish_tenglish(' '.join(latin_words))

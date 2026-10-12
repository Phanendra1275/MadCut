"""Pronunciation hints for the contextual chat-language writer."""
import re
import unicodedata
from indic_transliteration import sanscript
from spelling_profile import roman_words

# Conventional chat spelling and English loanwords. Keep వ/బ and negation
# distinct; never "correct" one Telugu word into a different spoken word.
TELUGU_CHAT={
 'ఉన్నాడు':'unnadu','ఉన్నావు':'unnav','చేస్తున్నావు':'chesthunnav','వస్తున్నాను':'vasthunna','వస్తాను':'vastha','అవును':'avunu','ఎక్కడ':'ekkada','ఏం':'em','రేపు':'repu','చేసి':'chesi','పంపు':'pampu','తెలియదు':'teliyadu','మీటింగ్':'meeting','ఎడిట్':'edit','హైదరాబాద్':'Hyderabad','విశాఖపట్నం':'Visakhapatnam','ఇన్స్టాగ్రామ్':'Instagram','యూట్యూబ్':'YouTube','చాట్‌జీపీటీ':'ChatGPT',
 'డిజైన్':'design','వెబ్‌సైట్':'website','వెబ్సైట్':'website','అప్‌లోడ్':'upload','అప్లోడ్':'upload','రెడీ':'ready','సెండ్':'send','చెయ్యి':'cheyyi','అయ్యిందా':'ayyinda',
 'ఆబ్జెక్ట్':'object','ఆబ్జెక్టు':'object','ఆబ్జెక్టులు':'objects','ఆబ్జెక్ట్‌లు':'objects','సాఫ్ట్‌వేర్':'software','సాఫ్ట్వేర్':'software','ఫైల్':'file','ఫైల్స్':'files','ప్రాజెక్ట్':'project','మోడల్':'model','డేటా':'data','అప్లికేషన్':'application','టైమ్‌లైన్':'timeline','టైమ్లైన్':'timeline','క్యాప్షన్':'caption','క్యాప్షన్స్':'captions',
 'చాలా':'chala','కూడా':'kuda','ఉంది':'undi','ఉన్నాను':'unnanu','ఇప్పుడు':'ippudu','ఇంకా':'inka','ఏంటి':'enti','ఎలా':'ela','ఎందుకు':'enduku','వస్తా':'vastha','రా':'raa','ఆ':'aa','వెళ్తున్నా':'velthunna','చేస్తున్నా':'chesthunna','సరే':'sare','దగ్గర':'daggara','ఉంటా':'unta','పది':'padi','నిమిషాల్లో':'nimishallo',
 'అన్':'un','బాక్సింగ్':'boxing','బాక్సింగ్స్':'boxings','అన్‌బాక్సింగ్':'unboxing','అన్‌బాక్సింగ్స్':'unboxings','అన్\u200dబాక్సింగ్స్':'unboxings',
 'అన్బాక్సింగ్':'unboxing','అన్బాక్సింగ్స్':'unboxings','మొబైల్':'mobile','మొబైల్స్':'mobiles','ఫోన్':'phone','ఫోన్స్':'phones',
 'హార్ట్':'heart','ఫాలో':'follow','వీడియో':'video','వీడియోస్':'videos','కాలేజీ':'college','కంప్యూటర్':'computer','టెక్':'tech','బ్రో':'bro',
 'ఫస్ట్':'first','ఛానల్':'channel','చానల్':'channel','కెమెరా':'camera','ఫేస్':'face','సపోర్ట్':'support','స్టార్ట్':'start',
 'అసిస్టెంట్':'assistant','ప్రొఫెసర్':'professor','స్టూడెంట్':'student','స్టూడెంట్స్':'students','లైఫ్':'life','ట్రై':'try','ఎండ్':'end',
 'లగ్జరీ':'luxury','బీచ్':'beach','రిసార్ట్':'resort','రిసార్ట్స్':'resorts','ఫ్రాన్స్':'France',
 'ఇవన్నీ':'ivanni','అంటే':'ante','అంతే':'anthe','అసలు':'asalu','ఏదో':'edo','వింతగా':'vinthaga','చూసేవారు':'choosevaru','అన్నమాట':'annamata',
 'నువ్వు':'nuvvu','నేను':'nenu','వాళ్ళు':'vallu','వాళ్లు':'vallu','ఎవరి':'evari','మాట':'maata','వినలేదు':'vinaledu','రాలేదు':'raledu','కాదు':'kaadu',
 'కానీ':'kani','అయ్యాను':'ayyanu','ఇక్కడ':'ikkada','అయితే':'aithe','మాత్రం':'matram','నాకు':'naaku','చేయాలనిపించింది':'cheyalanipinchindi',
 'వస్తున్నావా':'vasthunnava','ఈరోజు':'eeroju','ఎక్కడికి':'ekkadiki','వెళ్తున్నావు':'velthunnav','బాగుంది':'bagundi',
}

def hint(text, language, glossary=None):
    script=sanscript.TELUGU if language=='Tenglish' else sanscript.DEVANAGARI
    english=[]
    def protect(match):
        english.append(match[0]);return '__'+str(len(english)-1)+'__'
    if language=='Tenglish':
        # Protect lexical spellings before transliteration, including embedded
        # English spelling. Punctuation remains exactly where the speaker's
        # written transcript puts it.
        lexicon={**TELUGU_CHAT,**(roman_words() if glossary is None else glossary)}
        normalized={k.replace('\u200c','').replace('\u200d',''):v for k,v in lexicon.items()}
        def lexical(match):
            word=match[0]
            plain=word.replace('\u200c','').replace('\u200d','')
            if plain in normalized:return normalized[plain]
            if word in lexicon:return lexicon[word]
            for stem in sorted(['కాలేజీ','కంప్యూటర్','వీడియో','మొబైల్','ఫోన్','బ్రో','మీటింగ్','ఇన్స్టాగ్రామ్','యూట్యూబ్','ఆబ్జెక్టు','ఆబ్జెక్ట్','సాఫ్ట్వేర్','ఫైల్','ప్రాజెక్ట్','మోడల్','డేటా','అప్లికేషన్','టైమ్లైన్','క్యాప్షన్','కెమెరా','ఛానల్','చానల్','స్టూడెంట్','స్టూడెంట్స్','ప్రొఫెసర్','అసిస్టెంట్','లైఫ్','సపోర్ట్'],key=len,reverse=True):
                suffix=plain[len(stem):] if plain.startswith(stem) else None
                endings={'కి':'ki','లో':'lo','తో':'tho','ని':'ni','కు':'ku','ల':'la','లు':'lu','ల్లో':'llo','లకి':'laki'}
                if suffix in endings:return normalized[stem]+' '+endings[suffix]
            return word
        text=re.sub(r'[\u0c00-\u0c7f\u200c\u200d]+',lexical,text)
    text=re.sub(r'[A-Za-z][A-Za-z0-9]*',protect,text)
    value=sanscript.transliterate(text,script,sanscript.IAST)
    value=re.sub(r'[ṁṃ](?=[kgcjṭḍtdśṣslnr])','n',value)
    if language=='Tenglish':
        value=re.sub(r'd(?!h)','dh',value)
        value=re.sub(r't(?!h)','th',value)
    substitutions={'ā':'aa','ī':'ee','ū':'oo','ṛ':'ru','ṝ':'roo','ś':'sh','ṣ':'sh','ṅ':'ng','ñ':'ny','ṁ':'m','ṃ':'m','ḥ':'h','ḻ':'l','ṭ':'t','ḍ':'d','ṇ':'n'}
    for original,replacement in substitutions.items():value=value.replace(original,replacement)
    value=''.join(c for c in unicodedata.normalize('NFKD',value) if not unicodedata.combining(c))
    # IAST c denotes the Telugu/Hindi "ch" sound, not English c.
    value=re.sub(r'\b[a-z]+\b',lambda m:m[0].replace('c','ch'),value)
    if language=='Tenglish':
        # Dental త was handled while IAST still distinguished it from ట.
        # A Latin t rule here loses that distinction and corrupts ఉంటే,
        # చుట్టుపక్కల, పెట్టి, etc. Never aspirate a flattened retroflex t.
        for a,b in {'kaalejee':'college','vidiyo':'video','veediyo':'video','sinimaa':'cinema','broo':'bro'}.items():value=value.replace(a,b)
    for i,word in enumerate(english):value=value.replace('__'+str(i)+'__',word)
    if language=='Tenglish':value=value.replace('\u200c','').replace('\u200d','')
    return value.strip()

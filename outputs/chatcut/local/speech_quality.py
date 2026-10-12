"""Conservative acoustic quality gates; scores are not proof of correctness."""
import math,re
from transcript_correction import acceptable

def quality(segment):
    values={}
    for source,target in [('avg_logprob','averageLogProbability'),('compression_ratio','compressionRatio'),('no_speech_prob','noSpeechProbability')]:
        value=getattr(segment,source,None)
        if isinstance(value,(int,float)) and math.isfinite(value):values[target]=round(value,4)
    return values

def decode_reasons(segment):
    q=quality(segment);reasons=[]
    if q.get('averageLogProbability',0)<-1:reasons.append('uncertain-recognition')
    if q.get('compressionRatio',0)>2.4:reasons.append('repetitive-recognition')
    if q.get('noSpeechProbability',0)>.6 and q.get('averageLogProbability',0)<-1:reasons.append('possible-silence')
    if '\ufffd' in segment.text:reasons.append('invalid-text')
    return reasons

def retry_better(original,candidate,terms=''):
    """Accept an acoustic retry only if it improves score AND preserves wording."""
    before=' '.join(s.text.strip() for s in original);after=' '.join(s.text.strip() for s in candidate)
    if not candidate or not acceptable(before,after,[t.strip() for t in re.split(r'[,\n]',terms) if t.strip()]):return False
    old=[quality(s).get('averageLogProbability') for s in original];new=[quality(s).get('averageLogProbability') for s in candidate]
    if None in old or None in new:return False
    return sum(new)/len(new)>sum(old)/len(old)+.15 and not any(decode_reasons(s) for s in candidate)

def audit(cue):
    reasons=list(cue.get('reviewReasons',[]));words=cue.get('words') or []
    if not words:reasons.append('estimated-word-timing')
    elif any(w['end']-w['start']>2 for w in words):reasons.append('long-word-alignment')
    if (isinstance(cue.get('confidence'),(int,float)) and cue['confidence']<.8) or any(isinstance(w.get('confidence'),(int,float)) and w['confidence']<.55 for w in words):reasons.append('uncertain-word')
    if reasons:cue.update(needsReview=True,reviewReasons=list(dict.fromkeys(reasons)))
    return cue

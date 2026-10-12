"""Bounded acoustic recovery proposals. VAD alone never authorizes new text.

Every proposal requires listening/review. Existing recognition and warnings
stay intact, including when the retry merely moves an already recognized word.
The callback recognizes ONLY the contextual interval and returns local times.
"""
from copy import deepcopy
from transcription_scoring import normalize
from transcript_provenance import fingerprint

POLICY = 'contextual-retry-review-v1'


def recover_gaps(raw, issues, retry, source_id, limit=2):
    attempts = []
    for index, gap in enumerate(issues):
        start, end = gap['start'], gap['end']
        interval = {'start': round(max(0, start-2), 3),
                    'end': round(min(raw['duration'], end+2), 3)}
        original = [deepcopy(c) for c in raw['cues']
                    if c['start'] < interval['end'] and c['end'] > interval['start']]
        evidence = {'policy': POLICY, 'sourceId': source_id, 'gap': deepcopy(gap),
                    'interval': interval, 'originalSegments': original,
                    'applied': False, 'requiresReview': True}
        evidence['id'] = fingerprint([POLICY, source_id, gap, interval])
        if index >= limit or end-start > 3 or end <= start:
            attempts.append({**evidence, 'status': 'deferred', 'reason': 'bounded-retry-budget'})
            continue
        try:
            result = retry(interval['start'], interval['end'])
            candidates = []
            for cue in result['cues']:
                candidate = deepcopy(cue)
                for k in ('start', 'end'):
                    candidate[k] = round(candidate[k]+interval['start'], 3)
                for key in ('words', 'rawWords', 'alignmentWords'):
                    for word in candidate.get(key, []):
                        for k in ('start', 'end'):
                            word[k] = round(word[k]+interval['start'], 3)
                if candidate.get('segment'):
                    candidate['segment'] = {k: round(v+interval['start'], 3)
                                            for k, v in candidate['segment'].items()}
                candidate['sourceSegmentIds'] = [c['id'] for c in original]
                candidate['recoveryAttemptId'] = evidence['id']
                candidates.append(candidate)
            covering = [deepcopy(w) for c in candidates for w in c.get('words', [])
                        if min(end, w['end'])-max(start, w['start']) >= .1]
            existing = {normalize(w) for c in original for w in c['text'].split()}
            novel = [w for w in covering if normalize(w['word']) not in existing]
            if not candidates:
                status, reason = 'inconclusive', 'retry-returned-no-recognition'
            elif not covering:
                status, reason = 'inconclusive', 'retry-has-no-reliable-gap-anchors'
            elif not novel:
                status, reason = 'alignment-disagreement', 'gap-covered-only-by-already-recognized-words'
            else:
                status, reason = 'review-required', 'possible-new-words-require-audio-review'
            evidence.update(status=status, reason=reason, candidates=candidates,
                            gapWords=covering, possibleNewWords=novel,
                            timingBasis='model-alignment-not-human-verified',
                            wordCountChanged=sum(len(c['text'].split()) for c in original) !=
                                             sum(len(c['text'].split()) for c in candidates))
        except Exception as exc:
            # Recovery diagnostics must not discard a successful baseline or gap.
            evidence.update(status='failed', reason='interval-retry-failed', error=str(exc))
        attempts.append(evidence)
    return attempts

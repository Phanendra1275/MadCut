"""Immutable recognition evidence, separate from caption transformations."""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class RecognitionSnapshot:
    # Serialized storage prevents callers/correction functions mutating evidence.
    encoded: str

    @classmethod
    def capture(cls, raw, pipeline):
        evidence = {'schemaVersion': 1, 'kind': 'raw-asr', 'pipelineVersion': pipeline,
                    'language': raw['language'], 'duration': raw['duration'],
                    'speechEngine': raw.get('speechEngine'),
                    'languageProbability': raw.get('languageProbability'),
                    'segments': deepcopy(raw['cues']),
                    'text': raw.get('rawTranscript', ' '.join(c['text'] for c in raw['cues']))}
        evidence['id'] = fingerprint(evidence)
        return cls(json.dumps(evidence, ensure_ascii=False, allow_nan=False))

    def export(self):
        return json.loads(self.encoded)


def source_cues(cues):
    result = deepcopy(cues)
    for cue in result:
        cue.setdefault('sourceSegmentIds', [cue['id']])
        cue.setdefault('sourceTiming', {'start': cue['start'], 'end': cue['end']})
        if cue.get('words'):
            cue.setdefault('sourceWords', deepcopy(cue['words']))
    return result


def caption_version(cues, parent_id, kind='corrected-native'):
    value = {'kind': kind, 'parentId': parent_id, 'segments': deepcopy(cues)}
    return {**value, 'id': fingerprint(value)}


def provenance(snapshot, corrected, attempts=()):
    raw = snapshot.export()
    return {'schemaVersion': 1, 'raw': raw,
            'corrected': caption_version(corrected, raw['id']),
            'recoveries': deepcopy(list(attempts))}

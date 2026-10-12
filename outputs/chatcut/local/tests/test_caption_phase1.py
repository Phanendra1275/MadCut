import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unicodedata
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from transcription_scoring import normalize, tokenize, score
from transcript_provenance import RecognitionSnapshot, source_cues, provenance
from transcript_correction import correct, apply
from timed_subtitles import subtitle_result, fast_tenglish
from caption_flow import prepare
from speech_recovery import recover_gaps


def cue(text='నువ్వు ఎక్కడికి వెళ్తునావ్', start=0, identifier='raw-1', confidence=None):
    words = [{'word': w, 'start': start+i*.5, 'end': start+(i+1)*.5,
              'confidence': confidence} for i, w in enumerate(text.split())]
    return {'id': identifier, 'text': text, 'start': start, 'end': words[-1]['end'],
            'words': words, 'confidence': confidence}


def recognition(cues=None, duration=4):
    cues = [cue()] if cues is None else cues
    return {'language': 'te', 'duration': duration, 'cues': cues,
            'rawTranscript': ' '.join(c['text'] for c in cues),
            'speechEngine': 'installed-model', 'languageProbability': None,
            'speechSpans': [{'start': c['start'], 'end': c['end']} for c in cues]}


class UnicodeScoringTests(unittest.TestCase):
    def test_combining_marks_survive(self):
        text = 'నువ్వు ఎలా ఉన్నావు నాకు తెలియదు చేస్తాను'
        for mark in (c for c in text if unicodedata.category(c).startswith('M')):
            self.assertIn(mark, normalize(text))
        self.assertEqual(normalize(text), text)

    def test_nfc_equivalent_telugu(self):
        text = 'కో కౌ కొ'
        self.assertEqual(score(text, unicodedata.normalize('NFD', text))['WER'], 0)

    def test_punctuation_only(self):
        self.assertEqual(score('నువ్వు ఎలా ఉన్నావు?', '“నువ్వు” ఎలా ఉన్నావు!')['WER'], 0)

    def test_punctuation_is_boundary(self):
        self.assertEqual(tokenize('రా,బ్రో—రేపు'), ['రా', 'బ్రో', 'రేపు'])

    def test_distinct_vowels_not_collapsed(self):
        for a, b in [('వస్తాను', 'వస్తునా'), ('కల', 'కాల'), ('కులం', 'కాలం'), ('నాకు', 'నీకు')]:
            with self.subTest(a=a, b=b):
                self.assertNotEqual(normalize(a), normalize(b))
                self.assertEqual(score(a, b)['wordErrors'], 1)

    def test_whitespace_and_mixed_case(self):
        self.assertEqual(tokenize('  ఈ\nVIDEO\tedit  చేసి '), ['ఈ', 'video', 'edit', 'చేసి'])

    def test_no_unrequested_stemming_or_romanization(self):
        self.assertNotEqual(normalize('వస్తాను'), normalize('vastha'))
        self.assertNotEqual(tokenize('రిసార్ట్ స్'), tokenize('రిసార్ట్స్'))

    def test_empty_reference_has_no_defined_rate(self):
        result = score('', 'హలో')
        self.assertIsNone(result['WER'])
        self.assertIsNone(result['CER'])
        self.assertEqual(result['wordErrors'], 1)


class TranscriptTests(unittest.TestCase):
    def test_snapshot_no_shared_references(self):
        raw = recognition(); original = copy.deepcopy(raw)
        snapshot = RecognitionSnapshot.capture(raw, 'test')
        raw['cues'][0]['text'] = 'mutated'
        snapshot.export()['segments'][0]['words'][0]['start'] = 999
        self.assertEqual(snapshot.export()['segments'], original['cues'])

    def test_corrections_separate_from_raw(self):
        raw = recognition(); before = copy.deepcopy(raw)
        snapshot = RecognitionSnapshot.capture(raw, 'test')
        corrected = correct(source_cues(raw['cues']), model_enabled=False)
        evidence = provenance(snapshot, corrected)
        self.assertEqual(raw, before)
        self.assertIn('వెళ్తునావ్', evidence['raw']['text'])
        self.assertIn('వెళ్తున్నావు', corrected[0]['text'])
        self.assertEqual(evidence['corrected']['parentId'], evidence['raw']['id'])
        self.assertEqual(corrected[0]['sourceSegmentIds'], ['raw-1'])
        self.assertEqual(corrected[0]['sourceWords'], before['cues'][0]['words'])

    def test_snapshot_hash_stable_through_serialization(self):
        raw = recognition(); a = RecognitionSnapshot.capture(raw, 'test')
        b = RecognitionSnapshot.capture(json.loads(json.dumps(raw)), 'test')
        self.assertEqual(a.export()['id'], b.export()['id'])

    def test_romanization_independent_and_timed(self):
        corrected = correct(source_cues([cue()]), model_enabled=False)
        corrected[0]['reviewReasons'] = ['fixture-review']
        before = copy.deepcopy(corrected)
        result = fast_tenglish(corrected)
        self.assertEqual(result[0]['text'], 'Nuvvu ekkadiki velthunnav?')
        self.assertEqual((result[0]['start'], result[0]['end']), (corrected[0]['start'], corrected[0]['end']))
        result[0]['sourceWords'][0]['start'] = 999
        result[0]['reviewReasons'].append('changed-output')
        self.assertEqual(corrected, before)

    def test_unknown_confidence_is_unknown(self):
        raw = recognition(); fixed = correct(raw['cues'], model_enabled=False)
        result = subtitle_result({**raw, 'cues': fixed})
        for version in result['versions'].values():
            for c in version:
                self.assertIsNone(c['qualityScores']['transcriptionConfidence'])
                self.assertIsNone(c['qualityScores']['languageConfidence'])
                self.assertIsNone(c['qualityScores']['correctionConfidence'])

    def test_changed_word_count_keeps_original_anchors(self):
        c = source_cues([cue('నువ్వు వస్తాను')])[0]
        original = copy.deepcopy(c['words'])
        apply(c, 'బ్రో నువ్వు వస్తాను', 'reviewed-test')
        self.assertEqual(c['sourceWords'], original)
        self.assertNotIn('words', c)
        self.assertEqual(c['timing'], 'estimated')

    def test_romanized_compound_marked_estimated(self):
        c = source_cues([cue('ఈ కెమెరాలో వీడియోకి ఫస్ట్ సపోర్ట్ ఉంది')])[0]
        result = fast_tenglish([c])[0]
        self.assertNotEqual(len(result['words']), len(c['words']))
        self.assertEqual(result['timing'], 'estimated')
        self.assertEqual(result['sourceWords'], c['words'])

    def test_segment_id_does_not_depend_on_other_segments(self):
        c = cue('నువ్వు వస్తాను', 1, 'stable')
        alone, _ = prepare([c], 4)
        together, _ = prepare([cue('బ్రో', 0, 'earlier'), c], 4)
        self.assertEqual(alone[0]['id'], together[1]['id'])
        self.assertEqual(alone[0]['sourceSegmentIds'], ['stable'])

    def test_incomplete_word_confidence_not_replaced_with_one(self):
        from speech_engine import aligned_written_words
        segment = SimpleNamespace(text='నువ్వు', words=[
            SimpleNamespace(word='నువ్', start=0, end=.3, probability=.9),
            SimpleNamespace(word='వు', start=.3, end=.5)])
        self.assertNotIn('confidence', aligned_written_words(segment)[0])


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.raw = recognition([cue('నువ్వు', 0), cue('వస్తాను', 1.5, 'raw-2')], 3)
        self.gap = {'start': .5, 'end': 1.5, 'reason': 'speech-without-word-alignment'}

    def test_retry_is_contextual_and_never_applied_silently(self):
        calls = []; before = copy.deepcopy(self.raw)
        def retry(start, end):
            calls.append((start, end))
            return recognition([cue('బ్రో', .6)], end-start)
        result = recover_gaps(self.raw, [self.gap], retry, 'source')
        self.assertEqual(calls, [(0, 3)])
        self.assertEqual(result[0]['status'], 'review-required')
        self.assertFalse(result[0]['applied'])
        self.assertTrue(result[0]['wordCountChanged'])
        self.assertEqual(self.raw, before)
        self.assertEqual(result[0]['gap'], self.gap)
        self.assertIsNone(result[0]['possibleNewWords'][0]['confidence'])
        self.assertEqual(result[0]['originalSegments'][0]['words'], before['cues'][0]['words'])

    def test_existing_word_is_alignment_disagreement(self):
        result = recover_gaps(self.raw, [self.gap], lambda a,b:recognition([cue('వస్తాను', .7)]), 'source')
        self.assertEqual(result[0]['status'], 'alignment-disagreement')
        self.assertFalse(result[0]['possibleNewWords'])
        self.assertFalse(result[0]['applied'])

    def test_failed_retry_keeps_gap(self):
        def failed(a,b):raise RuntimeError('test failure')
        result = recover_gaps(self.raw, [self.gap], failed, 'source')
        self.assertEqual(result[0]['status'], 'failed')
        self.assertEqual(result[0]['gap'], self.gap)

    def test_budget_keeps_unattempted_warning(self):
        calls = []
        result = recover_gaps(self.raw, [self.gap]*3, lambda a,b:calls.append((a,b)) or recognition([]), 'source', limit=1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[-1]['status'], 'deferred')

    def test_rebased_acoustic_timestamps_not_interpolated(self):
        raw = recognition([cue('నువ్వు', 10), cue('వస్తాను', 12, 'next')], 20)
        gap = {'start':10.5, 'end':12, 'reason':'speech-without-word-alignment'}
        result = recover_gaps(raw, [gap], lambda a,b:recognition([cue('బ్రో', 2.2)]), 'source')[0]
        self.assertEqual(result['interval'], {'start':8.5, 'end':14})
        self.assertEqual(result['candidates'][0]['words'][0]['start'], 10.7)
        self.assertEqual(result['timingBasis'], 'model-alignment-not-human-verified')


class ServiceContractTests(unittest.TestCase):
    def test_api_preserves_raw_and_progress_without_llm_or_audio_decode(self):
        import service
        raw = recognition(); baseline = copy.deepcopy(raw); job = {}
        def worker(request, callback=None):
            if callback:callback({**raw, 'processedSeconds':raw['duration']})
            return copy.deepcopy(raw)
        temp_root=Path(__file__).resolve().parents[2]/'.local/test-temp'
        temp_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as tmp:
            path = Path(tmp)/'input.wav';path.write_bytes(b'fixture')
            with patch.object(service, 'CACHE', Path(tmp)/'cache'), patch.object(service, 'recognition_key', return_value='fixture'), patch.object(service, 'speech_request_worker', side_effect=worker), patch.object(service, 'stop_engines'), patch.object(service, 'record_pids'), patch.object(service.spelling_profile, 'correct_native', return_value=0):
                result = service.transcribe(path, 'te', job)
                self.assertEqual(result['provenance']['raw']['segments'], baseline['cues'])
                self.assertEqual(result['rawTranscript'], baseline['rawTranscript'])
                self.assertIn('వెళ్తున్నావు', result['cues'][0]['text'])
                self.assertEqual(result['versions']['Tenglish'][0]['text'], 'Nuvvu ekkadiki velthunnav?')
                self.assertEqual(job['partial']['provenance'], result['provenance'])
                self.assertFalse(path.exists())
                cached = json.loads((Path(tmp)/'cache/fixture.json').read_text(encoding='utf-8'))
                self.assertEqual(cached, baseline)

    def test_tenglish_endpoint_does_not_recorrect_canonical(self):
        import service
        canonical = [cue()]; baseline = copy.deepcopy(canonical)
        with patch.object(service.transcript_correction, 'correct', side_effect=AssertionError('Romanization must not correct canonical text')):
            result = service.translate({'cues':canonical,'sourceLanguage':'te','language':'Tenglish','tone':'Accurate'}, {})
        self.assertEqual(canonical, baseline)
        self.assertEqual(result['nativeCues'], baseline)
        self.assertEqual((result['cues'][0]['start'],result['cues'][0]['end']), (canonical[0]['start'],canonical[0]['end']))

    def test_gap_warning_survives_recovery_and_speech_cache(self):
        import service
        raw=recognition([cue('నువ్వు',0),cue('వస్తాను',1.5,'raw-2')],3)
        raw['speechSpans']=[{'start':0,'end':3}]
        def diagnostic(raw,issues,retry,source_id):
            return recover_gaps(raw,issues,lambda a,b:recognition([cue('వస్తాను',.7)]),source_id)
        temp_root=Path(__file__).resolve().parents[2]/'.local/test-temp'
        temp_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as tmp:
            with patch.object(service,'CACHE',Path(tmp)/'cache'),patch.object(service,'recognition_key',return_value='fixture'),patch.object(service,'speech_request_worker',return_value=copy.deepcopy(raw)) as worker,patch.object(service,'recover_gaps',side_effect=diagnostic) as recovery,patch.object(service,'stop_engines'),patch.object(service,'record_pids'):
                first=Path(tmp)/'first.wav';first.write_bytes(b'fixture')
                result=service.transcribe(first,'te',{})
                second=Path(tmp)/'second.wav';second.write_bytes(b'fixture')
                cached=service.transcribe(second,'te',{})
                self.assertTrue(result['timelineQuality']['uncoveredSpeech'])
                self.assertEqual(result['timelineQuality'],cached['timelineQuality'])
                self.assertEqual(result['provenance'],cached['provenance'])
                self.assertEqual(result['provenance']['raw']['segments'],raw['cues'])
                self.assertFalse(any(a['applied'] for a in result['provenance']['recoveries']))
                self.assertEqual(worker.call_count,1)
                self.assertEqual(recovery.call_count,1)


if __name__ == '__main__':
    unittest.main(verbosity=2)

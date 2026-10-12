# Acceptance benchmark status

The required 160 real clips are unavailable. The user confirmed there are no videos for this benchmark currently. All eight groups of 20 in acceptance-dataset.json are explicitly missing references; none are marked passed. Existing three labeled read-speech samples are supplemental regression evidence, not a substitute for conversations, slang, noisy audio or code-switching.

For each benchmark clip supply an audio/video path, checked Telugu transcript, natural Tenglish reference, checked word boundaries and reviewer attribution. Raw ASR is recorded during the run. Compare WER/CER, token omissions, protected names/numbers, timing errors, VAD coverage warnings and final rendered frames. Set acceptance thresholds with the reviewer; a model's probability is not an accuracy certificate. Human review remains necessary for meaning, colloquial spelling, names and style.

Current repeatable checks: check-flow.py; ../test-natural-tenglish-v2.py; check-live.py; the browser/export verification described in CAPTION-FOUNDATION-UPDATE.md. Missing datasets are not silently skipped as passing tests.

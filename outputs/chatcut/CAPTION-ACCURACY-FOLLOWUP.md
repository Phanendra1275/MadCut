# Telugu/Tenglish accuracy follow-up

Implemented and tested 8 October 2026. Local processing remains free; no external AI service or new model download was added.

## Concrete fixes

- Fixed a reproduced Roman spelling bug: Telugu `ఆబ్జెక్ట్‌ల` previously produced `aabjekt‌la`, including an invisible script joiner. It now produces `object la`. Joiners are retained in native Telugu and removed from Roman output only.
- Added conventional spellings and productive Telugu suffix handling for common technical loanwords: object, file, project, software, model, data, application, timeline and caption. Original Latin names/numbers remain protected. This supplements the existing speech/morphology engine; it is not a claim of model training.
- Speech resync now refreshes both Telugu and Tenglish tracks and their word anchors together. Previously the native track was refreshed while Tenglish could keep stale timings. Natural/WhatsApp/Formal and emoji preferences are retained during resync; individual native look overrides survive.
- Conservative audio-based end refinement avoids holding the final word through trailing silence. It requires speech detection plus consecutive energy evidence, keeps a tail margin, and searches only the final word region. It changes alignment, not text.
- Missing word alignment, long word intervals and suspicious acoustic recognition are marked for review. Roman captions that cannot map reliably to native speech are explicitly marked as estimated timing.
- Recognition now retains segment average log probability, compression ratio and no-speech probability. These are diagnostic model scores, not calibrated correctness percentages.
- Added an acoustic decoder retry limited to two uncertain windows per upload. It reuses the encoder state. Healthy windows skip retries. Dense token-limit windows use existing split recovery instead. Changes require a better score plus protected meaning/name/number checks; otherwise the original remains.
- Progressive correction results are reused within a job when caption text, adjacent context and protected terms are unchanged. This avoids repeating correction work for captions already streamed to the editor.

## Verification and limits

- Native reference benchmark: 3 clips, 42 reference words, 4 word edits (9.52% WER), 1 character edit (0.38% CER). Scores are unchanged from the existing reference benchmark. Word-boundary differences contribute to word errors. This is a small formal-speech test, not evidence of general or perfect colloquial accuracy.
- Actual 69.9-second Prasad video: 55 captions, real progressive updates, first captions at 5.766 s and completion at 88.719 s in this run. Recognition diagnostics recorded 19 decoded windows, 5 token-limit recovery splits and zero acoustic retries. Earlier measurements were faster; this update does not establish a speed improvement across runs.
- Delayed Telugu audio: first caption at 2.232 s; final caption ends at 8.012 s rather than extending through trailing silence. Text correction and Roman conversion retain native cue intervals.
- Real browser native/Tenglish resync passed. Both tracks share updated cue intervals and Roman word anchors. Reload persistence passed. The synchronized captions exported in a real H.264/AAC MP4, 720x900, 30 fps; an extracted frame shows the expected `object la` caption.
- Tests passed for natural/formal/WhatsApp output, mixed English, names/numbers, negation preservation, repeated speech, missing timing warnings, correction memo reuse, anchor preservation and technical suffixes. TypeScript check, production build and Python compilation passed.
- Retry acceptance is tested with controlled cases; this high-confidence real-video run did not exercise a successful retry.

Use Generate captions for a fresh transcript. For an existing native transcript, use Sync captions to speech to refresh both native and Roman timing. Review uncertain wording and names. Audio alone plus high model confidence cannot guarantee every spoken word; no weights were fine-tuned in this update.

## Sources and evidence

The quality fields and decoding checks follow the installed faster-whisper implementation and its [official source](https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py). Local thresholds and guarded retry acceptance are application policies, not a guarantee made by that project.

Evidence is saved in `verification/caption-accuracy/`: reference benchmark, real-video progress/results, regression checks, synchronized project and rendered frame.

# MadCut: caption pipeline audit and staged implementation plan

Audit date: 12 October 2026. Scope: the existing local application in `outputs/chatcut`, its processing services, installed model configuration, and verification artifacts in `work/verification`. No application code was changed during this audit. This document distinguishes source inspection, checks run today, and older recorded results.

## Assessment

Keep the existing React/Vite frontend, FastAPI service, IndexedDB projects, shared Canvas caption renderer, and native FFmpeg encoder. The requested architecture is substantially present already. The priority is to strengthen provenance, acoustic coverage, alignment validation, evaluation, and resource management rather than replace the app or change only a prompt.

There is insufficient representative, human-verified Telugu evidence to select a production ASR winner or claim consistently accurate captions. Retain the installed Telugu model as the provisional baseline while comparing alternatives under controlled conditions. Local inference remains the default to preserve the user's no-API-fees requirement.

## 1. Existing implementation

| Area | Observed implementation and evidence |
| --- | --- |
| Active application | `local/main.tsx`, `local/app.tsx`, `app/page.tsx`: React 19 / TypeScript / Vite SPA, hash-based navigation. FastAPI serves the built SPA. Next, Drizzle, and Cloudflare dependencies exist but are not the active local runtime. |
| Projects and uploads | IndexedDB retains projects and uploaded files. Browser extension/playback validation and a 200 MB upload limit exist. Server uploads are written to disk in chunks. No active multi-user authentication or cloud storage is wired into this local app; the unused Next auth helper is not evidence of local authentication. |
| Speech | `local/speech_engine.py`: audio decoded once to mono 16 kHz, conservative preprocessing, Silero VAD, explicit Telugu selection by default, persistent faster-whisper worker. Telugu uses local `vasista22/whisper-telugu-medium`, converted to int8; multilingual large-v3 and small language detector are also installed. |
| Timing | Telugu uses VAD-guided decoding windows, context overlap, word ownership at window boundaries, and Whisper attention-based word timestamps. `caption_flow.py` groups words, repairs short VAD-supported gaps, flags uncovered speech, and validates ordering. This is not fixed-duration caption slicing. |
| Correction | `transcript_correction.py`: spelling rules, context-sensitive cache, protected terms, confidence/suspicion gates, optional local Qwen3-1.7B correction, and conservative acceptance checks. Only four uncertain passages per correction call receive model processing, with two concurrent requests. |
| Romanization | `natural_tenglish.py`, `chat_spelling.py`, `timed_subtitles.py`: approved spellings, English loanwords, conversational morphology, limited context rules, and Indic transliteration fallback. Four-thread processing and an in-memory cache exist. Natural, WhatsApp, and Formal modes exist. The fast path is rule based; its system-prompt constant does not itself run a contextual language model. |
| Translation | Separate `/api/translate` route; local Sarvam Translate and Qwen3-8B. English translation does not require sending the video to an LLM. |
| Editor and presets | Video preview, playback/seek, timeline, editable captions and times, global look, font/size/color/position, and word animations exist. There are 55 built-in preset entries, including 33 web recreations associated with supplied MOGRT sources. Arbitrary Adobe MOGRT execution is not implemented. |
| Export | `lib/render-caption.ts` draws preview and export captions. `lib/media.ts` creates caption PNG frames; `local/export_video.py` composites them with native FFmpeg. Video export is a real burned-in encode, not the original video plus a browser overlay. Subtitle exports and captions-only options also exist. |
| Jobs | `/api/jobs` reports status and partial transcription revisions. UI polls and displays preliminary captions. A single background worker services transcription, translation, trimming, and encoding. Jobs live only in memory. |

## 2. Prioritized findings

### P0: establish trustworthy accuracy and timing

1. **Accuracy measurement has a Unicode bug in one runner.** `work/verification/caption-foundation/check-live.py` removes punctuation using a pattern that also strips Telugu combining vowel marks. Distinct spellings can become identical during scoring. Consolidate scoring around Unicode NFC and punctuation-category handling that retains marks. An older benchmark helper already uses a safer approach; reuse one tested implementation.

2. **The editor does not persist an immutable raw ASR baseline.** The service returns raw transcript information, but `app/page.tsx` saves corrected native cues into `Project.original`; `lib/captions.ts` has no complete raw-ASR field. Individual `rawText` annotations cover some corrections only. Preserve raw segment/word data separately from corrected native captions, Romanization, translation, and user edits; add an original-versus-corrected view.

3. **Word alignment is implemented, but Telugu timing accuracy is unproven.** `setup-telugu.py` inserts standard Whisper-medium alignment heads into the Telugu-specialized model. `speech_engine.py` then adds attention-derived timestamps after decoding without timestamps. This is a plausible implementation, not a Telugu alignment benchmark. Compare against manually checked word boundaries before choosing another aligner. Do not assume a generic WhisperX/CTC aligner supports Telugu well.

4. **A recorded coverage warning remains unresolved.** The stored 69-second creator test flags uncovered VAD speech at 51.44–52.19 seconds. VAD is imperfect, so this is a review target rather than proof of a missing word. Listen to that interval and its context, inspect the raw recognition, and selectively retry the acoustic interval when justified. Extending caption display across it cannot recover unrecognized speech.

5. **Correction deliberately cannot recover substantial ASR errors.** Acceptance requires equal token counts and high per-word/whole-caption similarity. This protects meaning and timestamps, but rejects most missing words, merged/split words, or major substitutions. High-confidence ASR errors can also pass the suspicion gate. Preserve this conservative default; use reviewed, bounded acoustic retries for omissions and uncertainty. Any accepted word-boundary change needs an explicit mapping back to original timing rather than fabricated anchors.

### P1: reliability, latency, and media limits

6. **Server media preflight is incomplete.** `/api/transcribe` checks extension, emptiness, and size, but does not first probe streams, actual duration, dimensions, or audio presence. Audio decoding loads the entire track into RAM before later caption limits apply. Add bounded FFprobe validation and meaningful no-audio/unsupported/duration errors before inference. Document matching frontend/backend limits.

7. **Long animated exports are browser-memory constrained.** The browser accumulates PNG frames and a ZIP, with a 450 MiB frame-data cap and 18,000 timestamps. The backend allows 500 MiB expanded frames and at most 600 seconds. At 30 fps, animated clips approach the frame cap around ten minutes; at 60 fps, around five. Downloading the final export also creates a whole-file browser Blob. Use bounded frame transfer or a parity-tested background renderer; preserve the shared rendering behavior.

8. **Jobs are ephemeral and one operation can block all others.** One executor handles speech, language, and export. Restart loses job status; there is no general cancellation, durable retry policy, or in-flight deduplication. FFmpeg has no task watchdog. Add a small persistent operational job store, bounded queues, cancellation/timeouts, and GPU-aware scheduling. Keep existing IndexedDB project storage.

9. **English translation has avoidable startup and serial work.** Its general engine startup loads both Qwen3-8B and Sarvam Translate and stops speech/correction workers. Accurate English primarily needs Sarvam. Translation then runs cue by cue without a reusable translation cache or partial translated-caption updates. Load only the needed model; batch nearby text with stable IDs and bounded context; cache transformations and publish completed groups.

10. **Output generation is not fully on demand.** The Telugu path currently generates native and Romanized captions together. Separate canonical transcription from requested transformations while retaining useful cached outputs. Changing text/mode must not rerun audio recognition.

11. **Single-segment audio regeneration is missing.** Text edits preserve block times, but speech resynchronization uploads the video and aligns the full native track. Add a bounded segment retry with context and an explicit option to adjust timing. A changed word count currently removes precise word anchors; expose that limitation rather than presenting estimated animation as measured timing.

### P2: rendering controls and deployment consistency

12. `Look` supports global font/size/fill/position/animation but not user-adjustable outline/background properties. Extend the existing shared renderer and export serialization together. Telugu fonts are present and loaded; each font/render path still needs fresh glyph and exported-frame verification.

13. Local Host/Origin checks and random temporary names are useful loopback protections, not internet-facing authentication. Upload limits do not fully bound multipart parsing before handlers run. Normal cleanup uses `finally`, but restart can leave orphan uploads; export expiry cleanup is opportunistic. Add startup/periodic cleanup confined to owned job directories, request limits, and structured errors before any hosted deployment.

14. Setup reproducibility needs attention: base setup does not install optional correction automatically and can overwrite its configuration; some dependencies/model downloads are less tightly pinned than the Telugu model. Pin tested revisions/checksums, preserve config extensions, and show component readiness separately. Installing models and updating a glossary are not model fine-tuning.

## 3. What has actually been verified

### Checks run during this audit

- Current website returned HTTP 200. `/api/health` reported local/offline mode, speech ready, fast captions enabled, and no API fees. Optional language engines were not loaded (`languageReady: false`), which is not by itself a failure.
- TypeScript type checking passed.
- `check-flow.py`: 23 checks passed.
- `test-natural-tenglish-v2.py`: 21 examples plus guards passed.
- `check-roman-fallback.py`: 11 checks passed.

These are useful regression checks, not a new end-to-end Telugu audio accuracy evaluation. No fresh ASR job, full video export, or hardware comparison was run during this inspection.

### Older artifacts inspected, not rerun today

- The three labeled FLEURS Telugu read-speech clips total approximately 25.2 seconds. A Unicode-safe recalculation of stored outputs gives **4 word edits / 42 reference words = 9.52% WER** and **1 character edit / 264 reference characters = 0.38% CER**. Several word edits reflect compound-word boundaries. The dataset transcripts have not been manually verified by a Telugu reviewer for this project.
- A 9 October creator run recorded the first partial result at **8.312 seconds**, completion at **50.172 seconds** for approximately 69 seconds of media, and 34 caption blocks. Cached runs are not comparable to uncached speech recognition latency.
- Prior browser/export artifacts report shared styling, unchanged caption timing after edits, persistence, subtitle downloads, and a playable three-second 720×1280 H.264/AAC export. The dedicated gap-rendering fixture uses manual caption times; it does not prove audio alignment.
- One stored English translation example preserves segment timing. It does not establish translation quality for slang, negation, names, or long conversations.

**Not verified:** representative conversational/dialect/noise/code-switching ASR quality; Romanized Telugu WER against human references; word-boundary timing error; silence/music hallucination rates; overlapping speakers; long-form reliability; the complete requested no-audio and noisy-media matrix. The 160-clip manifest contains missing-reference placeholders, not passing tests. The user previously confirmed that additional benchmark videos are unavailable.

## 4. Model recommendation and trade-offs

No candidate below has won a controlled representative Telugu benchmark in this project. Compare on the same decoded audio, same source language, and recorded revisions; measure complete pipeline latency as well as recognition speed.

| Candidate | Role, deployment, and trade-off |
| --- | --- |
| Installed Telugu Whisper-medium | Provisional baseline. Already converted, integrated, and locally available. Preserve explicit `te`, VAD, streaming partials, and conservative correction. Existing limited tests cannot establish general superiority. [Model card](https://huggingface.co/vasista22/whisper-telugu-medium). |
| Installed Whisper large-v3 | Existing multilingual comparator and potential selective acoustic fallback. Measure code-switching, omissions, alignment, and compute cost against the Telugu baseline before routing traffic to it. |
| Whisper large-v3-turbo | First speed challenger: its decoder is reduced from 32 to four layers, with an accuracy trade-off according to its model card. Benchmark Telugu and timing on this machine; do not infer Telugu accuracy from general speed claims. Test a pinned compatible faster-whisper conversion in isolation. [Model card](https://huggingface.co/openai/whisper-large-v3-turbo). |
| AI4Bharat IndicConformer 600M | Telugu-capable hybrid CTC/RNNT, MIT model, gated access. Different runtime/integration requirements; evaluate in a separate environment. CTC is a possible alignment research path, not proof of acceptable Telugu word timing. [Model card](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual). |
| IndicTranscribe Core | Newer Indic candidate linked from the IndicConformer card. Native-script output and single-speaker training require particular scrutiny for Latin technical terms, numbers, and overlapping speech. Access and its distinct license/deployment terms need review before hosting. Do not replace the deployed baseline on card claims alone. [Model card](https://huggingface.co/bodhan-ai/indic-transcribe-core). |
| Sarvam hosted ASR | Optional operational comparator if the free-only requirement changes. The current pricing page lists ₹30/audio-hour for standard STT and ₹45/audio-hour for batch with diarization. It is not a permanently free production solution. No customer media was uploaded to a provider for this audit. [Official pricing](https://www.sarvam.ai/api-pricing), [STT documentation](https://docs.sarvam.ai/api/api-guides-tutorials/speech-to-text/overview). |

Local models avoid per-request API fees but still consume hardware, storage, electricity, and maintenance. Benchmark cold-start and warm throughput, peak RAM/VRAM, CPU fallback, and model-swap costs before setting limits. Do not promise near-real-time performance on every user's machine.

## 5. Incremental implementation plan and exit gates

| Stage | Changes in the existing project | Verification required before advancing |
| --- | --- | --- |
| 1 — Audit | This document only; preserve application code and UI. | Separate fresh checks, historical evidence, and missing evidence. Completed for the inspected local implementation. |
| 2 — Benchmark and select | Consolidate Unicode-safe metrics under `work/verification`; record dataset provenance, model/config revisions, language, cold/warm state, and hardware. Add ASR adapters only where needed. | Paired native WER/CER, omissions, names/numbers/code-switching, first partial latency, total latency/audio duration, resource peaks, silence false positives, and manually checked timing median/p95. Romanized references scored separately with an agreed spelling policy. Report coverage gaps honestly; three read clips are only a regression baseline. |
| 3 — Native Telugu first | `local/service.py`, `speech_engine.py`, `caption_flow.py`, `lib/captions.ts`, `app/page.tsx`: media probe, immutable raw transcript/anchors, bounded audio handling, persisted provenance, interval-level recovery, visible uncertainty and coverage warnings. | Native recognition and original/corrected comparison survive reload; word accounting and chunk boundaries hold; no unrelated content added during silence; invalid/no-audio inputs fail clearly. Synthetic silence/no-audio fixtures test mechanics, not real-world Telugu accuracy. |
| 4 — Romanized Telugu | `natural_tenglish.py`, `chat_spelling.py`, normalization data, `timed_subtitles.py`, mode controls: corrected Telugu as input, Natural default, protected vocabulary and cached transforms. Keep Formal and faithful WhatsApp options. | Native and Romanized block times match exactly; mixed English/names/numbers survive; unknown terms remain reviewable; no English translation or added slang/emojis. Validate conversational examples and human-reviewed real audio separately. |
| 5 — English translation | `local/service.py` and frontend translation updates: on-demand translator loading, context-bounded batches with stable IDs, cache, partial results, segment-only regeneration. | Translation keeps source boundaries, names, numbers, negation, and meaning; language switching never retranscribes audio. Do not claim translated English words have independently aligned acoustic timestamps. |
| 6 — Editor and export | Extend `Look`, shared Canvas renderer, font loading, editor comparison/timing tools, and bounded export transfer. Preserve templates, transformations, and existing subtitle exports. | Frame comparisons between preview/export at word transitions and silence; Telugu glyphs; 720p/1080p and original aspect ratio; actual burned-in pixels, audio sync, download/playback. Text edits preserve timing; explicit timing edits revalidate anchors. |
| 7 — Reliability and deployment | Durable local job records, bounded scheduling with shared-GPU arbitration, deduplication, retry/cancel/watchdog behavior, safe orphan cleanup, dependency/model manifests, setup docs. | Restart/retry/cancellation/resource-limit tests; regression upload→ASR→edit→export flow; noisy/multi-speaker/music/long-video cases as real reviewed material becomes available. Missing references remain an explicit acceptance limitation. |

### Data and timing contract

Retain immutable raw ASR segments and words with model provenance and real confidence where available. Derive corrected native captions, Romanized captions, and translations as separate versions linked by stable IDs. Keep unknown confidence as unknown; do not invent probability scores. Preserve original segment timing during text transformation. When word counts change, retain original anchors separately and mark mapped/estimated animation timing explicitly. Timing repair should be traceable, avoid overlaps, and never conceal missing recognition by holding unrelated text over speech.

### Immediate work order

1. Repair the scoring harness and establish the reproducible baseline.
2. Preserve raw ASR in project data and expose comparison/uncertainty.
3. Investigate the flagged speech interval and quantify word alignment before tuning acoustic retries.
4. Add media preflight and safe bounds, then verify native Telugu end to end.
5. Improve Romanization on that verified native track, then translation and export reliability.

No new template features, UI rewrite, paid provider migration, or model fine-tuning is justified before these foundations have evidence. Model selection remains provisional until representative reviewed Telugu evaluation is possible.

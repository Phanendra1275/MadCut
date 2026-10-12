# Caption fundamentals update — 9 October 2026

Implemented and running locally. **Full accuracy acceptance remains open.** No new template features were added in this update.

## Causes found and changes made

- Caption grouping used a three-word limit and could split a short spoken phrase. Grouping now uses preserved word anchors, punctuation, conversational boundaries, actual pauses, character limits and duration. Defaults are six words, two lines, 36 characters per line and four seconds. Reading limits are configurable; unusually short/long captions are marked for review instead of extending them across silence.
- Preview rendering independently hid text shortly after the final aligned word. That could create a blank interval even after a caption's timeline end had been extended. Speech-backed captions now use their validated presentation interval in the shared preview/export renderer, including keyword effects.
- The old gap action could extend text without speech evidence. Holds now require VAD evidence and are limited to the selected maximum, up to 250 ms. Word anchors remain unchanged. Real silence is retained, and cue intervals do not overlap.
- A continuous VAD region was buffered until every internal inference section finished. Recognition now yields bounded acoustic sections progressively. Overlapping context is assigned using aligned word centers; caption display timing is still determined by speech, not fixed windows.
- Expensive correction could delay preliminary results. Pass one uses spelling rules and cached corrections; the final pass selectively uses the installed small correction model with two concurrent requests and a bounded workload. Uncertain content that cannot safely be corrected remains marked for review.
- Telugu correction now runs on decoded utterances before caption grouping and Romanization. It preserves the source transcript separately, protects supplied names and existing Latin words/numbers, and rejects unsafe model changes.
- A Romanization fallback applied `t → th` after flattening Telugu ట and త into Latin characters. That produced forms such as `chutthupakkala`. The redundant rule was removed; the dental/retroflex distinction is handled before flattening. Familiar English loanwords and their Telugu postpositions now retain spellings such as `camera lo`, `channel`, `first`, `support`, and `students`.
- Natural endings remain guided by an expandable data file plus spoken morphology and context checks. Existing Natural, WhatsApp and Formal modes remain available. No model weights were fine-tuned, and unfamiliar spellings still need review.
- Applying a preset to All now clears old per-caption overrides across language tracks and resets that preset's font, accent and entry defaults. Text edits preserve caption block times and do not call transcription. Invalidated word highlighting is marked for review. Sync/import/trim operations clear stale VAD metadata where timing changes.
- A service-stop path comparison failed when Windows command lines used forward slashes. Normalizing separators now allows the updated owned service to restart correctly.

## Verification

| Check | Observed result |
|---|---|
| Timing/coverage regression suite | 23 checks passed |
| Natural Tenglish examples and semantic guards | 21 examples plus guards passed |
| New dental/retroflex, loanword and name regressions | 11 checks passed |
| Type checking and production build | Passed |
| Editor/browser | No console errors; speech-backed hold visible; actual silence cleared; five caption effects checked |
| Global preset and text edit | All language overrides cleared; block timing unchanged; no transcription/alignment/translation request |
| Draft persistence | Edited caption and attached video restored after reload |
| Upload and Generate buttons | Real cached Telugu/Tenglish results populated all 34 editor captions, with word anchors and the coverage warning |
| Subtitle downloads | SRT, VTT and ASS retained both edited captions; SRT/VTT preserved exact block timestamps |
| Actual export | Three-second H.264/AAC MP4, 720×1280, 30 fps; held caption and silence frames inspected |

The renderer test uses manually specified timing fixtures over supplied footage. It verifies rendering behavior; it is **not** a labeled speech accuracy test.

## Measured speed and accuracy limits

On the supplied 69-second creator video, the first preliminary captions appeared at **6.6 seconds** in one warm run and **8.3 seconds** in the final uncached run. The final run completed in **50.2 seconds**. Earlier buffering delayed the first partial until approximately 43 seconds. This change improves first-result latency; it does not claim a comparable reduction in total recognition time. Cached processing of that video took **0.33 seconds**, reusing acoustic recognition.

The three existing labeled read-speech samples had word error rates of **10%, 20%, and 0%**: four word errors over 42 reference words, or 9.52% aggregated WER. They are small supplemental tests, not evidence of universal accuracy or natural conversational performance.

The creator video has no verified transcript or word boundaries. Its segmentation retained all 158 recognized words, but this does not prove that every spoken word was recognized. VAD coverage flags **51.44–52.19 seconds** for review. This interval is displayed in the editor rather than silently filled with invented text. Some recognition errors, uncommon names, regional usage and Roman spellings may still require editing.

ASR scores are retained where provided. Correction and Tenglish confidence remain unknown (`null`); no artificial confidence values are presented. Compound Roman word splits use mapped native intervals, not independently measured Roman phoneme timing.

## Required benchmark

The requested eight categories of 20 real clips are listed in `../../work/verification/caption-foundation/acceptance-dataset.json`. All 160 slots are explicitly awaiting verified media, Telugu references, natural Tenglish references and checked word boundaries. The user confirmed no additional videos are currently available. None of these slots are counted as passed. Full acceptance cannot be declared until that benchmark and human review are completed.

Repeatable evidence and checks are in `../../work/verification/caption-foundation/`: `check-flow.py`, `check-roman-fallback.py`, `check-live.py`, `check-streaming.py`, `check-browser.mjs`, `check-ui-generation.mjs`, result JSON files, editor screenshots, subtitles and exported MP4. `live-v13-uncached-results.json` preserves uncached measurements; `live-results.json` contains the final cached spelling checks.

## Using the update

MadCut is running at http://127.0.0.1:5173/. Refresh the editor and generate captions again to apply the new pipeline to an existing video. Saved drafts are preserved. Compatible recognition caches are reused; unsupported old cache versions are invalidated. Existing upload, editing, subtitle export, video export and the built-in template library remain available.

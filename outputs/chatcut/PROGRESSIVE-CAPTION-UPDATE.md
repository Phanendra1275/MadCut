# Progressive Telugu and Tenglish caption update

MadCut now sends one uploaded video to local audio decoding, recognizes speech in bounded windows, corrects only transcript text, produces faithful Tenglish, validates caption timing, and publishes results to the editor as they become available. No video is sent to a language model and no paid API is used.

## Implemented behavior

- Telugu-trained Whisper medium remains accelerated on the NVIDIA GPU, with CPU fallback. Speech is extracted once by PyAV into mono 16 kHz audio. Long passages use VAD windows of about 10 seconds, merged up to 12 seconds; short clips retain their complete audio. Windows are intentionally not split blindly at four-second boundaries, which could cut Telugu syllables.
- Recognition keeps word intervals, decoder segment boundaries, selected/detected language and ASR word confidence when available. Scores are model confidence, not calibrated percentages of correctness. Explicitly selected Telugu does not run an unnecessary detector; auto detection retains its language score.
- Actual backend progress is polled every second. Partial native/Tenglish tracks appear while the speech worker continues recognition. Percentages derive from processed audio duration; there is no simulated progress animation. GPU recognition remains sequential to fit local memory. Text conversion uses four workers and model correction uses at most two requests concurrently, reconstructing original order.
- Conservative Telugu spelling rules and approved glossary spellings run first. High-confidence text is preserved. Low-confidence or known suspicious spellings can use the smaller local Qwen3-1.7B model, exclusively on caption text plus nearby transcript context. Its system prompt contains the requested Telugu correction instructions. The installed model uses Q8_0, not the existing 8B creative-language model.
- Model correction is bounded to four uncached candidates per update, an eight-second request timeout and two requests at once. Uncertain candidates beyond the budget stay unchanged for review. Cold model loading can add delay only when deeper correction is needed. Rejected proposals are cached too, avoiding repeated guesses. Corrections preserve cue start/end; same-count spelling changes retain anchors and carry an edited flag. Unsafe word-boundary changes do not receive invented word anchors.
- Acceptance rejects changed Latin names/brands, digits, protected terms, negation, large rewrites, omitted words and additional words. This deliberately limits automatic grammar changes. If uncertain, original text wins. Intentional spoken repetitions are preserved; only proven overlapping recovery duplicates are removed.
- Natural, WhatsApp and Formal Tenglish modes are available. Natural is default. The engine combines common chat spellings, English stem/Telugu suffix handling, spoken-form morphology, user spellings, and surrounding-context cache keys. Accurate Tenglish is not English translation. WhatsApp uses the same faithful spoken wording and does not invent “bro”; optional emojis decorate explicit laughter only. Formal retains fuller endings.
- Telugu-English code switching preserves original Latin text and common loanwords: `college lo`, `video ni edit`, `meeting undi`. Names such as Phanendra, GMRIT, Instagram, YouTube and ChatGPT passed preservation tests. Unknown native-script proper nouns can still need user-approved Roman spellings; do not treat the model as a name database.
- In-memory Roman conversion cache holds 2,048 text/mode/context/glossary combinations. Persistent correction cache retains 1,200 results. Raw recognition cache retains the latest 30 distinct uploads/configurations. Approved spellings are reapplied on cache reads.
- Dense Telugu overlap recovery no longer aborts the entire video when alignment token text is unusable: it decodes the retained interval without overlapping padding. Authoritative transcript text survives; unavailable word alignment remains estimated. Aligned anchors are clipped to validated cue bounds during recognition validation, before language correction.
- The home navigation, Projects header and editor header now use a subtle 8px blur and translucent dark surface. Home/Projects navigation stays visible when scrolling. The orange MadCut palette and editor layout remain in place.

## Verified examples

| Telugu | Natural Tenglish | Formal where different |
| --- | --- | --- |
| నువ్వు ఎక్కడికి వెళ్తున్నావు? | Nuvvu ekkadiki velthunnav? | Nuvvu ekkadiki veltunnavu? |
| ఏం చేస్తున్నావు? | Em chesthunnav? | Em chestunnavu? |
| రేపు కాలేజీలో మీటింగ్ ఉంది | Repu college lo meeting undi | Same mixed wording |
| ఈ వీడియోని edit చేసి నాకు పంపు | Ee video ni edit chesi naaku pampu | Same mixed wording |

A known misspelling `వెళ్తునావ్` became `వెళ్తున్నావు` while retaining the input cue and word intervals. Higher-confidence wording stayed unchanged. Actual small-model requests returned guarded/preserved results for uncertain test text; this is not evidence that it can repair every ASR error.

## Final measurements on this computer

RTX 4050 Laptop GPU (6 GB), 16 GB RAM. Local timings include upload/polling.

| Test | First captions / completion |
| --- | --- |
| Actual 69.9-second Prasad Tech master, uncached | First five captions: 2.61 seconds; complete: 43.11 seconds, 55 cues |
| Separate 3-second clip, model cold, uncached | Complete: 3.312 seconds |
| Actual editor, uncached 21-second excerpt | First captions: 4.689 seconds; complete: 12.388 seconds |

The full video emitted real intermediate progress (12%, 19%, 25%, 37%, 42%, 54%, 63%, 75%, 83%). Native and Tenglish cue intervals matched throughout. Word anchors were valid within cue bounds. Confidence survived recovery where alignment supplied it (49 of 55 cues); six cues had no reliable word confidence. All 55 native captions in this particular high-confidence run were preserved by the correction gate. This is a performance/timing verification, not a human-validated word-error-rate score.

The real UI displayed partial captions before completion, retained both language tracks after reload, defaulted to Natural and kept emoji mode off. Computed navigation blur is 8px. The final speech-timed Karaoke track exported to a real three-second 30 fps MP4. Production build, TypeScript, repetition, Telugu token preservation, mixed-language spelling, negation/name guards and correction-time preservation tests passed.

## Setup and limits

The correction model is already installed for this checkout. For another local setup, run `python local/setup-correction.py`; it downloads the pinned official small model into `.local/models/correction` and updates local configuration. Speech and other optional models are installed with the existing setup scripts. Stopping MadCut also stops its owned correction process.

[Official Qwen3-1.7B GGUF repository](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF) provides the Apache-2.0 model used here. This implementation does not fine-tune weights. A small model may misunderstand Telugu; guards and preservation reduce damage, but neither ASR confidence nor these tests guarantee perfect spelling or interpretation. Review uncertain words and names. SRT supplies subtitle intervals only; sync the native transcript to audio for word-level timing. Other translations and creative tones can still load slower optional models.

Measured latency is specific to this machine and these videos. The local service queues at most three jobs and uses one speech worker; shared hosting/subscription concurrency is not implemented. A smaller recognizer was not substituted merely to promise speed at the expense of Telugu recognition quality.

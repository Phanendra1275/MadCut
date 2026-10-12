# Telugu and Tenglish accuracy update — 8 October 2026

The local app now uses a Telugu-trained speech model, preserves complete Telugu words and sentences, and gives Accurate Tenglish a stricter instruction to preserve the spoken wording. Everything still runs on this computer without paid APIs.

## Use the update

Refresh http://127.0.0.1:5173/. Choose **Spoken language: Telugu** and **Caption tone: Accurate**, then click **Generate captions** to recognize your video again. Generating only another language version reuses the existing transcript, including any old recognition errors. Saved projects are not automatically overwritten.

For uncommon names, places, and brands, add their spellings in **Names & terms**. Correct the Telugu transcript once and use **Use edits for other languages** before generating other versions if a word still needs correction.

## What changed

- Telugu recognition uses [SpeechLab IIT Madras's Telugu-trained Whisper medium](https://huggingface.co/vasista22/whisper-telugu-medium), pinned to revision `bc8626d162a43fd3c9febcc34c27e5780815014e`, converted to CPU int8. English and Hindi retain multilingual Whisper large-v3.
- Extracted speech is PCM WAV, avoiding the previous additional MP3 compression.
- The recognizer keeps the authoritative written words instead of inserting spaces between Telugu word fragments supplied by alignment.
- Telugu is decoded before word alignment. Alignment cannot trigger a second recognition of trailing silence.
- Dense passages that hit the decoder's token limit are recognized again in smaller overlapping windows. This recovers the missing end of a sentence rather than saving partial bytes or a cut word. This limit is also described in the [upstream CTranslate2 issue](https://github.com/OpenNMT/CTranslate2/issues/2074); our recording reproduced exactly 224 output tokens before recovery.
- Telugu-script captions preserve recognized speech in every tone. Accurate Tenglish keeps the sentence and natural Latin spelling, with pronunciation hints and explicit instructions to preserve negatives, questions, names, and numbers.
- Short clips retain their audio boundaries so a quiet syllable is not removed by speech detection.

## Measured speech comparison

Three recordings from the **held-out Telugu FLEURS test split** were used: IDs 1912, 1908, and 1783; approximately 25 seconds total, with male and female speakers. The model card lists FLEURS train and development data among training sources; this comparison uses test data rather than those splits. [Dataset source](https://huggingface.co/datasets/google/fleurs).

Both models used CPU int8, Telugu transcription and beam size 5. Baseline is the previous generic Whisper large-v3 recognizer; updated is the installed Telugu model and corrected decoding path. No reference sentence or custom term was supplied to either recognizer.

| Measure | Previous | Updated |
| --- | ---: | ---: |
| Word errors / 42 reference words | 25 | 4 |
| Word error rate | 59.52% | 9.52% |
| Character error rate | 19.32% | 0.38% |
| Character errors / 264 reference characters | 51 | 1 |

Metrics normalize Unicode, case and punctuation. Character error also ignores spaces. Two updated word errors reflect joining the reference's separate resort/plural tokens into one written word; two reflect a split loanword and one spelling difference. The third recording matched the reference words. These are measured results on three short recordings, **not a claim of this accuracy for all Telugu speech**.

## Working app verification

A real MP4 containing Telugu speech went through browser upload, PCM extraction, local recognition, Telugu captions and Tenglish generation. The Telugu wording stayed identical after switching to WhatsApp tone. The app restored its draft after reload, preserved Telugu text in the SRT download, and exported a 1280 × 720 H.264 MP4 with AAC audio. An extracted frame was visually inspected for readable Telugu glyphs and matching caption text.

The browser run had zero uncaught errors, zero external network requests with remote requests blocked, and no horizontal overflow at a 390px viewport.

Additional Tenglish checks preserved two negations, the number 10, the mixed English word “college,” “bro,” and question marks. These checks test the language writer separately from speech recognition.

Automatic detection selected Telugu through the stronger multilingual fallback with a reported language confidence of approximately 0.857, and routed it to the Telugu recognizer. Explicit Telugu selection remains preferable when you know the video's language. A separate English regression check preserved the complete dialogue, “college,” and the number 10 using the original multilingual model.

Type checking, the production interface build, Python syntax checks, and text-preservation regressions passed. The regressions cover an alignment splitting a Telugu word, corrupted alignment text, and zero-duration aligned words without dropping the recognized text. Raw speech measurements and the browser and Tenglish checks are saved in `verification/telugu/`.

## Remaining limits

Names, dialects, noise, fast speech and mixed-language dialogue can still produce errors. Only a small formal-speech sample was measured here; the user's failing video has not been supplied for direct comparison. Word alignment is approximate, and timings for translated or edited captions can be estimated. Other Tenglish tones intentionally allow phrasing changes and should be reviewed for meaning. Recognition remains slower than playback on this computer.

The model's Apache 2.0 license is included in `licenses/telugu-whisper-Apache-2.0.txt`. Model downloads and conversion happen during setup; normal recognition is local.

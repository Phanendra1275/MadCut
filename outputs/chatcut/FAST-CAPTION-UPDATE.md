# Faster timed captions — verified local update

MadCut now creates speech-timed subtitles first, then derives Accurate Tenglish from that transcript. Both tracks return in the same job. No paid service or model training was used.

## Errors classified and fixes

| Error class | Cause found | Change |
| --- | --- | --- |
| Long first recognition | NVIDIA GPU present but speech inference ran on CPU | Enabled the project-local NVIDIA math runtime; same Telugu Whisper weights and beam size 5, GPU int8_float16 with CPU fallback |
| Waiting after speech finished | Two large optional language models reloaded before returning recognition; Accurate Tenglish then requested another model pass | Return timed native subtitles and faithful chat spelling immediately; translations and creative tones load models only when requested |
| Repeated work | New speech process/model load for each job; repeat videos re-recognized | Persistent sequential speech worker and local raw-recognition cache |
| Duplicate acoustic work | Timing alignment encoded the same recognition window again | Reuse the single acoustic encoding when valid; fallback for other cases |
| Delayed/mismatched highlighting | Leading silence and Latin word mapping could shift boundaries | Refine conservative speech onset per decoding window; preserve exact native word intervals for direct Latin matches |
| SRT timeline drift | Automatic uniform word grouping could estimate new cue boundaries without speech anchors | Keep imported SRT intervals intact; group automatically only when actual anchors exist |
| Browser preprocessing delay | Browser extracted audio before sending it to speech service | Upload original media directly; PyAV decodes audio into mono 16 kHz samples locally |

## Measured on this computer

Intel i5-13420H, 16 GB RAM, NVIDIA RTX 4050 Laptop GPU (6 GB), Windows. The benchmark used a 12.011-second excerpt of the supplied Prasad Tech video and a separate 3-second clip. Timings include local upload/job polling; the full 69.9-second master was not benchmarked in this update.

| Test | CPU fast-pipeline baseline | Final GPU pipeline |
| --- | ---: | ---: |
| First uncached 12-second clip | 94.068 s | 18.638 s |
| Repeat same clip | 0.315 s | 0.360 s |
| Different uncached 3-second clip, model warm | 16.567 s | 2.115 s |
| Accurate Tenglish from timed Telugu | 0.215 s | 0.211 s |

The first recognition was about 5 times faster in this test. The model remains warm after recognition. The real editor's cached click-to-ready time was 2.53 seconds, including its UI polling, rendering and state updates. Hardware, audio length, model switches and queued jobs affect latency; these are local measurements, not subscription-service performance guarantees.

## Timing and editor verification

- Actual video upload returned native SRT plus Telugu and Tenglish JSON tracks from one speech request, without a translation request.
- Native/Tenglish cue intervals match exactly. Available word anchors drive highlights; compound-word splits remain approximate.
- Corrected Telugu on a test with two seconds of leading silence aligned to 2.232–7.880 seconds. The original incorrect 0–6.720 interval was replaced; the supplied corrected wording was preserved.
- Imported native SRT converted to Tenglish without recognizing audio again, changing cue intervals, or inventing word anchors. Imported SRT has subtitle timing only; use **Sync captions to speech** on the Telugu track for word timing.
- Both tracks and imported captions survived editor reload. The desktop editor fits one 1920×970 screen.
- Optional English translation still returned “Are you coming to college today?” from the Telugu test sentence. Switching back to speech releases those optional models.
- A new 3-second speech-timed Karaoke caption track exported to a real 30 fps MP4; the exported caption frame was inspected.
- Regression checks passed for spoken repetitions, recovery duplicates, changed negation/questions, Telugu token splits, pauses and spelling-anchor preservation. TypeScript and production build passed.

## Using it

Refresh MadCut and generate the video once again. Select Telugu as the spoken language and Accurate for fastest faithful Telugu/Tenglish. If you already have a good SRT, import it and generate the Tenglish version directly. Correct the native transcript once, use the edits for other languages, and sync its timing to speech if necessary. Existing saved projects are not silently overwritten.

Recognition and spelling are improved, not perfect. The supplied screenshot is not a human-verified transcript, so no perfect accuracy or word error rate is claimed for the Prasad clip. Unknown names, noise and accents may still need correction. Accurate Tenglish uses known chat spellings and pronunciation conversion; creative/contextual rewriting is an optional slower tone. This update does not fine-tune model weights.

## Local runtime and retention

`python local/setup-speech-gpu.py` installs the pinned free NVIDIA cuBLAS runtime only into `.local/runtime/cuda-python` on supported Windows NVIDIA machines. Restart MadCut afterward. CPU fallback remains available. No global Python installation is modified.

Recognition cache files live in `.local/speech-cache`, contain raw timed transcript results, and retain the latest 30 entries. Keys include uploaded bytes, language, recognition terms, model files and pipeline version. Current approved glossary corrections are reapplied on read. Temporary uploaded media is deleted after each job. The worker is sequential; the local app does not implement multi-user subscription infrastructure.

Implementation references: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) documents GPU inference and PyAV decoding; [CTranslate2 installation](https://opennmt.net/CTranslate2/installation.html) describes supported GPU runtimes. Tests exercised this installed runtime rather than assuming GPU availability.

Evidence is in `verification/fast-pipeline/`.

# MadCut — Free Local Caption Studio

Double-click **Start-MadCut.cmd**, then use **http://127.0.0.1:5173/**.
Double-click **Stop-MadCut.cmd** when you finish to release the model memory.

No API key, paid API, subscription, or cloud inference is used. After the initial model downloads, recognition, translation, editing, and exports work locally. Video and audio stay on your computer.

The home page follows the supplied dark reference with MadCut branding and the orange palette. **Open App** opens the working caption editor. Existing drafts and older project files remain compatible.

## Workflow

1. Upload MP4, MOV, WebM, or MKV, up to 200 MB. Use “Prepare preview” if its codec does not play directly.
2. Select the spoken language or auto detection, a caption language, and a tone. Telugu is selected by default. Enter uncommon names, places, or brands in “Names & terms” when useful; use Telugu spelling for Telugu names. Generate captions.
3. Edit text and start/end times. On the original spoken-language track, click **Sync captions to speech** to realign corrected text against the video without rewriting its spelling. Then regenerate Accurate Tenglish to inherit the Telugu word timings. Select another language and generate a version from the original transcript. To correct recognition once for every language, edit a Telugu, Hindi, or English track and click “Use edits for other languages,” then regenerate the other tracks.
4. Choose a template or customize font size, position, color, and bold text.
5. Export SRT, VTT, ASS, or an MP4 with burned captions. MP4 supports 720p, 1080p, and 4K with original, 9:16, 16:9, or square framing. Aspect changes fit the video with letterboxing.

Tenglish means natural spoken Telugu in Latin letters, not English translation. Natural, WhatsApp and Formal Tenglish preserve the spoken sentence; emojis are off by default. Telugu captions apply conservative spelling correction while preserving recognized meaning; visual templates change presentation. Review generated wording and timing before publication. After an update, click “Generate captions” to apply the current pipeline to an existing video; compatible recognition caches are reused and saved drafts are not automatically overwritten.

The editor saves a draft and attached video on this device. Download the project JSON to keep a portable backup. To restore, import the project and attach the matching video. No cloud sync is included.

## Local models

- Telugu speech: SpeechLab IIT Madras's Telugu-trained Whisper medium, converted to int8, with NVIDIA int8_float16 acceleration when available and CPU fallback. English and Hindi use Whisper large-v3. Auto detection uses a separate multilingual detector before selecting the recognizer. No paid inference is used.
- The service decodes the uploaded video's audio directly to mono 16 kHz samples, avoiding browser audio extraction and intermediate lossy MP3 encoding. Telugu speech is decoded once per speech window, then its fixed transcript is aligned for word timing. Quiet syllables at the boundaries of short clips are retained. Text is never reconstructed by adding spaces between incomplete alignment tokens.
- Meaning and translation: Sarvam Translate, a specialist Indian-language model, Q4_K_M.
- Accurate Tenglish uses a fast local chat-spelling lexicon and pronunciation conversion, preserving native subtitle intervals and mapping speech word anchors. It does not wait for a language model. Unknown spellings still need review.
- Creative chat wording: Qwen3-8B, Q4_K_M, with Telugu pronunciation hints. Both language models run in llama.cpp b11474 through Vulkan. English ↔ Telugu/Hindi uses the specialist translator; Telugu ↔ Hindi pivots through English.
- Video: FFmpeg WebAssembly, with one shared canvas caption renderer for preview and MP4 exports.
- Original captions use speech word timing. Faithful Accurate Tenglish inherits native Telugu word anchors; compound-word splits are approximate. Other translations, paraphrases, and unsynced edits use estimated highlighting.

Browser video processing uses computer memory. 4K and long clips take more time and memory; use 720p if an export fails. Speech recognition runs in a separate process. Accurate Telugu and Tenglish generation starts only the speech worker and keeps it warm. Optional language models load only for other translations or creative tones; switching between speech and those models releases the previous models to fit memory. Recognition results are cached locally for the last 30 distinct uploads/configurations. This computer uses 16 GB RAM and a 6 GB NVIDIA GPU; close memory-heavy applications during generation. Clips can take longer than their playback duration to process.

## Setup and development

The prepared local runtime and configuration are in `.local/` and are ignored by Git. They contain model weights, executable files, logs, and this computer’s configuration, with no OpenAI credential.

For a fresh setup, run `python local/setup.py`. On Windows with an NVIDIA GPU, run `python local/setup-speech-gpu.py` to install the pinned CUDA math runtime into this project's `.local/runtime` folder, then restart MadCut. This optional download uses roughly 770 MB installed; CPU recognition works without it. If required Python modules are missing, it installs them in a project-local virtual environment. Model files are downloaded only during setup. Existing complete Whisper models are reused when available. `local/setup-telugu.py` downloads a pinned, checksum-verified Telugu checkpoint and converts it with an isolated CPU conversion environment. Conversion tools and source weights require several GB of storage; normal recognition uses the converted model and does not need PyTorch.

Build the interface with `node node_modules/vite/bin/vite.js build --config vite.local.config.ts`. Run the production local server with `python local/service.py`. The service binds only to 127.0.0.1; the chat writer binds only to 127.0.0.1:8766 and the specialist translator to 127.0.0.1:8767. Internal model endpoints use a temporary access token generated at startup.

## Accuracy and scope

This is a working local creator app, not a guarantee of publication-ready transcription. Telugu recognition may miss words or spelling, especially in noisy audio or accents. Review the original transcript and correct it before generating other languages. AI chat phrasing and translation may still require edits. Number-preservation checks reject translations that change explicit digits.

All 55 presets support motion tied to available word timestamps. Turn off Word-by-word animation for static captions. Template cards, the player and MP4 export use the same canvas renderer. Missing or invalid word timestamps use estimated highlighting and are marked for review; segmentation does not manufacture acoustic word times. ASS exports basic text styling rather than reproducing canvas chat bubbles. Subtitle import accepts SRT and VTT. Online hosting and shared accounts are not part of this local edition.

## Sources and licenses

[Qwen3](https://qwenlm.github.io/blog/qwen3/) and [the GGUF model](https://huggingface.co/Qwen/Qwen3-8B-GGUF) use Apache 2.0. [Whisper](https://github.com/openai/whisper), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), and [llama.cpp](https://github.com/ggml-org/llama.cpp) use MIT licenses. Noto Sans Telugu and Noto Sans Devanagari use the SIL Open Font License; font license files are in `public/fonts/`. FFmpeg core is GPL-2.0-or-later; [corresponding core source and build configuration](https://github.com/ffmpegwasm/ffmpeg.wasm/tree/main/packages/core) are available upstream. Preserve dependency licenses when redistributing this application.

[Sarvam Translate](https://huggingface.co/sarvamai/sarvam-translate) is GPL-3.0; this app uses the [Mungert GGUF conversion](https://huggingface.co/Mungert/sarvam-translate-GGUF). Its license is included in `licenses/sarvam-translate-GPL-3.0.txt`.

[Telugu-trained Whisper medium](https://huggingface.co/vasista22/whisper-telugu-medium) uses Apache 2.0, included in `licenses/telugu-whisper-Apache-2.0.txt`. Its pinned source revision, conversion format, and alignment configuration are recorded in `.local/models/whisper-telugu-medium/provenance.json`. See [the accuracy update](TELUGU-ACCURACY.md) for measured Telugu results and instructions for reprocessing existing videos.

See [the MadCut UI and timing update](MADCUT-UPDATE.md) for the new correction workflow and checks.

**Reference editor and spelling update:** MadCut now includes Projects, a two-step frame setup, actual thumbnail/waveform tracks, video transforms, caption grouping/delay, and Teach spellings. See [the Prasad Tech debugging report](PRASAD-SPELLING-UPDATE.md). Learned spellings are a local glossary, not fine-tuned model weights. Regenerate old language versions to apply the new spellings.

See CAPTION-ERROR-AUDIT.md for the spelling/timing fixes, supplied-template inventory and verified limits.

See [the fast caption pipeline update](FAST-CAPTION-UPDATE.md) for measured speed, exact SRT import behavior, and timing verification.

## Progressive captions and Tenglish modes

Long videos now show timed captions progressively. Natural Tenglish is the default; WhatsApp and Formal are available, with emojis off by default. Confidence-gated text correction uses the smaller local model only for uncertain passages; approved spellings and caches avoid repeated processing. See [the progressive caption update](PROGRESSIVE-CAPTION-UPDATE.md) for real-video timings, guards, setup and verified limits.

See [the current caption fundamentals update](CAPTION-FOUNDATION-UPDATE.md) for word-driven grouping, VAD-backed short-gap repair, progressive inference, spelling fixes, final editor/export checks and the pending 160-clip accuracy benchmark.

# MadCut local verification

**8 October MadCut update:** see [the UI and timing report](MADCUT-UPDATE.md) for the reference layout, corrected native-text alignment and Tenglish word timing checks.

**8 October accuracy update:** the Telugu recognizer and decoding path were replaced and measured on three held-out test recordings. See [the Telugu accuracy report](TELUGU-ACCURACY.md) for the before/after measurements, live Telugu-to-Tenglish upload/export verification and remaining limitations. The checks below describe the earlier local build.

The final browser run generated Tenglish from a video containing spoken English, edited a caption, reloaded the saved video and draft, reused an edited English transcript for other languages, and exported SRT, VTT, ASS, and a captioned MP4.

- MP4: H.264, 1280 × 720, AAC audio, approximately 6.67 seconds. Burned caption appearance was inspected in an extracted frame.
- Final browser run: zero uncaught page errors; no horizontal overflow at 390px; zero external network requests. External requests were blocked during this test.
- Local model checks: English speech transcription; five caption languages; Telugu-to-Tenglish questions and negatives; an unfamiliar 25-minute instruction and “I cannot come tomorrow”; WhatsApp wording from a negative Telugu sentence.
- All generation runs on this computer. No paid API key or inference service is configured.

## Limits observed

The Telugu recording exposed speech spelling and word errors. Correct the original transcript before producing other versions. AI chat spelling, grammar, and translations still require review. Generation can take several minutes on this computer. 720p MP4 was verified; 1080p/4K and all video codecs were not exhaustively tested. Other visual presets are static except Karaoke highlighting. Online hosting is not included.

**Reference editor / Prasad Tech update:** see [the real-video debugging report](PRASAD-SPELLING-UPDATE.md). The illustrated loanword passage, local learned spellings, project workflow, grouping and portrait video export were verified. This does not establish perfect accuracy over the full source recording.

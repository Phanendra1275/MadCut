# MadCut export, templates and trim update

Implemented 8 October 2026.

## Export

Reference-style rounded dark dialog with MadCut orange (#FF4D00). Video, Subtitles and Captions Only tabs. All controls are free, with no watermark or paid locks.

- MP4: 720p, 1080p, 2K or 4K; 30/60 fps; Low/Medium/High quality; optional original audio. Dimensions follow the project aspect ratio and media transform.
- Subtitle downloads: SRT, VTT and ASS with current text and timing. ASS has basic styling; complete animated looks require video or caption-layer export.
- Captions Only: green (#00B140) or blue (#0047BB) chroma MP4, or transparent ProRes 4444 MOV. Uses the same caption renderer as the preview and template cards.
- Browser creates caption frames; local native FFmpeg encodes them and combines source media. The source uploads once per export. Progress is shown during frame preparation and encoding.

## Template controls

Apply looks to All captions or Selected caption. Seven entry choices: Auto (template motion), Slide Up, Blur In, Slide Right, By Letter, Pop, None. Customize font, accent, text color, size, position and entry duration. Letter animation respects Telugu grapheme boundaries, including text outlines. Favorites and named style presets persist on this browser/device. No new MOGRT runtime/import was added in this update; these are browser-rendered template controls.

Caption controls include grouping, All/Selected delay and Reset to original. Newly generated language versions retain their reset baseline.

## Real trim behavior

Auto Trim and Silence panels analyze the uploaded audio with FFmpeg and propose timed cuts for review. Gentle/Balanced/Tight silence modes preserve breath padding. Optional filler and repeated-word cuts require sufficiently confident word timing; they default off. Off-topic removal remains a manual decision rather than an unsupported automatic claim.

Applying reviewed cuts renders a new video and retimes every caption language and word anchor. Restore original video works during the current editor session. Keep the source file: the original restore snapshot is not retained across a page reload; the trimmed draft is retained.

## Verified

- TypeScript check, production build and Python compilation passed.
- Real browser MP4, SRT, blue-screen MP4 and transparent MOV downloads passed after the final build.
- Tested video outputs: 3 seconds, 720x900, 60 fps. H.264/AAC for MP4; ProRes 4444 with alpha and PCM audio for MOV.
- Transparent output contained both alpha 0 and alpha 255; compositing over blue produced readable text and glow.
- Selected-caption animation, persisted preset/favorite, real audio silence analysis, applying cuts, caption retiming and source restoration passed in the browser.

## Practical limits

Native FFmpeg must be on PATH, or set ffmpeg_executable in .local/config.json. Browser export preparation is bounded to 18,000 frames and 450 MB of caption PNG data; shorter clips/lower resolution use less memory. Transparent MOV is substantially larger than MP4. Generated local export files expire after approximately 24 hours when a later export runs; downloaded copies remain available.

These changes preserve the existing Telugu/Tenglish speech pipeline. This update does not train or fine-tune a speech model, and does not establish perfect transcription accuracy. Review uncertain speech before publishing.

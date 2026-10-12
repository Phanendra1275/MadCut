# Video reference update — MadCut

Source: C:\Users\HP\Downloads\308a502e-226f-4199-a216-095b65e8d78f.mp4
Observed media: 720 x 1280, 30 fps, approximately 20.948 seconds. The source was preserved; only analysis derivatives were written into this workspace.

## Observed visual guidance

The recording shows a caption editor with neon green/white two-line text, lime word-drop motion, orange bold text mixed with a white script line, and red/white bold two-line captions. Short word reveals enter with the visible phrase changes. Its inner example captions contain Tamil/Tanglish wording (for example Scriptku ellame / Game vilayadi); the recording labels its feature Automatic Thanglish Caption. These visible example captions are separate from the outer recording's narration.

## Implemented

Four automatically available reference-based web presets:

- Neon Emerald: green first line, white second line, subtle upward word entry and glow.
- Lime Drop: white first line, lime second line, damped spring word-drop entry.
- Amber Script: warm amber body lettering with a white script second line.
- Scarlet Punch: red first line, white second line, short punch/reveal entry.

Latin bold reference styles use available Arial; script uses the existing bundled MadCut Script face. Telugu and Hindi keep the native-script fallback fonts. The video does not identify or include its original fonts; these are visual approximations rather than an exact font identification. Caption size, position, accents, entry animation and duration remain editable. Original 33 MOGRT files and every existing preset remain available: 33 supplied templates plus 19 studio presets = 52 presets.

All reference animations are driven by existing word timestamps. Selecting a preset changes appearance only, not spelling, content or timing. The same caption renderer creates the live preview and export frames. Contrasting outlines improve readability over footage; explicit By Letter mode uses the same revealed text for both outline and fill.

## Caption accuracy

The actual local auto-language check on this supplied clip returned an uncertain-language error. It was not forced into Telugu, and no transcript was invented or used to train spelling rules. The inner Tanglish examples are not Telugu correction ground truth. No new Telugu ASR accuracy claim can be established from this reference recording.

Improved the language-detection message: an uncertain clip asks for the actual spoken language, while confidently detected unsupported languages are named and are not presented as Telugu transcription failures. Current supported transcription languages remain Telugu, Hindi and English. Telugu natural spelling, mixed-language protection and conservative correction remain unchanged. Existing 21 natural Tenglish examples and speech-anchor regressions passed again. No model weights were trained.

## Verification

Production build and TypeScript check passed; Python compilation passed for the language-detection change.

Real browser checks passed:
- 52 automatic presets and all four new selections.
- Three distinct word-animation frames for every new preset.
- Correct default accents/font selection.
- Exact preservation of caption strings and every word/cue timestamp.
- Selected preset persists across reload.
- A real animated Lime Drop 720p MP4 export, with its decoded frame visually inspected.
- No browser JavaScript errors.

Evidence: verification/video-reference/results.json, styles-preview.png, export-frame.png, saved-project.json, recognition.json and the source contact sheets. The uncertain audio is recorded honestly; it is not counted as successful transcription.

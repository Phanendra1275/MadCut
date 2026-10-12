# MadCut — Prasad Tech spelling and editor update

## What was debugged

The video named in the supplied screenshots was found at `C:/Users/HP/Downloads/Prasad Tech.mp4`. Its source was preserved. A local 18–30 second excerpt was used for recognition comparison and editor/export checks.

The Telugu-trained recognizer captured:

> మొబైల్స్ అన్ బాక్సింగ్స్ ఇవన్నీ అంటే అసలు ఏదో వింతగా చూసేవారు అన్నమాట

The previous Roman-letter path could reject conventional English loanwords and fall back to rigid pronunciation spelling. The fallback also split the prefix in `un boxings`. The updated writer receives conventional loanword and common chat spellings, and joins `unboxings` after generation as well as in the fallback. The checked passage now produces:

> mobiles unboxings ivanni ante asalu edo vinthaga choosevaru annamata

Its nine Roman words inherit the original speech anchors; `unboxings` spans the two native recognition words. Questions, negation and omitted-word guards remain enabled. The multilingual recognizer was also tested and produced worse text on this excerpt, so it was not adopted as a replacement.

This is a spelling-path fix verified on the illustrated passage, not a measured claim of perfect recognition throughout the entire video. A short background/transition phrase in the comparison remains uncertain. No independently reviewed complete reference transcript was available, so word-error-rate or 100% accuracy claims would be unsupported.

## Learning corrections

**Teach spellings** stores user-approved native-word corrections and preferred Tenglish spellings in `.local/spelling-profile.json`. They are reused for new recognition and Roman spelling. Entries persist, can be removed, and never upload to a cloud service. Regenerate captions after adding an entry. This is glossary learning; no speech-model weights were fine-tuned. Training model weights responsibly requires reviewed audio/transcript pairs rather than treating generated captions as ground truth.

Existing drafts are preserved. To apply this update to an existing project, open it, choose Accurate Tenglish and generate that language version. If its original Telugu transcript is wrong, regenerate Telugu or correct it, sync it to speech, then regenerate Tenglish.

## Reference editor

The supplied screenshots informed the projects dashboard, device statistics, upload dialog, two-step frame/background selection, Media/Text rail, left caption controls, central preview, right transform/templates panel, and three-track timeline. Branding remains MadCut. The local plan has unlimited caption generation; no artificial two-minute quota is imposed.

Implemented controls include native and Roman captions, six templates, one-to-twelve words per caption, caption delay with undo, 9:16/Original/1:1/4:5/16:9 frames, background color, scale, independent width/height, position and rotation. Actual thumbnail frames and an actual audio waveform are extracted from the attached video. These are not decorative placeholder tracks. Projects and videos remain on this device; the old single-draft database is migrated without deleting its current project. The reference's Auto Trim, Silence and tracking tools are not claimed as implemented.

## Verification

- TypeScript, production build, Python compilation, negative/question/missing-word preservation, repeated-word recovery and learned native/Roman spelling tests passed.
- Actual local model generation returned the conventional spelling above and inherited word timing.
- Browser checks passed for project creation, video metadata, thumbnail timeline, transform controls, learned spelling save/delete, caption grouping, draft reload, project persistence and exports.
- The exported test excerpt was H.264 720 x 1280 with AAC audio, 12 seconds. An inspected frame displayed `mobiles unboxings ivanni` with `unboxings` highlighted at its speech interval.
- Browser verification recorded zero uncaught errors, zero external network requests and no mobile horizontal overflow at 390px.

Evidence and interface screenshots are in `verification/prasad-update/`. Source media and intermediate working clips are not packaged there.

Additional export verification passed for a 4:5 frame, custom blue background, 115% media scale, X/Y positioning and 8-degree rotation. The output was 720 x 900 with original audio. Its exported frame and corrected preview were inspected. Caption delay retained word timing and could be undone. Final desktop/mobile editor fit checks passed with no page errors or horizontal overflow.

# MadCut caption error audit and template pack

## Causes and fixes

| Error class | Confirmed code cause | Fix |
|---|---|---|
| Captions remain too long | Recognition grouped up to five seconds; new language versions retained complete phrases | Generate short groups of up to three words; split at speech pauses over 0.45 seconds. Preserve all recognized text. |
| Captions remain through silence | Fill gaps extended cue ends to the next caption; renderer retained revealed words until cue end | Bridge only 0.15 seconds. Clear the overlay during measured pauses and 0.15 seconds after the last spoken word, including static mode. |
| Editing damages timing | Every edit removed all word anchors | Same-length spelling edits retain anchors and mark wording for review. Timing edits rescale anchors. Added/removed words invalidate word alignment and are shown as estimated. |
| Old caption obscures a newer caption | Timing edits could create overlapping intervals; playback selected the first match | Reject invalid/overlapping timing edits. Prefer the latest matching cue for legacy drafts in preview/export. |
| Tenglish spelling varies | The language writer could keep phonetic variants despite known loanword/chat spellings | Canonicalize known spellings from the Telugu source and user glossary. Match English x to phonetic ks so unboxings is recognized correctly. Preserve questions, negation and spoken words. |
| Recognition chooses the wrong Telugu word | Speech recognition can mishear speech, especially names and loanwords | Retain the Telugu-trained recognizer, original-transcript editor, Names & terms and user-approved spelling glossary. Do not silently guess replacements. Recognition accuracy still requires checking the audio. |
| Imported captions paired with old media | Project import retained the prior video and rejected duration mismatches | Import detaches prior media and resets playback/history; attach the matching video. |
| Export differs across a silence | Static exports only sampled cue boundaries | Include word onset/end and silence-clear boundaries in static export frames. Use the same renderer as playback. |

Existing saved captions are preserved. For an old long-caption project use Apply word grouping; regenerate captions to run the improved speech pipeline. A corrected transcript can be synchronized to speech before generating Tenglish. Existing edits are marked for review rather than claimed as forced alignment.

## Supplied templates

Inspected 33 MOGRT files, their definitions, thumbnails, font names and effect requirements. Added 23 web recreations: four slides, four blur slides, four bounce slides, two bounce shrinks, two bounce expands, Flex Bounce, three gradients, Jitter Shine, Static Shine and Zoom In. Total gallery: 38 templates.

These recreations use the shared canvas renderer for native text, word onset, directional entrance, blur, bounce, scale, gradient and shine. Arial is used for Latin text in the pack recreations; native Telugu/Hindi retain their script fonts. MOGRT files contain binary Adobe projects, not browser animation definitions. Effects such as Deep Glow and proprietary fonts (SF UI Text, Coolvetica, Edwardian Script, Vivaldii) are not bundled. Premium Text and the complex mixed-layer templates have been inventoried, not represented as exact working imports. No supplied archive/project was modified or executed. These are recreations, not exact Adobe keyframe conversions.

## Verification and limits

The actual 12-second Prasad excerpt was recognized into ten short groups and converted to Tenglish with mapped word times. Confirmed conventional spellings include mobiles, unboxings, ivanni, ante, asalu, edo, vinthaga, choosevaru and annamata. The rest of this excerpt has not been independently human-transcribed; no word-error-rate or perfect-accuracy claim is made. In particular, uncertain recognized names/words are retained for review rather than guessed.

Regression checks cover Telugu written-word splits, corrupted token text, repeated speech, omitted words, questions, negation, canonical spelling, pause grouping, same-length spelling edits, timing edits, overlapping edits, silence clearing and subtitle round trips. Browser checks cover 38 templates, future-word suppression, within-word animation, static mode, single-screen desktop/mobile layout, search and a real 30 fps MP4 export with audio. Evidence is in verification/caption-debug.

All processing remains local and free. This is code and glossary correction, not model fine-tuning: no labelled training dataset was supplied. Missing/unreliable word timestamps remain estimated and are labelled accordingly.

Final editor checks also passed with the actual ten-group clip: project import detaches prior media, visible template cards render, overlapping timing edits are rejected, and spelling edits preserve mapped anchors. A separate static export with synthetic pause anchors was visually checked at 0.6 s (overlay absent) and 1.8 s (overlay present). The restarted API produced mobiles unboxings with the original 0.94–2.10 s compound-word interval. TypeScript and the final production build passed.

# MadCut: natural Tenglish and default template library

Implemented 8 October 2026. The running app is available at http://127.0.0.1:5173/.

## Caption changes

Telugu captions receive conservative spelling/context correction before Romanization. The new native-token grammar layer handles conversational endings, question forms, mixed English words and sentence boundaries. Natural is the default; WhatsApp keeps the same spoken words without adding bro or emojis. Formal retains fuller endings. Telugu-source Tenglish now uses this faithful, fast path across tone selections; templates control its appearance.

Examples verified: Nuvvu ekkadiki velthunnav?; Em chesthunnav?; Nenu kuda vastha.; Naaku artham kaaledu.; Ee video ni edit chesi naaku pampu.; Website ready ayyinda?

Existing confidence-gated local correction remains available for uncertain transcription. Healthy captions use lightweight processing. Corrections and conversions are cached, independent caption conversion uses controlled parallelism, and the editor continues showing partial captions and stage progress. Video audio is extracted once; text conversion does not upload or reprocess the video.

Speech anchors and segment intervals stay attached during correction. Natural/Formal contractions map back to native word anchors; split compounds retain the existing explicitly mapped timing behavior. English names, brands and numbers are protected. Meaning checks reject changed negation, missing words and added words. Approved user spellings continue taking precedence.

This is a language-processing improvement, not model-weight training or a guarantee of perfect recognition. Unknown names, slang, unclear audio and phonetic fallback words can still need review. The speech recognition model was not changed in this update; no new ASR word-error-rate or real-time processing claim is made.

## Default templates

All 33 supplied MOGRT files are included, alongside the 15 existing studio presets: 48 presets automatically available in the editor. Minimal remains the clean default. The supplied ZIP and original MOGRT bytes are unchanged.

- public/templates/001.mogrt through 033.mogrt: original assets.
- public/templates/index.json and numbered JSON files: complete metadata and extracted original editable properties.
- public/templates/catalog.json: lightweight runtime metadata.
- public/template-previews/001.webp through 033.webp: previews drawn with the web export renderer.
- Numbered .source.webp files: retained source thumbnail representations.

Original template names are displayed and searchable, including original spelling such as Blure. Category filters, selection highlighting, favorites, animation options and original-file downloads are available. The selected preset survives caption edits and reload. Static thumbnails load lazily; only active/hovered cards animate. No large MOGRT assets are loaded automatically into browser memory.

The app uses web recreations of the supplied effects, not a native Adobe MOGRT execution engine. Complex distortions, plugin-specific controls and original proprietary fonts are approximated with supported web properties and available font fallbacks. The original MOGRTs remain available for native Adobe use. Preview and rendered MP4/MOV use the same web caption drawing function. Subtitle files retain timed text rather than all visual animations.

## Verification

- All 33 packaged MOGRT files matched their original ZIP members byte for byte; all 33 web thumbnails exist.
- 21 natural Tenglish examples passed, including mixed English, conversational endings, spelling corrections and exact speech anchor checks. Added words, changed names, numbers and negation are rejected.
- Natural, WhatsApp and Formal text API checks passed, including faithful output under Social Media tone selection.
- 100 text-only caption conversions took 0.104 seconds cold and 0.091 seconds warm on this computer. These timings exclude speech recognition and video processing.
- Real browser upload, actual local transcription, Telugu/Tenglish tracks, instant preset application, caption editing, reload persistence and a new-preset 720p MP4 export passed without browser errors. There were zero eager MOGRT requests.
- The new preset export was inspected as a decoded frame: H.264 video at 720 x 1280, 30 fps, 3 seconds, with AAC audio and rendered animated captions.
- Existing scoped animation, saved preset/favorites, real silence trimming, caption retiming and Restore original video checks passed.
- TypeScript checking, production build, Python compilation and focused spelling/timing/repetition regressions passed.

Evidence is in verification/default-library. Existing upload, editing, subtitle and rendered video export paths remain in place. All processing remains local and free; no paid API was added.

Final export regression: real MP4, SRT, blue-screen MP4 and transparent ProRes MOV UI exports also passed at 60 fps. Final health confirms speechReady=true and fastCaptions=true. The separate general language engine reports languageReady=false; the verified Telugu-to-Tenglish path works independently, but other translation providers are not newly validated in this update.

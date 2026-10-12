# MadCut player and word motion update

The studio follows the supplied editor geometry: a 60 px header; 84 px tool rail; 320 px left panel; 400 px right panel; central player; full-width 346 px transport/timeline area at 1920 x 970. Panels scroll internally. The editor fits one viewport on desktop and mobile; mobile tools open as drawers.

15 presets share one canvas renderer across template cards, preview and MP4 export. Added Glow Script, Ink Flow, Script Duo, Typo Stairs, Kinetic Stack, Hyper Clean, Editorial, Trio Lockup and Pop Tag. Script Duo preserves the script word's capitalization. Preview follows the video clock each animation frame; export renders motion at 30 fps. Animation can be disabled. Search, frame transform, aspect selection, safe-zone/grid overlays, timeline zoom, seek and undo remain available.

Verification: TypeScript and production build passed. Browser checks passed at 1920 x 970 and 390 x 844 without page overflow or JavaScript errors. All 15 presets suppress future words and reveal words at their recorded onset; fade/pop/lift presets change between adjacent animation samples. Static mode shows the complete caption. Live video-clock motion and selected-template persistence after reload also passed. Exported the actual Prasad clip with Kinetic Stack, a 4:5 frame, transforms and audio: H.264 720 x 900, 30 fps, AAC, 3 seconds.

These presets reproduce the reference's visual direction using bundled free Anton and Great Vibes fonts (licenses included in public/fonts). Exact proprietary preset motion cannot be determined from still images. MOGRT files and any required fonts/reference renders can help match those presets; this app does not directly play Adobe MOGRT files.

Word motion is only as accurate as its timestamps. Missing/invalid word anchors use estimated spacing; speech alignment is available for corrected native transcripts. This update changes presentation, not speech-model training, and does not promise perfect recognition. Animated export is limited to approximately 10 minutes and consumes browser memory; long 4K exports have not been verified. ASS retains basic subtitle styling rather than these canvas animations.

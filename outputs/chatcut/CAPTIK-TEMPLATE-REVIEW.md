# MadCut template review — 8 October 2026

Reference inspected live: https://captik.in/#templates and https://captik.in/templates. The live gallery differs from the search engine cached page: the browser displayed 72 styles with Popular, Behind you, Bold & animated, Clean and Property reels filters. We compared the visible motions, not their unverified transcription or speed claims.

| Observed reference behavior | MadCut change / remaining gap |
| --- | --- |
| Same footage across template examples | Cards now use a frame from the user's video, current caption text and real timing intervals; hover loops a motion demonstration. Apply plays the actual speech timeline. |
| Large keyword + small support text | Keyword Spotlight uses the actual active word as the large line and already-spoken words as context. |
| Active word wipe | Word Wipe reveals a colored plate across the active word, with dark lettering only over the revealed portion. |
| Bright word emphasis | Focus Glow accents the active word and softens surrounding words. |
| Behind subject lettering | Not implemented. Requires a real foreground mask plus shared preview/export composition. No simulated crop or misleading feature badge added. |
| Video inside letters | Not implemented. Requires masking the moving footage inside glyphs in both preview and export. |
| Intricate typography / native MOGRT motion | Existing 33 original MOGRT files are retained. Browser presets remain web recreations, not execution of Adobe compositions. Font substitutes remain disclosed. |

The library now has 55 presets (33 supplied + 22 studio). Existing categories, favorites, saved styles, per-caption application, customization, source downloads and export options remain available. Only visible cards allocate full thumbnail canvases; off-screen cards release their buffers. Only hovered/selected visible cards animate. Cards share the existing player; no extra video decoder per card and no AI request per style switch.

The shared caption renderer produces both preview and export frames. These changes do not alter transcript text or timestamps and do not claim better speech recognition accuracy. Demo caption text is a manually supplied style fixture, not a verified transcription of the test audio.

Validation: TypeScript and production build; 55 library entries; real footage posters; three changing word frames for each new effect; caption text unchanged; selected style persisted after reload; actual H.264/AAC 720×1280, 30 fps, 3-second export. Export frame inspected at 2.1 seconds. Evidence: work/verification/captik-review/.

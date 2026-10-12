# MadCut — reference UI and caption timing update

The application is branded MadCut and runs at http://127.0.0.1:5173/. Start it with Start-MadCut.cmd; stop it with Stop-MadCut.cmd. It remains free and local, with no API payments or account required.

## Reference interface

The supplied screenshot informed the black-and-emerald home page: announcement bar, navigation, italic hero emphasis, green waves, portrait preview, language chips, metric grid, caption-template gallery, timeline section, creator cards, pricing, accordion FAQ, final call to action, and oversized MadCut footer. Open App and template buttons lead into the working editor. The editor uses the same emerald palette.

Content describes the implemented five caption modes and six editor templates. The reference portrait is a static illustration taken from the supplied screenshot, not a playable demo. The supplied source image was not modified. Mobile layouts avoid horizontal overflow. Existing drafts and project files remain compatible.

## Telugu and Tenglish correction workflow

1. Select Telugu as the spoken language and generate Telugu-script captions. The installed Telugu-trained speech model remains in use.
2. Correct any misheard words in that native track. Add omitted words rather than inventing dialogue.
3. Click **Sync captions to speech**. This aligns the exact corrected native text against the original audio, updates the original transcript, and keeps spelling intact. For short clips, it searches the whole clip, so an incorrect initial offset can be corrected.
4. Generate **Tenglish**, with **Accurate** tone. Faithful Roman text inherits the native speech-word anchors. If the writer omits a word, changes a question or changes negation, the app falls back to native pronunciation spelling.
5. Choose Karaoke for word highlighting, review the video, then export.

Speech onset refinement prevents the first caption word from highlighting confidently detected leading silence. It does not trim speech-recognition audio or discard words. Dense-passage recovery now retains intentionally repeated words; it removes a recovery duplicate only when the matching word intervals substantially overlap.

Tenglish compound-word splits use approximate positions within their native word interval. Paraphrased tones, other translations and unsynced edits still have estimated word highlighting. Forced alignment is a timing aid, not an independent spelling correction model; its text must match the spoken wording. Long clips are aligned in bounded windows near their supplied times, so very large global offsets should be corrected before syncing. Recognition, slang spelling and timing can still require review.

## Verified checks — 8 October 2026

- TypeScript and production interface build passed.
- A real Telugu speech sample with two seconds of added leading silence and three seconds of added trailing silence was aligned from an incorrect zero-second caption start. Corrected start: **2.232 seconds**, versus measured energy onset near **2.28 seconds**. All ten native words and their exact spelling were preserved.
- Accurate Tenglish inherited all ten native word intervals in the local API check.
- Regression checks preserved intentionally repeated words, removed a true overlapping recovery duplicate, rejected an omitted spoken word and changed negation, and preserved native text despite fragmented alignment tokens.
- Desktop home-page controls, language preview, template-to-editor routing and FAQ passed. Desktop/mobile checks recorded no uncaught page errors or external network requests, and no horizontal overflow at 390px.

Evidence is in verification/madcut/. The earlier recognition benchmark remains documented in TELUGU-ACCURACY.md; these timing checks are separate and do not establish accuracy on the user's missing problem clip.

The browser correction workflow preserved the ten-word native sentence, realigned its first word to 0.240 seconds, and generated ten mapped Tenglish words. Saved drafts reloaded with the same text. The SRT preserved text and times; the burned MP4 was H.264 1280 x 720 with AAC audio and 6.72-second duration. An exported frame at 1.0 second showed the expected word 'kriyalu' highlighted. No uncaught page errors or remote network requests were recorded, and mobile had no horizontal overflow.

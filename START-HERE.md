# MadCut project handoff — 12 October 2026

The existing application source, supplied template assets, fonts, licenses, setup scripts, local service, and freshly built `local-dist` interface are included. The archive preserves the workspace layout: application files are in `outputs/chatcut`, and supplemental regression scripts are in `work/verification`.

## Current computer

The original `outputs/chatcut` folder still contains the installed dependencies and local model/runtime files. Use `Start-MadCut.cmd` there. Browser drafts and uploaded videos saved in IndexedDB belong to the browser profile; they are not ordinary project-folder files. Use the application's project download to back them up.

## Portable archive

The ZIP excludes `node_modules`, large local model weights and executable runtimes, personal runtime configuration, logs, recognition caches, rendered exports, environment/credential files, and obsolete build caches. These exclusions are recorded in the archive manifest. The locally approved spelling glossary is included separately under `handoff/local-settings`; copy it to `.local/spelling-profile.json` after setup if desired.

On another Windows computer:

1. Extract the archive and open a terminal in `MadCut/outputs/chatcut`.
2. Install Node.js 22.13 or later, Python 3.12, and FFmpeg/FFprobe on PATH.
3. Run `npm ci` to install JavaScript dependencies.
4. Run `python local/setup.py` to install the local AI dependencies and download the models. This requires internet access and substantial disk space during setup; inference runs locally afterward. Inspect setup output and model configuration before starting.
5. Run `python local/setup-correction.py` if the optional lightweight correction model is needed. Optional NVIDIA support is set up with `python local/setup-speech-gpu.py`.
6. Run `npm run build` if changing the frontend. A current build is already included.
7. Double-click `Start-MadCut.cmd`, or run `python local/service.py`, then open `http://127.0.0.1:5173/`.

Setup was not rerun in a clean environment during packaging. Model licensing and deployment details are described in README.md and the included licenses. No paid API migration or new model download was performed for this handoff.

## Latest Phase 1 work and verification status

Changes include a shared NFC/Unicode-category scoring policy, separate raw ASR provenance, source IDs and original anchors, preserved edit versions, contextual speech-recovery diagnostics, and a small collapsible original/corrected transcript comparison. Romanization no longer silently corrects the canonical transcript through the transformation endpoint.

Actual checks completed:

- 25 targeted Python tests passed, including Unicode marks, immutability, unknown confidence, timing preservation, recovery warnings, and service contracts.
- Existing caption-flow checks: 23 passed.
- Existing natural Tenglish checks: 21 examples plus guards passed.
- Existing Romanization fallback checks: 11 passed.
- TypeScript type checking passed.
- Production Vite build passed, with the existing large-bundle warning.

The Python service-contract tests mock recognition; they do not establish real-audio accuracy. The source recording was available, and a bounded retry of 49.44–54.19 seconds recognized existing neighbouring words with different alignment around the 51.44–52.19 warning. This is diagnostic evidence only, without a human-verified reference. Recovery proposals are not automatically applied and do not erase the warning or original anchors.

The preceding implementation turn was interrupted. Fresh browser persistence, UI integration, restart with the changed backend, and the complete upload-to-export regression flow remain unverified for these latest changes. Do not describe Phase 1 as fully accepted or claim improved real-world Telugu accuracy yet. No unrelated UI redesign, ASR-model replacement, or export architecture work was undertaken.

To run the new targeted suite from `outputs/chatcut`:

```powershell
python -X utf8 -m unittest discover -s local/tests -p test_caption_phase1.py -v
node node_modules/typescript/bin/tsc --noEmit --incremental false
```

Run the older supplemental scripts from the extracted `MadCut` workspace root. Some integration scripts require the original creator recording at its recorded external path; it is not bundled.

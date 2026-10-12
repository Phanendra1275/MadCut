# MadCut template font setup

Completed 8 October 2026. Refresh the running MadCut page to use the font update.

## Installed and connected

Inter Variable and Satisfy Regular were installed for the current Windows user. The Inter font includes the Black / 900 named weight. Poppins, Arial, Vivaldi and Edwardian Script were already installed.

The app now bundles Poppins Bold, Poppins ExtraBold, the original Inter Black webfont and Satisfy Regular with their licenses. Caption previews and MP4/MOV exports wait for their selected fonts to load. Preset font mapping uses the original MOGRT font metadata rather than applying Arial to every template. Custom font controls include Poppins, Inter Black, Satisfy, Vivaldi and Edwardian. Native Telugu/Hindi text uses the Noto script fonts.

| Required source font | Current MadCut font | Availability |
| --- | --- | --- |
| Arial-BoldMT | Arial Bold | Existing local Windows font |
| Inter-Black | Inter Black 900 | Bundled original webfont; Inter Variable installed on Windows |
| Poppins-ExtraBold | Poppins ExtraBold 800 | Bundled; already installed on Windows |
| Poppins-Bold | Poppins Bold 700 | Bundled; already installed on Windows |
| Satisfy-Regular | Satisfy Regular | Bundled and installed on Windows |
| Vivaldii | Vivaldi | Existing local font; alias verified in Chrome |
| EdwardianScriptITC | Edwardian Script ITC | Existing local font; alias verified in Chrome |
| SFUIText-Heavy | Inter Black | Free substitute |
| Coolvetica-Regular | Poppins Bold | Free substitute |
| Coolvetica-Cond | Anton | Free substitute |

The 33 originals retain their bytes. Font metadata is recorded in public/templates/index.json and each numbered JSON file. All 33 web thumbnails were regenerated with the updated fonts. Their runtime URLs have a new version marker to refresh browser caches. All 52 presets remain available, and captions/timestamps are unchanged.

## Why three source faces remain substituted

Poppins and Inter use the SIL Open Font License; Satisfy uses Apache 2.0. Their source licenses are included beside the unchanged font files. Coolvetica's current free desktop package does not provide web embedding rights. Apple's SF font terms restrict website-content use. No paid font purchase or restricted font bundle was added.

Windows font files were not copied into the website. Vivaldi and Edwardian are loaded from the local system, with Great Vibes as a portable fallback for computers without those faces. Exact local script-face metrics were verified on this computer. Other devices will need the original system fonts for those exact script faces.

Primary references:
- https://github.com/google/fonts/tree/main/ofl/poppins
- https://github.com/rsms/inter/tree/master/docs/font-files
- https://github.com/google/fonts/tree/main/apache/satisfy
- https://typodermicfonts.com/license/
- https://developer.apple.com/fonts/
- https://learn.microsoft.com/en-us/typography/fonts/font-faq

## Windows installer repair

The first installer mistakenly reset the existing HKCU Fonts registry key. The font files were intact. Registrations were reconstructed from all 265 intact user-font records; previously observed Poppins, Inter Bold and SF Pro entries were verified restored. The corrected installer preserves the existing registry key, backs it up before writing and refuses to overwrite different font files. A repeat installation was tested: every current font registration stayed unchanged. This was a registration repair, not recovery of deleted font files; no font files were deleted.

Install-Template-Fonts.ps1 is supplied for reinstalling the two added Windows fonts. It operates for the current user without requiring a machine-wide font installation. Registry backup files are in .local/font-backups. Installing these fonts on another device does not install the restricted original faces.

## Verification

- Browser-loaded font faces verified: Poppins 700 and 800, Inter Black 900, Satisfy, Vivaldi and Edwardian.
- Vivaldi and Edwardian aliases had matching metrics to their actual installed system faces.
- A real 720p Satisfy / Butter Up MP4 export was generated and its decoded frame visually inspected.
- 52 presets present; no browser JavaScript errors.
- All 33 MOGRT files remain byte-identical to the supplied ZIP; all refreshed preview files exist.
- TypeScript check, production build and the 21 natural Tenglish regression examples passed.
- Repeated Windows installation preserves every font registry entry.

Font installation improves typography. Existing web motion recreations and Telugu speech/correction behavior remain unchanged. Adobe-native MOGRT import/font resolution was not tested.

Evidence: verification/font-setup/font-browser-results.json, satisfy-export-frame.png, export-probe.json and inter-variable-instances.json.

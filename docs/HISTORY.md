# Flux — Recovered Development History

This page reconstructs the development history found in the original **All flux shi** archive.

The archive contains duplicates, packaged builds, old caches, experimental branches and unrelated files. Rather than pretending every folder was a formal release, this history groups the source into meaningful stages.

## How the archive was classified

Several folders are exact source duplicates under different names:

- `Flux BETA` = **Flux 1.1 Patch**
- `Flux 3.0 BETA` = **Flux 1.2 (liquid glass)**
- `Flux 3.1 Realease` = **Flux-fixed (3)**
- `Flux 3.2 Beta` = **Flux-fixed (4)**
- `Flux 3.3 Dev build` = **Flux-fixed (5)**

The Windows-package folders, portable builds and GitHub packaging kits are build/distribution copies rather than separate product versions.

`Flux developer build 1.3` appears to be a smaller experimental/divergent snapshot, so it is kept separate from the main recovered sequence.

---

## Stage 1 — First Release

The original usable Flux baseline.

**Core areas present**
- Dashboard
- Tasks
- Calendar
- Statistics
- Dark / Light / Sakura themes
- Early animated backgrounds
- SQLite task storage

This release established the page structure, task cards, dashboard statistics and theme manager that later versions expanded.

## Stage 2 — 1.1 Patch

A broad stability and theme-behavior pass.

**Recovered changes**
- Added start/stop lifecycle handling to Aurora and Stars animations.
- Reworked the Sakura background from the older leaf model into a petal-based effect.
- Added live theme-change propagation across the app.
- Improved Dashboard refresh behavior after task completion.
- Improved Tasks, Calendar and Statistics refresh/update handling.
- Added theme subscriptions/signals in the theme manager.

## Stage 3 — 1.2 Liquid Glass

The first clear visual-design update.

**Recovered changes**
- Added `glass_effects.py`.
- Introduced refractive/glass frame helpers.
- Added a glass icon-button style.
- Reworked the header, sidebar, stat cards and task cards around the glass aesthetic.
- Updated Tasks, Calendar and Statistics styling to match.

## Experimental branch — Developer Build 1.3

The archive also contains **Flux developer build 1.3**.

Its source layout is significantly smaller than the mainline snapshots around it, so it is treated as an experimental development branch rather than inserted into the stable sequence.

## Stage 4 — Stability / Fixed Series

A long sequence of `Flux-fixed` snapshots followed the liquid-glass work. These are better understood as iterative stabilization builds than as ten completely separate product generations.

### Fixed snapshot 3

Focused on polishing dialogs, cards and page behavior after the liquid-glass changes.

### Fixed snapshot 4 — Settings & Lock Screen

**Added**
- Lock screen
- Settings page
- Settings manager
- Persistent app settings
- User-name personalization across header/dashboard

### Fixed snapshots 5–8 — Lock-screen polish

Successive passes refined:
- lock-screen presentation
- theme selection on the lock screen
- accent colors
- text/translucency treatment
- clock rendering
- startup/unlock behavior

### Fixed snapshot 9 — Dashboard utilities

**Added**
- Mini calendar widget
- Reusable progress ring
- Sidebar progress support
- Task-card context-menu improvements
- Additional visual polish to Sakura and dashboard components

### Fixed snapshot 10 — Notes Update

**Added**
- Notes page
- Notes manager
- Note database model and persistence
- Note locking / PIN support
- Search and note-management flows
- Expanded icon-rendering system

This is the first recovered source snapshot with the Notes experience integrated into Flux.

## Stage 5 — Quality-of-Life / Themes Update

This is the newest source generation found in the archive and matches the current app direction.

**Major additions**
- Focus page with timer presets and session tracking
- Weekly Progress dashboard card and configurable weekly goal
- Task sorting by priority/newest/oldest/due date/title
- Undo after deleting tasks
- Toast notification system
- Quote/banner component
- Reduce-motion setting
- Custom-theme controls and live customization
- Dedicated theme picker
- Expanded branding system

**Theme expansion**
- Astro
- Borealis
- Ember
- Forest
- Mono
- Nebula
- Ocean
- Snow
- Synthwave
- Void
- Custom theme system
- Refactored shared theme base/palette generation

**New animation systems**
- Astro planetary background
- Synthwave background
- More configurable Aurora and Stars effects

**Focus/statistics infrastructure**
- Focus-session database storage
- Focus manager for daily/weekly totals
- Weekly task-completion calculations

This stage is large enough to be treated as a **major Flux update**, not just another patch.

---

## Intentionally excluded from product history

The source dump also contains material that should not become public release clutter:

- `__pycache__` / `.pyc` files
- duplicate requirements files
- generated PyInstaller/portable output
- installer output such as `FluxSetup.exe`
- GitHub/installer helper kits
- duplicate ZIPs of source already represented elsewhere
- unrelated `Dopamine-3.0.9.zip`
- screen recordings and miscellaneous unrelated media

These are fine as private backups, but they would make the public repository much harder to understand.

## Going forward

`main` remains the current Flux source. Historical source can later be preserved through tags/releases while this document stays the human-readable record of the app's evolution.

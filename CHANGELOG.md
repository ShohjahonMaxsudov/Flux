# Changelog

Notable Flux changes, reconstructed from the original source snapshots.

For the full recovered history and duplicate-map, see **[docs/HISTORY.md](docs/HISTORY.md)**.

## v1.0.3 — Navigation & 60 FPS Patch

### Navigation
- Enlarged dock icons and active glass bubble to match the intended minimal proportions.
- Widened/tallened the dock and strengthened the thin theme-reactive rim.
- Removed the hard-edged bottom panel completely.
- Replaced it with a fully feathered bottom atmosphere fade that starts transparent and blends naturally into the window edge.
- Removed duplicate active-pill animation calls.

### Performance
- Removed all live background grabbing from the dock/bottom atmosphere.
- Tasks, Notes, Statistics, Focus, Calendar and Dashboard now render first and refresh their data on the next event-loop tick.
- Removed the main synchronous work that made tab switches feel delayed.

### Motion
- Aurora, Stars, Sakura, Astro and Synthwave now run on precise ~60 FPS timers instead of the previous ~30 FPS timers.
- Particle and Sakura movement is time-scaled so the higher frame rate does not make animations run twice as fast.

## v1.0.2 — Emergency Dock Hotfix

### Fixed
- Removed the expensive 90 ms multi-layer live capture that caused severe UI lag.
- Moved blur out of the dock and into a separate bottom atmosphere gradient.
- Reduced blurred-background sampling to a lightweight low-resolution pass.
- Removed costly page-wide fade effects during navigation.
- Fixed bottom-blur positioning and stacking after the dock refactor.

### Redesigned
- Increased navigation icon size for better readability.
- Returned to a simpler Mentor-inspired dock structure: one moving active pill, restrained glass and minimal chrome.
- Removed dock labels, the progress rail and decorative center indicator.
- Kept Settings visually separated without making the dock feel crowded.
- Added a full-width bottom gradient blur so the animated Flux atmosphere remains visible behind navigation.

## Current — Quality-of-Life / Themes Update

### Added
- Focus page with timer presets and session tracking
- Weekly Progress card and configurable weekly goal
- Task sorting controls
- Undo for deleted tasks
- Toast notifications
- Quote/banner component
- Reduce-motion option
- Custom theme creator and live customization controls
- Expanded theme picker and branding system
- Astro and Synthwave animated backgrounds
- Focus-session persistence and daily/weekly totals

### Themes
Expanded the theme system with Astro, Borealis, Ember, Forest, Mono, Nebula, Ocean, Snow, Synthwave, Void and Custom, alongside the existing themes.

### Improved
- Theme architecture and palette generation
- Aurora and Stars configurability
- Dashboard and task interactions
- Statistics/focus infrastructure
- Icon coverage and visual consistency

## Fixed Snapshot 10 — Notes Update

### Added
- Notes page
- Notes manager and persistence
- Note locking / PIN support
- Search and note-management flows
- Expanded app icon system

## Fixed Snapshot 9 — Dashboard Utilities

### Added
- Mini calendar
- Progress ring
- Sidebar progress integration

### Improved
- Task-card context menu
- Dashboard/Sakura visuals

## Fixed Snapshots 4–8 — Settings & Lock Screen

### Added
- Lock screen
- Settings page
- Persistent settings manager
- User-name personalization

### Improved
Successive snapshots refined lock-screen themes, accents, translucency, clock rendering and startup behavior.

## 1.2 — Liquid Glass

### Added
- Refractive glass helpers
- Glass-frame utilities
- Glass icon-button styling

### Improved
Header, sidebar, stat cards, task cards and main pages received the liquid-glass visual pass.

## 1.1 — Patch

### Improved
- Theme-change propagation
- Animation start/stop behavior
- Dashboard refresh handling
- Tasks, Calendar and Statistics updates
- Sakura animation system

## First Release

Initial Flux foundation with Dashboard, Tasks, Calendar, Statistics, SQLite storage and the first theme/animation system.

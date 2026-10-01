<div align="center">

<img src="assets/flux_icon.png" width="120" alt="Flux logo">

# Flux

### Your day, in flow.

A modern Windows productivity app for tasks, focus, notes, calendar planning and personal statistics — built with Python and PySide6.

[![Build Windows app](https://github.com/ShohjahonMaxsudov/Flux/actions/workflows/build.yml/badge.svg)](https://github.com/ShohjahonMaxsudov/Flux/actions/workflows/build.yml)
![Platform](https://img.shields.io/badge/platform-Windows-0078D4?logo=windows11&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white)

**[Download releases](https://github.com/ShohjahonMaxsudov/Flux/releases)** · **[Patch notes](CHANGELOG.md)** · **[Evolution](docs/HISTORY.md)** · **[Build from source](docs/BUILDING.md)**

</div>

---

<p align="center">
  <img src="https://github.com/user-attachments/assets/51eb538e-2fe5-40f6-a4d2-cbdb67dd14c9" alt="Flux theme gallery" width="100%">
</p>

## ✦ What is Flux?

Flux is a desktop productivity workspace designed to keep daily planning in one place without feeling like a spreadsheet.

Tasks, focus sessions, notes, calendars and statistics live inside one customizable interface with animated themes and a native desktop feel.

## Features

| | Feature | What it does |
|---|---|---|
| ◈ | **Dashboard** | At-a-glance view of your day, progress and activity |
| ✓ | **Tasks** | Create, edit, organize and complete daily tasks |
| ◫ | **Calendar** | Plan around dates and upcoming work |
| ◎ | **Focus** | Dedicated space for distraction-free work sessions |
| ✎ | **Notes** | Keep quick thoughts and longer notes inside Flux |
| ↗ | **Statistics** | Track progress and productivity over time |
| ✦ | **Themes** | Switch between a large collection of visual styles |
| ◌ | **Animations** | Theme-specific particles, glow, stars, sakura, aurora and more |
| 🔒 | **Lock screen** | Built-in app lock experience |
| ⚙ | **Settings** | Personalize Flux to match the way you work |

## Themes

Flux ships with a growing theme system rather than a single light/dark toggle.

Current theme modules include:

**Astro · Borealis · Dark · Ember · Forest · Light · Mono · Nebula · Ocean · Sakura · Snow · Synthwave · Void**

Several themes also have their own animation layer, including stars, aurora, sakura, particles, glow and synthwave effects.

## Built for Windows

Flux is packaged as a normal Windows desktop app.

The GitHub Actions workflow can automatically produce:

- **FluxSetup.exe** — standard Windows installer
- **Flux-portable-windows.zip** — portable build

No Python installation is required for people using the packaged app.

> Builds are generated from the source in this repository. See [Building Flux](docs/BUILDING.md) for developer instructions.

## Data

Flux stores app data locally using **SQLite**. Packaged builds keep writable user data outside protected installation folders so your tasks and notes can persist across updates.

## Tech stack

- **Python**
- **PySide6 / Qt**
- **SQLite**
- **PyInstaller**
- **Inno Setup**
- **GitHub Actions**

## Project structure

```text
Flux/
├── animations/        # Motion and theme effects
├── assets/            # Icons, logos and branding
├── database/          # SQLite models and persistence
├── themes/            # Theme engine and palettes
├── ui/
│   └── pages/         # Dashboard, Tasks, Calendar, Focus, Notes...
├── app.py             # Main application window
└── main.py            # Entry point
```

## Current major update

The newest recovered generation is the **Quality-of-Life / Themes Update**.

It introduced Focus sessions, Weekly Progress, task sorting, undo, toast notifications, custom themes, expanded animations and a much larger theme collection.

See **[CHANGELOG.md](CHANGELOG.md)** for patch notes and **[docs/HISTORY.md](docs/HISTORY.md)** for the reconstructed development history.

## Development status

Flux is actively evolving. The focus is currently on:

- UI polish and consistency
- smoother interactions and animations
- better scheduling and productivity workflows
- stronger customization
- stability and packaging

---

<div align="center">

### ✦ Flux

**Build your day. Keep the flow.**

Made by [ShohjahonMaxsudov](https://github.com/ShohjahonMaxsudov)

</div>

# Flux

A desktop task, notes & calendar manager built with PySide6 (Qt).

This copy has been set up so it can be packaged into a real Windows
app — a `Flux.exe` people can just double-click, and/or a
`FluxSetup.exe` installer like a normal downloaded program — instead
of needing Python installed to run it.

## What changed from your original code

- **`database/database.py`** — the database now lives in
  `%LOCALAPPDATA%\Flux\flux.db` once the app is packaged, instead of
  next to the source files. This matters because a packaged app is
  often installed somewhere read-only (`Program Files`) and, built
  as a single exe, actually runs from a temp folder that gets wiped
  every session — so the old path would have silently lost every
  task on the *second* launch. Running from source with
  `python main.py` is unaffected.
- **`main.py`** — now sets the app/window icon from `assets/icon.ico`.
- **`requirements.txt`** — de-duplicated and version-pinned.
- New packaging files: `assets/icon.ico`, `Flux.spec`,
  `version_info.txt`, `installer.iss`, `build.bat`,
  `.github/workflows/build.yml`, `.gitignore`.

Everything else is your app, untouched.

---

## Option A (recommended): let GitHub build it for you

You don't need a Windows machine at all for this — GitHub's servers
build it and hand you the finished files.

1. Create a new repo on GitHub and push this folder to it:
   ```bash
   git init
   git add .
   git commit -m "Flux"
   git branch -M main
   git remote add origin https://github.com/<you>/flux.git
   git push -u origin main
   ```
2. Tag a release and push the tag — this is what triggers the build:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. Go to the **Actions** tab on your repo and watch "Build Windows
   app" run (a couple of minutes). When it finishes, open the
   **Releases** page on your repo sidebar — `v1.0.0` will have two
   files attached:
   - **`FluxSetup.exe`** — proper installer (Start Menu shortcut,
     optional desktop icon, uninstaller). This is the one to hand to
     someone who just wants to install it like any other program.
   - **`Flux-portable-windows.zip`** — no-install version: unzip it
     anywhere and run `Flux.exe` inside.

Anyone can then download either file straight from your Releases
page — no Python required on their end. Pushing a new tag (`v1.0.1`,
etc.) later builds and publishes an update the same way.

## Option B: build it yourself on Windows

Needs a Windows PC (or VM) with Python 3.10+ installed.

1. Copy this whole `Flux` folder to the Windows machine.
2. Double-click **`build.bat`**. It installs the dependencies and
   runs PyInstaller for you.
3. Your app is now at `dist\Flux\Flux.exe`. The whole `dist\Flux`
   folder is the app — keep it together (zip it to share it as-is).
4. Optional, for a real installer instead of a folder: install
   [Inno Setup](https://jrsoftware.org/isinfo.php) (free), then run
   `ISCC installer.iss` (or open `installer.iss` in the Inno Setup
   app and click Compile). You'll get `installer_output\FluxSetup.exe`.

---

## Publishing on GitHub

Following Option A already gets your code *and* built app on GitHub.
A couple of extras worth doing:
- Add a short description and a screenshot or two to the repo so
  visitors know what they're downloading.
- The `README` badge/link for your latest release is:
  `https://github.com/<you>/flux/releases/latest`

## Sharing on Telegram

Nothing special needed — in any chat or channel, use the attach/file
button and upload `FluxSetup.exe` or `Flux-portable-windows.zip`
directly (Telegram allows large file uploads, well over what this
app needs). Or just paste the GitHub release link from above; either
works fine, but a direct GitHub link means you're not re-uploading a
new file by hand for every update.

## A note on your existing data

Your current `database/flux.db` (next to the source) keeps working
exactly as before when you run `python main.py`. It is **not**
bundled into the built exe and is excluded from git via
`.gitignore` — so your personal tasks/notes don't end up published
on GitHub. If you want to carry your existing tasks into the
packaged app, just copy your current `database/flux.db` to
`%LOCALAPPDATA%\Flux\flux.db` once, after installing/running the
built app for the first time.

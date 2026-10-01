# Building Flux

Flux is a Python + PySide6 Windows desktop app.

## Automatic GitHub build

The repository contains a GitHub Actions workflow at:

```
.github/workflows/build.yml
```

A push to `main` builds the current Windows app automatically.

The workflow produces:

- `FluxSetup.exe` — installable Windows setup
- `Flux-portable-windows.zip` — portable build

You can download completed builds from the **Actions** tab under the build's **Artifacts** section.

### Publishing a tagged release

Version tags matching `v*` also trigger the Windows build.

Example:

```bash
git tag v1.2.0
git push origin v1.2.0
```

Tagged builds are configured to publish the generated installer and portable archive to GitHub Releases.

## Local Windows build

Requirements:

- Windows
- Python 3.10+
- pip
- Optional: Inno Setup 6 for the installer

From the repository root:

```bat
build.bat
```

The portable application is built to:

```
dist\Flux\Flux.exe
```

Keep the whole `dist\Flux` folder together.

To create the installer manually after building:

```bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

The installer configuration currently outputs:

```
release\FluxSetup.exe
```

## Main source layout

```text
main.py             Entry point
app.py              Main application shell
ui/                 UI components
ui/pages/           Main application pages
themes/             Theme engine
animations/         Visual effects
database/           SQLite persistence
assets/             Icons and branding
```

## Notes

Do not commit generated build output, virtual environments or Python cache files. The repository `.gitignore` excludes these files for future commits.

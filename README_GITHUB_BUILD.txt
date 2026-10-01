FLUX -> GITHUB -> WINDOWS INSTALLER
====================================

Your original RAR has 141 files.
Most of the extra files are Python __pycache__ / *.pyc junk.

After removing those cache files and the duplicate requirements.txt.txt,
the real Flux project is only about 78 files, so it fits under GitHub's
100-files-at-once browser uploader limit.

RECOMMENDED PATH
----------------
1) Extract Flux.rar.
2) Drag the extracted Flux folder onto prepare_flux_for_github.bat.
3) Copy these THREE things from this kit into the extracted Flux folder:
       .github\
       installer.iss
       .gitignore

   The final structure should look like:

       Flux\
         .github\
           workflows\
             build-windows.yml
         animations\
         assets\
         database\
         themes\
         ui\
         utils\
         app.py
         main.py
         requirements.txt
         installer.iss
         .gitignore

4) Upload the CONTENTS of that Flux folder to a new GitHub repository.
   main.py should be visible on the repo home page.

   Better: use GitHub Desktop and push the folder. It is not limited by
   the browser's 100-files-per-upload UI limit.

5) Open the repository on GitHub -> Actions.
6) Open "Build Flux Windows Installer".
7) If it did not already run after the push, click "Run workflow".
8) When the run is green, open it.
9) Under Artifacts, download:
       Flux-Windows-Installer

10) The downloaded artifact contains:
       FluxSetup.exe

That EXE is the installable Windows setup for Flux.

IMPORTANT
---------
Do NOT upload:
- __pycache__
- *.pyc
- build/
- dist/
- release/

The .gitignore in this kit prevents them from being committed later.

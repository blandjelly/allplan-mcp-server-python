# M0 Library visibility fix — 0.1.2

Date: 2026-10-07. Tasks: M0.2 / M0.5; UAT-00 retest.

## Owner observation

The owner reports Allplan **2026-1-7**, checked in the application's UI. Setup steps 1–5 for package 0.1.1 were completed, but PythonHost could not be found in the Library palette. UAT-00: **BLOCKED**; UAT-01: **NOT_RUN**. The actual selected Windows Local path and installation log have not yet been inspected. This is owner-reported version evidence, not an automatic host probe or accepted build.

## Confirmed installer defect and correction

The inherited installer placed `StartPythonHost.pyp` under `Local\PythonParts\PythonHost`. The [official 2026 file-location documentation](https://pythonparts.allplan.com/2026/manual/key_components/#file-locations) requires PYP files under `Library` to appear in the Library palette. Portable 0.1.1 tests checked file copying but missed the incorrect destination.

Version 0.1.2 installs `Local\Library\PythonHost\StartPythonHost.pyp`, retaining `Local\PythonPartsScripts\PythonHost` for scripts. Upgrade backs up the previous library, scripts and legacy `PythonParts\PythonHost` folder, then removes the obsolete location. Restore recovers the previous layout, including 0.1.1 backup records, without changing unrelated library items. Installation output now includes the full PYP path and UI library location.

## Portable evidence

Linux external Python 3.12.14, FastMCP 3.2.4. `python -m unittest discover -s tests -v`: **25 tests PASS**, 3.749 seconds. New regression assertions cover the documented Library destination, absence of the obsolete destination, migration from the 0.1.1 layout, recovery of that layout, preservation of unrelated Library entries and order-independent old backup metadata. Existing package integrity, transport and fake-adapter checks also pass. `git diff --check`: PASS. Version 0.1.2 external package sync and wheel/sdist build completed.

The final 0.1.2 ZIP is extracted, integrity-checked and installed/restored in a temporary user folder before delivery. This does not verify visibility or script startup in a real Allplan session.

## Small retest

Close Allplan. Extract 0.1.2 into its own folder and run Setup.cmd, selecting the same actual Allplan user Local folder. Reopen Allplan and navigate to Library → Private → PythonHost → StartPythonHost, with any PythonPart-hiding filter cleared. First report whether the entry appears and starts. If it is still absent, supply `logs\installation.json` from the new package to inspect the exact selected path. Continue the existing UAT-00 prompts only after starting the host; the integrated M0 gate stays pending.

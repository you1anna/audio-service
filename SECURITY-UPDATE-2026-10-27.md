# Security dependency update — 27 October 2026

Python 3.12.16 and repaired pip/certificate trust must be installed per host. The requirements now set safe minimums for already-used HTTP, IDNA and MessagePack dependencies. On the Mac mini, stop the watcher using its existing launchd runbook before changing its environment. From python_service run `.venv/bin/python -m pip install -r requirements.txt`, `.venv/bin/python -m pip check`, and `.venv/bin/python -m unittest discover -s tests`. Then use the existing host-specific service runbook to restart and inspect health.

MacBook Air: 50 synthetic tests and pip check passed after the targeted updates. No real audio processing, library/config modification or service restart was performed. Preserve per-host FLAC retention and SSD guards. If validation fails, leave the watcher stopped and forward-fix; do not restore vulnerable dependencies or delete processing markers.

The repository default branch is now main, following the personal-repository convention; master is retained. Existing Mac mini clones should fetch and switch to main before installing. The remote FLAC input-format fix was preserved and its tests rerun.

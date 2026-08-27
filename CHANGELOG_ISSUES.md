# Issues & Technical Decisions Changelog
## Running record of real bugs, wrong assumptions, and fixes encountered during development

---

### [Execution & OS Environment]
- **Issue:** `uvicorn.exe` blocked on Windows with `An Application Control policy has blocked this file` (WDAC/AppLocker policy blocking `.exe` stubs generated in `venv/Scripts/`).
- **Fix:** Launch uvicorn via Python module invocation (`python -m uvicorn app.main:app --reload --port 8000`) or `python -m app.main`.
- **Status:** Documented and resolved.

---

### [Setup & Dependency Management]
- **Issue:** Running `ml/combine_data.py` failed with `ModuleNotFoundError: No module named 'faker'`.
- **Root Cause:** `faker` is required by `ml/combine_data.py` (documented in `docs/architecture.md` §4 & §6) to generate synthetic customer names and decline labels, but was omitted from `backend/requirements.txt`.
- **Fix:** Added `faker>=24.0.0` to `backend/requirements.txt` and installed it into the active virtual environment.
- **Status:** Resolved. Tested and verified `ml/combine_data.py` runs cleanly.

---

### [Scaffolding & Layout]
- **Issue / Finding:** Project files were initially located flat in repository root.
- **Fix:** Moved documentation into `docs/` and ML artifacts/notebooks into `ml/` conforming to `docs/architecture.md` §7.
- **Status:** Resolved.

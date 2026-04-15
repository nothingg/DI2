# prototype_v2

Desktop prototype for the DI rewrite. This version uses:

- `PySide6` for the desktop UI
- `Playwright` for browser automation
- adapter-based execution so each biller can implement its own workflow

## Current scope

- One GUI with biller + date selection
- One runnable adapter example: `mpay`
- Temp workspace per job
- Failure artifacts per job: screenshot, HTML snapshot, and metadata
- Final output path per biller/date
- Basic structured logging and error handling

## Layout

```text
prototype_v2/
  app.py
  requirements.txt
  README.md
  .env.example
  app/
    adapters/
    core/
    infra/
    ui/
```

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chrome
```

## Configure

Copy `.env.example` to `.env` and fill in the values you need.

Important notes:

- `MPAY_USERNAME` and `MPAY_PASSWORD` are read from environment variables.
- `PLAYWRIGHT_SLOW_MO_MS` adds a delay after each Playwright action for debugging.
- `REAL_CHROME_EXECUTABLE` is optional. Use it if you want to point to a local Chrome binary.
- `BROWSER_MODE=real_profile` is reserved for the real-browser/manual-assisted path. The prototype keeps the enum and config now, but the first working path is `managed`.

## Run

```powershell
python app.py
```

## What this prototype proves

- The UI does not call scripts directly.
- A job request flows through a central `JobRunner`.
- Each biller is an adapter with a common contract.
- Files are downloaded into a per-job temp directory first, then moved into a final output directory only after validation.

## Mpay status

`mpay` is implemented as a prototype adapter. It contains the real structure and Playwright flow, but selectors and popup handling may still need site-specific refinement on a live run.

## Failure artifacts

When a job fails, the prototype stores debug files under:

```text
runs/<job_id>/artifacts/
```

Current artifacts:

- `failure-screenshot.png`
- `failure-page.html`
- `failure-meta.txt`

## Next steps

1. Run the prototype against a real `mpay` session and refine selectors.
2. Add screenshot/html capture on failure.
3. Add a manual-assisted browser mode for anti-bot sites.
4. Add more biller adapters.

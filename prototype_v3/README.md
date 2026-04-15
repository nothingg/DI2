# prototype_v3

Rewrite scaffold for the DI desktop automation project.

Current scope:

- New project layout separated from the legacy scripts
- `mpay` as the first biller adapter
- PySide6 desktop UI
- Playwright browser automation with Chrome channel
- Temp run directories, output directories, and failure artifacts

Planned next steps:

1. Wire the `mpay` flow to real selectors and downloads.
2. Move validated legacy logic into the new adapter structure.
3. Add more billers after the `mpay` pattern settles.

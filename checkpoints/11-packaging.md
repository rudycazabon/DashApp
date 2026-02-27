# Checkpoint 11 — Packaging and Distribution

## Date
2026-02-26

## Summary
Configured `pyproject.toml` for proper wheel distribution and verified the full
`uv build` → `uv tool install` workflow.

## Changes

### `pyproject.toml`
- Added `[build-system]` section (setuptools ≥ 61) — without it, setuptools failed
  with "multiple top-level packages discovered in flat-layout"
- Added `[tool.setuptools]` with `py-modules = ["main", "config", "loader"]` to
  include the three top-level modules that aren't part of a package
- Added `[tool.setuptools.packages.find]` with `include = ["db*", "tools*", "tui*",
  "util*"]` to include only application packages (excludes `tests`, `checkpoints`,
  `.venv`)
- Added `[tool.setuptools.package-data]` with `"*" = ["manifest.json"]` to bundle
  all `tools/*/manifest.json` files into the wheel
- Moved `textual-dev` from `[project] dependencies` to `[tool.uv] dev-dependencies`
  (it is a development utility, not a runtime requirement)

## Verification
- `uv build` → produces `dist/dashapp-0.1.0.tar.gz` and
  `dist/dashapp-0.1.0-py3-none-any.whl`
- `uv tool install dist/dashapp-0.1.0-py3-none-any.whl` → installs cleanly with
  53 runtime packages (no `textual-dev`)
- `dashapp` command available at `~/.local/bin/dashapp`
- All 6 `manifest.json` files confirmed present in the installed site-packages
- All 90 tests pass

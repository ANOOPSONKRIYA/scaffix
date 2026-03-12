# Scaffix Project Guide

This document explains the internal logic and design decisions of Scaffix so the project is easy to maintain.

## 1) Purpose

Scaffix solves one repeated task: generating a predictable numbered folder layout with common child directories.

Example use cases:
- Daily coding challenge folders
- Batch task directories
- Assignment or sprint skeletons

## 2) Core Design Principles

- **Clarity first**: all actions are prompt-driven and visible to the user.
- **Safety first**: final confirmation before filesystem writes.
- **Idempotent writes**: `os.makedirs(..., exist_ok=True)` avoids hard failures if rerun.
- **Resilience**: one folder failure should not stop all remaining folders.

## 3) Runtime Flow

Scaffix execution (`scaffix.cli.main`) runs in this order:

1. `get_folder_range()`
   - Reads `start` and `end` as integers.
   - Validates `end >= start`.

2. `get_zero_padding(end)`
   - Computes default width from `end` digit length.
   - Returns padding width or `0`.

3. `get_subdirectories()`
   - Reads optional comma-separated values.
   - Trims spaces and allows empty input to create only parent folders.

4. `get_base_path()`
   - Uses current working directory if blank.
   - Validates directory; can create missing path on approval.

5. `confirm_and_create(...)`
   - Prints summary and small tree preview.
   - Waits for explicit confirmation.
   - Creates parent and child directories.
   - Reports created/skipped counts.

## 4) File Responsibilities

- `src/scaffix/cli.py`
  - All interaction and creation logic.
  - This is the main file to extend for new features.

- `src/scaffix/__main__.py`
  - Entrypoint for `python -m scaffix`.

- `src/scaffix/__init__.py`
  - Package metadata (`__version__`).

- `pyproject.toml`
  - Packaging metadata and script mapping:
    - `scaffix = "scaffix.__main__:main"`

## 5) Error and Exit Strategy

- Invalid user input loops until valid.
- `KeyboardInterrupt` is handled gracefully in `main()`.
- Filesystem errors are reported with folder name context.

## 6) How to Extend Safely

If you add features, keep this structure:
- Add new input collection before `confirm_and_create`.
- Preserve summary/preview so users can verify intent.
- Keep write operations inside a single controlled function.
- Avoid silent behavior changes.

## 7) Testing Priorities (Recommended)

1. Range validation (`end < start` rejected)
2. Subdirectory parsing (spaces/empty values)
3. Zero padding behavior
4. Base path creation flow
5. Directory creation counts in partial-failure scenarios

## 8) Contributor Quick Start

```bash
pip install -e .
scaffix
```

Or:

```bash
python -m scaffix
```

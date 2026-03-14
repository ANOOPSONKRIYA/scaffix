# Scaffix

Scaffix is a small interactive CLI that creates numbered folder structures with consistent subdirectories.

Goal: make repetitive workspace setup fast, safe, and predictable.

[![CI](https://github.com/ANOOPSONKRIYA/scaffix/actions/workflows/ci.yml/badge.svg)](https://github.com/ANOOPSONKRIYA/scaffix/actions/workflows/ci.yml)
[![Version](https://img.shields.io/pypi/v/scaffix?label=Version)](https://pypi.org/project/scaffix/#history)
[![Python](https://img.shields.io/pypi/pyversions/scaffix?label=Python)](https://pypi.org/project/scaffix/)
[![License](https://img.shields.io/github/license/ANOOPSONKRIYA/scaffix?label=License)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/scaffix?label=PyPI)](https://pypi.org/project/scaffix/)

---

## ✨ Features

- Create parent folders in any numeric range (for example: `1` to `100`)
- Optional zero padding (for example: `001`, `002`, `003`)
- Optional custom child directories in every parent folder
- Explicit skip option when you do not want folder-in-folder creation
- Preview and confirmation before filesystem changes
- Colored output for better CLI readability
- Cleaner tree-style preview formatting
- Progress bar during folder generation
- Error logging to `scaffix.log`
- Idempotent creation (`exist_ok=True`) to avoid hard failures on reruns

---

## 🧠 How Scaffix Works

Scaffix follows a simple step-by-step flow:

1. Ask for folder range (`start` and `end`)
2. Ask whether names should be zero-padded
3. Ask whether subdirectories are needed; press Enter with no input to skip for parent-only output
4. Ask for base output path
5. Show summary + preview tree
6. Ask confirmation and then create directories

If one folder fails to create, Scaffix continues with the next folder and reports results at the end.

---

## 📦 Installation (Local Development)

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/scaffix.git
cd scaffix
```

Install in editable mode:

```bash
pip install -e .
```

Run:

```bash
scaffix
```

Alternative run mode:

```bash
python -m scaffix
```

Check version:

```bash
scaffix --version
```

---

## 🚀 Example Usage

```
Enter START number: 1
Enter END number: 5
Zero-pad folder names? Y
Create subdirectories inside each folder? Y
Subdirectories: code, task
Base path: ./demo
```

Output structure:

```
01/
   ├── code/
   ├── task/
02/
   ├── code/
   ├── task/
...
```

---

## 📁 Project Structure

```text
src/scaffix/
├── __init__.py   # Package metadata (__version__)
├── __main__.py   # python -m scaffix entrypoint
└── cli.py        # Interactive prompts + folder creation logic

tests/            # Test suite
```

Quick parent-only example:

```text
Enter START number: 1
Enter END number: 100
Zero-pad folder names? N
Create subdirectories inside each folder? N
Base path: ./demo
```

For deeper internal flow, see `docs/PROJECT_GUIDE.md`.

---

## 🛠 Developer Notes

- Main entry function: `scaffix.cli.main()`
- Safe cancellation: `Ctrl + C` exits cleanly
- Errors are handled per folder to avoid stopping the whole run
- Runtime errors are logged to `scaffix.log`
- Current Python requirement: `>=3.8`

### Dev setup

```bash
pip install -e .[dev]
pre-commit install
```

Run checks locally:

```bash
black --check src tests
pytest
```

---

## 🚢 Release & Publishing

- Semantic versioning is enabled using conventional commits.
- `.github/workflows/semantic-release.yml` handles automated version/tag/release.
- `.github/workflows/publish-pypi.yml` publishes to PyPI when a GitHub release is published.
- For PyPI automation, configure a Trusted Publisher for this repository in PyPI.

---

## ✅ Suggested Next Improvements

- Add automated tests for input parsing and creation behavior
- Add a non-interactive mode with CLI flags (`--start`, `--end`, etc.)
- Add optional dry-run mode (preview without creating)

---

## 🏷 Version

Current version: 1.0.1

---

## 📄 License

MIT License
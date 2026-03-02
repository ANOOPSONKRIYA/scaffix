# Scaffix

Scaffix is a small interactive CLI that creates numbered folder structures with consistent subdirectories.

Goal: make repetitive workspace setup fast, safe, and predictable.

![CI](https://github.com/ANOOPSONKRIYA/scaffix/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PyPI](https://img.shields.io/pypi/v/scaffix)
![Downloads](https://img.shields.io/pypi/dm/scaffix)

---

## ✨ Features

- Create parent folders in any numeric range (for example: `1` to `100`)
- Optional zero padding (for example: `001`, `002`, `003`)
- Create custom child directories in every parent folder
- Preview and confirmation before filesystem changes
- Idempotent creation (`exist_ok=True`) to avoid hard failures on reruns

---

## 🧠 How Scaffix Works

Scaffix follows a simple step-by-step flow:

1. Ask for folder range (`start` and `end`)
2. Ask whether names should be zero-padded
3. Ask for comma-separated subdirectory names
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

tests/            # Test suite (currently empty)
```

For deeper internal flow, see `docs/PROJECT_GUIDE.md`.

---

## 🛠 Developer Notes

- Main entry function: `scaffix.cli.main()`
- Safe cancellation: `Ctrl + C` exits cleanly
- Errors are handled per folder to avoid stopping the whole run
- Current Python requirement: `>=3.8`

---

## ✅ Suggested Next Improvements

- Add automated tests for input parsing and creation behavior
- Add a non-interactive mode with CLI flags (`--start`, `--end`, etc.)
- Add optional dry-run mode (preview without creating)

---

## 🏷 Version

Current version: 1.0.0

---

## 📄 License

MIT License
# Scaffix

Scaffix is a simple and interactive CLI tool that generates numbered folder structures with custom subdirectories.

![CI](https://github.com/ANOOPSONKRIYA/scaffix/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- Create folders in a numeric range (e.g., 0–90)
- Optional zero-padding (01, 02, 03...)
- Custom subdirectories inside each folder
- Interactive CLI experience
- Safe confirmation before creation

---

## 📦 Installation (Local Development)

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/scaffix.git
cd scaffix
```

Install locally:

```bash
pip install -e .
```

Run:

```bash
scaffix
```

---

## 🚀 Example Usage

```
Enter START number: 1
Enter END number: 5
Zero-pad folder names? Y
Subdirectories: code, task
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

## 🏷 Version

Current version: 1.0.0

---

## 📄 License

MIT License
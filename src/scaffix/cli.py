#!/usr/bin/env python3
"""
Interactive CLI for generating numbered folder structures.

Execution flow:
1) Collect user inputs (range, padding, subfolders, base path)
2) Show a summary + small preview tree
3) Ask for final confirmation
4) Create directories safely with per-folder error handling

Design goals:
- Keep prompts beginner-friendly and explicit
- Make behavior predictable and easy to trace
- Remain idempotent by using `exist_ok=True`
"""

import os
import sys
from scaffix import __version__


def get_folder_range():
    """Prompt for the numeric folder range and validate boundaries."""
    print("\n" + "=" * 50)
    print("       📁 FOLDER GENERATOR CLI")
    print("=" * 50)

    while True:
        try:
            start = int(input("\n🔹 Enter START number (e.g., 0): ").strip())
            end = int(input("🔹 Enter END number   (e.g., 90): ").strip())
            if end < start:
                print("❌ END must be >= START. Try again.")
                continue
            return start, end
        except ValueError:
            print("❌ Please enter valid integers.")


def get_zero_padding(end):
    """Ask whether folder names should be zero-padded.

    Returns:
        int: number of digits to use with zfill, or 0 for no padding.
    """
    digits = len(str(end))
    while True:
        pad = input(f"\n🔹 Zero-pad folder names? (e.g., '01' instead of '1') [Y/n]: ").strip().lower()
        if pad in ("", "y", "yes"):
            return digits
        elif pad in ("n", "no"):
            return 0
        else:
            print("❌ Please enter Y or N.")


def get_subdirectories():
    """Prompt for comma-separated subdirectory names.

    Empty input or only separators are rejected until valid names are provided.
    """
    print("\n🔹 Enter subdirectory names to create inside EACH folder.")
    print("   (comma-separated, e.g.: code, task)")

    while True:
        raw = input("   ➜ Subdirectories: ").strip()
        if not raw:
            print("❌ Please enter at least one subdirectory name.")
            continue
        subdirs = [s.strip() for s in raw.split(",") if s.strip()]
        if not subdirs:
            print("❌ No valid names found. Try again.")
            continue
        return subdirs


def get_base_path():
    """Prompt for a base output directory and ensure it exists.

    If the user leaves it empty, current working directory is used.
    If the path does not exist, user is asked whether to create it.
    """
    while True:
        path = input("\n🔹 Base path to create folders in (press Enter for current dir): ").strip()
        if not path:
            path = os.getcwd()

        if os.path.isdir(path):
            return path
        else:
            create = input(f"   '{path}' doesn't exist. Create it? [Y/n]: ").strip().lower()
            if create in ("", "y", "yes"):
                try:
                    os.makedirs(path, exist_ok=True)
                    return path
                except OSError as e:
                    print(f"❌ Error creating path: {e}")
            else:
                print("   Okay, try a different path.")


def confirm_and_create(base_path, start, end, padding, subdirs):
    """Preview the plan, ask confirmation, then create folder tree.

    Args:
        base_path (str): Target root directory.
        start (int): Starting folder number (inclusive).
        end (int): Ending folder number (inclusive).
        padding (int): zfill width. Zero means no padding.
        subdirs (list[str]): Child directories to create inside each folder.
    """
    total_folders = end - start + 1
    total_dirs = total_folders * (1 + len(subdirs))

    # Summary helps users validate intent before any filesystem changes.
    print("\n" + "=" * 50)
    print("       📋 SUMMARY")
    print("=" * 50)
    print(f"  Base Path      : {base_path}")
    print(f"  Folder Range   : {start} → {end} ({total_folders} folders)")
    print(f"  Zero-Padded    : {'Yes' if padding else 'No'}")
    print(f"  Subdirectories : {', '.join(subdirs)}")
    print(f"  Total dirs     : {total_dirs}")
    print("=" * 50)

    # Small tree preview gives confidence about naming + structure.
    print("\n  📂 Preview (first 3 folders):\n")
    for i in range(start, min(start + 3, end + 1)):
        name = str(i).zfill(padding) if padding else str(i)
        print(f"    {name}/")
        for sd in subdirs:
            print(f"      ├── {sd}/")
    if total_folders > 3:
        print(f"    ... and {total_folders - 3} more folders")

    # Hard stop on negative confirmation: no writes are performed.
    confirm = input("\n🔹 Proceed? [Y/n]: ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("\n❌ Cancelled. No folders created.")
        return

    # Continue creating even if one folder fails, then report aggregate result.
    created = 0
    skipped = 0
    for i in range(start, end + 1):
        name = str(i).zfill(padding) if padding else str(i)
        folder_path = os.path.join(base_path, name)

        try:
            os.makedirs(folder_path, exist_ok=True)
            for sd in subdirs:
                sub_path = os.path.join(folder_path, sd)
                os.makedirs(sub_path, exist_ok=True)
            created += 1
        except OSError as e:
            print(f"  ⚠️  Error creating '{name}': {e}")
            skipped += 1

    # Final run summary.
    print("\n" + "=" * 50)
    print("       ✅ DONE!")
    print("=" * 50)
    print(f"  Created : {created} folders")
    if skipped:
        print(f"  Skipped : {skipped} folders (errors)")
    print(f"  Location: {base_path}")
    print("=" * 50 + "\n")

def main():
    """Entry point for command-line execution."""
    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"Scaffix v{__version__}")
        sys.exit(0)

    try:
        start, end = get_folder_range()
        padding = get_zero_padding(end)
        subdirs = get_subdirectories()
        base_path = get_base_path()
        confirm_and_create(base_path, start, end, padding, subdirs)
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user. Bye!")
        sys.exit(0)
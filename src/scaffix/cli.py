#!/usr/bin/env python3
"""
Folder Generator CLI
Creates numbered folders with custom subdirectories inside each.
"""

import os
import sys
from scaffix import __version__


def get_folder_range():
    """Ask user for the folder naming range."""
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
    """Ask user if they want zero-padded names."""
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
    """Ask user for subdirectory names."""
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
    """Ask user for the base output directory."""
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
    """Show summary and create folders after confirmation."""
    total_folders = end - start + 1
    total_dirs = total_folders * (1 + len(subdirs))

    # --- Preview ---
    print("\n" + "=" * 50)
    print("       📋 SUMMARY")
    print("=" * 50)
    print(f"  Base Path      : {base_path}")
    print(f"  Folder Range   : {start} → {end} ({total_folders} folders)")
    print(f"  Zero-Padded    : {'Yes' if padding else 'No'}")
    print(f"  Subdirectories : {', '.join(subdirs)}")
    print(f"  Total dirs     : {total_dirs}")
    print("=" * 50)

    # --- Show tree preview ---
    print("\n  📂 Preview (first 3 folders):\n")
    for i in range(start, min(start + 3, end + 1)):
        name = str(i).zfill(padding) if padding else str(i)
        print(f"    {name}/")
        for sd in subdirs:
            print(f"      ├── {sd}/")
    if total_folders > 3:
        print(f"    ... and {total_folders - 3} more folders")

    # --- Confirm ---
    confirm = input("\n🔹 Proceed? [Y/n]: ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("\n❌ Cancelled. No folders created.")
        return

    # --- Create ---
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

    # --- Result ---
    print("\n" + "=" * 50)
    print("       ✅ DONE!")
    print("=" * 50)
    print(f"  Created : {created} folders")
    if skipped:
        print(f"  Skipped : {skipped} folders (errors)")
    print(f"  Location: {base_path}")
    print("=" * 50 + "\n")

def main():
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
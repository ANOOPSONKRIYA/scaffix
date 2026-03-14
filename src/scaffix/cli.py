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

import logging
import os
import sys

from colorama import Fore, Style, init

from scaffix import __version__

init(autoreset=True)

LOGGER = logging.getLogger("scaffix")
LOG_FILE = "scaffix.log"


def configure_logging(log_file=LOG_FILE):
    """Configure file-based error logging for troubleshooting."""
    if LOGGER.handlers:
        return LOGGER

    LOGGER.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.propagate = False
    return LOGGER


def color_text(text, color):
    """Return colored text for CLI readability."""
    return f"{color}{text}{Style.RESET_ALL}"


def format_folder_name(index, padding):
    """Format numeric folder names with optional zero padding."""
    return str(index).zfill(padding) if padding else str(index)


def render_preview_tree(start, end, padding, subdirs, preview_limit=3):
    """Build a compact, readable tree preview for the first folders."""
    lines = []
    preview_end = min(start + preview_limit - 1, end)

    for i in range(start, preview_end + 1):
        name = format_folder_name(i, padding)
        lines.append(f"{name}/")
        for idx, subdir in enumerate(subdirs):
            branch = "└──" if idx == len(subdirs) - 1 else "├──"
            lines.append(f"   {branch} {subdir}/")

    if preview_end < end:
        lines.append(f"... and {end - preview_end} more folders")

    return "\n".join(lines)


def print_progress(current, total, width=30):
    """Render a simple in-place progress bar for folder creation."""
    if total <= 0:
        return

    ratio = current / total
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    end = "\n" if current == total else "\r"
    print(color_text(f"  Progress: [{bar}] {current}/{total}", Fore.CYAN), end=end, flush=True)


def get_folder_range():
    """Prompt for the numeric folder range and validate boundaries."""
    print(color_text("\n" + "=" * 50, Fore.BLUE))
    print(color_text("       📁 FOLDER GENERATOR CLI", Fore.BLUE))
    print(color_text("=" * 50, Fore.BLUE))

    while True:
        try:
            start = int(input("\n🔹 Enter START number (e.g., 0): ").strip())
            end = int(input("🔹 Enter END number   (e.g., 90): ").strip())
            if end < start:
                print(color_text("❌ END must be >= START. Try again.", Fore.RED))
                continue
            return start, end
        except ValueError:
            print(color_text("❌ Please enter valid integers.", Fore.RED))


def get_zero_padding(end):
    """Ask whether folder names should be zero-padded.

    Returns:
        int: number of digits to use with zfill, or 0 for no padding.
    """
    digits = len(str(end))
    while True:
        pad = (
            input(f"\n🔹 Zero-pad folder names? (e.g., '01' instead of '1') [Y/n]: ")
            .strip()
            .lower()
        )
        if pad in ("", "y", "yes"):
            return digits
        elif pad in ("n", "no"):
            return 0
        else:
            print(color_text("❌ Please enter Y or N.", Fore.RED))


def get_subdirectories():
    """Prompt for optional comma-separated subdirectory names.

    Users can press Enter with no input to skip the entire step and create
    only parent folders.
    """
    while True:
        choice = (
            input(
                "\n🔹 Create subdirectories inside each folder? [y/N, Enter to skip]: "
            )
            .strip()
            .lower()
        )
        if choice in ("", "n", "no"):
            return []
        if choice in ("y", "yes"):
            break
        print(color_text("❌ Please enter Y or N.", Fore.RED))

    print("   Enter subdirectory names to create inside EACH folder.")
    print("   (comma-separated, e.g.: code, task | type 'skip' to cancel this step)")

    while True:
        raw = input("   ➜ Subdirectories: ").strip()
        if not raw or raw.lower() == "skip":
            return []
        subdirs = [s.strip() for s in raw.split(",") if s.strip()]
        if not subdirs:
            print(
                color_text(
                    "❌ No valid names found. Add names or type 'skip' to cancel.", Fore.RED
                )
            )
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
                    print(color_text(f"❌ Error creating path: {e}", Fore.RED))
                    LOGGER.exception("Failed to create base path: %s", path)
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
    print(color_text("\n" + "=" * 50, Fore.BLUE))
    print(color_text("       📋 SUMMARY", Fore.BLUE))
    print(color_text("=" * 50, Fore.BLUE))
    print(f"  Base Path      : {base_path}")
    print(f"  Folder Range   : {start} → {end} ({total_folders} folders)")
    print(f"  Zero-Padded    : {'Yes' if padding else 'No'}")
    print(f"  Subdirectories : {', '.join(subdirs) if subdirs else '(none)'}")
    print(f"  Total dirs     : {total_dirs}")
    print(color_text("=" * 50, Fore.BLUE))

    # Small tree preview gives confidence about naming + structure.
    print(color_text("\n  📂 Preview (first 3 folders):\n", Fore.MAGENTA))
    print(render_preview_tree(start, end, padding, subdirs, preview_limit=3))

    # Hard stop on negative confirmation: no writes are performed.
    confirm = input("\n🔹 Proceed? [Y/n]: ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print(color_text("\n❌ Cancelled. No folders created.", Fore.YELLOW))
        return

    # Continue creating even if one folder fails, then report aggregate result.
    created = 0
    skipped = 0
    processed = 0
    for i in range(start, end + 1):
        name = format_folder_name(i, padding)
        folder_path = os.path.join(base_path, name)

        try:
            os.makedirs(folder_path, exist_ok=True)
            for sd in subdirs:
                sub_path = os.path.join(folder_path, sd)
                os.makedirs(sub_path, exist_ok=True)
            created += 1
        except OSError as e:
            print(color_text(f"  ⚠️  Error creating '{name}': {e}", Fore.RED))
            LOGGER.exception("Failed to create folder '%s' in '%s'", name, base_path)
            skipped += 1
        finally:
            processed += 1
            print_progress(processed, total_folders)

    # Final run summary.
    print(color_text("\n" + "=" * 50, Fore.GREEN))
    print(color_text("       ✅ DONE!", Fore.GREEN))
    print(color_text("=" * 50, Fore.GREEN))
    print(color_text(f"  Created : {created} folders", Fore.GREEN))
    if skipped:
        print(color_text(f"  Skipped : {skipped} folders (errors)", Fore.YELLOW))
        print(color_text(f"  Logs    : {os.path.abspath(LOG_FILE)}", Fore.YELLOW))
    print(f"  Location: {base_path}")
    print(color_text("=" * 50, Fore.GREEN) + "\n")


def main():
    """Entry point for command-line execution."""
    configure_logging()

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
        print(color_text("\n\n👋 Cancelled by user. Bye!", Fore.YELLOW))
        sys.exit(0)
    except Exception as exc:
        LOGGER.exception("Unexpected CLI error: %s", exc)
        print(color_text("\n❌ Unexpected error. See scaffix.log for details.", Fore.RED))
        sys.exit(1)

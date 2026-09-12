#!/usr/bin/env python3
"""Validate/list existing analysis commands; execution requires --execute."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def within_root(path):
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Profile paths must remain inside this repository")
    return path


def load_profile(path):
    path = within_root(path if path.is_absolute() else ROOT / path)
    config = json.loads(path.read_text())
    if config.get("schema_version") != "1.0":
        raise ValueError("Unsupported profile schema")
    commands = config.get("commands")
    if not isinstance(commands, list) or not commands:
        raise ValueError("Profile requires a nonempty command list")
    resolved = []
    for item in commands:
        cwd = within_root(ROOT / item.get("cwd", "."))
        argv = item.get("argv")
        if not cwd.is_dir() or not isinstance(argv, list) or len(argv) < 2:
            raise ValueError("Invalid working directory or command array")
        if not all(isinstance(a, str) and a and "\x00" not in a for a in argv):
            raise ValueError("Command arguments must be nonempty strings")
        if argv[0] != "{python}":
            raise ValueError("Profiles must use the current Python interpreter placeholder")
        script = within_root(cwd / argv[1])
        if script.suffix != ".py" or not script.is_file():
            raise ValueError("Profile Python entry point is missing")
        resolved.append((cwd, [sys.executable, str(script), *argv[2:]]))
    return config, resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Repository-relative or absolute profile JSON")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate and print commands only (default)")
    mode.add_argument("--execute", action="store_true", help="Run commands sequentially; generated outputs may be replaced")
    args = parser.parse_args()
    if args.config is None:
        parser.print_help()
        print("\nAvailable profiles:")
        for path in sorted((ROOT / "configs").glob("*.json")):
            print(" ", path.relative_to(ROOT))
        return
    try:
        config, commands = load_profile(args.config)
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    print(f"Profile: {config['name']}", flush=True)
    print(config.get("purpose", ""), flush=True)
    print("Execution profiles were added for this repository; historical runs did not use these JSON wrappers.", flush=True)
    for cwd, argv in commands:
        print(f"[{cwd.relative_to(ROOT)}] {shlex.join(argv)}", flush=True)
    if not args.execute:
        print("Dry run completed; no subprocesses or scientific outputs created.")
        return
    print(config.get("output_warning", "Commands may replace generated outputs."), flush=True)
    for cwd, argv in commands:
        subprocess.run(argv, cwd=cwd, check=True)


if __name__ == "__main__":
    main()

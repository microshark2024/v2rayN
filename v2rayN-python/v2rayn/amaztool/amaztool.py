"""AmazTool - Self-update utility.

Ported from v2rayN AmazTool.
Handles updating the application binary after download.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import zipfile

from v2rayn.common import logging_config

_tag = "AmazTool"


def self_update(
    new_archive: str,
    target_dir: str,
    restart_exe: str = "",
    restart_args: list[str] | None = None,
) -> bool:
    """Perform self-update from archive.

    This function:
    1. Waits for the main process to exit
    2. Extracts the new archive to the target directory
    3. Optionally restarts the application

    Args:
        new_archive: Path to the update archive (zip)
        target_dir: Target directory to extract to
        restart_exe: Path to executable to restart after update
        restart_args: Arguments for restart executable

    Returns:
        True on success
    """
    try:
        # Wait a moment for the main process to exit
        time.sleep(2)

        if not os.path.exists(new_archive):
            print(f"Update archive not found: {new_archive}")
            return False

        # Extract archive
        print(f"Extracting update to {target_dir}...")
        with zipfile.ZipFile(new_archive, "r") as zf:
            zf.extractall(target_dir)

        # Clean up archive
        try:
            os.remove(new_archive)
        except Exception:
            pass

        print("Update complete.")

        # Restart if requested
        if restart_exe and os.path.exists(restart_exe):
            print(f"Restarting: {restart_exe}")
            subprocess.Popen(
                [restart_exe] + (restart_args or []),
                cwd=os.path.dirname(restart_exe),
            )

        return True
    except Exception as ex:
        print(f"Update failed: {ex}")
        logging_config.save_log_ex(_tag, ex)
        return False


def main() -> int:
    """AmazTool command-line entry point.

    Usage: amaztool <archive> <target_dir> [restart_exe] [restart_args...]
    """
    if len(sys.argv) < 3:
        print("Usage: amaztool <archive> <target_dir> [restart_exe] [restart_args...]")
        return 1

    archive = sys.argv[1]
    target_dir = sys.argv[2]
    restart_exe = sys.argv[3] if len(sys.argv) > 3 else ""
    restart_args = sys.argv[4:] if len(sys.argv) > 4 else []

    success = self_update(archive, target_dir, restart_exe, restart_args)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

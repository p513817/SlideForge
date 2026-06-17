"""Environment checks for SlideForge."""

import shutil
import subprocess
import sys


FFMPEG_INSTALL_HELP = [
    "Install ffmpeg and make sure both ffmpeg and ffprobe are available on PATH.",
    "Windows options:",
    "  winget install Gyan.FFmpeg",
    "  choco install ffmpeg",
    "  scoop install ffmpeg",
    "Manual download: https://ffmpeg.org/download.html",
    "After installing, open a new terminal and run: ffmpeg -version",
]


def find_executable(name: str) -> str | None:
    return shutil.which(name)


def get_tool_version(executable: str) -> str:
    try:
        result = subprocess.run(
            [executable, "-version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "version unavailable"

    first_line = result.stdout.splitlines()[0].strip() if result.stdout else ""
    return first_line or "version unavailable"


def print_ffmpeg_install_help() -> None:
    for line in FFMPEG_INSTALL_HELP:
        print(f"   {line}" if line else "")


def check_ffmpeg():
    """Ensure ffmpeg and ffprobe are available."""
    if find_executable("ffmpeg") is None:
        print("ERROR: ffmpeg was not found.")
        print_ffmpeg_install_help()
        sys.exit(1)
    if find_executable("ffprobe") is None:
        print("ERROR: ffprobe was not found.")
        print_ffmpeg_install_help()
        sys.exit(1)


def check_powerpoint():
    """Ensure pywin32 PowerPoint COM support is available."""
    try:
        import win32com.client
        return True
    except ImportError:
        print("ERROR: pywin32 was not found. Run: pip install pywin32")
        sys.exit(1)


def doctor() -> bool:
    """Print environment status without running a conversion."""
    ok = True
    print("SlideForge environment check")
    print("-" * 28)

    for tool in ("ffmpeg", "ffprobe"):
        executable = find_executable(tool)
        if executable:
            print(f"OK: {tool} found at {executable}")
            print(f"    {get_tool_version(executable)}")
        else:
            print(f"ERROR: {tool} was not found on PATH.")
            ok = False

    try:
        import win32com.client  # noqa: F401
        print("OK: pywin32 PowerPoint COM support is available")
    except ImportError:
        print("ERROR: pywin32 was not found. Run: pip install pywin32")
        ok = False

    if not ok:
        print()
        print_ffmpeg_install_help()

    return ok


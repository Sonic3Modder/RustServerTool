import subprocess
from pathlib import Path
import platform
import os
from PyQt6.QtCore import QThread, pyqtSignal


class InstallWorker(QThread):
    progress = pyqtSignal(dict)   # emits each line as {"type": "info"/"error", "message": "..."}
    finished = pyqtSignal(dict)   # emits {"success": bool, "lines": [...]}

    def __init__(self, path: str | Path):
        super().__init__()
        if not isinstance(path, (str, Path)):
            raise TypeError(f"Expected str or Path, got {type(path).__name__}")
        self.path = path
        self._lines = []

    def run(self):
        process = subprocess.Popen(
            [
                "steamcmd",
                "+login", "anonymous",
                "+force_install_dir", str(self.path),
                "+app_update", "258550",
                "validate",
                "+quit"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for line in process.stdout:
            line = line.strip()
            if line:
                entry = {"type": "info", "message": line}
                self._lines.append(entry)
                self.progress.emit(entry)

        for line in process.stderr:
            line = line.strip()
            if line:
                entry = {"type": "error", "message": line}
                self._lines.append(entry)
                self.progress.emit(entry)

        process.wait()

        executable = "RustDedicated.exe" if platform.system() == "Windows" else "RustDedicated"
        success = os.path.exists(Path(self.path) / executable)

        self.finished.emit({
            "success": success,
            "lines": self._lines
        })


def install(path: str | Path) -> dict:
    """
    Synchronous install -- only use this outside of a Qt UI context.
    For GUI use, use InstallWorker instead to avoid freezing the UI.
    """
    if not isinstance(path, (str, Path)):
        raise TypeError(f"Expected str or Path, got {type(path).__name__}")

    process = subprocess.Popen(
        [
            "steamcmd",
            "+login", "anonymous",
            "+force_install_dir", str(path),
            "+app_update", "258550",
            "validate",
            "+quit"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    lines = []

    for line in process.stdout:
        line = line.strip()
        if line:
            lines.append({"type": "info", "message": line})

    for line in process.stderr:
        line = line.strip()
        if line:
            lines.append({"type": "error", "message": line})

    process.wait()

    # Check for the actual Rust server executable, not just the folder
    executable = "RustDedicated.exe" if platform.system() == "Windows" else "RustDedicated"
    rust_server_installed = os.path.exists(Path(path) / executable)

    return {
        "success": rust_server_installed,
        "lines": lines
    }
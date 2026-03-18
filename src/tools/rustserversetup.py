import subprocess
from pathlib import Path
import platform
import os
from PyQt6.QtCore import QThread, pyqtSignal
import socket


class InstallWorker(QThread):

    progress = pyqtSignal(dict)
    finished = pyqtSignal(dict)

    def check_connection(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            conn = True
        except OSError:
            conn = False
        return conn

    def __init__(self, path: str | Path):
        super().__init__()
        if not isinstance(path, (str, Path)):
            raise TypeError(f"Expected str or Path, got {type(path).__name__}")
        self.path = path
        self._lines = []

    def run(self):
        try:
            if self.check_connection() == True:

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

            elif self.check_connection() == False:
                self.finished.emit({
                    "success": False,
                    "lines": [{"type": "error", "message": "No internet connection. Please check your connection and try again."}]
                })

        except Exception as e:
            self.finished.emit({
                "success": False,
                "lines": [{"type": "error", "message": f"Installation failed: {str(e)}"}]
            })


    def install(self, path: str | Path) -> dict:

        def check_connection():
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                conn = True
            except OSError:
                conn = False
            return conn

        try:
            if check_connection() == True:

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

                executable = "RustDedicated.exe" if platform.system() == "Windows" else "RustDedicated"
                rust_server_installed = os.path.exists(Path(path) / executable)

                return {
                    "success": rust_server_installed,
                    "lines": lines
                }

            elif check_connection() == False:
                return {
                    "success": False,
                    "lines": [{"type": "error", "message": "No internet connection. Please check your connection and try again."}]
                }

        except Exception as e:
            return {
                "success": False,
                "lines": [{"type": "error", "message": f"Installation failed: {str(e)}"}]
            }
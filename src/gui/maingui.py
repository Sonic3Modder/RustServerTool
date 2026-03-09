from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import shutil
from datetime import datetime
from src.tools import steamcmdsetup
from src.tools import rustserversetup
from pathlib import Path
import subprocess
import darkdetect
import configparser
import platform
import os
import sys


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        self.setLayout(layout)

        if getattr(sys, 'frozen', False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent

        logo_path = str(base / "logo.png")

        # 32px logo
        self.logo = QLabel()
        pix = QPixmap(logo_path)
        self.logo.setPixmap(
            pix.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
        )

        self.title = QLabel("Rust Utility Server Tool")
        self.title.setStyleSheet("font-weight: bold; border: none;")

        self.min_btn   = QPushButton("─")
        self.max_btn   = QPushButton("□")
        self.close_btn = QPushButton("✕")

        for btn in [self.min_btn, self.max_btn, self.close_btn]:
            btn.setFixedSize(32, 28)
            btn.setFlat(True)

        self.close_btn.setObjectName("closeTitleBtn")
        self.close_btn.setStyleSheet("""
            QPushButton#closeTitleBtn:hover { background-color: #C0392B; color: white; }
        """)

        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.setFixedHeight(40)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.window().windowHandle()
            if handle:
                handle.startSystemMove()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            if win.isMaximized():
                win.showNormal()
            else:
                win.showMaximized()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window
        )

        # Icon
        if getattr(sys, 'frozen', False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent

        icon_path = str(base / "logo.png")
        print("Icon path:", icon_path)
        print("Icon exists:", os.path.exists(icon_path))
        self.setWindowIcon(QIcon(icon_path))

        # Load config
        if getattr(sys, 'frozen', False):
            config_path = Path(sys.executable).parent / "config.ini"
        else:
            config_path = Path(__file__).parent.parent.parent / "config.ini"

        config = configparser.ConfigParser()
        config.read(config_path)
        self.server_path = config["Path"]["server_path"]
        self.config_path = config_path

        # Font
        if getattr(sys, 'frozen', False):
            font_base = Path(sys.executable).parent
        else:
            font_base = Path(__file__).parent

        QFontDatabase.addApplicationFont(
            str(font_base / "fonts" / "Roboto-Condensed-Regular.ttf")
        )

        # Track current theme
        self.current_theme = darkdetect.theme()
        self.apply_theme(self.current_theme)

        # Central widget + main layout
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.widget.setLayout(self.main_layout)

        # Title bar
        self.titlebar = TitleBar(self)
        self.titlebar.min_btn.clicked.connect(self.showMinimized)
        self.titlebar.max_btn.clicked.connect(self._toggle_maximize)
        self.titlebar.close_btn.clicked.connect(self.close)
        self.main_layout.addWidget(self.titlebar)

        # Menu bar
        self.menubar = QMenuBar()
        file_menu = self.menubar.addMenu("File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)
        self.main_layout.addWidget(self.menubar)

        # Content area
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)
        content.setLayout(content_layout)
        self.main_layout.addWidget(content, stretch=1)

        # Player List
        self.player_label = QLabel("Players:")
        content_layout.addWidget(self.player_label)

        self.players = QListWidget()
        self.players.setStyleSheet("""
        QListWidget::item {
            padding: 4px;
            font-size: 12pt;
        }
        """)
        content_layout.addWidget(self.players)

        content_layout.addStretch()

        # Run Button
        self.run_btn = QPushButton("Run Server ▶")
        self.run_btn.setObjectName("runButton")
        self.run_btn.setStyleSheet("""
        QPushButton#runButton {
            background-color: #27ae60;
            color: white;
            font-size: 14px;
            border-radius: 1px;
            padding: 6px 10px;
            min-width: 100px;
            min-height: 20px;
        }
        QPushButton#runButton:hover { background-color: #2E995B; }
        QPushButton#runButton:pressed { background-color: #1e8449; }
        """)
        content_layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.run_btn.clicked.connect(self.check_install)

        # Clock label
        self.time_label = QLabel("")
        content_layout.addWidget(self.time_label)

        # Bottom resize grip
        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 2, 2)
        bottom_bar.setLayout(bottom_layout)
        bottom_layout.addStretch()
        self.grip = QSizeGrip(self)
        bottom_layout.addWidget(self.grip)
        self.main_layout.addWidget(bottom_bar)

        self.setGeometry(100, 100, 420, 400)
        self.setWindowTitle("Rust Utility Server Tool")

        # Timer for clock
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)
        self.update_time()

        # Timer for theme watching
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_theme)
        self.theme_timer.start(2000)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.titlebar.max_btn.setText("□")
        else:
            self.showMaximized()
            self.titlebar.max_btn.setText("❐")

    def apply_theme(self, theme: str):
        if getattr(sys, 'frozen', False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent

        qss_path = base / ("style_dark.qss" if theme == "Dark" else "style_light.qss")
        if not qss_path.exists():
            print("QSS file not found:", qss_path)
            return
        with open(qss_path, "r") as f:
            self.setStyleSheet(f.read())
        print(f"Theme applied: {theme} ({qss_path.name})")

    def check_theme(self):
        new_theme = darkdetect.theme()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_theme(new_theme)

    def update_time(self):
        now = datetime.now()
        self.formatted = now.strftime("%H:%M:%S")
        self.time_label.setText(f"Current time: {self.formatted}")

    def check_install(self):
        steamcmd_exists = shutil.which("steamcmd") is not None
        executable = "RustDedicated.exe" if platform.system() == "Windows" else "RustDedicated"
        rust_exists = os.path.exists(Path(self.server_path) / executable)

        if not steamcmd_exists:
            QApplication.beep()
            reply = QMessageBox.question(
                self,
                "SteamCMD Missing",
                "SteamCMD is not installed. Do you want to install it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                print(f"{self.formatted}: Installing SteamCMD...")
                steamcmdsetup.install()
            else:
                print(f"{self.formatted}: User canceled SteamCMD installation.")
            return

        if not rust_exists:
            QApplication.beep()
            reply = QMessageBox.question(
                self,
                "Rust Server Missing",
                f"Rust server not found at {self.server_path}. Install it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                print(f"{self.formatted}: Installing Rust server...")
                self.start_install()
            else:
                print(f"{self.formatted}: User canceled Rust server installation.")
            return

        print(f"{self.formatted}: All good, starting server...")
        try:
            subprocess.Popen([str(Path(self.server_path) / executable)])
        except Exception as e:
            print(f"{self.formatted}: Failed to start server: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start server: {e}")

    def start_install(self):
        self.run_btn.setEnabled(False)
        self.worker = rustserversetup.InstallWorker(Path(self.server_path))
        self.worker.progress.connect(self.on_install_progress)
        self.worker.finished.connect(self.on_install_finished)
        self.worker.start()

    def on_install_progress(self, entry: dict):
        print(f"{self.formatted}: {entry['message']}")

    def on_install_finished(self, result: dict):
        self.run_btn.setEnabled(True)
        if result["success"]:
            print(f"{self.formatted}: Rust server installed successfully.")
            QApplication.beep()
        else:
            QMessageBox.critical(self, "Install Failed", "Rust server installation failed.")

    def closeEvent(self, event):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if not config.has_section("Window"):
            config.add_section("Window")
        geo = self.geometry()
        config["Window"]["x"] = str(geo.x())
        config["Window"]["y"] = str(geo.y())
        config["Window"]["width"] = str(geo.width())
        config["Window"]["height"] = str(geo.height())
        with open(self.config_path, "w") as f:
            config.write(f)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
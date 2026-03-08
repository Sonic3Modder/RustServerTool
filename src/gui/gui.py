from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import shutil
from datetime import datetime
from src.tools import steamcmdsetup

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # GUI Setup
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle("Rust Server Tool")

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        # Run Button
        self.run_btn = QPushButton("Run Server ▶")
        self.run_btn.setObjectName("runButton")
        self.run_btn.setStyleSheet("""
        QPushButton#runButton {
            background-color: #27ae60;  /* dark green */
            color: white;
            font-size: 14px;
            border-radius: 1px;
            padding: 6px 10px;         /* smaller padding */
            min-width: 100px;
            min-height: 20px;
        }

        QPushButton#runButton:hover {
            background-color: #2E995B;  /* lighter green */
        }

        QPushButton#runButton:pressed {
            background-color: #1e8449;  /* darker green */
        }
        """)
        
        self.layout.addStretch()
        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.run_btn.clicked.connect(self.check_install)

        # Label to show time
        self.time_label = QLabel("")

        # QTimer to refresh time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # every 1000ms = 1 second
        self.update_time()  # initial update

    def update_time(self):
        now = datetime.now()
        self.formatted = now.strftime("%H:%M:%S")
        self.time_label.setText(f"Current time: {self.formatted}")

    def check_install(self):
        if shutil.which("steamcmd") is not None:
            print(f"{self.formatted}: SteamCMD is already installed.")
            return
        else:
            reply = QMessageBox.question(
                self,
                "Error",
                "SteamCMD is not installed. Do you want to install it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                print(f"{self.formatted}: Installing SteamCMD...")
                steamcmdsetup.install()
            else:
                print(f"{self.formatted}: User canceled SteamCMD installation.")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
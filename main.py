import configparser
from pathlib import Path
import sys
import os

config_path = Path(__file__).parent / "config.ini"
config = configparser.ConfigParser()

def create_defaults():
    if not config_path.exists():
        config["App"] = {
            "theme": "auto",
            "language": "en"
        }
        config["Window"] = {
            "width": "420",
            "height": "400",
            "x": "100",
            "y": "100"
        }
        config["Path"] = {
            "server_path": str(Path.home() / "RustServer")
        }
        with open(config_path, "w") as f:
            config.write(f)
        print("config.ini created with defaults")
    else:
        print("config.ini already exists, skipping.")

def run():
    create_defaults()
    from src.gui.maingui import MainWindow
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
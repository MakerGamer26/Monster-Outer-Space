import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.database import init_db
import os

def main():
    # Initialize DB
    init_db()

    # Ensure assets folder
    if not os.path.exists("assets"):
        os.makedirs("assets")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

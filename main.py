import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.gui.intro import IntroWindow
from src.database import init_db
from src.game_engine import GameEngine
import os

def main():
    # Initialize DB
    init_db()

    # Ensure assets folder
    if not os.path.exists("assets"):
        os.makedirs("assets")

    app = QApplication(sys.argv)

    engine = GameEngine()
    team = engine.get_player_team()

    if not team:
        # First run or reset state
        intro = IntroWindow(engine)

        def on_intro_finished():
            # Need to keep reference to main_window or make it global/member
            # Simple way: create new window logic here
            global main_window
            main_window = MainWindow()
            main_window.show()

        intro.finished.connect(on_intro_finished)
        intro.show()
    else:
        window = MainWindow()
        window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

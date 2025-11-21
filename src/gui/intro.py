from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from src.constants import TYPES
from src.models import Monster, Ability
import os

class IntroWindow(QMainWindow):
    # Signal emitted when intro is done, passing the generated starter monster
    finished = pyqtSignal()

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Bienvenue - Monstres Infinis")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Top: Robot and Dialogue
        self.top_layout = QHBoxLayout()

        # Robot Image
        self.lbl_robot = QLabel()
        self.lbl_robot.setFixedSize(200, 200)
        self.lbl_robot.setStyleSheet("background-color: #222; border-radius: 10px;")
        self.generate_robot_image()
        self.top_layout.addWidget(self.lbl_robot)

        # Dialogue Bubble
        self.lbl_dialogue = QLabel(
            "Bonjour ! Je suis ton assistant IA.\n"
            "Bienvenue dans le monde des Monstres Infinis.\n"
            "Ici, chaque créature est unique, générée par l'intelligence artificielle.\n"
            "Pour commencer ton aventure, choisis une affinité élémentaire :"
        )
        self.lbl_dialogue.setWordWrap(True)
        self.lbl_dialogue.setStyleSheet("""
            background-color: white;
            color: black;
            padding: 15px;
            border-radius: 15px;
            border: 2px solid #333;
            font-size: 14px;
        """)
        self.top_layout.addWidget(self.lbl_dialogue, stretch=1)

        self.layout.addLayout(self.top_layout)

        # Type Selection Grid
        self.lbl_instruction = QLabel("Choisissez votre premier type :")
        self.lbl_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_instruction)

        self.grid_types = QGridLayout()
        self.layout.addLayout(self.grid_types)

        self.create_type_buttons()

        # Apply Style
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: white; }
            QLabel { color: white; }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #666; }
        """)

    def generate_robot_image(self):
        # Check if exists, else generate placeholder or AI
        path = "assets/intro_robot.png"
        if not os.path.exists(path):
            # Try AI generation or placeholder
            try:
                # Prompt AI for robot
                # Since this is blocking UI, usually we'd do it async, but for simplicity:
                self.engine.ai._create_placeholder_image(path, "Robot Assistant")
                # If AI connected, real gen:
                # path = self.engine.ai.generate_image("Cute sci-fi robot assistant, pixel art style", "intro_robot")
            except:
                pass

        if os.path.exists(path):
            self.lbl_robot.setPixmap(QPixmap(path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def create_type_buttons(self):
        row = 0
        col = 0
        max_cols = 5

        for t in TYPES:
            btn = QPushButton(t)
            btn.clicked.connect(lambda _, type_name=t: self.select_starter(type_name))
            self.grid_types.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def select_starter(self, type_name):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous commencer avec le type {type_name} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.lbl_dialogue.setText("Génération de votre compagnon en cours... Veuillez patienter.")
            QApplication.processEvents() # Force update UI

            # Generate Starter
            try:
                stats = self.engine.ai.generate_monster_stats(level=1, context=f"starter pokemon type {type_name}")
                # Force type to match choice if AI deviated
                stats['type_1'] = type_name

                monster = Monster(stats)
                path = self.engine.ai.generate_image(stats.get('description', 'starter'), f"starter_{monster.uuid}")
                monster.image_path = path

                # Abilities
                abilities_data = self.engine.ai.generate_abilities(type_name, count=4)
                monster.abilities = [Ability(a) for a in abilities_data]

                self.engine.save_monster(monster)

                QMessageBox.information(self, "Compagnon trouvé !", f"Voici {monster.name} ! Prenez-en soin.")
                self.finished.emit()
                self.close()

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur de génération : {str(e)}")

from PyQt6.QtWidgets import QApplication

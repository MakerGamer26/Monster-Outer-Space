from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from src.gui.home import HomeWidget
from src.gui.shop import ShopWidget
from src.gui.combat import CombatWidget
from src.game_engine import GameEngine
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monstres Infinis")
        self.resize(1024, 768)

        # Initialize Engine
        self.engine = GameEngine()

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Navigation Bar
        self.nav_bar = QHBoxLayout()
        self.btn_home = QPushButton("🏠 Le Foyer")
        self.btn_shop = QPushButton("🛒 Boutique")
        self.btn_combat = QPushButton("⚔️ Combat")

        self.nav_bar.addWidget(self.btn_home)
        self.nav_bar.addWidget(self.btn_shop)
        self.nav_bar.addWidget(self.btn_combat)

        self.layout.addLayout(self.nav_bar)

        # Content Area (Stacked)
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        # Pages
        self.home_page = HomeWidget(self.engine)
        self.shop_page = ShopWidget(self.engine)
        self.combat_page = CombatWidget(self.engine)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.shop_page)
        self.stack.addWidget(self.combat_page)

        # Signals
        self.btn_home.clicked.connect(lambda: self.switch_tab(0))
        self.btn_shop.clicked.connect(lambda: self.switch_tab(1))
        self.btn_combat.clicked.connect(lambda: self.switch_tab(2))

        # Style
        self.apply_styles()

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        # Refresh pages when visited
        if index == 0:
            self.home_page.refresh()
        elif index == 1:
            self.shop_page.refresh()
        elif index == 2:
            self.combat_page.refresh()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)

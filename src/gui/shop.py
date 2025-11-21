from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QGroupBox
)
from src.game_engine import RecruitmentSystem

class ShopWidget(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.recruitment_system = RecruitmentSystem(engine)

        self.layout = QVBoxLayout(self)

        # Header
        self.lbl_title = QLabel("🛒 Boutique")
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.lbl_title)

        self.lbl_money = QLabel()
        self.layout.addWidget(self.lbl_money)

        # Recruitment Section
        self.group_recruit = QGroupBox("Capture Jeune")
        self.layout_recruit = QVBoxLayout()

        self.lbl_recruit_desc = QLabel(f"Recrutez un monstre de niveau 1 pour {self.recruitment_system.cost} crédits.")
        self.layout_recruit.addWidget(self.lbl_recruit_desc)

        self.btn_recruit = QPushButton("Recruter (Aléatoire)")
        self.btn_recruit.clicked.connect(self.recruit_monster)
        self.layout_recruit.addWidget(self.btn_recruit)

        self.group_recruit.setLayout(self.layout_recruit)
        self.layout.addWidget(self.group_recruit)

        # Item Shop Section
        self.group_items = QGroupBox("Objets")
        self.layout_items = QVBoxLayout()

        self.create_buy_btn("Ball de Capture (100$)", "ball", 100)
        self.create_buy_btn("Potion de Soin (50$)", "potion", 50)
        self.create_buy_btn("Rappel (200$)", "revive", 200)
        self.create_buy_btn("Boost Attaque (150$)", "boost_atk", 150)
        self.create_buy_btn("Boost Vitesse (150$)", "boost_spd", 150)
        self.create_buy_btn("Copieur de Capacité (1000$)", "ability_copier", 1000)

        self.group_items.setLayout(self.layout_items)
        self.layout.addWidget(self.group_items)

        self.layout.addStretch()

        self.refresh()

    def create_buy_btn(self, label, item_id, cost):
        btn = QPushButton(label)
        btn.clicked.connect(lambda: self.buy_item(item_id, cost))
        self.layout_items.addWidget(btn)

    def buy_item(self, item_id, cost):
        if self.engine.buy_item(item_id, cost):
             QMessageBox.information(self, "Achat", f"Vous avez acheté : {item_id}")
             self.refresh()
        else:
             QMessageBox.warning(self, "Erreur", "Pas assez d'argent !")

    def refresh(self):
        money = self.engine.get_player_money()
        inv = self.engine.get_inventory()
        inv_str = ", ".join([f"{k}: {v}" for k, v in inv.items()])
        self.lbl_money.setText(f"💰 Argent: {money} | Sac: {inv_str}")
        self.btn_recruit.setEnabled(money >= self.recruitment_system.cost)

    def recruit_monster(self):
        monster, msg = self.recruitment_system.draft_monster()
        if monster:
            QMessageBox.information(self, "Succès", f"Vous avez recruté {monster.name} !")
            self.refresh()
        else:
            QMessageBox.warning(self, "Erreur", msg)

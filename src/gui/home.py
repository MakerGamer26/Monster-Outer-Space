from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QGridLayout, QPushButton, QFrame, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from src.gui.exchange import ExchangeDialog, ImportDialog
import os

class HomeWidget(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.layout = QVBoxLayout(self)

        # Header
        self.header_layout = QHBoxLayout()
        self.lbl_title = QLabel("🏡 Le Foyer")
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.btn_import = QPushButton("📥 Importer")
        self.btn_import.clicked.connect(self.open_import)

        self.lbl_money = QLabel("💰 Argent: 0")

        self.header_layout.addWidget(self.lbl_title)
        self.header_layout.addWidget(self.btn_import)
        self.header_layout.addStretch()

        self.btn_reset = QPushButton("⚠️ Réinitialiser")
        self.btn_reset.setStyleSheet("background-color: #800; color: white;")
        self.btn_reset.clicked.connect(self.do_reset)
        self.header_layout.addWidget(self.btn_reset)

        self.header_layout.addWidget(self.lbl_money)
        self.layout.addLayout(self.header_layout)

        # Monster Grid (Scrollable)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        self.refresh()

    def refresh(self):
        # Update Money
        money = self.engine.get_player_money()
        self.lbl_money.setText(f"💰 Argent: {money}")

        # Clear Grid
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        # Load Monsters
        monsters = self.engine.get_all_monsters()
        row = 0
        col = 0
        max_cols = 4

        if not monsters:
            lbl_empty = QLabel("Aucun monstre. Allez dans la boutique pour en recruter !")
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(lbl_empty, 0, 0)
            return

        for monster in monsters:
            card = self.create_monster_card(monster)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_monster_card(self, monster):
        frame = QFrame()
        frame.setStyleSheet("background-color: #3a3a3a; border-radius: 10px; padding: 5px;")
        layout = QVBoxLayout(frame)

        # Image
        lbl_img = QLabel()
        lbl_img.setFixedSize(100, 100)
        lbl_img.setStyleSheet("background-color: #222; border-radius: 5px;")
        if monster.image_path and os.path.exists(monster.image_path):
            pixmap = QPixmap(monster.image_path)
            lbl_img.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(lbl_img, alignment=Qt.AlignmentFlag.AlignCenter)

        # Info
        lbl_name = QLabel(f"{monster.name} (Lv {monster.level})")
        lbl_name.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)

        lbl_stats = QLabel(f"HP: {monster.hp_max} | Atk: {monster.attack}")
        layout.addWidget(lbl_stats, alignment=Qt.AlignmentFlag.AlignCenter)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_evolve = QPushButton("🧬")
        btn_evolve.setToolTip("Évoluer")
        btn_evolve.clicked.connect(lambda: self.evolve_monster(monster))

        btn_export = QPushButton("📤")
        btn_export.setToolTip("Échanger")
        btn_export.clicked.connect(lambda: self.export_monster(monster))

        btn_copy = QPushButton("💿")
        btn_copy.setToolTip("Copier Capacité (Nécessite Item)")
        btn_copy.clicked.connect(lambda: self.open_copier(monster))

        btn_layout.addWidget(btn_evolve)
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_copy)
        layout.addLayout(btn_layout)

        return frame

    def open_import(self):
        dlg = ImportDialog(self.engine, self)
        if dlg.exec():
            self.refresh()

    def export_monster(self, monster):
        dlg = ExchangeDialog(monster, self)
        dlg.exec()

    def open_copier(self, target_monster):
        # Check inventory
        inv = self.engine.get_inventory()
        if inv.get('ability_copier', 0) <= 0:
            QMessageBox.warning(self, "Objet Manquant", "Il vous faut un 'Copieur de Capacité'.")
            return

        # Select Source Monster
        monsters = self.engine.get_all_monsters()
        sources = [m for m in monsters if m.id != target_monster.id and (m.type_1 == target_monster.type_1 or m.type_1 == target_monster.type_2)]

        if not sources:
            QMessageBox.warning(self, "Aucune Source", "Aucun autre monstre compatible (même type) trouvé.")
            return

        # Simple Input Dialog for Source ID (In a real app, a proper Selector Dialog)
        # For this prototype, let's pick the first compatible one or list names
        from PyQt6.QtWidgets import QInputDialog
        items = [f"{m.name} ({m.type_1})" for m in sources]
        item, ok = QInputDialog.getItem(self, "Choisir Source", "Monstre Source:", items, 0, False)

        if ok and item:
            # Find monster obj
            source = next(m for m in sources if f"{m.name} ({m.type_1})" == item)

            # Select Ability
            if not source.abilities:
                QMessageBox.warning(self, "Erreur", "Le monstre source n'a pas de capacités.")
                return

            ab_items = [a.name for a in source.abilities]
            ab_name, ok_ab = QInputDialog.getItem(self, "Choisir Capacité", "Capacité à copier:", ab_items, 0, False)

            if ok_ab and ab_name:
                # consume item
                self.engine.use_item('ability_copier')
                success, msg = self.engine.copy_ability(source, target_monster, ab_name)
                if success:
                    QMessageBox.information(self, "Succès", msg)
                else:
                    # Refund? In this simple logic, we already consumed.
                    # Ideally verify before consume.
                    # Re-add item
                    self.engine.buy_item('ability_copier', 0) # Hack to re-add
                    QMessageBox.warning(self, "Echec", msg)

    def do_reset(self):
        # Double Confirmation
        reply = QMessageBox.warning(
            self, "Réinitialiser",
            "Attention ! Vous allez perdre TOUTES vos données. Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            reply2 = QMessageBox.critical(
                self, "Confirmation Finale",
                "Êtes-vous vraiment sûr ? Cette action est irréversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply2 == QMessageBox.StandardButton.Yes:
                self.engine.reset_game()
                QMessageBox.information(self, "Reset", "Jeu réinitialisé. Relancez l'application pour recommencer.")
                # Close app or Restart. Simpler to close.
                # Or we can try to show IntroWindow again but that requires access to main stack or app.
                import sys
                sys.exit(0)

    def evolve_monster(self, monster):
        # Check conditions
        if monster.level < 45 and monster.evolution_stage == 0:
            QMessageBox.warning(self, "Impossible", "Niveau 45 requis pour la première évolution.")
            return
        if monster.level < 90 and monster.evolution_stage == 1:
             QMessageBox.warning(self, "Impossible", "Niveau 90 requis pour la deuxième évolution.")
             return
        if monster.evolution_stage >= 2 and not monster.is_mythical:
             QMessageBox.warning(self, "Impossible", "Ce monstre a atteint son stade final.")
             return

        confirm = QMessageBox.question(self, "Évolution", f"Voulez-vous faire évoluer {monster.name} ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Patience", "L'IA génère l'évolution... Cela peut prendre quelques secondes.")
            # Call AI Logic
            new_stats = self.engine.ai.evolve_monster_stats(monster.to_dict(), monster.evolution_stage)

            # Update Monster
            monster.name = new_stats.get('name', monster.name)
            monster.hp_max = int(new_stats.get('hp_max'))
            monster.attack = int(new_stats.get('attack'))
            # ... update others ...
            monster.evolution_stage += 1

            # New Image
            path = self.engine.ai.generate_image(new_stats.get('description', monster.name), f"evo_{monster.uuid}")
            monster.image_path = path

            self.engine.save_monster(monster)
            self.refresh()
            QMessageBox.information(self, "Félicitations !", f"Votre monstre a évolué en {monster.name} !")

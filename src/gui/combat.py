from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from src.game_engine import CombatSystem
import os

class CombatWidget(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.combat_system = None

        self.layout = QVBoxLayout(self)

        # Top: Enemy
        self.enemy_layout = QVBoxLayout()
        self.lbl_enemy_img = QLabel()
        self.lbl_enemy_img.setFixedSize(200, 200)
        self.lbl_enemy_img.setStyleSheet("background-color: #444;")
        self.lbl_enemy_info = QLabel("Enemy")
        self.bar_enemy_hp = QProgressBar()
        self.bar_enemy_hp.setStyleSheet("QProgressBar::chunk { background-color: red; }")

        self.enemy_layout.addWidget(self.lbl_enemy_img, alignment=Qt.AlignmentFlag.AlignCenter)
        self.enemy_layout.addWidget(self.lbl_enemy_info, alignment=Qt.AlignmentFlag.AlignCenter)
        self.enemy_layout.addWidget(self.bar_enemy_hp)
        self.layout.addLayout(self.enemy_layout)

        # Log
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(100)
        self.layout.addWidget(self.log_box)

        # Bottom: Player
        self.player_layout = QHBoxLayout()

        # Player Visual
        self.player_vis_layout = QVBoxLayout()
        self.lbl_player_img = QLabel()
        self.lbl_player_img.setFixedSize(150, 150)
        self.lbl_player_img.setStyleSheet("background-color: #444;")
        self.lbl_player_info = QLabel("Player")
        self.bar_player_hp = QProgressBar()
        self.bar_player_hp.setStyleSheet("QProgressBar::chunk { background-color: green; }")

        self.player_vis_layout.addWidget(self.lbl_player_img)
        self.player_vis_layout.addWidget(self.lbl_player_info)
        self.player_vis_layout.addWidget(self.bar_player_hp)
        self.player_layout.addLayout(self.player_vis_layout)

        # Controls
        self.controls_layout = QVBoxLayout()

        # Abilities Grid
        self.abilities_layout = QGridLayout()
        self.controls_layout.addLayout(self.abilities_layout)

        self.btn_capture = QPushButton("🕸️ Capturer (nécessite 'ball')")
        self.btn_boost_atk = QPushButton("💪 Boost Atk")
        self.btn_boost_spd = QPushButton("⚡ Boost Vit")
        self.btn_flee = QPushButton("🏃 Fuir")
        self.btn_start = QPushButton("🔍 Chercher un Combat")

        self.controls_layout.addWidget(self.btn_capture)
        self.controls_layout.addWidget(self.btn_boost_atk)
        self.controls_layout.addWidget(self.btn_boost_spd)
        self.controls_layout.addWidget(self.btn_flee)
        self.controls_layout.addWidget(self.btn_start)

        self.player_layout.addLayout(self.controls_layout)
        self.layout.addLayout(self.player_layout)

        self.btn_start.clicked.connect(self.start_combat)
        self.btn_capture.clicked.connect(self.do_capture)
        self.btn_boost_atk.clicked.connect(lambda: self.use_boost("boost_atk", "attack"))
        self.btn_boost_spd.clicked.connect(lambda: self.use_boost("boost_spd", "speed"))
        self.btn_flee.clicked.connect(self.flee)

        # Initial State
        self.set_combat_active(False)

    def set_combat_active(self, active):
        # self.btn_attack.setEnabled(active) # Removed generic attack
        for i in range(self.abilities_layout.count()):
            widget = self.abilities_layout.itemAt(i).widget()
            if widget:
                widget.setEnabled(active)

        self.btn_capture.setEnabled(False) # Enabled when won
        self.btn_boost_atk.setEnabled(active)
        self.btn_boost_spd.setEnabled(active)
        self.btn_flee.setEnabled(active)
        self.btn_start.setEnabled(not active)

    def refresh(self):
        pass

    def start_combat(self):
        self.team = [m for m in self.engine.get_player_team() if m.current_hp > 0]
        if not self.team:
            QMessageBox.warning(self, "Attention", "Tous vos monstres sont KO ou vous n'en avez pas.")
            return

        self.combat_system = CombatSystem(self.team, self.engine)
        self.active_monster_idx = 0
        self.active_monster = self.team[self.active_monster_idx]

        self.log("Recherche d'un adversaire...")
        self.enemy = self.combat_system.generate_enemy()

        self.log(f"Un {self.enemy.name} sauvage apparaît (Niveau {self.enemy.level}) !")
        self.update_ui()
        self.setup_abilities()
        self.set_combat_active(True)
        self.btn_capture.setEnabled(False)

    def setup_abilities(self):
        # Clear old buttons
        for i in reversed(range(self.abilities_layout.count())):
            self.abilities_layout.itemAt(i).widget().setParent(None)

        abilities = self.active_monster.abilities
        if not abilities:
            # Fallback button
            btn = QPushButton("Lutte (Défaut)")
            btn.clicked.connect(lambda: self.do_attack(None))
            self.abilities_layout.addWidget(btn, 0, 0)
        else:
            row = 0
            col = 0
            for ab in abilities:
                btn = QPushButton(f"{ab.name}\n(Pow: {ab.damage})")
                btn.clicked.connect(lambda a=ab: self.do_attack(a))
                self.abilities_layout.addWidget(btn, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1

    def update_ui(self):
        # Update Enemy UI
        self.lbl_enemy_info.setText(f"{self.enemy.name} (Lv {self.enemy.level})")
        self.bar_enemy_hp.setMaximum(self.enemy.hp_max)
        self.bar_enemy_hp.setValue(self.enemy.current_hp)
        if self.enemy.image_path and os.path.exists(self.enemy.image_path):
             self.lbl_enemy_img.setPixmap(QPixmap(self.enemy.image_path).scaled(200, 200))

        # Update Player UI
        self.lbl_player_info.setText(f"{self.active_monster.name} (Lv {self.active_monster.level})")
        self.bar_player_hp.setMaximum(self.active_monster.hp_max)
        self.bar_player_hp.setValue(self.active_monster.current_hp)
        if self.active_monster.image_path and os.path.exists(self.active_monster.image_path):
             self.lbl_player_img.setPixmap(QPixmap(self.active_monster.image_path).scaled(150, 150))

    def do_attack(self, ability):
        # Player Attack
        move_name = ability.name if ability else "Lutte"
        dmg = self.combat_system.attack(self.active_monster, self.enemy, ability)
        self.log(f"{self.active_monster.name} utilise {move_name} et inflige {dmg} dégâts !")

        if self.enemy.current_hp <= 0:
            self.win_combat()
            return

        # Enemy Attack (Turn resolution)
        # Pick random enemy ability if available
        enemy_ab = None
        if self.enemy.abilities:
            import random
            enemy_ab = random.choice(self.enemy.abilities)

        dmg_enemy = self.combat_system.attack(self.enemy, self.active_monster, enemy_ab)
        move_name_enemy = enemy_ab.name if enemy_ab else "Attaque"
        self.log(f"L'ennemi {self.enemy.name} utilise {move_name_enemy} et inflige {dmg_enemy} dégâts !")

        if self.active_monster.current_hp <= 0:
            self.log(f"{self.active_monster.name} est KO !")
            self.switch_monster()

        self.update_ui()

    def switch_monster(self):
        # Find next alive monster
        next_mon = None
        for m in self.team:
            if m.current_hp > 0:
                next_mon = m
                break

        if next_mon:
            self.active_monster = next_mon
            self.log(f"En avant, {self.active_monster.name} !")
            self.update_ui()
            self.setup_abilities()
        else:
            self.set_combat_active(False)
            QMessageBox.critical(self, "Défaite", "Toute votre équipe est KO.")

    def win_combat(self):
        self.log(f"Vous avez vaincu {self.enemy.name} !")
        self.set_combat_active(False)
        self.btn_capture.setEnabled(True) # Unlock capture
        self.btn_start.setEnabled(True)

        # XP Gain
        xp = self.enemy.level * 10
        leveled = self.active_monster.gain_xp(xp)
        self.log(f"Gain de {xp} XP.")
        if leveled:
            self.log(f"{self.active_monster.name} monte au niveau {self.active_monster.level} !")

        self.engine.save_monster(self.active_monster)

    def do_capture(self):
        # Check inventory
        if not self.engine.use_item("ball"):
             QMessageBox.warning(self, "Objet Manquant", "Vous avez besoin d'une 'ball' (à acheter en boutique).")
             return

        # Success chance (Simplified: 100% if won as per user request "capturer une fois vaincu seulement")
        # User said: "buy items allowing to capture ONLY after defeated".
        import random
        if random.random() > 0.3: # 70% chance
            self.log("Capture réussie !")
            # Reset stats before saving (remove boss buff if any, heal)
            self.enemy.current_hp = self.enemy.hp_max
            self.engine.save_monster(self.enemy)
            QMessageBox.information(self, "Capturé !", f"{self.enemy.name} a rejoint votre équipe.")
            self.btn_capture.setEnabled(False)
        else:
            self.log("La capture a échoué... La ball s'est brisée.")
            self.btn_capture.setEnabled(False)

    def flee(self):
        self.log("Vous avez fui.")
        self.set_combat_active(False)

    def use_boost(self, item_name, stat_name):
        if self.engine.use_item(item_name):
            # Apply transient boost
            current = getattr(self.active_monster, f"battle_{stat_name}", getattr(self.active_monster, stat_name))
            setattr(self.active_monster, f"battle_{stat_name}", int(current * 1.5))
            self.log(f"Boost {stat_name} utilisé ! (+50%)")
        else:
            QMessageBox.warning(self, "Objet manquant", f"Vous n'avez pas de {item_name}.")

    def log(self, text):
        self.log_box.append(text)

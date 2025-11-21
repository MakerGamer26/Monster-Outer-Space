import unittest
from src.game_engine import GameEngine, CombatSystem
from src.models import Monster, Ability
from src.constants import get_type_multiplier
from src.database import init_db, DB_PATH
import os

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        self.engine = GameEngine()
        self.engine.ai.generate_monster_stats = lambda level, context: {
            "name": "Test", "hp_max": 100, "attack": 10, "defense": 10, "speed": 10,
            "type_1": "Eau", "type_2": None, "mp_max": 10, "is_mythical": False
        }
        self.engine.ai.generate_image = lambda d, f: "test.png"
        self.engine.ai.generate_abilities = lambda t, c: []

    def test_type_effectiveness(self):
        # Water vs Fire (2.0)
        m1 = Monster({"name": "WaterMon", "type_1": "Eau", "attack": 10, "hp_max": 100, "defense": 10})
        m2 = Monster({"name": "FireMon", "type_1": "Feu", "attack": 10, "hp_max": 100, "defense": 10})

        combat = CombatSystem([], self.engine)

        # Attack m1 -> m2 (Water -> Fire)
        ab = Ability({"name": "Splash", "type": "Eau", "damage": 100})

        # Expected: (10 * 100 / 10) * 2.0 = 200 damage (approx)
        dmg = combat.attack(m1, m2, ab)
        self.assertTrue(dmg > 150, f"Damage {dmg} should be high due to weakness")

    def test_reset(self):
        # Add data
        self.engine.save_monster(Monster({"name": "ToBeDeleted", "type_1": "Normal"}))
        cursor = self.engine.db_conn.cursor()
        cursor.execute("SELECT count(*) as c FROM monsters")
        self.assertEqual(cursor.fetchone()['c'], 1)

        # Reset
        self.engine.reset_game()

        cursor.execute("SELECT count(*) as c FROM monsters")
        self.assertEqual(cursor.fetchone()['c'], 0)

if __name__ == '__main__':
    unittest.main()

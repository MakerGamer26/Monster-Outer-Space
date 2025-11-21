import unittest
from src.game_engine import GameEngine, CombatSystem, ExchangeSystem
from src.models import Monster
import os
import sqlite3
from src.config import DB_PATH

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        # Use a test DB
        from src.database import init_db, DB_PATH
        import os
        # Ensure DB is fresh for tests
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

        self.engine = GameEngine()
        # Mock AI for speed
        self.engine.ai.generate_monster_stats = lambda level, context: {
            "name": "TestMon", "hp_max": 100, "attack": 20, "defense": 10, "speed": 10,
            "is_mythical": False, "type_1": "Normal", "type_2": None, "mp_max": 10
        }
        self.engine.ai.generate_image = lambda d, f: "test.png"

    def test_recruitment(self):
        initial_money = self.engine.get_player_money()
        self.engine.db_conn.execute("UPDATE player SET money=1000") # Ensure funds

        # We need to instantiate RecruitmentSystem properly if we test it,
        # but let's test the engine methods used by it.
        from src.game_engine import RecruitmentSystem
        rs = RecruitmentSystem(self.engine)

        monster, msg = rs.draft_monster()
        self.assertIsNotNone(monster)
        self.assertEqual(monster.level, 1)
        self.assertTrue(self.engine.get_player_money() < 1000)

    def test_combat_generation(self):
        combat = CombatSystem([], self.engine)
        enemy = combat.generate_enemy()
        self.assertIsNotNone(enemy)
        self.assertTrue(enemy.hp_max > 0)

    def test_exchange_security(self):
        m = Monster({"name": "TradeMon", "hp_max": 50})
        code = ExchangeSystem.generate_code(m)

        restored = ExchangeSystem.load_code(code)
        self.assertEqual(restored.name, "TradeMon")

        # Tamper check
        import base64, json
        decoded = json.loads(base64.b64decode(code).decode())
        decoded['data']['hp_max'] = 9999 # Cheat
        tampered_payload = json.dumps(decoded).encode()
        tampered_code = base64.b64encode(tampered_payload).decode()

        self.assertIsNone(ExchangeSystem.load_code(tampered_code))

if __name__ == '__main__':
    unittest.main()

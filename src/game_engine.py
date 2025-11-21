import random
import json
import hashlib
import hmac
import base64
from src.config import SECRET_KEY, BOSS_PROBABILITY, MAX_TEAM_SIZE
from src.models import Monster, Ability
from src.database import get_db_connection
from src.ai_manager import AIManager

class GameEngine:
    def __init__(self):
        self.ai = AIManager()
        self.db_conn = get_db_connection()

    def get_player_team(self):
        """Returns list of Monster objects."""
        # Simplified: In this prototype, team is just the first 3 monsters in DB.
        # In a full game, we'd have a 'is_in_team' flag.
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM monsters LIMIT ?", (MAX_TEAM_SIZE,))
        rows = cursor.fetchall()
        monsters = []
        for row in rows:
            m = Monster(dict(row))
            m.abilities = self.get_monster_abilities(m.id)
            monsters.append(m)
        return monsters

    def get_all_monsters(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM monsters")
        rows = cursor.fetchall()
        monsters = []
        for row in rows:
            m = Monster(dict(row))
            m.abilities = self.get_monster_abilities(m.id)
            monsters.append(m)
        return monsters

    def get_monster_abilities(self, monster_id):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT a.* FROM abilities a
            JOIN monster_abilities ma ON a.id = ma.ability_id
            WHERE ma.monster_id = ?
        ''', (monster_id,))
        rows = cursor.fetchall()
        return [Ability(dict(row)) for row in rows]

    def get_player_money(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT money FROM player WHERE id = 1")
        return cursor.fetchone()['money']

    def update_player_money(self, amount):
        cursor = self.db_conn.cursor()
        cursor.execute("UPDATE player SET money = money + ? WHERE id = 1", (amount,))
        self.db_conn.commit()
        return self.get_player_money()

    def buy_item(self, item_name, cost):
        if self.get_player_money() >= cost:
            self.update_player_money(-cost)
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO inventory (item_name, quantity, category)
                VALUES (?, 1, 'item')
                ON CONFLICT(item_name) DO UPDATE SET quantity = quantity + 1
            """, (item_name,))
            self.db_conn.commit()
            return True
        return False

    def use_item(self, item_name):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT quantity FROM inventory WHERE item_name = ?", (item_name,))
        row = cursor.fetchone()
        if row and row['quantity'] > 0:
            cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE item_name = ?", (item_name,))
            self.db_conn.commit()
            return True
        return False

    def get_inventory(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE quantity > 0")
        return {row['item_name']: row['quantity'] for row in cursor.fetchall()}

    def heal_monster(self, monster_id, full_restore=False):
        # Logic to restore HP in DB
        cursor = self.db_conn.cursor()
        # For now, just full restore implicitly when using item
        # Real implementation would read max_hp and update current_hp (if we stored current_hp in DB)
        pass

    def save_monster(self, monster):
        cursor = self.db_conn.cursor()

        # Check if exists
        cursor.execute("SELECT id FROM monsters WHERE uuid = ?", (monster.uuid,))
        existing = cursor.fetchone()

        monster_id = None

        if existing:
            monster_id = existing['id']
            cursor.execute('''
                UPDATE monsters SET level=?, xp=?, hp_max=?, mp_max=?, attack=?, defense=?, speed=?, evolution_stage=?, name=?, image_path=?
                WHERE uuid=?
            ''', (monster.level, monster.xp, monster.hp_max, monster.mp_max, monster.attack, monster.defense, monster.speed, monster.evolution_stage, monster.name, monster.image_path, monster.uuid))
        else:
            cursor.execute('''
                INSERT INTO monsters (uuid, name, is_mythical, type_1, type_2, level, xp, hp_max, mp_max, attack, defense, speed, evolution_stage, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (monster.uuid, monster.name, monster.is_mythical, monster.type_1, monster.type_2, monster.level, monster.xp, monster.hp_max, monster.mp_max, monster.attack, monster.defense, monster.speed, monster.evolution_stage, monster.image_path))
            monster_id = cursor.lastrowid

            # Save abilities for new monster
            if monster.abilities:
                for ability in monster.abilities:
                    # Check if ability exists in pool, if not add
                    cursor.execute("SELECT id FROM abilities WHERE name = ?", (ability.name,))
                    ab_row = cursor.fetchone()
                    if ab_row:
                        ab_id = ab_row['id']
                    else:
                        cursor.execute('''
                            INSERT INTO abilities (name, description, type, damage, heal, cost_mp, cost_hp, cooldown_local, cooldown_global, stun_duration, drain_percent, is_legendary, image_path)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (ability.name, ability.description, ability.type, ability.damage, ability.heal, ability.cost_mp, ability.cost_hp, ability.cooldown_local, ability.cooldown_global, ability.stun_duration, ability.drain_percent, ability.is_legendary, ability.image_path))
                        ab_id = cursor.lastrowid

                    # Link
                    cursor.execute("INSERT OR IGNORE INTO monster_abilities (monster_id, ability_id) VALUES (?, ?)", (monster_id, ab_id))

        self.db_conn.commit()

class CombatSystem:
    def __init__(self, player_team, engine):
        self.player_team = player_team # List of Monster objects
        self.engine = engine
        self.enemy = None
        self.turn_log = []
        self.is_boss_fight = False

    def generate_enemy(self):
        """
        Logic:
        1. Determine level (2 to 80).
        2. Determine if Boss (1% chance).
        3. 1/(Existing Monsters + 1) chance of new monster vs existing.
        """
        level = random.randint(2, 80)
        is_boss = random.random() < BOSS_PROBABILITY

        cursor = self.engine.db_conn.cursor()
        cursor.execute("SELECT count(*) as count FROM monsters")
        count = cursor.fetchone()['count']

        # Chance for new monster
        new_monster_chance = 1.0 / (count + 1)

        if random.random() < new_monster_chance or count == 0:
            # Generate New
            stats = self.engine.ai.generate_monster_stats(level=level, context="boss" if is_boss else "wild")
            if is_boss:
                stats['is_mythical'] = True
                # Boost stats x10 (simulated here roughly)
                for key in ['hp_max', 'attack', 'defense', 'speed']:
                    stats[key] = int(stats.get(key, 10) * 10)

            # Create visuals immediately? Or wait? Let's do it now.
            monster = Monster(stats)
            img_path = self.engine.ai.generate_image(stats.get('description', 'monster'), f"wild_{monster.uuid}")
            monster.image_path = img_path

            # Generate Abilities
            abilities_data = self.engine.ai.generate_abilities(monster.type_1, count=4)
            monster.abilities = [Ability(a) for a in abilities_data]

            self.enemy = monster
            self.is_boss_fight = is_boss
        else:
            # Pick existing (clone it for combat)
            cursor.execute("SELECT * FROM monsters ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            monster = Monster(dict(row))
            monster.abilities = self.engine.get_monster_abilities(monster.id)

            # Adjust level to the random encounter level
            # Rough scaling:
            level_diff = level - monster.level
            growth = 1.05 ** level_diff
            monster.level = level
            monster.hp_max = int(monster.hp_max * growth)
            monster.attack = int(monster.attack * growth)
            # ... apply variation +/- 10%
            self.enemy = monster
            self._apply_variation(self.enemy)

        self.enemy.current_hp = self.enemy.hp_max
        return self.enemy

    def _apply_variation(self, monster):
        for stat in ['hp_max', 'attack', 'defense', 'speed']:
            val = getattr(monster, stat)
            variation = random.uniform(0.9, 1.1)
            setattr(monster, stat, int(val * variation))

    def attack(self, attacker, defender, ability=None):
        """
        Calculates damage.
        """
        # Check for boosts (transient attributes not saved to DB, injected at runtime)
        atk_stat = getattr(attacker, 'battle_attack', attacker.attack)
        def_stat = getattr(defender, 'battle_defense', defender.defense)

        # Simple formula
        # Damage = (Attack * Power / Defense) * Random(0.85, 1.0)
        power = ability.damage if ability else 50 # Default struggle move
        damage = int((atk_stat * power / max(1, def_stat)) * random.uniform(0.85, 1.0))
        defender.current_hp = max(0, defender.current_hp - damage)
        return damage

class RecruitmentSystem:
    def __init__(self, engine):
        self.engine = engine
        self.cost = 500 # Base cost

    def draft_monster(self):
        money = self.engine.get_player_money()
        if money < self.cost:
            return None, "Not enough money"

        self.engine.update_player_money(-self.cost)

        # Generate Level 1 Weak Monster
        stats = self.engine.ai.generate_monster_stats(level=1, context="weak starter")
        monster = Monster(stats)
        path = self.engine.ai.generate_image(stats.get('description'), f"draft_{monster.uuid}")
        monster.image_path = path

        # Abilities
        abilities_data = self.engine.ai.generate_abilities(monster.type_1, count=4)
        monster.abilities = [Ability(a) for a in abilities_data]

        self.engine.save_monster(monster)
        return monster, "Success"

class ExchangeSystem:
    @staticmethod
    def generate_code(monster):
        """
        Serialize monster data + HMAC signature.
        """
        data = monster.to_dict()
        json_str = json.dumps(data, sort_keys=True)

        # Create signature
        sig = hmac.new(SECRET_KEY, json_str.encode(), hashlib.sha256).hexdigest()

        # Combine
        payload = json.dumps({'data': data, 'sig': sig})
        return base64.b64encode(payload.encode()).decode()

    @staticmethod
    def load_code(code_str):
        try:
            decoded = base64.b64decode(code_str).decode()
            payload = json.loads(decoded)

            data = payload['data']
            sig = payload['sig']

            # Verify signature
            json_str = json.dumps(data, sort_keys=True)
            expected_sig = hmac.new(SECRET_KEY, json_str.encode(), hashlib.sha256).hexdigest()

            if hmac.compare_digest(sig, expected_sig):
                return Monster(data)
            else:
                raise ValueError("Invalid signature")
        except Exception as e:
            print(f"Exchange Error: {e}")
            return None

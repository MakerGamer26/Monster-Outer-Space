import sqlite3
import json
from src.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Monsters Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monsters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE, -- For exchange identification
            name TEXT,
            is_mythical BOOLEAN,
            type_1 TEXT,
            type_2 TEXT,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            hp_max INTEGER,
            mp_max INTEGER, -- "PM" in French
            attack INTEGER,
            defense INTEGER, -- Resistance
            speed INTEGER,
            evolution_stage INTEGER DEFAULT 0,
            image_path TEXT,
            original_owner TEXT
        )
    ''')

    # Abilities Table (Pool of known abilities)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            description TEXT,
            type TEXT,
            damage INTEGER,
            heal INTEGER, -- Regeneration
            cost_mp INTEGER,
            cost_hp INTEGER,
            cooldown_local INTEGER,
            cooldown_global INTEGER,
            stun_duration INTEGER,
            drain_percent INTEGER,
            is_legendary BOOLEAN,
            image_path TEXT
        )
    ''')

    # Monster-Ability Mapping (A monster knows specific moves)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monster_abilities (
            monster_id INTEGER,
            ability_id INTEGER,
            FOREIGN KEY(monster_id) REFERENCES monsters(id),
            FOREIGN KEY(ability_id) REFERENCES abilities(id)
        )
    ''')

    # Player Inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_name TEXT PRIMARY KEY,
            quantity INTEGER DEFAULT 0,
            category TEXT -- 'ball', 'potion', 'boost', 'revive'
        )
    ''')

    # Player Stats / Game State
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            money INTEGER DEFAULT 1000,
            name TEXT DEFAULT 'Joueur'
        )
    ''')

    # Initialize player if not exists
    cursor.execute('INSERT OR IGNORE INTO player (id, money) VALUES (1, 1000)')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

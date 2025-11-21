from src.ai_manager import AIManager
from src.models import Monster
import os

def test_generation():
    print("Testing AI Manager...")
    ai = AIManager()

    print("Generating Monster Stats...")
    stats = ai.generate_monster_stats(level=5)
    print(f"Generated: {stats.get('name')}")

    monster = Monster(stats)
    print(f"Monster Created: {monster.name} (HP: {monster.hp_max})")

    print("Generating Image (Placeholder)...")
    if not os.path.exists("assets"):
        os.makedirs("assets")

    path = ai.generate_image(stats.get('description', 'monster'), f"test_{monster.uuid}")
    print(f"Image saved to: {path}")

    print("Generating Abilities...")
    abilities = ai.generate_abilities(monster.type_1, count=2)
    print(f"Abilities: {[a['name'] for a in abilities]}")

if __name__ == "__main__":
    test_generation()

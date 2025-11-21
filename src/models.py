import math
import random
import uuid

class Monster:
    def __init__(self, data=None):
        if data:
            self.id = data.get('id')
            self.uuid = data.get('uuid', str(uuid.uuid4()))
            self.name = data.get('name')
            self.is_mythical = bool(data.get('is_mythical'))
            self.type_1 = data.get('type_1')
            self.type_2 = data.get('type_2')
            self.level = data.get('level', 1)
            self.xp = data.get('xp', 0)
            self.hp_max = data.get('hp_max')
            self.mp_max = data.get('mp_max')
            self.attack = data.get('attack')
            self.defense = data.get('defense')
            self.speed = data.get('speed')
            self.evolution_stage = data.get('evolution_stage', 0)
            self.image_path = data.get('image_path')

            # Dynamic Stats (In-battle)
            self.current_hp = self.hp_max
            self.current_mp = self.mp_max
            self.abilities = [] # To be populated

    @property
    def xp_next_level(self):
        # Exponential curve
        # Example: Level 1->2 needs 100. Level 99->100 needs massive amount.
        return int(100 * (self.level ** 1.5)) # Simple exponential

    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_next_level and self.level < 100:
            self.xp -= self.xp_next_level
            self.level_up()
            leveled_up = True
        return leveled_up

    def level_up(self):
        self.level += 1
        # Stat growth (approx 5-10% per level usually, but we can make it simple)
        growth_factor = 1.05
        self.hp_max = int(self.hp_max * growth_factor)
        self.mp_max = int(self.mp_max * growth_factor)
        self.attack = int(self.attack * growth_factor)
        self.defense = int(self.defense * growth_factor)
        self.speed = int(self.speed * growth_factor)

        # Heal on level up
        self.current_hp = self.hp_max
        self.current_mp = self.mp_max

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'is_mythical': self.is_mythical,
            'type_1': self.type_1,
            'type_2': self.type_2,
            'level': self.level,
            'xp': self.xp,
            'hp_max': self.hp_max,
            'mp_max': self.mp_max,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'evolution_stage': self.evolution_stage,
            'image_path': self.image_path
        }

class Ability:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.description = data.get('description')
        self.type = data.get('type')
        self.damage = data.get('damage', 0)
        self.heal = data.get('heal', 0)
        self.cost_mp = data.get('cost_mp', 0)
        self.cost_hp = data.get('cost_hp', 0)
        self.cooldown_local = data.get('cooldown_local', 0)
        self.cooldown_global = data.get('cooldown_global', 0)
        self.stun_duration = data.get('stun_duration', 0)
        self.drain_percent = data.get('drain_percent', 0)
        self.is_legendary = bool(data.get('is_legendary'))
        self.image_path = data.get('image_path')

        # In-battle state
        self.current_cooldown = 0

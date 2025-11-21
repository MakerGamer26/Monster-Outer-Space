import os
import sys

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# User requested Gemini 2.5. Using the closest available experimental or pro alias.
# Note: 'gemini-2.5' might not be the exact string yet, defaulting to a high capability model variable.
GEMINI_MODEL_TEXT = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
GEMINI_MODEL_IMAGE = "imagen-3.0-generate-001"

# Game Constants
DB_PATH = os.path.join("data", "game.db")
ASSETS_PATH = "assets"

# Gameplay Constants
MAX_TEAM_SIZE = 3
BOSS_PROBABILITY = 0.01
EVOLUTION_LEVEL_1 = 45
EVOLUTION_LEVEL_2 = 90
MAX_LEVEL = 100

# Security
SECRET_KEY = b'change_this_to_a_random_key_for_production' # For hash generation

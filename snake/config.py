import pygame
import os
import json

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Grid / Block Size
BLOCK_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Food Colors
FOOD_NORMAL_COLOR = (255, 0, 0)       # Red
FOOD_WEIGHTED_COLOR = (255, 215, 0)   # Gold
FOOD_DISAPPEARING_COLOR = (0, 255, 255) # Cyan
FOOD_POISON_COLOR = (139, 0, 0)       # Dark Red

# Power-up Colors
POWERUP_SPEED_COLOR = (0, 0, 255)     # Blue
POWERUP_SLOW_COLOR = (128, 0, 128)    # Purple
POWERUP_SHIELD_COLOR = (255, 165, 0)  # Orange

# Obstacle Color
OBSTACLE_COLOR = (139, 69, 19)        # Brown / Wood

# Database Configuration
DB_HOST = "localhost"
DB_PORT = 5434
DB_USER = "postgres"
DB_PASS = "password"
DB_NAME = "snake_db"

# UI Colors
UI_BG = (30, 30, 40)
UI_TEXT = (220, 220, 220)
UI_BTN = (60, 60, 80)
UI_BTN_HOVER = (90, 90, 110)

pygame.font.init()
FONT_LARGE = pygame.font.SysFont("Arial", 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Arial", 32)
FONT_SMALL = pygame.font.SysFont("Arial", 24)

# Settings utility
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"snake_color": [0, 255, 0], "grid_overlay": True, "sound": True}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"snake_color": [0, 255, 0], "grid_overlay": True, "sound": True}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

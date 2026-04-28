import json
import os

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_leaderboard(scores):
    # Sort and keep top 10
    scores.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_scores = scores[:10]
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(top_scores, f, indent=4)
    except Exception as e:
        print(f"Error saving leaderboard: {e}")

def add_score(name, score, distance):
    scores = load_leaderboard()
    scores.append({"name": name, "score": score, "distance": distance})
    save_leaderboard(scores)

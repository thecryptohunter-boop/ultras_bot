import json
import random
import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CATEGORIES_FILE = DATA_DIR / "categories.json"
CARDS_FILE = DATA_DIR / "cards.json"


def load_json(path: Path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_today_categories():
    categories = load_json(CATEGORIES_FILE)
    day = datetime.datetime.now().strftime("%A").lower()
    return categories.get(day, [])


def get_random_card(category: str):
    cards = load_json(CARDS_FILE)
    items = cards.get(category, [])
    if not items:
        return None
    return random.choice(items)


def get_post_for_today():
    today_categories = get_today_categories()
    if not today_categories:
        return None

    category = random.choice(today_categories)
    card = get_random_card(category)

    if not card:
        return None

    return {
        "category": category,
        "text": card.get("text", ""),
        "file_id": card.get("image")
    }

import json

FILE = "data/categories.json"


def load_categories():

    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_categories(data):

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

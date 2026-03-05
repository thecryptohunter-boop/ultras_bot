import json

FILE = "data/categories.json"


def load_categories():

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print("JSON ERROR:", e)
        return {}


def save_categories(data):

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

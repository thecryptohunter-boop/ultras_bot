import json
import os
from pathlib import Path

FILE_PATH = Path("data/categories.json")


def load_categories():
    if not FILE_PATH.exists():
        return {}
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_categories(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_item(code):
    data = load_categories()
    category = data.get(code)

    if not category or not category["items"]:
        return None, "empty"

    idx = category["last_index"]

    if idx >= len(category["items"]):
        if not category["finished_notified"]:
            category["finished_notified"] = True
            save_categories(data)
            return None, "finished"
        return None, "stop"

    item = category["items"][idx]

    category["last_index"] += 1
    save_categories(data)

    return item, "ok"

def add_item(code: str, file_id: str, text: str):
    data = load_categories()

    if code not in data:
        return False

    data[code]["items"].append({
        "file_id": file_id,
        "text": text
    })

    save_categories(data)
    return True

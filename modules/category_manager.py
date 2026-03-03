import json
import os

DATA_PATH = "data/categories.json"


def load_categories():
    if not os.path.exists(DATA_PATH):
        return {}

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_categories(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_next_item(code):
    data = load_categories()
    category = data.get(code)

    if not category or not category.get("items"):
        return None, "empty"

    idx = category.get("last_index", 0)

    if idx >= len(category["items"]):
       if not category.get("finished_notified"):
           category["finished_notified"] = True
           save_categories(data)
           return None, "finished"
       return None, "stop"

    item = category["items"][idx]

    category["last_index"] = idx + 1
    data[code] = category
    save_categories(data)

    return {
        "title": category["title"],
        "tag": category["tag"],
        "file_id": item.get("file_id"),
        "text": item.get("text")
    }, "ok"

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

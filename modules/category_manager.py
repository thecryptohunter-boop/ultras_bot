import json
from pathlib import Path

BASE_PATH = Path("data/categories")


def load_category(name: str):
    path = BASE_PATH / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_category(name: str, data):
    path = BASE_PATH / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_next_item(name: str):
    data = load_category(name)
    if not data or not data["items"]:
        return None, "empty"

    idx = data["current_index"]

    if idx >= len(data["items"]):
        return None, "finished"

    item = data["items"][idx]
    data["current_index"] += 1
    save_category(name, data)

    return item, "ok"


def reset_category(name: str):
    data = load_category(name)
    if not data:
        return
    data["current_index"] = 0
    save_category(name, data)

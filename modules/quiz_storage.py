import json
from pathlib import Path

QUESTIONS_FILE = Path("data/quiz_questions.json")
RESULTS_FILE = Path("data/quiz_results.json")


def load_questions(date):

    if not QUESTIONS_FILE.exists():
        return []

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get(date, [])


def load_results():

    if not RESULTS_FILE.exists():
        return {}

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(data):

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

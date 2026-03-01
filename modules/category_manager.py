import sqlite3

DB_PATH = "data/bot.db"

DEFAULT_IMAGE = None   # сюда можно прописать file_id дефолтной картинки
DEFAULT_TEXT = None    # сюда можно прописать дефолтный текст


def get_category(code: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT title, image_file_id, text
        FROM categories
        WHERE code = ?
    """, (code,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "title": row[0],
        "image": row[1] or DEFAULT_IMAGE,
        "text": row[2] or DEFAULT_TEXT or row[0]
    }


def set_category_image(code: str, file_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE categories
        SET image_file_id = ?
        WHERE code = ?
    """, (file_id, code))

    conn.commit()
    conn.close()


def set_category_text(code: str, text: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE categories
        SET text = ?
        WHERE code = ?
    """, (text, code))

    conn.commit()
    conn.close()

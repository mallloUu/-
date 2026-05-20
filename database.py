import sqlite3
import os
import sys


def _data_dir() -> str:
    """Папка для recipes.db: рядом с исходниками или в %APPDATA% у собранного exe."""
    if getattr(sys, "frozen", False):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        path = os.path.join(base, "KulinarnayaKniga")
        os.makedirs(path, exist_ok=True)
        return path
    return os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(_data_dir(), "recipes.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            login    TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Администратор по умолчанию
    cur.execute("SELECT COUNT(*) FROM users WHERE login='admin'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (login, password, is_admin) VALUES (?, ?, ?)",
            ("admin", "admin123", 1)
        )

    # Таблица рецептов (теперь привязана к user_id)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL DEFAULT 1,
            title        TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            cook_time    INTEGER NOT NULL,
            ingredients  TEXT    NOT NULL,
            instructions TEXT    NOT NULL,
            is_favorite  INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Миграция: добавить user_id если старая БД без этой колонки
    cur.execute("PRAGMA table_info(recipes)")
    columns = [row["name"] for row in cur.fetchall()]
    if "user_id" not in columns:
        cur.execute("ALTER TABLE recipes ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")

    conn.commit()
    conn.close()


# ─── Авторизация / пользователи ─────────────────────────────────────────────

def authenticate(login: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE login=? AND password=?", (login, password))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def register_user(login: str, password: str) -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (login, password, is_admin) VALUES (?, ?, 0)", (login, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, login, is_admin FROM users ORDER BY login")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM recipes WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def reset_password(user_id: int, new_password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
    conn.commit()
    conn.close()


# ─── CRUD рецептов ───────────────────────────────────────────────────────────

def add_recipe(user_id, title, category, cook_time, ingredients, instructions, is_favorite=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO recipes (user_id, title, category, cook_time, ingredients, instructions, is_favorite)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, title, category, cook_time, ingredients, instructions, is_favorite)
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_recipe(recipe_id, title, category, cook_time, ingredients, instructions, is_favorite):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE recipes SET title=?, category=?, cook_time=?, ingredients=?,"
        " instructions=?, is_favorite=? WHERE id=?",
        (title, category, cook_time, ingredients, instructions, is_favorite, recipe_id)
    )
    conn.commit()
    conn.close()


def delete_recipe(recipe_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()


def get_all_recipes(user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute("SELECT * FROM recipes WHERE user_id=? ORDER BY title", (user_id,))
    else:
        cur.execute("SELECT * FROM recipes ORDER BY title")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_favorites(user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute("SELECT * FROM recipes WHERE is_favorite=1 AND user_id=? ORDER BY title", (user_id,))
    else:
        cur.execute("SELECT * FROM recipes WHERE is_favorite=1 ORDER BY title")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_by_ingredient(query, user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    q = f"%{query}%"
    if user_id:
        cur.execute("SELECT * FROM recipes WHERE ingredients LIKE ? AND user_id=? ORDER BY title", (q, user_id))
    else:
        cur.execute("SELECT * FROM recipes WHERE ingredients LIKE ? ORDER BY title", (q,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_by_category(category, user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute("SELECT * FROM recipes WHERE category=? AND user_id=? ORDER BY title", (category, user_id))
    else:
        cur.execute("SELECT * FROM recipes WHERE category=? ORDER BY title", (category,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_favorite(recipe_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_favorite FROM recipes WHERE id=?", (recipe_id,))
    row = cur.fetchone()
    if row:
        new_val = 0 if row["is_favorite"] else 1
        cur.execute("UPDATE recipes SET is_favorite=? WHERE id=?", (new_val, recipe_id))
        conn.commit()
    conn.close()

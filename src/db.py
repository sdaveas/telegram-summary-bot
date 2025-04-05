import os
import sqlite3
from telebot.types import Message
from utils import logging

logger = logging.GetLogger()

DATABASE_PATH = os.getenv('DATABASE_PATH')

def init():
    logger.info("Initializing database at %s", DATABASE_PATH)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, chat_id INTEGER, user_id INTEGER,
                  username TEXT, first_name TEXT, message_text TEXT, date INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS context
                 (chat_id INTEGER PRIMARY KEY, context_text TEXT, last_updated INTEGER)''')
    conn.commit()
    conn.close()


def store_message(message: Message):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO messages (chat_id, user_id, username, first_name, message_text, date) VALUES (?, ?, ?, ?, ?, ?)",
              (message.chat.id, message.from_user.id, message.from_user.username,
               message.from_user.first_name, message.text, message.date))
    conn.commit()
    conn.close()


def get_recent_messages(chat_id, cutoff_time):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT username, message_text FROM messages WHERE chat_id = ? AND date >= ? ORDER BY date", (chat_id, cutoff_time))
    messages = c.fetchall()
    conn.close()
    return messages


def delete_old_messages(chat_id, cutoff_time):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE chat_id = ? AND date < ?", (chat_id, cutoff_time))
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def get_all_chat_ids():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT chat_id FROM messages")
    chat_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return chat_ids


def store_context(chat_id: int, context: str) -> None:
    """Store or update context for a specific chat."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO context (chat_id, context_text, last_updated) VALUES (?, ?, strftime('%s', 'now'))",
              (chat_id, context))
    conn.commit()
    conn.close()


def get_context(chat_id: int) -> str:
    """Get the context for a specific chat."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT context_text FROM context WHERE chat_id = ?", (chat_id,))
    result = c.fetchone()
    conn.close()

    return result[0] if result else ""


def remove_context(chat_id: int):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM context WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
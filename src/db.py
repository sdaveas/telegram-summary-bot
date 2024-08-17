import os
import sqlite3
from telebot.types import Message

DATABASE_PATH = os.getenv('DATABASE_PATH')

def init():
    print(f"Initializing database at {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, chat_id INTEGER, user_id INTEGER,
                  username TEXT, first_name TEXT, message_text TEXT, date INTEGER)''')
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

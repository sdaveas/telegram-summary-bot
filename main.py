import os
import telebot
from telebot.types import Message
import sqlite3
import datetime
from collections import defaultdict

bot = telebot.TeleBot(os.getenv('TG_BOT_TOKEN'))

# Initialize database
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, chat_id INTEGER, user_id INTEGER, 
                  username TEXT, first_name TEXT, message_text TEXT, date INTEGER)''')
    conn.commit()
    conn.close()

# Store message in database
def store_message(message: Message):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (chat_id, user_id, username, first_name, message_text, date) VALUES (?, ?, ?, ?, ?, ?)",
              (message.chat.id, message.from_user.id, message.from_user.username, 
               message.from_user.first_name, message.text, message.date))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['help'])
def help(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Usage: /summary \n\
                     M(minutes) (e.g., /summary 30)\n\
                     H(hours) M(minutes) (e.g., /summary 12 30)\n\
                     D(days) H(hours) M(minutes) (e.g., /summary 2 12 30)\n\
                     ")

@bot.message_handler(commands=['summary'])
def summarize(message: Message):
    chat_id = message.chat.id
    command_parts = message.text.split()

    mins = 10
    hours = 0
    days = 0
    
    if len(command_parts) == 1:
        msg = "using default values: %d days, %d hours, %d mins" % (days, hours, mins)
        bot.reply_to(message, msg)
    elif len(command_parts) == 2:
        mins = command_parts[1]
    elif len(command_parts) == 3:
        hours = command_parts[1]
        mins = command_parts[2]
    elif len(command_parts) == 4:
        days = command_parts[1]
        hours = command_parts[2]
        mins = command_parts[3]
    else:
        help(message)
        return

    delta = datetime.timedelta(days=int(days), hours=int(hours), minutes=int(mins))
    cutoff_time = int((datetime.datetime.now() - delta).timestamp())

    # Get recent messages from database
    recent_messages = get_recent_messages(chat_id, cutoff_time)

    if not recent_messages:
        bot.reply_to(message, f"No messages in the last {days} days and {hours} hours.")
        return

    # Simple summarization: count messages per user
    user_message_counts = defaultdict(int)
    for msg in recent_messages:
        user = msg[3] or msg[4]  # username or first_name
        user_message_counts[user] += 1

    # Create a summary
    summary = f"Summary of the last {days} days and {hours} hours:\n\n"
    summary += f"Total messages: {len(recent_messages)}\n"
    summary += "Messages per user:\n"
    for user, count in user_message_counts.items():
        summary += f"- {user}: {count}\n"

    bot.reply_to(message, summary)

def get_recent_messages(chat_id, cutoff_time):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE chat_id = ? AND date >= ? ORDER BY date DESC", (chat_id, cutoff_time))
    messages = c.fetchall()
    conn.close()
    return messages

@bot.message_handler(func=lambda message: True)
def handle_messages(message: Message):
    store_message(message)

# Initialize database and start the bot
if __name__ == "__main__":
    init_db()
    bot.polling()
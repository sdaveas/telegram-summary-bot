import os
import telebot
from telebot.types import Message
import sqlite3
import datetime
from collections import defaultdict
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys, prioritizing environment variables over .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

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
    bot.send_message(chat_id, "Usage: \n\
    /summary (defaults to 10 minutes)\n\
    /summary <minutes>\n\
    /summary <hours> <minutes>\n\
    /summary <days> <hours> <minutes>\n\
    ")

@bot.message_handler(commands=['ask'])
def ask(message: Message):
    request = message.text.split('/ask', 1)[1]

    summary = get_generic_response(request)
    bot.reply_to(message, summary)

@bot.message_handler(commands=['summary'])
def summarize(message: Message):
    chat_id = message.chat.id
    command_parts = message.text.split()

    mins = 10
    hours = 0
    days = 0
    
    if len(command_parts) == 1:
        print("No time specified, defaulting to 10 minutes")
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

    discussion = ""
    for msg in recent_messages:
        discussion += f"{msg[0]}: {msg[1]}\n"

    summary = get_ai_summary(discussion)

    bot.reply_to(message, summary)

def get_recent_messages(chat_id, cutoff_time):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT username, message_text FROM messages WHERE chat_id = ? AND date >= ? ORDER BY date", (chat_id, cutoff_time))
    messages = c.fetchall()
    conn.close()
    return messages

summary_request = "can you summarize briefly this discussion for me? Answer in the language the messages were sent, and don't make any prologue\n"

def get_generic_response(request):
    prompt = f"{HUMAN_PROMPT}" + request + f"{AI_PROMPT}"
    return ask_ai(prompt)

def get_ai_summary(discussion):
    prompt = f"{HUMAN_PROMPT}" + summary_request + discussion + f"{AI_PROMPT}"
    return ask_ai(prompt)

def ask_ai(prompt):
    try:
        response = anthropic.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=300,
        )
        return response.completion
    except Exception as e:
        return f"Error generating AI summary: {str(e)}"

def delete_old_messages(chat_id, cutoff_time):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE chat_id = ? AND date < ?", (chat_id, cutoff_time))
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    return deleted_count

@bot.message_handler(commands=['clean'])
def clean_old_messages(message: Message):
    chat_id = message.chat.id
    one_day_ago = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    deleted_count = delete_old_messages(chat_id, one_day_ago)
    bot.reply_to(message, f"Deleted {deleted_count} messages older than 1 day.")

@bot.message_handler(func=lambda message: True)
def handle_messages(message: Message):
    store_message(message)

# Initialize database and start the bot
if __name__ == "__main__":
    init_db()
    bot.polling()
import os
import telebot
from telebot.types import Message
import brain as brain
import db as db
import utils.utils as utils

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

DEFAULT_SUMMARY_DEPTH_EXPRESSION = '1h'


def start_polling():
    bot.polling()


@bot.message_handler(commands=['credits'])
def credits(message: Message):
    msg = "https://github.com/sdaveas/telegram-summary-bot with ❤️"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['help'])
def help(message: Message, error_msg=""):
    msg = error_msg + utils.help_message(DEFAULT_SUMMARY_DEPTH_EXPRESSION)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['ask'])
def ask(message: Message):
    request = message.text.split('/ask', 1)[1]
    summary = brain.get_generic_response(request)
    bot.reply_to(message, summary)


@bot.message_handler(commands=['clean'])
def clean_old_messages(message: Message):
    deleted_count = db.delete_old_messages(message.chat.id, utils.one_day_ago())
    bot.reply_to(message, f"Deleted {deleted_count} messages older than 1 day.")


@bot.message_handler(commands=['summary'])
def summarize(message: Message):
    chat_id = message.chat.id
    summary_depth_expression = message.text.split()

    if len(summary_depth_expression) == 1:
        summary_depth_seconds = utils.time_expression_to_seconds(DEFAULT_SUMMARY_DEPTH_EXPRESSION)
    elif len(summary_depth_expression) == 2:
        summary_depth_seconds = utils.time_expression_to_seconds(summary_depth_expression[1])
    else:
        help(message + "invalid /summary argument number\n")

    if summary_depth_seconds == 0:
        help(message, "invalid /summary argument\n")
        return

    cutoff_time = utils.seconds_to_timestamp(summary_depth_seconds)
    recent_messages = db.get_recent_messages(chat_id, cutoff_time)

    if not recent_messages:
        bot.reply_to(message, f"No messages in the last {summary_depth_expression}")
        return

    discussion = ""
    for msg in recent_messages:
        discussion += f"{msg[0]}: {msg[1]}\n"

    summary = brain.get_discussion_summary(discussion)
    bot.reply_to(message, summary)


@bot.message_handler(func=lambda message: True)
def handle_messages(message: Message):
    db.store_message(message)
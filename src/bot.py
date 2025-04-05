import os
import telebot
from telebot.types import Message
import flask
from flask import request
import brain as brain
import db as db
import utils.utils as utils
import utils.logging as logging

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

WEBHOOK_LISTEN = os.getenv('WEBHOOK_LISTEN', '0.0.0.0')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 8443))

CLOUD_RUN_URL = os.getenv('CLOUD_RUN_URL')
WEBHOOK_HOST = CLOUD_RUN_URL or os.getenv('WEBHOOK_HOST')

WEBHOOK_URL_PATH = f"/{TELEGRAM_BOT_TOKEN}/"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = flask.Flask(__name__)

DEFAULT_SUMMARY_DEPTH_EXPRESSION = '1h'

logger = logging.GetLogger()

# Webhook endpoint
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

# Your existing command handlers remain the same
@bot.message_handler(commands=['credits'])
def credits(message: Message):
    logger.info("credits command received")
    msg = "https://github.com/sdaveas/telegram-summary-bot with ❤️"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['help'])
def help(message: Message, error_msg=""):
    logger.info("help command received with msg: [%s]", error_msg)
    msg = error_msg + utils.help_message(DEFAULT_SUMMARY_DEPTH_EXPRESSION)
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['ask'])
def ask(message: Message):
    logger.info("ask command received with prompt: [%s]", message.text)
    request = message.text.split('/ask', 1)[1]
    summary = brain.get_generic_response(request)
    bot.reply_to(message, summary)

@bot.message_handler(commands=['clean'])
def clean_old_messages(message: Message):
    logger.info("clean command received")
    deleted_count = db.delete_old_messages(message.chat.id, utils.one_day_ago())
    bot.reply_to(message, f"Deleted {deleted_count} messages older than 1 day.")

def get_discussion(chat_id, summary_depth_expression):
    if summary_depth_expression is None:
        summary_depth_seconds = utils.time_expression_to_seconds(DEFAULT_SUMMARY_DEPTH_EXPRESSION)
    else:
        summary_depth_seconds = utils.time_expression_to_seconds(summary_depth_expression)

    if summary_depth_seconds == 0:
        return None

    cutoff_time = utils.seconds_to_timestamp(summary_depth_seconds)
    recent_messages = db.get_recent_messages(chat_id, cutoff_time)

    if not recent_messages:
        logger.debug("No messages in the last [%s]", summary_depth_expression)
        return None

    logger.debug("Recent messages: [%s]", recent_messages)

    discussion = ""
    for msg in recent_messages:
        discussion += f"{msg[0]}: {msg[1]}\n"

    return discussion

@bot.message_handler(commands=['summary'])
def summarize(message: Message):
    logger.info("summary command received")

    chat_id = message.chat.id
    summary_depth_expression = message.text.split()

    if len(summary_depth_expression) == 1:
        summary_depth_expression = None
    elif len(summary_depth_expression) == 2:
        summary_depth_expression = summary_depth_expression[1]
    else:
        help(message, "invalid /summary argument number\n")
        return

    discussion = get_discussion(chat_id, summary_depth_expression)
    if discussion is None:
        bot.reply_to(message, f"No messages in the specified time range")
        return

    summary = brain.get_discussion_summary(discussion)
    bot.reply_to(message, summary)

@bot.message_handler(commands=['question'])
def ask_question(message: Message):
    logger.info("question command received")

    chat_id = message.chat.id
    command_parts = message.text.split(maxsplit=2)

    if len(command_parts) < 3:
        help(message, "Invalid /question format. Use: /question [time_range] Your question\n")
        return

    summary_depth_expression = command_parts[1]
    question = command_parts[2]

    discussion = get_discussion(chat_id, summary_depth_expression)
    if discussion is None:
        bot.reply_to(message, f"No messages in the specified time range")
        return

    answer = brain.get_answer_to_question(discussion, question)
    bot.reply_to(message, answer)

@bot.message_handler(commands=['cal'])
def calculate(message: Message):
    logger.info("cal command received with expression: [%s]", message.text)

    expression = message.text.split('/cal', 1)[1].strip()

    if not expression:
        bot.reply_to(message, "Please provide a mathematical expression to evaluate.\nExample: /cal 2+2")
        return

    allowed_chars = set('0123456789+-*/(). ')
    if not all(c in allowed_chars for c in expression):
        bot.reply_to(message, "Invalid expression. Only basic math operations (+, -, *, /) and numbers are allowed.")
        return

    try:
        result = eval(expression)
        bot.reply_to(message, f"Result: {result}")
    except Exception as e:
        logger.error("Error evaluating expression: %s", str(e))
        bot.reply_to(message, "Error: Invalid mathematical expression")

@bot.message_handler(func=lambda message: True)
def handle_messages(message: Message):
    logger.debug("adding message to db: [%s]", message.text)
    db.store_message(message)

def start():
    logger.info("starting webhook with url: [%s] + [%s]", WEBHOOK_HOST, WEBHOOK_URL_PATH)

    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_HOST + WEBHOOK_URL_PATH)

    app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT)
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

ADMIN_USER_ID = os.getenv('ADMIN_USER_ID', 0)

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
    context = db.get_context(message.chat.id)
    summary = brain.get_generic_response(request, context)
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

    context = db.get_context(chat_id)
    summary = brain.get_discussion_summary(discussion, context)
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

    context = db.get_context(chat_id)
    answer = brain.get_answer_to_question(discussion, question, context)
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

@bot.message_handler(commands=['broadcast'])
def broadcast(message: Message):
    logger.info("broadcast command received")

    if str(message.from_user.id) != ADMIN_USER_ID:
        logger.error("User %s is not authorized to use this command. ADMIN_USER_ID is %s", message.from_user.id, ADMIN_USER_ID)
        bot.reply_to(message, "You are not authorized to use this command. Your user id is: " + str(message.from_user.id))
        return

    broadcast_text = message.text.split('/broadcast', 1)[1].strip()
    if not broadcast_text:
        bot.reply_to(message, "Please provide a message to broadcast.\nExample: /broadcast Hello everyone!")
        return

    chat_ids = db.get_all_chat_ids()
    if not chat_ids:
        bot.reply_to(message, "No chats found.")
        return

    success_count = 0
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, broadcast_text)
            success_count += 1
        except Exception as e:
            logger.error("Failed to send broadcast to chat %s: %s", chat_id, str(e))

    bot.reply_to(message, f"Broadcast completed. Successfully sent to {success_count} out of {len(chat_ids)} chats.")

@bot.message_handler(content_types=['photo'])
def handle_messages(message: Message):
    logger.info("message contains photo and caption is: [%s]", message.caption)

    if message.caption is None:
        logger.debug("skipping photo with no caption")
        return

    parts = message.caption.split(' ', 1)
    if parts[0] == 'split_bill' or parts[0] == 'sb':
        raw = message.photo[-1].file_id
        file_info = bot.get_file(raw)
        photo_bytes = bot.download_file(file_info.file_path)

        description = ""
        if len(parts) > 1:
            description = parts[1]

        context = db.get_context(message.chat.id)
        split_bill_result = brain.split_bill(photo_bytes, description, context)

        logger.info("received analysis result: [%s]", split_bill_result)
        bot.reply_to(message, str(split_bill_result))

        return


@bot.message_handler(commands=['set_context'])
def set_context(message: Message):
    """Set the context for the current chat."""
    logger.info("setcontext command received")

    context = message.text.split('/set_context', 1)[1].strip()
    if not context:
        bot.reply_to(message, "Please provide a context message.\nExample: /setcontext This is a work chat about project X")
        return

    db.store_context(message.chat.id, context)
    bot.reply_to(message, "Context updated successfully!")


@bot.message_handler(commands=['get_context'])
def get_context(message: Message):
    """Get the context for the current chat."""
    logger.info("get_context command received")

    context = db.get_context(message.chat.id)
    bot.reply_to(message, "Context: " + context)

@bot.message_handler(commands=['clear_context'])
def clear_context(message: Message):
    """Clear the context for the current chat."""
    logger.info("clear_context command received")

    db.remove_context(message.chat.id)
    bot.reply_to(message, "Context cleared")

# This needs to be the last handler, otherwise it will catch commands as text messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message: Message):
    logger.debug("adding message to db: [%s]", message.text)
    db.store_message(message)


def start():
    logger.info("starting webhook with url: [%s] + [%s]", WEBHOOK_HOST, WEBHOOK_URL_PATH)

    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_HOST + WEBHOOK_URL_PATH)

    app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT)
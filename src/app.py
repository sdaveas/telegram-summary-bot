from dotenv import load_dotenv
import db as db
import bot as bot
import prober as prober
import threading
import os
import utils.logging as logging

logger = logging.GetLogger()

load_dotenv()

if __name__ == "__main__":
    logger.info("starting Telegram Bot")

    prober_thread = threading.Thread(target=prober.start)
    prober_thread.start()

    db.init()
    bot.start()
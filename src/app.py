from dotenv import load_dotenv
import db as db
import bot as bot
import prober as prober
import threading
import os

load_dotenv()
print('port:', os.getenv('PORT'))

if __name__ == "__main__":
    prober_thread = threading.Thread(target=prober.start)
    prober_thread.start()

    db.init()
    bot.start()
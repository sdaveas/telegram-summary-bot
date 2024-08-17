from dotenv import load_dotenv
import db as db
import bot as bot

load_dotenv()

if __name__ == "__main__":
    db.init()
    bot.start_polling()
from dotenv import load_dotenv
import db.db as db
import bot.bot as bot

load_dotenv()

# Initialize database and start the bot
if __name__ == "__main__":
    db.init()
    bot.polling()
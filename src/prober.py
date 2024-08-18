import os
from flask import Flask

PORT= int(os.environ.get('PORT'))
app = Flask(__name__)

@app.route('/')
def index():
    return "Telegram Bot is running!"

@app.route('/healthz')
def health_check():
    return "OK", 200

def start():
    app.run(host='0.0.0.0', port=PORT)
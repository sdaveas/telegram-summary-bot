import os
from flask import Flask
from utils import logging

logger = logging.GetLogger()

HOST='0.0.0.0'
PORT= int(os.environ.get('PORT'))
app = Flask(__name__)

@app.route('/')
def index():
    return "Telegram Bot is running!"

@app.route('/healthz')
def health_check():
    return "OK", 200

def start():
    logger.info("starting prober in %s:%s", HOST, PORT)
    app.run(host=HOST, port=PORT)
import os
from flask import Flask
from utils import logging

logger = logging.GetLogger()

PROBE_HOST= os.getenv('PROBE_HOST', '0.0.0.0')
PROBE_PORT= int(os.environ.get('PROBE_PORT', 8080))
app = Flask(__name__)

@app.route('/')
def index():
    return "Telegram Bot is running!"

@app.route('/healthz')
def health_check():
    return "OK", 200

def start():
    logger.info("starting prober in %s:%s", PROBE_HOST, PROBE_PORT)
    app.run(host=PROBE_HOST, port=PROBE_PORT)
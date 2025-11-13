import threading
from bot import app as telegram_app
from web_server import app as web_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_telegram_bot():
    """Run Telegram bot in a separate thread"""
    logger.info("Starting Telegram bot...")
    telegram_app.run()

def run_web_server():
    """Run Flask web server"""
    logger.info("Starting web server...")
    web_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Run web server in main thread
    run_web_server()

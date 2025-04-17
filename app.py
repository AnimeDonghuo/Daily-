from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

def init_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def extract_dailymotion_url(url):
    driver = init_selenium()
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Dailymotion")]'))
        ).click()
        
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        video_id = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', iframe.get_attribute("src"))
        return f"https://www.dailymotion.com/video/{video_id.group(1)}" if video_id else None

    except Exception as e:
        logger.error(f"Selenium error: {str(e)}")
        return None
    finally:
        driver.quit()

def start(update: Update, _):
    update.message.reply_text("🚀 Send me a LuciferDonghua/SeaTV link to extract the Dailymotion URL!")

def handle_message(update: Update, _):
    url = update.message.text
    if not url.startswith(('http://', 'https://')):
        update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return

    update.message.reply_text("⏳ Processing...")
    if dm_url := extract_dailymotion_url(url):
        update.message.reply_text(f"✅ Extracted URL:\n{dm_url}")
    else:
        update.message.reply_text("❌ Failed to extract Dailymotion link")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    # Set webhook on startup
    bot.set_webhook(f"https://YOUR_KOYEB_APP.koyeb.app/{TELEGRAM_TOKEN}")
    app.run(host='0.0.0.0', port=8080)

from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

def extract_dailymotion_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        
        # Wait for Dailymotion button and click it
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Dailymotion") or contains(@href, "dailymotion.com")]'))
        ).click()
        
        # Wait for iframe to load
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        
        embed_url = iframe.get_attribute("src")
        video_id = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', embed_url)
        if video_id:
            return f"https://www.dailymotion.com/video/{video_id.group(1)}"
        return None

    except Exception as e:
        print(f"Selenium error: {str(e)}")
        return None
    finally:
        driver.quit()

def start(update: Update, context):
    update.message.reply_text("🚀 Send me a SeaTV/LuciferDonghua link to extract the Dailymotion URL!")

def handle_message(update: Update, context):
    url = update.message.text.strip()
    if not re.match(r'^https?://', url):
        update.message.reply_text("❌ Please send a valid URL (e.g., https://seatv-24.xyz/...)")
        return

    dm_url = extract_dailymotion_url(url)
    if dm_url:
        update.message.reply_text(f"✅ Extracted URL:\n{dm_url}")
    else:
        update.message.reply_text("❌ Failed to extract Dailymotion link. The site may require manual interaction.")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.process_update(update)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

def extract_dailymotion_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for iframe first (common in SeaTV/LuciferDonghua)
        iframe = soup.find('iframe', src=re.compile(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)'))
        if iframe:
            video_id = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', iframe['src']).group(1)
            return f"https://www.dailymotion.com/video/{video_id}"

        # Check for JavaScript data (fallback)
        script = soup.find('script', string=re.compile(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)'))
        if script:
            video_id = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', script.text).group(1)
            return f"https://www.dailymotion.com/video/{video_id}"

        return None

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

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
        update.message.reply_text("❌ No Dailymotion link found. The site may use dynamic loading (try Selenium).")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.process_update(update)
    return jsonify(success=True)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

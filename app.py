from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import re
import os
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

app = Flask(__name__)

# Initialize Telegram Bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

def extract_dailymotion_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Method 1: Check for JavaScript variables
        script_data = soup.find('script', string=re.compile(r'dailymotion\.com/embed/video'))
        if script_data:
            video_id = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', script_data.text)
            if video_id:
                return f"https://www.dailymotion.com/video/{video_id.group(1)}"

        # Method 2: Check iframe
        iframe = soup.find('iframe', src=re.compile(r'dailymotion\.com/embed/video/[a-zA-Z0-9]+'))
        if iframe:
            embed_url = iframe['src']
            video_id = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', embed_url)
            if video_id:
                return f"https://www.dailymotion.com/video/{video_id.group(1)}"

        return None

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Telegram Handlers
def start(update: Update, context):
    update.message.reply_text("🚀 Send me a SeaTV link, and I'll extract the Dailymotion URL!")

def handle_message(update: Update, context):
    url = update.message.text
    if not url.startswith(("http://", "https://")):
        update.message.reply_text("❌ Please send a valid URL.")
        return

    dm_url = extract_dailymotion_url(url)
    if dm_url:
        update.message.reply_text(f"✅ Extracted Dailymotion URL:\n{dm_url}")
    else:
        update.message.reply_text("❌ Failed to extract Dailymotion link. The site may use dynamic loading.")

# Flask Webhook Setup
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    # Set webhook (run once)
    bot.set_webhook(url=f"https://YOUR_KOYEB_APP.koyeb.app/{TELEGRAM_TOKEN}")
    app.run(host='0.0.0.0', port=8080)

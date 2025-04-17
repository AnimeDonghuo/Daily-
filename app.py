import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from bs4 import BeautifulSoup
import re

# Initialize Flask
app = Flask(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dailymotion URL pattern
DAILYMOTION_PATTERN = re.compile(
    r'(https?://)?(www\.)?dailymotion\.com/(video|embed)/([a-zA-Z0-9]+)'
)

@app.route('/')
def home():
    return "Dailymotion Extractor Bot is running!"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🌟 Dailymotion Link Extractor Bot 🌟\n\n"
        "Send me a website URL to extract Dailymotion links!"
    )

def extract_dailymotion_links(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Check iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            match = DAILYMOTION_PATTERN.search(src)
            if match:
                video_id = match.group(4)
                links.append(f"https://www.dailymotion.com/video/{video_id}")
        
        return links
    
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return []

def handle_url(update: Update, context: CallbackContext) -> None:
    url = update.message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        update.message.reply_text("Please send a valid URL starting with http:// or https://")
        return
    
    try:
        links = extract_dailymotion_links(url)
        
        if not links:
            update.message.reply_text("No Dailymotion links found on this page.")
            return
        
        response = f"Found {len(links)} Dailymotion link(s):\n\n" + "\n".join(links)
        update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("Failed to process URL. Please try another one.")

def main():
    # Initialize Telegram bot
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), use_context=True)
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))
    
    # Start polling
    updater.start_polling()
    
    # Start Flask
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    
    # Keep running
    updater.idle()

if __name__ == '__main__':
    main()

import os
import logging
import re
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Enhanced Dailymotion pattern matching
DM_PATTERN = re.compile(
    r'(?:https?:\/\/(?:www\.)?dailymotion\.com\/(?:video|embed)\/([a-zA-Z0-9]+)|'
    r'(?:data-video-id=["\']([a-zA-Z0-9]+)["\'])|'
    r'(?:dailymotion\.com\/player\.html\?video=([a-zA-Z0-9]+))'
)

def extract_dm_links(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        found_links = set()

        # Check all potential embed locations
        for element in soup.find_all(['iframe', 'div', 'script', 'a']):
            src = element.get('src', '') or element.get('href', '') or str(element)
            
            # Find all matches in the element
            matches = DM_PATTERN.finditer(src)
            for match in matches:
                video_id = match.group(1) or match.group(2) or match.group(3)
                if video_id:
                    found_links.add(f"https://www.dailymotion.com/video/{video_id}")

        # Check for alternative server links
        server_sections = soup.find_all(lambda tag: 'server' in str(tag).lower() or 'mirror' in str(tag).lower())
        for section in server_sections[:3]:  # Check first 3 server sections
            for a in section.find_all('a', href=True):
                if not any(x in a['href'] for x in ['dailymotion', 'facebook', 'youtube']):
                    try:
                        server_resp = session.get(a['href'], headers=headers, timeout=10)
                        server_soup = BeautifulSoup(server_resp.text, 'html.parser')
                        for iframe in server_soup.find_all('iframe'):
                            src = iframe.get('src', '')
                            if 'dailymotion' in src:
                                found_links.add(src)
                    except:
                        continue

        return list(found_links)
    
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return []

@app.route('/')
def home():
    return "Dailymotion Extractor Bot is running!"

@app.route('/health')
def health_check():
    return "OK", 200

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🌟 Dailymotion Link Extractor Bot 🌟\n\n"
        "Send me any anime/donghua website URL and I'll extract embedded Dailymotion links!\n\n"
        "Example: https://luciferdonghua.in/series-name-episode-123"
    )

def handle_url(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    
    if not re.match(r'^https?://', url, re.I):
        update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return
    
    try:
        update.message.reply_chat_action('typing')
        links = extract_dm_links(url)
        
        if not links:
            update.message.reply_text("🔍 No Dailymotion links found. The site may use a different video host.")
            return
        
        response = "✅ Found Dailymotion Links:\n\n" + "\n".join(
            f"{i+1}. {link}" for i, link in enumerate(links)
        )
        update.message.reply_text(response, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        update.message.reply_text("⚠️ Failed to process URL. Please try another one.")

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
    app.run(host='0.0.0.0', port=port, debug=False)
    
    # Keep running
    updater.idle()

if __name__ == '__main__':
    main()

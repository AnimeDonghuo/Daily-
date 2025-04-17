import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, request, render_template, jsonify
import threading
import time
from datetime import datetime
from config import CONFIG

# Initialize Flask app
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

# Storage for analytics
analytics_data = {
    'total_requests': 0,
    'successful_extractions': 0,
    'popular_sites': {}
}

# ===== Telegram Bot Functions =====
def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message with menu."""
    keyboard = [
        [InlineKeyboardButton("How to Use", callback_data='help')],
        [InlineKeyboardButton("Top Sites", callback_data='topsites')],
        [InlineKeyboardButton("Web Dashboard", url=CONFIG['WEB_URL'])]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "🌟 *Dailymotion Link Extractor Bot* 🌟\n\n"
        "Send me any website URL and I'll extract embedded Dailymotion links!\n\n"
        "🔹 *Features:*\n"
        "- Extract multiple Dailymotion links\n"
        "- Clean, direct video URLs\n"
        "- Web dashboard for manual extraction\n\n"
        "Try sending a URL now!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def extract_dailymotion_links(url):
    """Extract Dailymotion links from a webpage."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Check iframes and links
        for element in soup.find_all(['iframe', 'a']):
            src = element.get('src', '') or element.get('href', '')
            match = DAILYMOTION_PATTERN.search(src)
            if match:
                video_id = match.group(4)
                links.append(f"https://www.dailymotion.com/video/{video_id}")
        
        return list(set(links))
    
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return []

def handle_url(update: Update, context: CallbackContext) -> None:
    """Handle URL messages."""
    url = update.message.text.strip()
    analytics_data['total_requests'] += 1
    
    if not url.startswith(('http://', 'https://')):
        update.message.reply_text("⚠️ Please send a valid URL starting with http:// or https://")
        return
    
    try:
        domain = url.split('/')[2]
        analytics_data['popular_sites'][domain] = analytics_data['popular_sites'].get(domain, 0) + 1
        
        links = extract_dailymotion_links(url)
        
        if not links:
            update.message.reply_text("🔍 No Dailymotion links found.")
            return
        
        analytics_data['successful_extractions'] += 1
        
        response = (
            f"✅ *Found {len(links)} Dailymotion link(s)* on [this page]({url}):\n\n" +
            "\n".join([f"• {link}" for link in links]) +
            f"\n\n_Extracted at {datetime.now().strftime('%I:%M %p')}_"
        )
        
        update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"URL handling error: {e}")
        update.message.reply_text("❌ Error processing URL. Please try another one.")

# ===== Web Routes =====
@app.route('/')
def dashboard():
    return render_template('dashboard.html', 
                         total_requests=analytics_data['total_requests'],
                         success_rate=analytics_data['successful_extractions'])

@app.route('/extract', methods=['POST'])
def web_extract():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    links = extract_dailymotion_links(url)
    return jsonify({"success": True, "links": links})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# ===== Run Services =====
def run_bot():
    """Run the Telegram bot."""
    updater = Updater(CONFIG['TELEGRAM_TOKEN'])
    dispatcher = updater.dispatcher
    
    # Commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))
    
    updater.start_polling()
    updater.idle()

def run_web():
    """Run the web server."""
    app.run(host='0.0.0.0', port=CONFIG['PORT'])

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    web_thread = threading.Thread(target=run_web)
    
    bot_thread.start()
    web_thread.start()
    
    bot_thread.join()
    web_thread.join()

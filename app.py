import os
from flask import Flask
from telegram.ext import Updater

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Dailymotion Extractor Bot is running!"

# Your Telegram bot code here
def main():
    # Initialize Telegram bot
    updater = Updater(os.getenv('TELEGRAM_TOKEN'))
    
    # Add handlers and other bot setup...
    
    # Start Flask and bot together
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()

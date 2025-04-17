import os

CONFIG = {
    'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN', 'your-telegram-bot-token'),
    'PORT': int(os.getenv('PORT', 8080)),
    'WEB_URL': os.getenv('WEB_URL', 'https://your-app-name.koyeb.app'),
    'OWNER_ID': int(os.getenv('OWNER_ID', 123456789))  # Your Telegram user ID
}

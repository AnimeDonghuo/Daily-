import os

CONFIG = {
    'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN', 'your-telegram-bot-token'),
    'PORT': int(os.getenv('PORT', 8080)),
    'WEB_URL': os.getenv('WEB_URL', 'https://your-app-name.koyeb.app'),
    'OWNER_ID': int(os.getenv('OWNER_ID', 123456789))  # Your Telegram user ID
    
# Koyeb Deployment URL (for webhook)
KOYEB_APP_URL = "https://YOUR_APP_NAME.koyeb.app"

# Selenium Settings
CHROME_OPTIONS = {
    "headless": True,
    "no-sandbox": True,
    "disable-dev-shm-usage": True
}

# Timeouts (in seconds)
SELENIUM_TIMEOUT = 20

# Dailymotion Link Extractor Bot

Telegram bot + web dashboard for extracting embedded Dailymotion links from websites.

## Features

- Extract Dailymotion links from any webpage
- Telegram bot interface
- Web dashboard for manual extraction
- Health checks for Koyeb deployment

## Deployment on Koyeb

1. Fork this repository
2. Create a new Koyeb app and connect your GitHub repo
3. Add these secrets in Koyeb:
   - `telegram-token` - Your Telegram bot token
   - `owner-id` - Your Telegram user ID
4. Deploy!

## Environment Variables

- `TELEGRAM_TOKEN` - Telegram bot token
- `PORT` - Port to run on (default: 8080)
- `OWNER_ID` - Your Telegram user ID
- `WEB_URL` - Your Koyeb app URL

## Health Check

The service includes a TCP health check at `/health` that Koyeb will use to verify the service is running.

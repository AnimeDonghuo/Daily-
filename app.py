from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def extract_dailymotion_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Method 1: Check for JavaScript variables (common in SeaTV)
        script_data = soup.find('script', string=re.compile(r'dailymotion\.com/embed/video'))
        if script_data:
            video_id = re.search(r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)', script_data.text)
            if video_id:
                return f"https://www.dailymotion.com/video/{video_id.group(1)}"

        # Method 2: Check iframe (fallback)
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

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    dm_url = extract_dailymotion_url(url)
    if dm_url:
        return jsonify({"dailymotion_url": dm_url})
    else:
        return jsonify({"error": "Dailymotion link not found in page source"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

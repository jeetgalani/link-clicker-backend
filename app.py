from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

app = Flask(__name__)
CORS(app)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/117.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0"
]

scheduled_jobs = {}

def run_browser_session(url, click_count, wait_time):
    user_agent = random.choice(USER_AGENTS)
    options = Options()
    options.add_argument("--incognito")
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless=new')

    for _ in range(click_count):
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(wait_time)
        driver.quit()
        time.sleep(1)

@app.route('/run', methods=['POST'])
@app.route('/run', methods=['POST'])
@app.route('/run', methods=['POST'])
def run_script():
    try:
        data = request.json
        print("📥 Received POST request with data:", data)

        url = data.get('url')
        click_count = int(data.get('clickCount', 1))
        wait_time = int(data.get('waitTime', 5))
        is_scheduled = data.get('isScheduled', False)
        interval_time = int(data.get('intervalTime', 5))

        def job():
            print(f"🌀 Running browser session for {url} ({click_count}x clicks)")
            run_browser_session(url, click_count, wait_time)
            if scheduled_jobs.get(url):
                scheduled_jobs[url] = threading.Timer(interval_time * 60, job)
                scheduled_jobs[url].start()

        if is_scheduled:
            print(f"⏰ Scheduling job for {url} every {interval_time} min")
            if url in scheduled_jobs:
                scheduled_jobs[url].cancel()
            scheduled_jobs[url] = threading.Timer(0, job)
            scheduled_jobs[url].start()
        else:
            if url in scheduled_jobs:
                print(f"❌ Canceling existing schedule for {url}")
                scheduled_jobs[url].cancel()
                del scheduled_jobs[url]
            print(f"🚀 Starting one-time run for {url}")
            threading.Thread(target=run_browser_session, args=(url, click_count, wait_time)).start()

        return jsonify({"status": "Script triggered"})

    except Exception as e:
        print("❌ ERROR OCCURRED:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)

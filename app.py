from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import random
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

# In-memory run log
run_logs = []

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/117.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0"
]

scheduled_jobs = {}

def run_browser_session(url, click_count, wait_time):
    print(f"🧪 Starting session: {url} | {click_count} clicks | wait {wait_time}s", flush=True)
    user_agent = random.choice(USER_AGENTS)

    try:
        with sync_playwright() as p:
            for i in range(click_count):
                print(f"➡️ Launching browser ({i+1}/{click_count})...", flush=True)
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=user_agent, viewport={"width": 1280, "height": 800})
                page = context.new_page()

                print("🌐 Navigating to URL...", flush=True)
                page.goto(url, timeout=60000)
                page.wait_for_timeout(wait_time * 1000)

                browser.close()
                print("🛑 Browser closed", flush=True)
                time.sleep(1)

        run_logs.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "url": url,
            "status": "✅ Success",
            "clickCount": click_count,
            "waitTime": wait_time
        })
        print("✅ Appended success log", flush=True)

    except Exception as e:
        print(f"❌ Error during Playwright session: {e}", flush=True)
        run_logs.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "url": url,
            "status": f"❌ Error: {str(e)}",
            "clickCount": click_count,
            "waitTime": wait_time
        })
        

@app.route('/run', methods=['POST'])
def run_script():
    try:
        data = request.json
        print("📥 Received POST request with data:", data, flush=True)

        url = data.get('url')
        click_count = int(data.get('clickCount', 1))
        wait_time = int(data.get('waitTime', 5))
        is_scheduled = data.get('isScheduled', False)
        interval_time = int(data.get('intervalTime', 5))

        def job():
            print(f"🌀 Running browser session for {url} ({click_count}x clicks)", flush=True)
            run_browser_session(url, click_count, wait_time)
            if scheduled_jobs.get(url):
                scheduled_jobs[url] = threading.Timer(interval_time * 60, job)
                scheduled_jobs[url].start()

        if is_scheduled:
            print(f"⏰ Scheduling job for {url} every {interval_time} min", flush=True)
            if url in scheduled_jobs:
                scheduled_jobs[url].cancel()
            scheduled_jobs[url] = threading.Timer(0, job)
            scheduled_jobs[url].start()
        else:
            if url in scheduled_jobs:
                print(f"❌ Canceling existing schedule for {url}", flush=True)
                scheduled_jobs[url].cancel()
                del scheduled_jobs[url]
            print(f"🚀 Starting one-time run for {url}", flush=True)
            threading.Thread(target=run_browser_session, args=(url, click_count, wait_time), daemon=True).start()

        return jsonify({"status": "Script triggered"})

    except Exception as e:
        print("❌ ERROR OCCURRED:", e, flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(run_logs[-10:])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)

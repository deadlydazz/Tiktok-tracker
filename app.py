import os
import re
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import httpx

app = Flask(__name__)

def fetch_tiktok_data(username: str):
    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=10.0) as client:
            response = client.get(url)
            if response.status_code != 200:
                return {"error": f"Failed to fetch profile (Status code {response.status_code})"}

            match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', response.text)
            if not match:
                return {"error": "Failed to parse profile metadata."}

            data = json.loads(match.group(1))
            user_detail = data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {})

            if not user_detail or "userInfo" not in user_detail:
                return {"error": "User not found or profile is private."}

            user_info = user_detail["userInfo"]["user"]
            stats = user_detail["userInfo"]["stats"]

            item_list = user_detail.get("itemList", [])
            last_active = "No videos published"
            if item_list:
                latest_ts = int(item_list[0].get("createTime", 0))
                if latest_ts > 0:
                    last_active = datetime.fromtimestamp(latest_ts).strftime("%Y-%m-%d %H:%M:%S")

            return {
                "username": user_info.get("uniqueId"),
                "nickname": user_info.get("nickname"),
                "region": user_info.get("region", "Unknown"),
                "last_active": last_active,
                "followers": stats.get("followerCount", 0),
                "following": stats.get("followingCount", 0)
            }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    return jsonify(fetch_tiktok_data(username))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

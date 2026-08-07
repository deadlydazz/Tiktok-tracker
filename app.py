from flask import Flask, render_template, request
import requests
import datetime

app = Flask(__name__)

# RapidAPI Credentials
API_KEY = "4ee2a09994msh26e01f588e4bf33p100b2ajsn6f794c45ba5a"
API_HOST = "tiktok-api23.p.rapidapi.com"
API_URL = "https://tiktok-api23.p.rapidapi.com/api/user/info"

def get_creation_date(user_id):
    """Calculates account creation timestamp from 19-digit User ID"""
    try:
        binary_id = bin(int(user_id))[2:]
        timestamp = int(binary_id[:32], 2)
        return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime('%B %d, %Y')
    except Exception:
        return "N/A"

@app.route('/', methods=['GET', 'POST'])
def home():
    profile_data = None
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip().replace('@', '')
        
        if not username:
            error = "Please enter a username."
        else:
            headers = {
                "x-rapidapi-key": API_KEY,
                "x-rapidapi-host": API_HOST
            }
            params = {"uniqueId": username}
            
            try:
                response = requests.get(API_URL, headers=headers, params=params, timeout=10)
                res = response.json()
                
                # Extract details if found
                if response.status_code == 200 and 'userInfo' in res:
                    user_info = res['userInfo']['user']
                    stats = res['userInfo']['stats']
                    user_id = user_info.get('id')
                    
                    followers = stats.get('followerCount', 0)
                    total_likes = stats.get('heartCount', 0)
                    video_count = stats.get('videoCount', 0)
                    
                    profile_data = {
                        'username': user_info.get('uniqueId'),
                        'nickname': user_info.get('nickname'),
                        'user_id': user_id,
                        'created_at': get_creation_date(user_id) if user_id else "N/A",
                        'region': user_info.get('region', 'Unknown'),
                        'signature': user_info.get('signature', 'No bio provided'),
                        'verified': user_info.get('verified', False),
                        'followers': f"{followers:,}",
                        'following': f"{stats.get('followingCount', 0):,}",
                        'hearts': f"{total_likes:,}",
                        'videos': f"{video_count:,}",
                        'avatar': user_info.get('avatarLarger')
                    }
                else:
                    error = "User not found or account is private."
            except Exception as e:
                error = f"Error: {str(e)}"
                
    return render_template('index.html', data=profile_data, error=error)

if __name__ == '__main__':
    app.run(debug=True)

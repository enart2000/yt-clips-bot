import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot działa 24/7!"

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
PLAYLIST_ID = "PLay5QSQwkdl4"

def check_new_clips():
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={PLAYLIST_ID}&maxResults=1&key={YOUTUBE_API_KEY}"
    try:
        res = requests.get(url).json()
        
        if "error" in res:
            print(f"[!] Błąd YouTube API: {res['error']['message']}")
            return

        if "items" in res and res["items"]:
            latest_video = res["items"][0]["snippet"]
            video_id = latest_video["resourceId"]["videoId"]
            title = latest_video.get("title", "Nowy film")
            video_url = f"https://youtu.be/{video_id}"
            
            print(f"[Odebrano z YT] Najnowszy film w API: '{title}' (ID: {video_id})")
            
            last_id = ""
            if os.path.exists("last_id.txt"):
                with open("last_id.txt", "r") as f:
                    last_id = f.read().strip()
                    
            if video_id != last_id:
                print(f"[+] Nowy klip wykryty! Wysyłam na Discorda: {video_url}")
                webhook_res = requests.post(WEBHOOK_URL, json={"content": f"{video_url}"})
                print(f"[+] Status Discord Webhooka: {webhook_res.status_code}")
                
                with open("last_id.txt", "w") as f:
                    f.write(video_id)
            else:
                print(f"[-] Film '{title}' jest już zapisany jako wysłany.")
        else:
            print("[-] Brak filmów w playliście / playlista pusta.")
    except Exception as e:
        print(f"[!] Wyjątek w kodzie: {e}")

def loop():
    print("🚀 Bot startuje...")
    while True:
        check_new_clips()
        time.sleep(60)

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

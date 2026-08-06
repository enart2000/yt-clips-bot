import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot działa 24/7!"

PLAYLISTS = [
    {"name": "petarda", "id": "PLK9pErdOuahs", "file": "last_id_1.txt"},
    {"name": "mati", "id": "PLRbpSD4BjGPw", "file": "last_id_2.txt"},
    {"name": "enart", "id": "PLJ77qM8QV3tQ", "file": "last_id_3.txt"},
]

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def check_playlist(player_name, playlist_id, storage_file):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=1&key={YOUTUBE_API_KEY}"
    try:
        res = requests.get(url).json()
        
        if "error" in res:
            print(f"[!] Błąd YouTube API dla {player_name}: {res['error']['message']}")
            return

        if "items" in res and res["items"]:
            latest_video = res["items"][0]["snippet"]
            video_id = latest_video["resourceId"]["videoId"]
            title = latest_video.get("title", "Nowy klip")
            video_url = f"https://youtu.be/{video_id}"
            
            last_id = ""
            if os.path.exists(storage_file):
                with open(storage_file, "r") as f:
                    last_id = f.read().strip()
                    
            if video_id != last_id:
                print(f"[+] Nowy klip od {player_name}! Wysyłam na Discorda: {video_url}")
                
                message = f"**{player_name}** dodał nowe vidijo!\n{video_url}"
                
                webhook_res = requests.post(WEBHOOK_URL, json={"content": message})
                print(f"[+] Status Discord Webhooka ({player_name}): {webhook_res.status_code}")
                
                with open(storage_file, "w") as f:
                    f.write(video_id)
            else:
                print(f"[-] Baza aktualna dla {player_name} ('{title}')")
        else:
            print(f"[-] Playlista gracza {player_name} jest pusta.")
    except Exception as e:
        print(f"[!] Wyjątek u gracza {player_name}: {e}")

def check_all_clips():
    for player in PLAYLISTS:
        check_playlist(player["name"], player["id"], player["file"])

def loop():
    print("🚀 Bot startuje (obsługa 3 playlist)...")
    while True:
        check_all_clips()
        time.sleep(60)

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

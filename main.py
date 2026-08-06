import os
import requests

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
PLAYLIST_ID = "UUmAle3PfyFItqxLjlbTev-w"

def check_new_clips():
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={PLAYLIST_ID}&maxResults=1&key={YOUTUBE_API_KEY}"
    res = requests.get(url).json()
    
    if "items" in res and res["items"]:
        latest_video = res["items"][0]["snippet"]
        video_id = latest_video["resourceId"]["videoId"]
        video_url = f"https://youtu.be/{video_id}"
        
        last_id = ""
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r") as f:
                last_id = f.read().strip()
                
        if video_id != last_id:
            print(f"Znaleziono nowy klip: {video_url}")
            requests.post(WEBHOOK_URL, json={"content": f"{video_url}"})
            with open("last_id.txt", "w") as f:
                f.write(video_id)
        else:
            print("Brak nowych klipów.")

if __name__ == "__main__":
    check_new_clips()

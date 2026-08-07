import os
import time
import requests

PLAYLISTS = [
    {"name": "petarda", "id": "PLK9pErdOuahs", "file": "sent_ids_1.txt"},
    {"name": "mati",    "id": "PLRbpSD4BjGPw", "file": "sent_ids_2.txt"},
    {"name": "enart",   "id": "PLJ77qM8QV3tQ", "file": "sent_ids_3.txt"},
]

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def load_sent_ids(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return None

def save_sent_ids_bulk(file_path, video_ids):
    with open(file_path, "w") as f:
        for vid in video_ids:
            f.write(f"{vid}\n")

def save_sent_id(file_path, video_id):
    with open(file_path, "a") as f:
        f.write(f"{video_id}\n")

def send_to_discord(message, video_url):
    if not WEBHOOK_URL:
        print("[!] BŁĄD: Zmienna DISCORD_WEBHOOK nie jest ustawiona!")
        return False
        
    attempt = 1
    while True:
        try:
            response = requests.post(WEBHOOK_URL, json={"content": message})
            
            if response.status_code in [200, 204]:
                print(f"[+] Discord przyjął wiadomość (Status {response.status_code})")
                return True
            elif response.status_code == 429:
                data = response.json()
                retry_after = data.get("retry_after", 5)
                print(f"[⏳] KLIP OCZEKUJE NA WYSŁANIE ({video_url}) - Discord Rate Limit (429)! Czekam {retry_after} sek... (Próba #{attempt})")
                time.sleep(retry_after)
            else:
                print(f"[⏳] KLIP OCZEKUJE NA WYSŁANIE ({video_url}) - Błąd Discorda (Status {response.status_code}). Ponawiam za 5 sek... (Próba #{attempt})")
                time.sleep(5)
        except Exception as e:
            print(f"[⏳] KLIP OCZEKUJE NA WYSŁANIE ({video_url}) - Wyjątek połączenia: {e}. Ponawiam za 5 sek... (Próba #{attempt})")
            time.sleep(5)
            
        attempt += 1

def check_playlist(player_name, playlist_id, storage_file):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"
    try:
        res = requests.get(url).json()
        
        if "error" in res:
            print(f"[!] Błąd YouTube API dla {player_name}: {res['error']['message']}")
            return

        if "items" in res and res["items"]:
            latest_title = res["items"][0]["snippet"].get("title", "Brak tytułu")
            print(f"[*] API pobrało dla {player_name} ({len(res['items'])} filmów). Najnowszy na liście: '{latest_title}'")

            sent_ids = load_sent_ids(storage_file)
            current_video_ids = []

            for item in res["items"]:
                snippet = item["snippet"]
                title = snippet.get("title", "Nowy klip")
                if title not in ["Deleted video", "Private video"]:
                    current_video_ids.append(snippet["resourceId"]["videoId"])

            if sent_ids is None:
                print(f"[*] Inicjalizacja dla {player_name}. Zapisuję {len(current_video_ids)} pozycji.")
                save_sent_ids_bulk(storage_file, current_video_ids)
                return

            items = list(reversed(res["items"]))
            new_found = False

            for item in items:
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]
                title = snippet.get("title", "Nowy klip")

                if title in ["Deleted video", "Private video"]:
                    continue

                if video_id not in sent_ids:
                    new_found = True
                    video_url = f"https://youtu.be/{video_id}"
                    print(f"[+] Nowy klip od {player_name}! Próba wysyłki: {video_url}")
                    
                    message = f"**{player_name}** dodał nowe vidijo!\n{video_url}"
                    
                    if send_to_discord(message, video_url):
                        save_sent_id(storage_file, video_id)
                        sent_ids.add(video_id)
                    
                    time.sleep(1)

            if not new_found:
                print(f"[-] Brak nowych filmów u {player_name}.")
        else:
            print(f"[-] Playlista gracza {player_name} jest pusta.")
    except Exception as e:
        print(f"[!] Wyjątek u gracza {player_name}: {e}")

def check_all_clips():
    for player in PLAYLISTS:
        check_playlist(player["name"], player["id"], player["file"])

if __name__ == "__main__":
    print("🚀 Bot startuje na serwerze dedykowanym...")
    while True:
        check_all_clips()
        time.sleep(30)

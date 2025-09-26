import os
import sys
import yt_dlp
import vlc
import time

CACHE_DIR = "songs"
os.makedirs(CACHE_DIR, exist_ok=True)


def cached_filename(artist: str, title: str) -> str:
    """Return expected cache filename (safe string)."""
    safe_name = f"{artist}_{title}".replace(" ", "_")
    return os.path.join(CACHE_DIR, safe_name)


def download_song(query: str, base_path: str) -> str:
    """
    Download YouTube audio and return final MP3 path.
    base_path should not have an extension.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "outtmpl": base_path + '.m4a',  # no extension, let postprocessor handle it
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        # The postprocessor changes extension to .mp3
        m4a_file = ydl.prepare_filename(info)
        m4a_file = os.path.splitext(m4a_file)[0] + ".m4a"
        return m4a_file


def play_song(artist: str, title: str) -> None:
    query = f"{artist} {title}"
    base_path = cached_filename(artist, title)
    mp3_file = base_path + ".mp3"

    if os.path.exists(mp3_file):
        print(f"[INFO] Using cached version: {mp3_file}")
    else:
        print(f"[INFO] Downloading: {query}")
        try:
            mp3_file = download_song(query, base_path)
        except Exception as e:
            print(f"[ERROR] Failed to download song: {e}")
            return

    print(f"[INFO] Playing {mp3_file}")
    try:
        player = vlc.MediaPlayer(mp3_file)
        player.play()
        while True:
            state = player.get_state()
            if state in (vlc.State.Ended, vlc.State.Error):
                break
            time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Could not play song: {e}")


def main():
    if len(sys.argv) < 3:
        print("Usage: play-song <artist> <song>")
        sys.exit(1)

    artist = sys.argv[1]
    title = " ".join(sys.argv[2:])
    play_song(artist, title)


if __name__ == "__main__":
    main()

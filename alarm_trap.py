# Run this script to have a random song that charted between 1985-2005 play a la the alarm trap from DCC
import billboard
from speak import speak
from random import randint
from time import time
from ytdl import play_song
if __name__ == "__main__":

    year = randint(1985, 2005)
    spot = randint(0, 19)
    start = time()
    top20_list = billboard.get_top20(year, force_refresh=False)
    if not top20_list:
        print(f'no songs returned for {year}')
        exit(0)
    if len(top20_list) < 20:
        spot = randint(0, len(top20_list))
    rank, title, artist = top20_list[spot]
    speak(f"peaking at number {rank} in {year}, it's {title} by {artist}!")
    play_song(artist, title)
    print(f"[Done in {time() - start:.2f}s]")
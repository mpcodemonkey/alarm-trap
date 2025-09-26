"""
billboard_top20.py
Fetch Billboard Year-End Hot 100 Top 20 songs for a given year.

Features:
- Caching (JSON file)
- Error handling
- Fallback web scraping if billboard.py fails
"""

import os
import json
import time
from typing import List, Tuple

import urllib.request
import urllib.error
from bs4 import BeautifulSoup

try:
    import billboard
except ImportError:
    billboard = None

CACHE_FILE = "billboard_cache.json"


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def fetch_with_billboard(year: int) -> List[Tuple[int, str, str]]:
    """Try fetching using the billboard.py library"""
    if billboard is None:
        return []
    try:
        chart = billboard.ChartData("hot-100", year=str(year))
        results = []
        for i, entry in enumerate(chart):
            if i >= 20:
                break
            results.append((i + 1, entry.title, entry.artist))
        return results
    except Exception as e:
        print(f"[WARN] billboard.py failed: {e}")
        return []


def fetch_with_scraping(year: int) -> List[Tuple[int, str, str]]:
    """Fallback: scrape Billboard year-end Hot 100 for given year"""
    url = f"https://www.billboard.com/charts/year-end/{year}/hot-100-songs/"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        print(f"[ERROR] Failed to fetch Billboard page: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")

    results = []
    entries = soup.select("li.o-chart-results-list__item")
    if not entries:
        # Billboard often uses div containers instead
        entries = soup.select("div.o-chart-results-list-row")

    rank = 1
    for entry in entries:
        title_el = entry.select_one("h3")
        artist_el = entry.select_one("span.c-label")
        if not title_el or not artist_el:
            continue
        title = title_el.get_text(strip=True)
        artist = artist_el.get_text(strip=True)
        results.append((rank, title, artist))
        rank += 1
        if rank > 20:
            break
    return results


def get_top20(year: int, force_refresh: bool = False) -> List[Tuple[int, str, str]]:
    """Get top 20 songs for given year with caching & fallback"""
    cache = load_cache()
    key = str(year)

    if not force_refresh and key in cache:
        return cache[key]

    # Try primary method
    results = fetch_with_billboard(year)
    if not results:
        print("[INFO] Falling back to web scraping...")
        results = fetch_with_scraping(year)

    if results:
        cache[key] = results
        save_cache(cache)
    return results


def print_top20(year: int, force_refresh: bool = False):
    results = get_top20(year, force_refresh=force_refresh)
    if not results:
        print(f"No data found for {year}.")
        return
    print(f"Top 20 Billboard Year-End Hot 100 for {year}")
    for rank, title, artist in results:
        print(f"{rank}. '{title}' — {artist}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Billboard Top 20 songs for a year.")
    parser.add_argument("year", type=int, help="Year to fetch")
    parser.add_argument("--refresh", action="store_true", help="Force refresh (ignore cache)")
    args = parser.parse_args()

    start = time.time()
    print_top20(args.year, force_refresh=args.refresh)
    print(f"[Done in {time.time() - start:.2f}s]")

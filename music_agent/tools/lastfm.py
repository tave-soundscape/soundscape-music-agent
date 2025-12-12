import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Last.fm API를 호출하여 특정 태그의 인기 곡을 가져오는 tool.
def call_lastfm_api(tag: str, limit: int = 50) -> List[Dict[str, Any]]:

    if not LASTFM_API_KEY:
        print(" 에러: LASTFM_API_KEY가 없습니다.")
        return []

    params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        raw_tracks = data.get("tracks", {}).get("track", [])
        cleaned_tracks = []

        for track in raw_tracks:
            artist_info = track.get("artist")
            artist_name = artist_info.get("name") if isinstance(artist_info, dict) else str(artist_info)

            cleaned_tracks.append({
                "title": track.get("name"),
                "artist": artist_name,
                "url": track.get("url"),
            })

        return cleaned_tracks

    except Exception as e:
        print(f" Last.fm API 호출 실패 (Tag: {tag}): {e}")
        return []
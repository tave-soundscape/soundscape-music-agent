import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict
from music_agent.state import Track, Artist
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from typing import Annotated
from concurrent.futures import ThreadPoolExecutor
from music_agent import config
from music_agent.constants import (
    PLAYLIST_SEARCH_LIMIT,
    MAX_TRACKS_PER_PLAYLIST,
    ARTIST_SEARCH_LIMIT,
    DEFAULT_MARKET
)
from music_agent.spotify_helpers import create_track_from_spotify_data

# Spotify API 호출용 전역 스레드풀
# 동시 접속자 10명 기준, 노드당 최대 3-9개 병렬 호출 예상
# 50개로 충분한 여유 확보 (외부 API I/O 대기용이므로 CPU 부담 없음)
spotify_thread_pool = ThreadPoolExecutor(max_workers=50, thread_name_prefix="spotify-api-executor")

auth_manager = SpotifyClientCredentials(
    client_id=config.SPOTIPY_CLIENT_ID,
    client_secret=config.SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)

def search_playlists(query: str, market: str = DEFAULT_MARKET, limit: int = PLAYLIST_SEARCH_LIMIT) -> List[Dict]:
    results = sp.search(q=query, type="playlist", limit=limit, market=market)
    items = results.get("playlists", {}).get("items", [])
    return [{
            "name": item.get("name"),
            "id": item.get("id"),
            "spotify_url": item.get("external_urls", {}).get("spotify")
            } for item in items if item is not None]

def search_artist(query: str):
    result = sp.search(q=query, type="artist", limit=ARTIST_SEARCH_LIMIT, market=DEFAULT_MARKET)
    item = result.get("artists", {}).get("items", [])[0]
    return {
        "genres": item.get("genres"),
        "name": item.get("name"),
        "popularity": item.get("popularity"),
    }

def collect_playlist_tracks(playlist_id: str) -> list[Track]:
    results = sp.playlist(
        playlist_id=playlist_id,
        market=DEFAULT_MARKET,
        fields="tracks.items(track(id,name,duration_ms,uri,external_urls,album(id,name,release_date,images,uri,),artists(id,name)))"
    )
    items = results.get("tracks", {}).get("items", [])
    return [
        create_track_from_spotify_data(track)
        for item in items
        if (track := item.get("track"))
    ]

@tool
def make_playlist(
        query: str,
        tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    query 값으로 스포티파이의 플레이리스트를 검색하고 검색된 곡들을 context_candidates에 추가합니다.
    """
    count = 0
    seen_id = set()
    res = []
    res_playlists = search_playlists(query)

    # 병렬로 플레이리스트 트랙 수집
    def fetch_playlist_tracks(pl):
        try:
            return collect_playlist_tracks(pl.get("id"))
        except Exception:
            return []

    futures = [spotify_thread_pool.submit(fetch_playlist_tracks, pl) for pl in res_playlists]

    for future in futures:
        tracks = future.result()
        for track in tracks:
            if track.tid not in seen_id:
                res.append(track)
                seen_id.add(track.tid)
                count += 1
        if count >= MAX_TRACKS_PER_PLAYLIST:
            break

    return Command(
        update={
            "context_candidates": res,
            "messages": [
                ToolMessage(
                    content=f"성공적으로 '{query}'에 대한 {len(res)}곡의 후보를 찾았습니다.",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

def search_artist_tracks_by_context(artist_name: str, location: str, goal: str, limit: int = 5) -> List[Track]:
    """가수명과 현재 상황(위치, 목표)을 조합하여 최적의 트랙을 검색합니다."""
    query = f"{artist_name}"

    results = sp.search(q=query, type="track", limit=limit, market=DEFAULT_MARKET)
    items = results.get("tracks", {}).get("items", [])

    return [create_track_from_spotify_data(t) for t in items]

if __name__ == "__main__":
    res =  search_artist_tracks_by_context("結束バンド", "library", "active")
    print(res)
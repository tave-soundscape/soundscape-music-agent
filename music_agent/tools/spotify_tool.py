import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict
from music_agent.state import Track, Artist
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from typing import Annotated
from music_agent import config

auth_manager = SpotifyClientCredentials(
    client_id=config.SPOTIPY_CLIENT_ID,
    client_secret=config.SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)

def search_playlists(query: str, market: str = "KR", limit: int = 3) -> List[Dict]:
    results = sp.search(q=query,type="playlist",limit=limit,market=market)
    items = results.get("playlists", {}).get("items", [])
    return [{
            "name": item.get("name"),
            "id": item.get("id"),
            "spotify_url": item.get("external_urls", {}).get("spotify")
            }for item in items if item is not None ]

def search_artist(query: str):
    result = sp.search(q=query, type="artist", limit=1, market="KR")
    item = result.get("artists", {}).get("items", [])[0]
    return {
        "genres": item.get("genres"),
        "name": item.get("name"),
        "popularity": item.get("popularity"),
    }

def collect_playlist_tracks(playlist_id: str) -> list[Track]:
    results = sp.playlist(playlist_id=playlist_id, market="KR",
                        fields="tracks.items(track(id,name,duration_ms,uri,external_urls,album(id,name,release_date,images,uri,),artists(id,name)))")
    items = results.get("tracks", {}).get("items", [])
    return [
    Track(
        tid=track["id"], tn=track["name"], tu=track["uri"],
        turl=(track.get("external_urls") or {}).get("spotify"),
        ms=track["duration_ms"],
        ai=track["album"]["id"], an=track["album"]["name"], au=track["album"]["uri"],
        img=track["album"]["images"][0].get("url") if track["album"]["images"] else None,
        at=[Artist(atid=a["id"], atn=a["name"]) for a in track["artists"]]
    ) for item in items if (track := item.get("track"))
]

@tool
def make_playlist(
        query: str,
        tool_call_id: Annotated[str, InjectedToolCallId]  # 자동으로 ID를 주입.
) -> Command:
    """
    query 값으로 스포티파이의 플레이리스트를 검색하고 검색된 곡들을 context_candidates에 추가합니다.
    """
    count = 0
    seen_id = set()
    res = []
    res_playlists = search_playlists(query)

    for pl in res_playlists:
        tracks = collect_playlist_tracks(pl.get("id"))
        for track in tracks:
            if track.tid not in seen_id:
                res.append(track)
                seen_id.add(track.tid)
                count += 1
        if count >= 150:
            break

    return Command(
        update={
            "context_candidates": res,
            "messages": [
                ToolMessage(
                    content=f"성공적으로 '{query}'에 대한 {len(res)}곡의 후보를 찾았습니다.",
                    tool_call_id=tool_call_id  # 이제 정의된 ID를 사용합니다.
                )
            ]
        }
    )

def get_artist_top_tracks(artist_name: str):
    """아티스트 이름을 검색하여 해당 아티스트의 Top Tracks를 가져옵니다."""
    search_res = sp.search(q=artist_name, limit=1, type="artist", market="KR")
    items = search_res.get("artists", {}).get("items", [])
    if not items:
        return []

    artist_id = items[0]["id"]

    top_tracks_res = sp.artist_top_tracks(artist_id, country="KR")
    tracks_data = top_tracks_res.get("tracks", [])[:10]

    return [
        Track(
            tid=t["id"], tn=t["name"], tu=t["uri"],
            turl=(t.get("external_urls") or {}).get("spotify"),
            ms=t["duration_ms"],
            ai=t["album"]["id"], an=t["album"]["name"], au=t["album"]["uri"],
            img=t["album"]["images"][0].get("url") if t["album"]["images"] else None,
            at=[Artist(atid=a["id"], atn=a["name"]) for a in t["artists"]]
        ) for t in tracks_data
    ]


def search_artist_tracks_by_context(artist_name: str, location: str, goal: str, limit: int = 5) -> List[Track]:
    """가수명과 현재 상황(위치, 목표)을 조합하여 최적의 트랙을 검색합니다."""
    # query = f"{artist_name} {location} {goal}"
    query = f"{artist_name} {location}"

    results = sp.search(q=query, type="track", limit=limit, market="KR")
    items = results.get("tracks", {}).get("items", [])

    return [
        Track(
            tid=t["id"], tn=t["name"], tu=t["uri"],
            turl=(t.get("external_urls") or {}).get("spotify"),
            ms=t["duration_ms"],
            ai=t["album"]["id"], an=t["album"]["name"], au=t["album"]["uri"],
            img=t["album"]["images"][0].get("url") if t["album"]["images"] else None,
            at=[Artist(atid=a["id"], atn=a["name"]) for a in t["artists"]]
        ) for t in items
    ]

if __name__ == "__main__":
    res =  search_artist_tracks_by_context("結束バンド", "library", "active")
    print(res)
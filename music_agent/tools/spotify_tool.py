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
        tool_call_id: Annotated[str, InjectedToolCallId]  # 자동으로 ID를 주입받습니다.
) -> Command:
    """
    query 값으로 스포티파이의 플레이리스트를 검색하고 검색된 곡들을 candidate_tracks에 추가합니다.
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
            "candidate_tracks": res,
            "messages": [
                ToolMessage(
                    content=f"성공적으로 '{query}'에 대한 {len(res)}곡의 후보를 찾았습니다.",
                    tool_call_id=tool_call_id  # 이제 정의된 ID를 사용합니다.
                )
            ]
        }
    )
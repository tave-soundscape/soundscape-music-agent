from music_agent.state import Track, Artist
from typing import Dict, Any, List


#Spotify API 응답을 Track 객체로 변환하는 헬퍼 함수
def create_track_from_spotify_data(track_data: Dict[str, Any]) -> Track:
    """
    Spotify API 응답 데이터를 Track 객체로 변환

    Args:
        track_data: Spotify API의 track 객체

    Returns:
        Track: 변환된 Track 객체
    """
    return Track(
        tid=track_data["id"],
        tn=track_data["name"],
        tu=track_data["uri"],
        turl=(track_data.get("external_urls") or {}).get("spotify"),
        ms=track_data["duration_ms"],
        ai=track_data["album"]["id"],
        an=track_data["album"]["name"],
        au=track_data["album"]["uri"],
        img=track_data["album"]["images"][0].get("url") if track_data["album"]["images"] else None,
        at=[Artist(atid=a["id"], atn=a["name"]) for a in track_data["artists"]],
        rd=track_data["album"]["release_date"]
    )


def is_track_allowed(track: Track, exclude_keywords: List[str], exclude_artists: List[str]) -> bool:
    """
    트랙이 필터링 기준을 통과하는지 확인

    Args:
        track: 검사할 Track 객체
        exclude_keywords: 제목에서 제외할 키워드 목록
        exclude_artists: 제외할 아티스트 이름 목록

    Returns:
        bool: True이면 허용, False이면 필터링
    """
    title_lower = track.tn.lower()

    # 제목에 금지 키워드 확인
    has_forbidden_title = any(word in title_lower for word in exclude_keywords)
    if has_forbidden_title:
        return False

    # 아티스트에 금지된 이름 확인
    has_forbidden_artist = any(artist.atn == name for artist in track.at for name in exclude_artists)
    if has_forbidden_artist:
        return False

    return True


def get_unique_tracks(tracks: List[Track]) -> List[Track]:
    """
    트랙 리스트에서 중복 제거 (tid 기준)

    Args:
        tracks: Track 리스트

    Returns:
        List[Track]: 중복 제거된 Track 리스트
    """
    unique_dict = {t.tid: t for t in tracks}
    return list(unique_dict.values())



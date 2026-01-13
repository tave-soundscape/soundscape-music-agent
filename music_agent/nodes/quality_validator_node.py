from music_agent.state import AgentState
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Tuple
from music_agent.constants import (
    MAX_ITERATION_COUNT,
    MAX_ARTIST_TRACK_COUNT,
    MIN_RECENT_TRACK_RATIO,
    MIN_GENRE_MATCH_RATIO,
    RECENT_TRACK_DAYS
)
from music_agent.utils import parse_release_date, calculate_percentage


def _validate_preferred_artists(final_tracks, preferred_artists) -> Tuple[Dict[str, int], bool, List[str]]:
    """
    선호 아티스트 매칭 검증

    Returns:
        Tuple[Dict, bool, List]: (아티스트별 곡 수, 추가 필요 여부, 부족한 아티스트 목록)
    """
    preferred_artist_count = {artist: 0 for artist in preferred_artists}

    for track in final_tracks:
        for artist in track.at:
            artist_name = artist.atn
            # 선호 아티스트 목록에 있는지 확인
            for pref_artist in preferred_artists:
                if pref_artist.lower() in artist_name.lower() or artist_name.lower() in pref_artist.lower():
                    preferred_artist_count[pref_artist] += 1

    # 각 아티스트별 최소 1곡씩 있어야 함
    missing_artists = [name for name, count in preferred_artist_count.items() if count == 0]
    needs_more = bool(missing_artists and len(preferred_artists) > 0)

    return preferred_artist_count, needs_more, missing_artists


def _validate_recent_tracks(final_tracks) -> Tuple[float, int, bool]:
    """
    신곡 비율 검증 (최근 1년)

    Returns:
        Tuple[float, int, bool]: (신곡 비율, 신곡 개수, 추가 필요 여부)
    """
    current_date = datetime(2026, 1, 13)
    one_year_ago = current_date - timedelta(days=RECENT_TRACK_DAYS)

    recent_tracks = []
    for track in final_tracks:
        release_date = parse_release_date(track.rd)
        if release_date and release_date >= one_year_ago:
            recent_tracks.append(track)

    recent_track_ratio = calculate_percentage(len(recent_tracks), len(final_tracks))
    recent_track_count = len(recent_tracks)
    needs_recent = recent_track_ratio < MIN_RECENT_TRACK_RATIO

    return recent_track_ratio, recent_track_count, needs_recent


def _validate_artist_diversity(final_tracks) -> Tuple[bool, int, Tuple]:
    """
    아티스트 다양성 검증

    Returns:
        Tuple[bool, int, Tuple]: (다양성 OK 여부, 최대 곡 수, 가장 많은 아티스트)
    """
    artist_counter = Counter()
    for track in final_tracks:
        for artist in track.at:
            artist_counter[artist.atn] += 1

    max_count = max(artist_counter.values()) if artist_counter else 0
    artist_diversity_ok = max_count <= MAX_ARTIST_TRACK_COUNT
    most_common = artist_counter.most_common(1)[0] if artist_counter else None

    return artist_diversity_ok, max_count, most_common


def _validate_genre_match(final_tracks, user_persona) -> Tuple[float, List[str], bool]:
    """
    장르 일치도 검증

    Returns:
        Tuple[float, List, bool]: (장르 일치율, 부족한 장르 목록, 보완 필요 여부)
    """
    preferred_genres = set(user_persona.get("preferred_genres", []))

    # final_tracks의 아티스트들의 장르 수집
    final_genres = set()
    artist_details = user_persona.get("artists_details", [])

    # 각 트랙의 아티스트 ID로 장르 매핑
    for track in final_tracks:
        for artist in track.at:
            # artist_details에서 해당 아티스트의 장르 찾기
            for detail in artist_details:
                if detail.get("name", "").lower() == artist.atn.lower():
                    final_genres.update(detail.get("genres", []))

    # 교집합 계산
    if preferred_genres and final_genres:
        genre_intersection = preferred_genres.intersection(final_genres)
        genre_match_ratio = len(genre_intersection) / len(preferred_genres)
    else:
        genre_match_ratio = 1.0  # 선호 장르가 없으면 통과

    missing_genres = list(preferred_genres - final_genres)
    needs_enhancement = genre_match_ratio < MIN_GENRE_MATCH_RATIO and bool(preferred_genres)

    return genre_match_ratio, missing_genres, needs_enhancement


def quality_validator_node(state: AgentState) -> dict:
    """
    최종 선곡 결과를 4가지 기준으로 검증:
    1. 선호 아티스트 매칭
    2. 신곡 비율 (최근 1년)
    3. 아티스트 다양성
    4. 장르 일치도
    """
    # 반복 횟수 증가
    iteration_count = state.get("iteration_count", 0) + 1

    # 최대 반복 횟수 도달 시 무조건 통과
    if iteration_count > MAX_ITERATION_COUNT:
        return {
            "iteration_count": iteration_count,
            "validation_feedback": {"forced_pass": True},
            "needs_more_preference": False,
            "needs_recent_tracks": False
        }

    final_tracks = state.get("final_tracks", [])
    preferred_artists = state.get("user_context", {}).get("preferred_artists", [])
    user_persona = state.get("user_persona", {})

    validation_feedback = {}
    needs_more_preference = False
    needs_recent_tracks = False

    # ===== 검증 1: 선호 아티스트 매칭 =====
    artist_count, needs_more_pref, missing = _validate_preferred_artists(final_tracks, preferred_artists)
    validation_feedback["preferred_artist_count"] = artist_count
    if missing:
        validation_feedback["missing_artists"] = missing
    needs_more_preference = needs_more_pref

    # ===== 검증 2: 신곡 비율 =====
    recent_ratio, recent_count, needs_recent = _validate_recent_tracks(final_tracks)
    validation_feedback["recent_track_ratio"] = recent_ratio
    validation_feedback["recent_track_count"] = recent_count
    needs_recent_tracks = needs_recent

    # ===== 검증 3: 아티스트 다양성 =====
    diversity_ok, max_count, most_common = _validate_artist_diversity(final_tracks)
    validation_feedback["artist_diversity_ok"] = diversity_ok
    validation_feedback["max_artist_count"] = max_count
    validation_feedback["most_common_artist"] = most_common

    # ===== 검증 4: 장르 일치도 =====
    genre_ratio, missing_genres, needs_genre = _validate_genre_match(final_tracks, user_persona)
    validation_feedback["genre_match_ratio"] = genre_ratio
    validation_feedback["missing_genres"] = missing_genres

    # 장르 불일치 시에도 needs_recent_tracks로 context_agent 트리거
    if needs_genre:
        needs_recent_tracks = True

    return {
        "iteration_count": iteration_count,
        "validation_feedback": validation_feedback,
        "needs_more_preference": needs_more_preference,
        "needs_recent_tracks": needs_recent_tracks
    }


def decide_next_step(state: AgentState) -> str:
    """
    검증 결과에 따라 다음 노드를 결정하는 라우팅 함수
    """
    iteration_count = state.get("iteration_count", 0)
    validation_feedback = state.get("validation_feedback", {})

    # 최대 반복 도달 시 무조건 진행
    if iteration_count > MAX_ITERATION_COUNT:
        return "proceed"

    # 1순위: 아티스트 다양성 체크
    if not validation_feedback.get("artist_diversity_ok", True):
        return "reselect"

    # 2순위: 선호 아티스트 부족
    if state.get("needs_more_preference", False):
        return "enhance_preference"

    # 3순위: 신곡 부족 또는 장르 불일치
    if state.get("needs_recent_tracks", False):
        return "enhance_context"

    # 모두 통과
    return "proceed"


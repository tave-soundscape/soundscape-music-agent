from music_agent.state import AgentState
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Tuple
from music_agent.constants import (
    MAX_ITERATION_COUNT,
    MAX_ARTIST_TRACK_COUNT,
    MIN_RECENT_TRACK_RATIO,
    RECENT_TRACK_DAYS,
    MIN_PREFERRED_ARTIST_COUNT
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

    # 3명 중 2명 이상만 있으면 통과
    missing_artists = [name for name, count in preferred_artist_count.items() if count == 0]
    matched_count = len(preferred_artists) - len(missing_artists)
    needs_more = matched_count < MIN_PREFERRED_ARTIST_COUNT and len(preferred_artists) > 0

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



def quality_validator_node(state: AgentState) -> dict:
    """
    최종 선곡 결과를 3가지 기준으로 검증:
    1. 선호 아티스트 매칭 (3명 중 2명 이상)
    2. 신곡 비율 (최근 1년, 20% 이상)
    3. 아티스트 다양성 (한 아티스트당 최대 4곡)
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


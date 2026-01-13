from music_agent.state import AgentState
import random
from music_agent.constants import (
    TARGET_FINAL_TRACK_COUNT,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_ARTIST_NAMES
)
from music_agent.spotify_helpers import is_track_allowed, get_unique_tracks


def filter_remix_tracks_node(state: AgentState):
    """
    리믹스/리마스터 트랙 필터링 노드

    3단계 처리:
    1. 기존 후보 필터링 (제목 키워드 및 아티스트 체크)
    2. 20곡 미만 시 추가 후보에서 필터링하여 추가
    3. 20곡 초과 시 랜덤 샘플링으로 정확히 20곡 맞춤

    제외 조건:
    - 제목에 "remix", "remaster", "mix", "master", "live" 포함
    - 특정 아티스트 ("한의 노래" 등)

    Args:
        state: AgentState 객체

    Returns:
        dict: final_tracks (정확히 20곡)
    """
    candidates = state["final_tracks"]

    # 백업용 후보 저장 (필터링 후 부족할 경우 사용)
    all_context = state.get("context_candidates", [])
    all_preference = state.get("preference_candidates", [])

    filtered_tracks = []
    excluded_tracks = []

    # 1단계: 기존 후보 필터링
    for track in candidates:
        if is_track_allowed(track, EXCLUDE_TITLE_KEYWORDS, EXCLUDE_ARTIST_NAMES):
            filtered_tracks.append(track)
        else:
            excluded_tracks.append(track)

    # 2단계: 필터링 후 20곡 미만이면 추가
    if len(filtered_tracks) < TARGET_FINAL_TRACK_COUNT:
        needed = TARGET_FINAL_TRACK_COUNT - len(filtered_tracks)

        # 이미 선택되지 않은 후보들 중에서 선택
        filtered_ids = {t.tid for t in filtered_tracks}
        excluded_ids = {t.tid for t in excluded_tracks}

        remaining = [
            t for t in (all_context + all_preference)
            if t.tid not in filtered_ids and t.tid not in excluded_ids
        ]

        # 중복 제거
        remaining_list = get_unique_tracks(remaining)

        # 필터링 기준 적용하여 추가
        additional_tracks = []
        for track in remaining_list:
            if len(additional_tracks) >= needed:
                break

            if is_track_allowed(track, EXCLUDE_TITLE_KEYWORDS, EXCLUDE_ARTIST_NAMES):
                additional_tracks.append(track)

        filtered_tracks.extend(additional_tracks)

        # 그래도 부족하면 랜덤 샘플링 (필터링 무시)
        if len(filtered_tracks) < TARGET_FINAL_TRACK_COUNT and len(remaining_list) > 0:
            still_needed = TARGET_FINAL_TRACK_COUNT - len(filtered_tracks)
            additional = random.sample(
                remaining_list,
                min(still_needed, len(remaining_list))
            )
            filtered_tracks.extend(additional)

    # 3단계: 정확히 20곡으로 맞추기
    if len(filtered_tracks) > TARGET_FINAL_TRACK_COUNT:
        filtered_tracks = random.sample(filtered_tracks, TARGET_FINAL_TRACK_COUNT)

    return {"final_tracks": filtered_tracks}


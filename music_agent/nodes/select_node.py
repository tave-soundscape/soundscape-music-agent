import random
from music_agent.state import AgentState
from collections import Counter
from music_agent.constants import (
    SELECTION_BUFFER_COUNT,
    PREFERENCE_TRACK_COUNT,
    CONTEXT_TRACK_COUNT,
    MAX_ARTIST_TRACK_COUNT,
    TARGET_FINAL_TRACK_COUNT
)
from music_agent.spotify_helpers import get_unique_tracks


def selection_node(state: AgentState):
    """
    후보 트랙에서 최종 25곡을 선정하는 노드

    - 선호 아티스트 기반: 9곡
    - 상황 기반: 16곡
    - 총 25곡 선정 (필터링 여유분 고려)

    아티스트 다양성 검증 실패 시 중복 제거 로직 실행

    Args:
        state: AgentState 객체

    Returns:
        dict: final_tracks, context_candidates, preference_candidates
    """
    ctx_candidates = state.get("context_candidates", [])
    pref_candidates = state.get("preference_candidates", [])
    validation_feedback = state.get("validation_feedback", {})

    unique_ctx = get_unique_tracks(ctx_candidates)
    unique_pref = get_unique_tracks(pref_candidates)

    # 필터링을 고려하여 25곡 선정 (필터링 후 최소 20곡 보장)
    if len(unique_pref) <= PREFERENCE_TRACK_COUNT:
        selected_pref = unique_pref
    else:
        selected_pref = random.sample(unique_pref, PREFERENCE_TRACK_COUNT)

    needed_ctx_count = SELECTION_BUFFER_COUNT - len(selected_pref)

    if len(unique_ctx) <= needed_ctx_count:
        selected_ctx = unique_ctx
    else:
        selected_ctx = random.sample(unique_ctx, needed_ctx_count)

    final_selection = selected_pref + selected_ctx

    # 순환 그래프: 아티스트 다양성 검증 실패 시 중복 제거
    if not validation_feedback.get("artist_diversity_ok", True):
        final_selection = _remove_duplicate_artists(
            final_selection,
            unique_ctx,
            unique_pref
        )

    random.shuffle(final_selection)

    return {
        "final_tracks": final_selection,
        "context_candidates": [],
        "preference_candidates": []
    }


def _remove_duplicate_artists(tracks, unique_ctx, unique_pref):
    """
    아티스트 중복 제거 헬퍼 함수

    한 아티스트가 MAX_ARTIST_TRACK_COUNT(4곡)를 초과하면
    해당 아티스트의 곡을 4곡으로 제한하고 나머지를 다른 곡으로 대체

    Args:
        tracks: 검사할 트랙 리스트
        unique_ctx: 상황 기반 후보 트랙
        unique_pref: 선호 아티스트 기반 후보 트랙

    Returns:
        List[Track]: 중복 제거된 트랙 리스트
    """
    # 아티스트별 곡 수 카운트
    artist_counter = Counter()
    for track in tracks:
        for artist in track.at:
            artist_counter[artist.atn] += 1

    # 4곡 초과하는 아티스트 찾기
    over_limit_artists = [
        name for name, count in artist_counter.items()
        if count > MAX_ARTIST_TRACK_COUNT
    ]

    if not over_limit_artists:
        return tracks

    # 중복 제거 로직
    filtered_selection = []
    artist_count = Counter()

    for track in tracks:
        track_artists = [a.atn for a in track.at]
        should_include = True

        for artist_name in track_artists:
            if artist_name in over_limit_artists and artist_count[artist_name] >= MAX_ARTIST_TRACK_COUNT:
                should_include = False
                break

        if should_include:
            filtered_selection.append(track)
            for artist_name in track_artists:
                artist_count[artist_name] += 1

    # 부족한 곡은 후보에서 추가
    if len(filtered_selection) < TARGET_FINAL_TRACK_COUNT:
        remaining_candidates = [
            t for t in unique_ctx + unique_pref
            if t not in filtered_selection
        ]
        if remaining_candidates:
            needed = TARGET_FINAL_TRACK_COUNT - len(filtered_selection)
            additional = random.sample(
                remaining_candidates,
                min(needed, len(remaining_candidates))
            )
            filtered_selection.extend(additional)

    return filtered_selection


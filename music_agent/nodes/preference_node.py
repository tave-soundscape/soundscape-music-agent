from music_agent.tools.spotify_tool import search_artist, search_artist_tracks_by_context, spotify_thread_pool
from music_agent.llm import model
from music_agent.state import AgentState
from music_agent.constants import DEFAULT_TRACK_LIMIT, ENHANCED_TRACK_LIMIT


def preference_analyzer_node(state: AgentState):
    """
    선호 아티스트 분석 및 사용자 페르소나 생성 노드

    1. 선호 아티스트를 Spotify에서 검색
    2. 장르, 인기도 정보 수집
    3. LLM이 사용자 음악 취향을 한 문장으로 요약

    Args:
        state: AgentState 객체

    Returns:
        dict: user_persona (preferred_genres, average_popularity, taste_summary, artist_details)
    """
    artists = state["user_context"].get("preferred_artists", [])
    artist_details = []

    # 병렬로 아티스트 정보 검색
    def fetch_artist_info(name):
        try:
            return search_artist(name)
        except Exception:
            return None

    futures = [spotify_thread_pool.submit(fetch_artist_info, name) for name in artists]
    artist_details = [future.result() for future in futures if future.result() is not None]

    if not artist_details:
        return {
            "user_persona": {
                "preferred_genres": [],
                "average_popularity": 0,
                "taste_summary": "특별한 취향 정보가 없습니다. 현재 상황에 가장 적합한 대중적인 곡들로 추천해주세요.",
                "artist_details": []
            }
        }

    all_genres = []
    for d in artist_details:
        all_genres.extend(d.get('genres', []))

    unique_genres = list(set(all_genres))
    avg_pop = sum([d.get('popularity', 0) for d in artist_details]) / len(artist_details)

    prompt = f"""
    당신은 음악 평론가입니다. 아래 아티스트 정보를 바탕으로 이 사용자의 음악적 페르소나를 50자 이내의 한 문장으로 요약하세요.

    [데이터]
    - 선호 아티스트: {', '.join([d['name'] for d in artist_details])}
    - 관련 장르: {', '.join(unique_genres)}
    - 인기도 평균: {avg_pop:.1f}/100

    [가이드]
    - 인기도 70점 이상: "최신 트렌드와 대중적인 메인스트림 음악을 즐김"
    - 인기도 40점 이하: "자신만의 색깔이 뚜렷한 인디/마니아틱한 음악을 즐김"
    - 장르의 특징(예: 발라드면 '감성적', 락이면 '에너지')을 반드시 포함할 것.
    - 선호 하는 장르들도 포함할 것.
    """

    response = model.invoke(prompt)

    return {
        "user_persona": {
            "preferred_genres": unique_genres,
            "average_popularity": avg_pop,
            "taste_summary": response.content.strip(),
            "artist_details": artist_details
        }
    }

def preference_search_node(state: AgentState):
    """
    선호 아티스트 기반 트랙 검색 노드

    일반 모드: 모든 선호 아티스트를 각 10곡씩 검색
    순환 모드: 부족한 아티스트만 20곡씩 집중 검색

    Args:
        state: AgentState 객체

    Returns:
        dict: preference_candidates, search_query
    """
    preferred_artists = state["user_context"].get("preferred_artists", [])
    location = state["user_context"].get("location")
    goal = state["user_context"].get("goal")

    # 순환 그래프: 선호 아티스트 부족 시 limit 증가
    needs_more_preference = state.get("needs_more_preference", False)
    validation_feedback = state.get("validation_feedback", {})

    # 부족한 아티스트만 집중 검색
    missing_artists = validation_feedback.get("missing_artists", [])

    # 검색 대상 결정
    if needs_more_preference and missing_artists:
        # 부족한 아티스트만 검색 (limit 증가)
        search_artists = missing_artists
        limit_per_artist = ENHANCED_TRACK_LIMIT
    else:
        # 일반 검색 (모든 선호 아티스트)
        search_artists = preferred_artists
        limit_per_artist = DEFAULT_TRACK_LIMIT

    all_preference_tracks = []
    seen_ids = set()

    # 검색한 아티스트 쿼리 기록
    preference_queries = []

    # 병렬로 아티스트별 트랙 검색
    location_value = location.value if hasattr(location, 'value') else location
    goal_value = goal.value if hasattr(goal, 'value') else goal

    def fetch_artist_tracks(artist_name):
        try:
            return artist_name, search_artist_tracks_by_context(
                artist_name=artist_name,
                location=location_value,
                goal=goal_value,
                limit=limit_per_artist
            )
        except Exception:
            return artist_name, []

    futures = [spotify_thread_pool.submit(fetch_artist_tracks, name) for name in search_artists]

    for future in futures:
        artist_name, tracks = future.result()
        for track in tracks:
            if track.tid not in seen_ids:
                all_preference_tracks.append(track)
                seen_ids.add(track.tid)

        # 검색한 아티스트를 쿼리 목록에 추가
        preference_queries.append(f"[선호 아티스트] {artist_name}")

    return {
        "preference_candidates": all_preference_tracks,
        "search_query": preference_queries
    }
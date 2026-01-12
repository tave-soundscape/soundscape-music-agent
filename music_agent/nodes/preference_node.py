from music_agent.tools.spotify_tool import search_artist, search_artist_tracks_by_context
from music_agent.llm import model
from music_agent.state import AgentState


def preference_analyzer_node(state: AgentState):
    artists = state["user_context"].get("preferred_artists", [])
    artist_details = []

    for name in artists:
        try:
            info = search_artist(name)
            if info:
                artist_details.append(info)
        except Exception as e:
            continue

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
    preferred_artists = state["user_context"].get("preferred_artists", [])
    location = state["user_context"].get("location")
    goal = state["user_context"].get("goal")

    all_preference_tracks = []
    seen_ids = set()

    for artist_name in preferred_artists:
        # 각 가수별로 '위치'와 '목표'를 섞어서 직접 트랙 검색 (10곡씩)
        tracks = search_artist_tracks_by_context(
            artist_name=artist_name,
            location=location.value if hasattr(location, 'value') else location,
            goal=goal.value if hasattr(goal, 'value') else goal,
            limit=10
        )

        for track in tracks:
            if track.tid not in seen_ids:
                all_preference_tracks.append(track)
                seen_ids.add(track.tid)

    return {
        "preference_candidates": all_preference_tracks
    }
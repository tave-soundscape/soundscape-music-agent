from music_agent.state import AgentState

def filter_remix_tracks_node(state: AgentState):
    candidates = state["final_tracks"]

    exclude_title_keywords = ["remix", "remaster", "mix", "master", "live"]
    exclude_artist_names = ["한의 노래"]

    filtered_tracks = []

    for track in candidates:
        # 곡 제목에 금지 키워드가 있는지 확인
        title_lower = track.tn.lower()
        has_forbidden_title = any(word in title_lower for word in exclude_title_keywords)

        # 아티스트 목록 중에 금지된 가수가 있는지 확인
        has_forbidden_artist = any(artist.atn == name for artist in track.at for name in exclude_artist_names)

        if not has_forbidden_title and not has_forbidden_artist:
            filtered_tracks.append(track)

    return {"final_tracks": filtered_tracks}
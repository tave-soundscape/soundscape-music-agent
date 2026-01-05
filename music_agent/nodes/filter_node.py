from music_agent.state import AgentState

def filter_remix_tracks_node(state: AgentState):
    candidates = state["final_tracks"]

    print(f"\n 리믹스 필터 적용 전 추천 곡 개수: {len(candidates)}곡")
    print("-" * 30)
    for i, track in enumerate(candidates, 1):
        artists = ", ".join([a.atn for a in track.at])
        print(f"{i}. {track.tn} - {artists}")

    exclude_keywords = ["remix", "remaster"]

    filtered_tracks = [
        track for track in candidates
        if not any(word in track.tn.lower() for word in exclude_keywords)
    ]

    return {"final_tracks": filtered_tracks}
import random
from music_agent.state import AgentState

def random_select_node(state: AgentState):
    candidates = state.get("candidate_tracks", [])

    unique_tracks_dict = {track.tid: track for track in candidates}
    unique_tracks = list(unique_tracks_dict.values())

    if len(unique_tracks) <= 150:
        selected = unique_tracks
    else:
        selected = random.sample(unique_tracks, 150)

    return {
        "final_tracks": selected,
        "candidate_tracks": []
    }
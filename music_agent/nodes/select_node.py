import random
from music_agent.state import AgentState

def random_select_node(state: AgentState):
    candidates = state.get("candidate_tracks", [])

    unique_tracks_dict = {track.tid: track for track in candidates}
    unique_tracks = list(unique_tracks_dict.values())

    target_count = 150

    if len(unique_tracks) <= target_count:
        selected = unique_tracks
    else:
        selected = random.sample(unique_tracks, target_count)

    return {
        "final_tracks": selected,
        "candidate_tracks": []
    }
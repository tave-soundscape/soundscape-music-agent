import random
from music_agent.state import AgentState

def selection_node(state: AgentState):
    ctx_candidates = state.get("context_candidates", [])
    pref_candidates = state.get("preference_candidates", [])

    def get_unique_tracks(tracks):
        unique_dict = {t.tid: t for t in tracks}
        return list(unique_dict.values())

    unique_ctx = get_unique_tracks(ctx_candidates)
    unique_pref = get_unique_tracks(pref_candidates)

    target_pref_count = 7
    target_ctx_count = 13

    if len(unique_pref) <= target_pref_count:
        selected_pref = unique_pref
    else:
        selected_pref = random.sample(unique_pref, target_pref_count)

    needed_ctx_count = 20 - len(selected_pref)

    if len(unique_ctx) <= needed_ctx_count:
        selected_ctx = unique_ctx
    else:
        selected_ctx = random.sample(unique_ctx, needed_ctx_count)

    final_selection = selected_pref + selected_ctx
    random.shuffle(final_selection)

    return {
        "final_tracks": final_selection,
        "context_candidates": [],
        "preference_candidates": []
    }
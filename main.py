from music_agent.graph import app
from music_agent.state import Location, Goal, Decibel
from langchain_core.messages import HumanMessage

def run_music_agent():
    inputs = {
        "user_context": {
            "location": Location.HOME,
            "goal": Goal.ANGER,
            "decibel": Decibel.QUIET
        },
        "messages": [HumanMessage(content="이 상황에 맞는 노래 찾아줘")],
        "search_query": [],
        "candidate_tracks": [],
        "final_tracks": []
    }

    final_state = app.invoke(inputs)

    print(f"\n 최종 추천 곡 개수: {len(final_state['final_tracks'])}곡")
    print(f" LLM의 검색어 선정 이유: {final_state["recommendation_reason"]}")
    print("검색어: ", final_state["search_query"])
    print("-" * 30)
    for i, track in enumerate(final_state['final_tracks'], 1):
        artists = ", ".join([a.atn for a in track.at])
        print(f"{i}. {track.tn} - {artists}")

    print("-" * 30)
    print("raw response")
    print(final_state['final_tracks'])
if __name__ == "__main__":
    run_music_agent()
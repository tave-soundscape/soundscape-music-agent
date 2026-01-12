from music_agent.graph import app
from music_agent.state import Location, Goal, Decibel
from langchain_core.messages import HumanMessage

def run_music_agent():
    inputs = {
        "user_context": {
            "location": Location.MOVING,
            "goal": Goal.ACTIVE,
            "decibel": Decibel.LOUD,
            "preferred_artists": ["SPYAIR","結束バンド","Han Yo Han"]
        },
        "messages": [HumanMessage(content="이 상황에 맞는 노래 찾아줘")],
        "search_query": [],
        "candidate_tracks": [],
        "final_tracks": []
    }

    final_state = app.invoke(inputs)

    # 1: 페르소나 분석 결과
    print("\n--- [User Persona Analysis] ---")
    print(f"분석된 취향: {final_state['user_persona']['taste_summary']}")

    # 2: 생성된 검색어
    print(f"\n에이전트 생성 검색어: {final_state['search_query']}")

    # 3: 최종 추천 사유
    print(f"\n추천 사유: {final_state['recommendation_reason']}")

    print(f"\n최종 추천 곡 개수: {len(final_state['final_tracks'])}곡")

    print("검색어: ", final_state["search_query"])
    print("-" * 30)
    for i, track in enumerate(final_state['final_tracks'], 1):
        artists = ", ".join([a.atn for a in track.at])
        print(f"{i}. {track.tn} - {artists}")

if __name__ == "__main__":
    run_music_agent()
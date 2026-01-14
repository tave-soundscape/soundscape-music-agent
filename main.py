from music_agent.graph import app
from music_agent.state import Location, Goal, Decibel
from langchain_core.messages import HumanMessage
from music_agent.utils import format_artist_names

def run_music_agent():
    inputs = {
        "user_context": {
            "location": Location.CAFE,
            "goal": Goal.FOCUS,
            "decibel": Decibel.LOUD,
            "preferred_artists": ["Drake","NewJeans","LE SSERAFIM"]
        },
        "messages": [HumanMessage(content="이 상황에 맞는 노래 찾아줘")],
        "search_query": [],
        "candidate_tracks": [],
        "final_tracks": [],
        # 순환 그래프 제어 변수 초기화
        "iteration_count": 0,
        "validation_feedback": {},
        "needs_more_preference": False,
        "needs_recent_tracks": False
    }

    final_state = app.invoke(inputs)

    # 순환 그래프 정보 출력
    print("\n=== [Circular Graph Info] ===")
    print(f"반복 횟수: {final_state.get('iteration_count', 0)}")
    print(f"검증 피드백: {final_state.get('validation_feedback', {})}")

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
        artists = format_artist_names(track.at)
        print(f"{i}. {track.tn} - {artists}")

if __name__ == "__main__":
    run_music_agent()
from langgraph.graph import StateGraph, END
from music_agent.state import AgentState

from music_agent.nodes.planner import query_planner
from music_agent.nodes.fetcher import track_fetcher
from music_agent.nodes.critic import vibe_critic


# 조건부 엣지 로직 (Router)
def check_status(state: AgentState):
    verified = state.get("verified_tracks", [])
    feedback = state.get("feedback")
    retry = state.get("retry_count", 0)

    # [1순위] Critic의 Feedback이 있으면 무조건 다시 Planner로
    if feedback:
        # 무한루프 방지
        if retry >= 3:
            print(f" [Router] 재시도 3회 초과 -> 최선책으로 종료")
            return END

        print(f" [Router] Critic 요청(\"{feedback}\") -> Planner로 회귀")
        return "planner"

    # [2순위] 피드백이 없는데 100곡이 넘었다 -> 성공, 종료
    if len(verified) >= 100:
        print(f" [Router] 목표 달성 및 비율 충족 -> 종료")
        return END

    # [3순위] 피드백도 없고 곡도 부족함  -> 다시 수집
    return "planner"


# 그래프 정의
workflow = StateGraph(AgentState)

# 노드 등록
workflow.add_node("planner", query_planner)
workflow.add_node("fetcher", track_fetcher)
workflow.add_node("critic", vibe_critic)

# 흐름 연결
workflow.set_entry_point("planner")
workflow.add_edge("planner", "fetcher")
workflow.add_edge("fetcher", "critic")

workflow.add_conditional_edges(
    "critic",
    check_status,
    {
        "planner": "planner",
        END: END
    }
)

app = workflow.compile()
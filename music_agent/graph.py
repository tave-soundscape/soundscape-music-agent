from langgraph.graph import StateGraph, END
from music_agent.state import AgentState
from music_agent.nodes import *

workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("analyze_preference", preference_analyzer_node)
workflow.add_node("context_agent", context_agent_node)
workflow.add_node("preference_search", preference_search_node)
workflow.add_node("tools", tool_node)
workflow.add_node("selection", selection_node)
workflow.add_node("quality_validator", quality_validator_node)  # 새로 추가
workflow.add_node("remix_track_filter", filter_remix_tracks_node)
workflow.add_node("generate_reason", generate_reason_node)

# 진입점
workflow.set_entry_point("analyze_preference")

# 기본 플로우 - 항상 순차 실행
workflow.add_edge("analyze_preference", "context_agent")
workflow.add_edge("context_agent", "tools")
workflow.add_edge("tools", "preference_search")
workflow.add_edge("preference_search", "selection")

# 필터링을 먼저 수행한 후 검증
workflow.add_edge("selection", "remix_track_filter")
workflow.add_edge("remix_track_filter", "quality_validator")

# 순환 구조: quality_validator → 조건부 분기
workflow.add_conditional_edges(
    "quality_validator",
    decide_next_step,
    {
        "reselect": "selection",              # 다양성 문제 → selection 재실행
        "enhance_preference": "preference_search",  # 선호 아티스트 부족 → preference_search
        "enhance_context": "context_agent",   # 신곡/장르 부족 → context_agent
        "proceed": "generate_reason"          # 통과 → 이유 생성
    }
)

# 종료
workflow.add_edge("generate_reason", END)

app = workflow.compile()
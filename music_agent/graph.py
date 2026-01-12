from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition
from music_agent.state import AgentState
from music_agent.nodes import *

workflow = StateGraph(AgentState)

workflow.add_node("analyze_preference", preference_analyzer_node)
workflow.add_node("context_agent", context_agent_node)
workflow.add_node("preference_search", preference_search_node)
workflow.add_node("tools", tool_node)
workflow.add_node("selection", selection_node)
workflow.add_node("remix_track_filter", filter_remix_tracks_node)
workflow.add_node("generate_reason", generate_reason_node)

workflow.set_entry_point("analyze_preference")
workflow.add_edge("analyze_preference", "context_agent")
workflow.add_conditional_edges(
    "context_agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "preference_search"
    }
)
workflow.add_edge("tools", "preference_search") # 툴 작업 완료 후 취향 검색으로
workflow.add_edge("preference_search", "selection")
workflow.add_edge("selection", "remix_track_filter")
workflow.add_edge("remix_track_filter", "generate_reason")
workflow.add_edge("generate_reason", END)

app = workflow.compile()
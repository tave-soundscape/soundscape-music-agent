from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition
from music_agent.state import AgentState
from music_agent.nodes import *

workflow = StateGraph(AgentState)

workflow.add_node("analyze_preference", preference_analyzer_node)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_node("random_select", random_select_node)
workflow.add_node("generate_reason", generate_reason_node)
workflow.add_node("remix_track_filter", filter_remix_tracks_node)

workflow.set_entry_point("analyze_preference")
workflow.add_edge("analyze_preference", "agent")
workflow.add_conditional_edges("agent", tools_condition) #  에이전트가 툴을 부르면 tools 노드로, 아니면 종료
workflow.add_edge("tools", "random_select")
workflow.add_edge("random_select", "remix_track_filter")
workflow.add_edge("remix_track_filter", "generate_reason")
workflow.add_edge("generate_reason", END)

app = workflow.compile()
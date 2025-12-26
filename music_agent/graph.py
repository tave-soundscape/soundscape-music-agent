from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition
from music_agent.state import AgentState
from music_agent.nodes import call_model, tool_node, random_select_node

workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_node("random_select", random_select_node)

workflow.set_entry_point("agent")

#  에이전트가 툴을 부르면 tools 노드로, 아니면 종료
workflow.add_conditional_edges("agent", tools_condition)

workflow.add_edge("tools", "random_select")
workflow.add_edge("random_select", END)

app = workflow.compile()
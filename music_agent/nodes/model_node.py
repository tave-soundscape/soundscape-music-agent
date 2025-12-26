from langchain_core.messages import SystemMessage, HumanMessage
from music_agent.state import AgentState
from music_agent.prompt import SYSTEM_PROMPT
from music_agent.tools import tools
from music_agent.llm import model

model_with_tools = model.bind_tools(tools)

def call_model(state: AgentState):
  context = state["user_context"]
  context_str = (
      f"현재 상황: 위치={context['location'].value}, "
      f"목표={context['goal'].value}, "
      f"소음={context['decibel'].value}")
  sys_msg = SystemMessage(content=SYSTEM_PROMPT + "\n\n" + context_str)

  response = model_with_tools.invoke([sys_msg] + state["messages"])

  queries = []
  if response.tool_calls:
      queries = [tc['args']['query'] for tc in response.tool_calls if tc['name'] == 'make_playlist']

  return {
          "messages": [response],
          "search_query": queries
      }
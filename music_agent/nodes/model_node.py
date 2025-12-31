from langchain_core.messages import SystemMessage, HumanMessage
from music_agent.state import AgentState
from music_agent.prompt import SYSTEM_PROMPT
from music_agent.tools import tools
from music_agent.llm import model

model_with_tools = model.bind_tools(tools)

def get_value(obj):
    # .value 속성이 있으면(Enum이면) 그거 사용, 없으면 그대로 반환
    return obj.value if hasattr(obj, 'value') else obj

def call_model(state: AgentState):
  context = state["user_context"]
  context_str = (
      f"현재 상황: 위치={get_value(context['location'])}, "
      f"목표={get_value(context['goal'])}, "
      f"소음 정도={get_value(context['decibel'])}"
  )
  sys_msg = SystemMessage(content=SYSTEM_PROMPT + "\n\n" + context_str)

  response = model_with_tools.invoke([sys_msg] + state["messages"])

  queries = []
  if response.tool_calls:
      queries = [tc['args']['query'] for tc in response.tool_calls if tc['name'] == 'make_playlist']

  return {
          "messages": [response],
          "search_query": queries
      }
from langchain_core.messages import SystemMessage, HumanMessage
from music_agent.state import AgentState
from music_agent.prompt import SYSTEM_PROMPT
from music_agent.tools import tools
from music_agent.llm import model
from music_agent.constants import (
    MIN_RECENT_TRACK_RATIO
)

model_with_tools = model.bind_tools(tools)

def get_value(obj):
    # .value 속성이 있으면(Enum이면) 그거 사용, 없으면 그대로 반환
    return obj.value if hasattr(obj, 'value') else obj

def context_agent_node(state: AgentState):
  context = state["user_context"]
  user_persona = state.get("user_persona", {})

  context_str = (
      f"현재 상황: 위치={get_value(context['location'])}, "
      f"목표={get_value(context['goal'])}, "
      f"소음 정도={get_value(context['decibel'])}"
  )

  # 선호 아티스트 정보 추가
  preferred_artists = context.get("preferred_artists", [])
  if preferred_artists:
      context_str += f"\n선호 아티스트: {', '.join(preferred_artists)}"

      # 페르소나 정보가 있으면 장르도 추가
      preferred_genres = user_persona.get("preferred_genres", [])
      if preferred_genres:
          genres = ", ".join(preferred_genres[:5])  # 최대 5개
          context_str += f"\n선호 장르: {genres}"
          context_str += f"\n→ Focus 상황이라도 이 장르의 차분한 버전을 검색에 포함하세요!"

  # ...existing code...
  needs_recent_tracks = state.get("needs_recent_tracks", False)
  validation_feedback = state.get("validation_feedback", {})

  additional_instructions = ""

  if needs_recent_tracks:
      recent_ratio = validation_feedback.get("recent_track_ratio", 0)
      if recent_ratio < MIN_RECENT_TRACK_RATIO:
          additional_instructions += "\n\n[중요] 신곡이 부족합니다. 반드시 '최신', 'new', 'latest' 키워드를 포함한 검색어를 생성하세요."

      missing_genres = validation_feedback.get("missing_genres", [])
      if missing_genres:
          genres_str = ", ".join(missing_genres[:3])  # 최대 3개 장르만
          additional_instructions += f"\n\n[중요] 다음 장르가 부족합니다: {genres_str}. 이 장르들을 명시적으로 포함한 검색어를 생성하세요."

  sys_msg = SystemMessage(content=SYSTEM_PROMPT + "\n\n" + context_str + additional_instructions)

  response = model_with_tools.invoke([sys_msg] + state["messages"])

  queries = []
  if response.tool_calls:
      queries = [tc['args']['query'] for tc in response.tool_calls if tc['name'] == 'make_playlist']

  return {
          "messages": [response],
          "search_query": queries
      }
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
          context_str += f"\n→ 선호 장르를 상황에 맞게 변형하여 검색에 포함하세요."

  # ...existing code...
  needs_recent_tracks = state.get("needs_recent_tracks", False)
  validation_feedback = state.get("validation_feedback", {})

  additional_instructions = ""

  if needs_recent_tracks:
      recent_ratio = validation_feedback.get("recent_track_ratio", 0)
      missing_genres = validation_feedback.get("missing_genres", [])

      feedback_parts = []

      if recent_ratio < MIN_RECENT_TRACK_RATIO:
          feedback_parts.append("신곡 비율이 낮습니다. 'New 2025', 'Latest 2026', 'New Release' 키워드를 포함한 검색어를 생성하세요.")

      if missing_genres:
          genres_str = ", ".join(missing_genres[:2])  # 최대 2개 장르만
          feedback_parts.append(f"다음 장르가 부족합니다: {genres_str}. 이 장르를 상황(목표/위치)과 조합한 검색어를 생성하세요.")

      if feedback_parts:
          additional_instructions = "\n\n[재검색 요청 - 부족한 부분만 보완]\n- " + "\n- ".join(feedback_parts)
          additional_instructions += "\n\n이번에는 2-3개 검색어만 생성하세요 (부족한 부분 집중 보완)."

  sys_msg = SystemMessage(content=SYSTEM_PROMPT + "\n\n" + context_str + additional_instructions)

  response = model_with_tools.invoke([sys_msg] + state["messages"])

  queries = []
  if response.tool_calls:
      queries = [tc['args']['query'] for tc in response.tool_calls if tc['name'] == 'make_playlist']

  return {
          "messages": [response],
          "search_query": queries
      }
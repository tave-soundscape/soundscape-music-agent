from music_agent.state import AgentState
from music_agent.llm import model


def generate_reason_node(state: AgentState):
    context = state["user_context"]
    # LLM이 생성했던 검색 쿼리 -> 에이전트의 의도를 가장 잘 나타냄
    queries = state.get("search_query", [])
    query_str = ", ".join(queries) if queries else "맞춤 테마"

    prompt = f"""
    [사용자 상황]
    위치: {context.get('location')}
    목표: {context.get('goal')}
    주변 소음: {context.get('decibel')}

    [선정 테마]
    {query_str}

    위 정보를 바탕으로 사용자에게 음악을 추천한 이유를 친절하고 전문적인 한국어로 한 문장 작성해주세요.
    말투는 '~했습니다' 또는 '~로 준비했습니다' 체를 사용하고, 50자 이내로 작성하세요.
    """

    response = model.invoke(prompt)

    return {
        "recommendation_reason": response.content
    }
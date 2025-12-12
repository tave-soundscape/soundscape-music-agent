import json
from langchain_core.messages import SystemMessage, HumanMessage
from music_agent.llm import llm
from music_agent.state import AgentState


def query_planner(state: AgentState):
    user_input = state['user_input']
    feedback = state.get("feedback")
    retry = state.get("retry_count", 0)

    # 모드에 따른 로그 출력
    if not feedback:
        print("\n--- [Planner] 1. 초기 전략 수립 ---")
        instruction = "Generate initial tags for Korea(60%), Global(35%), Japan(5%)."
    else:
        print(f"\n--- [Planner] 2. 전략 수정 (재시도 {retry + 1}회) ---")
        print(f"   📣 Critic 피드백: \"{feedback}\"")
        instruction = f"FIX THE SHORTAGE based on feedback: {feedback}. Focus ONLY on the missing region/genre."

    system_prompt = f"""
    You are a Music Curator.
    {instruction}

    CONTEXT RULES:
    1. Gym/Workout -> High Energy (k-pop dance, gym phonk, rock). NO ballads.
    2. Library -> Calm (piano, lo-fi).

    CRITICAL:
    - If feedback says 'Need more Korean', generate MANY varied Korean tags (e.g., k-pop, k-indie, k-hip-hop).
    - If feedback says 'Need more Global', generate pop/rock tags.

    OUTPUT JSON:
    {{
        "korea_tags": [...],
        "global_tags": [...],
        "japan_tags": [...]
    }}
    """

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Context: {user_input['location']}, Goal: {user_input['goal']}")
    ])

    try:
        content = response.content.replace("```json", "").replace("```", "").strip()
        tags_map = json.loads(content)
        print(f"   ✅ 전략 생성 완료: {tags_map}")
        return {"search_queries": tags_map}
    except:
        return {"search_queries": {"korea_tags": ["k-pop"], "global_tags": ["pop"], "japan_tags": ["j-pop"]}}

# import json
# from langchain_core.messages import SystemMessage, HumanMessage
# from music_agent.llm import llm
# from music_agent.state import AgentState
#
#
# def query_planner(state: AgentState):
#     user_input = state['user_input']  # 이제 이건 UserContext 객체입니다.
#     feedback = state.get("feedback")
#     retry = state.get("retry_count", 0)
#
#     # 1. 객체에서 값 꺼내기 (Enum이라서 .value로 실제 문자열을 가져옴)
#     loc = user_input.location.value
#     noise = user_input.decibel_level.value
#     goal = user_input.goal.value
#
#     # 로그 출력
#     if not feedback:
#         print("\n--- [Planner] 1. 초기 전략 수립 ---")
#         instruction = "Generate initial tags for Korea(60%), Global(35%), Japan(5%)."
#     else:
#         print(f"\n--- [Planner] 2. 전략 수정 (재시도 {retry + 1}회) ---")
#         print(f"   📣 Critic 피드백: \"{feedback}\"")
#         instruction = f"FIX THE SHORTAGE based on feedback: {feedback}. Focus ONLY on the missing region/genre."
#
#     system_prompt = f"""
#     You are a Music Curator.
#     {instruction}
#
#     CONTEXT RULES:
#     1. Gym/Workout -> High Energy.
#     2. Library -> Calm.
#
#     CRITICAL:
#     - If feedback says 'Need more Korean', generate MANY varied Korean tags.
#
#     OUTPUT JSON:
#     {{
#         "korea_tags": [...],
#         "global_tags": [...],
#         "japan_tags": [...]
#     }}
#     """
#
#     # 2. 변수 사용 (loc, noise, goal)
#     human_prompt = f"Context: {loc} (Noise: {noise}), Goal: {goal}"
#
#     messages = [
#         SystemMessage(content=system_prompt),
#         HumanMessage(content=human_prompt)
#     ]
#
#     response = llm.invoke(messages)
#
#     try:
#         content = response.content.replace("```json", "").replace("```", "").strip()
#         tags_map = json.loads(content)
#         print(f"   ✅ 전략 생성 완료: {tags_map}")
#         return {"search_queries": tags_map}
#     except:
#         return {"search_queries": {"korea_tags": ["k-pop"], "global_tags": ["pop"], "japan_tags": ["j-pop"]}}
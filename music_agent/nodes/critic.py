import random
from music_agent.state import AgentState


def vibe_critic(state: AgentState):
    candidates = state.get("candidate_tracks", [])
    retry = state.get("retry_count", 0)
    print(f"\n--- [Critic] 검증 및 비율 분석 (후보: {len(candidates)}곡) ---")

    # 1. 지역별 분류
    korea = [t for t in candidates if t.get('region_tag') == 'korea']
    global_ = [t for t in candidates if t.get('region_tag') == 'global']
    japan = [t for t in candidates if t.get('region_tag') == 'japan']

    k_cnt, g_cnt, j_cnt = len(korea), len(global_), len(japan)

    print(f"   📊 현재 확보: 🇰🇷{k_cnt} / 🇺🇸{g_cnt} / 🇯🇵{j_cnt}")

    # 2. 부족분 계산 (목표: 한60, 글35, 일5)
    # 재시도 3회차(마지막)면 부족해도 그냥 통과시킴
    feedback = ""
    if retry < 3:
        if k_cnt < 60:
            feedback += f"Need {60 - k_cnt} more Korean songs. "
        if g_cnt < 35:
            feedback += f"Need {35 - g_cnt} more Global songs. "
        if j_cnt < 5:
            feedback += f"Need {5 - j_cnt} more Japan songs. "

    if feedback:
        print(f"   ⚠️ 문제 발견: {feedback}")
        return {
            "verified_tracks": candidates,  # 현재 리스트 유지
            "feedback": feedback,
            "retry_count": retry + 1
        }

    else:
        # 3. [최종 정리] 비율에 맞춰 100곡으로 자르기 (Trimming)
        print("   ✅ 조건 충족! 최종 100곡 리스트 확정 중...")

        random.shuffle(korea)
        random.shuffle(global_)
        random.shuffle(japan)

        final_list = []
        final_list.extend(korea[:60])  # 한국 60곡
        final_list.extend(global_[:35])  # 글로벌 35곡
        final_list.extend(japan[:5])  # 일본 5곡

        # 혹시 부족하면 남은거에서 채우기 (Priority: Korea > Global > Japan)
        if len(final_list) < 100:
            remaining = [t for t in candidates if t not in final_list]
            needed = 100 - len(final_list)
            final_list.extend(remaining[:needed])

        # 최종 확인 로그
        fk = len([t for t in final_list if t.get('region_tag') == 'korea'])
        fg = len([t for t in final_list if t.get('region_tag') == 'global'])
        fj = len([t for t in final_list if t.get('region_tag') == 'japan'])

        print(f"   🎂 최종 완성: 총 {len(final_list)}곡 (🇰🇷{fk} / 🇺🇸{fg} / 🇯🇵{fj})")

        return {
            "verified_tracks": final_list,
            "feedback": None  # 피드백 없으므로 Router가 종료시킴
        }

# import random
# from music_agent.state import AgentState
#
#
# def vibe_critic(state: AgentState):
#     candidates = state.get("candidate_tracks", [])
#     retry = state.get("retry_count", 0)
#
#     # user_input은 객체지만, Critic 로직상 직접 꺼내 쓸 일이 적어서 여기선
#     # candidates 비율 분석에 집중하면 됩니다. (필요하다면 state['user_input'].goal.value 처럼 쓰면 됨)
#
#     print(f"\n--- [Critic] 검증 및 비율 분석 (후보: {len(candidates)}곡) ---")
#
#     # 1. 지역별 분류
#     korea = [t for t in candidates if t.get('region_tag') == 'korea']
#     global_ = [t for t in candidates if t.get('region_tag') == 'global']
#     japan = [t for t in candidates if t.get('region_tag') == 'japan']
#
#     k_cnt, g_cnt, j_cnt = len(korea), len(global_), len(japan)
#     print(f"   📊 현재 확보: 🇰🇷{k_cnt} / 🇺🇸{g_cnt} / 🇯🇵{j_cnt}")
#
#     # 2. 피드백 생성
#     feedback = ""
#     if retry < 3:
#         if k_cnt < 60: feedback += f"Need {60 - k_cnt} more Korean songs. "
#         if g_cnt < 35: feedback += f"Need {35 - g_cnt} more Global songs. "
#         if j_cnt < 5:  feedback += f"Need {5 - j_cnt} more Japan songs. "
#
#     if feedback:
#         print(f"   ⚠️ 문제 발견: {feedback}")
#         return {
#             "verified_tracks": candidates,
#             "feedback": feedback,
#             "retry_count": retry + 1
#         }
#
#     else:
#         # 3. 종료 및 Trimming
#         print("   ✅ 조건 충족! 최종 100곡 리스트 확정 중...")
#         random.shuffle(korea);
#         random.shuffle(global_);
#         random.shuffle(japan)
#
#         final_list = []
#         final_list.extend(korea[:60])
#         final_list.extend(global_[:35])
#         final_list.extend(japan[:5])
#
#         if len(final_list) < 100:
#             remaining = [t for t in candidates if t not in final_list]
#             final_list.extend(remaining[:100 - len(final_list)])
#
#         fk = len([t for t in final_list if t.get('region_tag') == 'korea'])
#         fg = len([t for t in final_list if t.get('region_tag') == 'global'])
#         fj = len([t for t in final_list if t.get('region_tag') == 'japan'])
#
#         print(f"   🎂 최종 완성: 총 {len(final_list)}곡 (🇰🇷{fk} / 🇺🇸{fg} / 🇯🇵{fj})")
#         return {
#             "verified_tracks": final_list,
#             "feedback": None
#         }
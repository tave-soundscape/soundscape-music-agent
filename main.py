
from dotenv import load_dotenv

# 1. 환경 변수 로드 (가장 먼저!)
load_dotenv()

# 2. 그래프 import (환경변수 로드 후)
from music_agent.graph import app


def main():
    print("🎧 음악 추천 에이전트를 시작합니다...")

    # 사용자 상황 입력 (예시)
    user_input = {
        "location": "gym",
        "decibel_level": "loud",
        "goal": "focus"
    }

    print(f"📍 상황: {user_input['location']}, 목표: {user_input['goal']}")

    # 초기 상태
    initial_state = {
        "user_input": user_input,
        "search_queries": [],
        "candidate_tracks": [],
        "verified_tracks": []
    }

    try:
        # 그래프 실행
        result = app.invoke(initial_state)

        final_list = result.get("verified_tracks", [])

        print(f"\n✅ 최종 추천 리스트 ({len(final_list)}곡):")
        print("=" * 40)
        for i, track in enumerate(final_list, 1):
            print(f"{i}. {track['artist']} - {track['title']}")
        print("=" * 40)

    except Exception as e:
        print(f"\n❌ 실행 중 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# import os
# import sys
# from dotenv import load_dotenv
#
# load_dotenv()
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#
# from music_agent.graph import app
# # 모델 import 추가
# from music_agent.models import UserContext, Location, Decibel, Goal
#
#
# def main():
#     print("🎧 음악 추천 에이전트를 시작합니다...")
#
#     # [수정] Pydantic 객체 생성 (오타 방지, 검증 자동화)
#     try:
#         user_input = UserContext(
#             location=Location.GYM,
#             decibel_level=Decibel.LOUD,
#             goal=Goal.FOCUS
#         )
#     except ValueError as e:
#         print(f"❌ 입력 에러: {e}")
#         return
#
#     print(f"📍 상황: {user_input.location.value} / 목표: {user_input.goal.value}")
#
#     # 초기 상태에 객체 주입
#     initial_state = {
#         "user_input": user_input,  # 👈 객체가 들어갑니다
#         "search_queries": {},
#         "candidate_tracks": [],
#         "verified_tracks": [],
#         "feedback": None,
#         "retry_count": 0
#     }
#
#     try:
#         result = app.invoke(initial_state)
#         final_list = result.get("verified_tracks", [])
#
#         print(f"\n✅ 최종 추천 리스트 ({len(final_list)}곡):")
#         print("=" * 60)
#         for i, track in enumerate(final_list, 1):
#             region = track.get('region_tag', 'global').upper()
#             print(f"{i:02d}. [{region}] {track['artist']} - {track['title']}")
#         print("=" * 60)
#
#     except Exception as e:
#         print(f"\n❌ 에러 발생: {e}")
#         import traceback
#         traceback.print_exc()
#
#
# if __name__ == "__main__":
#     main()
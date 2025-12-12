import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from music_agent.graph import app
from music_agent.models import UserContext, Location, Decibel, Goal

# TODO : 처음 전략 태그 한글로 만들어지면 플레이리스트 생성 안됨
# TODO : 디버깅용 출력문 전부 추후 삭제
def main():
    print(" 음악 추천 에이전트 시작")

    try:
        user_input = UserContext(
            location=Location.GYM,
            decibel_level=Decibel.LOUD,
            goal=Goal.FOCUS
        )
    except ValueError as e:
        print(f" 입력 에러: {e}")
        return

    print(f" 상황: {user_input.location.value} / 목표: {user_input.goal.value}")

    # 초기 상태에 객체 주입
    initial_state = {
        "user_input": user_input,
        "search_queries": {},
        "candidate_tracks": [],
        "verified_tracks": [],
        "feedback": None,
        "retry_count": 0
    }

    try:
        result = app.invoke(initial_state)
        final_list = result.get("verified_tracks", [])

        print(f"\n 최종 추천 리스트 ({len(final_list)}곡):")
        print("=" * 60)
        for i, track in enumerate(final_list, 1):
            region = track.get('region_tag', 'global').upper()
            print(f"{i:02d}. [{region}] {track['artist']} - {track['title']}")
        print("=" * 60)

    except Exception as e:
        print(f"\n 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
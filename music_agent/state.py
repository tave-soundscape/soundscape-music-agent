from typing import TypedDict, List, Optional

# 사용자 입력 데이터
class UserInput(TypedDict):
    location: str        # gym, cafe ...
    decibel_level: str   # loud, quiet ...
    goal: str            # focus, active ...
    fav_artists: List[str]
    fav_genres: List[str]

# 에이전트 메모리
class MusicAgentState(TypedDict):
    inputs: UserInput

    # 내부 사고 과정 (Internal Reasoning)
    # LLM이 분석한 검색 조건
    # {"min_bpm": 120, "target_energy": "high", "seed_genres": ["pop"]}
    search_criteria: dict

    # outputs
    recommendations: List[str] # 음악 리스트

    retry_count: int
    is_sufficient: bool   # 목표 달성 여부 (True/False)

    # 결과 저장소
    final_result: Optional[dict]
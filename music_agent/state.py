from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    user_input: Dict[str, str]  # 사용자 입력

    # 실행 흐름 제어용
    search_queries: Dict[str, List[str]]  # 검색할 태그들
    candidate_tracks: List[Dict[str, Any]]  # 수집된 후보군 (누적됨)
    verified_tracks: List[Dict[str, Any]]  # 검증 통과한 곡들

    # 순환(Loop)을 위한 핵심 필드
    feedback: Optional[str]  # Critic이 Planner에게 보내는 수정 요청사항
    retry_count: int  # 현재 재시도 횟수 (0부터 시작)
#
# from typing import TypedDict, List, Dict, Any, Optional
# from music_agent.models import UserContext  # 👈 import 추가
#
#
# class AgentState(TypedDict):
#     user_input: UserContext  # 👈 Dict 대신 객체 사용
#
#     # 나머지는 그대로 유지
#     search_queries: Dict[str, List[str]]
#     candidate_tracks: List[Dict[str, Any]]
#     verified_tracks: List[Dict[str, Any]]
#     feedback: Optional[str]
#     retry_count: int
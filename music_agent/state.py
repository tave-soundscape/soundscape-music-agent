from typing import TypedDict, List, Dict, Any, Optional
from music_agent.models import UserContext


class AgentState(TypedDict):
    user_input: UserContext
    search_queries: Dict[str, List[str]]
    candidate_tracks: List[Dict[str, Any]]
    verified_tracks: List[Dict[str, Any]]
    feedback: Optional[str]
    retry_count: int
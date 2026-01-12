import uvicorn
from fastapi import FastAPI
from langserve import add_routes
from music_agent.graph import app as music_agent_app
from music_agent.state import Track
from pydantic import BaseModel, Field

from typing import List, Optional
from music_agent.state import Track, UserPersona

# FastAPI 앱
server = FastAPI(
    title="Soundscape Music Agent Server",
    version="1.0",
    description="사용자 컨텍스트 기반 음악 추천 에이전트 API"
)

class UserContext(BaseModel):
    location: str = Field(..., description="위치 (gym, cafe, library, home 등)")
    goal: str = Field(..., description="목적 (focus, relax, active 등)")
    decibel: str = Field(..., description="소음 정도 (quiet, moderate, loud)")
    preferred_artists: List[str] = Field(default=[], description="선호하는 아티스트 이름 리스트 (최대 3명)")

# Request DTO
class MusicRequest(BaseModel):
    user_context: UserContext = Field(..., description="위치, 목표, 소음 정보")
    messages: list = Field(default=[], description="추가 메시지 리스트")

# Response DTO
class MusicResponse(BaseModel):
    final_tracks: List[Track] = Field(..., description="최종 선별된 20곡 리스트")
    recommendation_reason: str = Field(..., description="LLM이 작성한 추천 사유")
    user_persona: Optional[dict] = Field(None, description="분석된 사용자 취향 요약 정보")

# 3. API 등록
add_routes(
    server,
    music_agent_app,
    path="/music",
    input_type=MusicRequest,
    output_type=MusicResponse,
    enabled_endpoints=["invoke","playground"]
)

if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=8000)
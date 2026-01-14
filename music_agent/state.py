from enum import Enum
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
import operator
from pydantic import BaseModel, Field

class Location(str, Enum):
    GYM = "gym"
    CAFE = "cafe"
    LIBRARY = "library"
    HOME = "home"
    MOVING = "moving"
    PARK = "park"
    CO_WORKING = "co-working"

class Decibel(str, Enum):
    QUIET = "quiet"
    MODERATE = "moderate"
    LOUD = "loud"

class Goal(str, Enum):
    FOCUS = "focus"
    RELAX = "relax"
    SLEEP = "sleep"
    ACTIVE = "active"
    ANGER = "anger"
    CONSOLATION = "consolation"
    NEUTRAL = "neutral"
    STABILIZATION = "stabilization"

# Artist, Track은 DTO 역할 하므로 BaseModel 활용
class Artist(BaseModel):
    atid: str = Field(description="Artist ID")
    atn: str = Field(description="Artist Name")

class Track(BaseModel):
    tid: str = Field(description="Track ID")
    tn: str = Field(description="Track Name")
    tu: str = Field(description="Track URI")
    turl: str = Field(description="Track External Url")
    ms: int = Field(description="Duration in milliseconds")
    ai: str = Field(description="Album ID")
    an: str = Field(description="앨범 이름")
    au: str = Field(description="Album URI")
    img: str = Field(description="Album Image URL")
    rd: str = Field(description="Album Release Date (YYYY-MM-DD or YYYY)")
    at: List[Artist] = Field(description="List of Artists")

class ArtistMetadata(BaseModel):
    name: str
    genres: List[str]
    popularity: int

class UserContext(TypedDict):
  location: Location
  goal: Goal
  decibel: Decibel
  preferred_artists: List[str]

class UserPersona(TypedDict):
    preferred_genres: List[str]
    average_popularity: float         # 인기도 평균 (음악 성향 주류/비주류 판단 지표)
    taste_summary: str               # LLM이 분석한 한 줄 요약
    artists_details: List[ArtistMetadata] # 검색된 아티스트 상세 정보

class AgentState(TypedDict):
  user_context: UserContext
  user_persona: UserPersona
  search_query: Annotated[List[str], operator.add]  # 검색어 누적
  messages: Annotated[list, add_messages]
  context_candidates: Annotated[List[Track], operator.add]
  preference_candidates: Annotated[List[Track], operator.add]
  final_tracks: List[Track]
  recommendation_reason: str
  # 순환 그래프 제어 변수
  iteration_count: int
  validation_feedback: dict  # 검증 결과 상세 정보
  needs_more_preference: bool  # 선호 아티스트 곡 추가 필요 여부
  needs_recent_tracks: bool  # 신곡 추가 필요 여부

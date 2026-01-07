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
    img: str = Field(description="Album Image URL")
    an: str = Field(description="앨범 이름")
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
    averge_popularity: float         # 인기도 평균 (음악 성향 주류/비주류 판단 지표)
    taste_summary: str               # LLM이 분석한 한 줄 요약
    artists_details: List[ArtistMetadata] # 검색된 아티스트 상세 정보

class AgentState(TypedDict):
  user_context: UserContext
  user_persona: UserPersona
  search_query: List[str]
  messages: Annotated[list, add_messages]
  candidate_tracks: Annotated[List[Track], operator.add]
  final_tracks: List[Track]
  recommendation_reason: str
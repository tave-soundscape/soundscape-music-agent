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

# Artist, Track은 DTO 역할 하므로 BaseModel 활용
class Artist(BaseModel):
    atid: str = Field(description="Artist ID")
    atn: str = Field(description="Artist Name")

class Track(BaseModel):
    tid: str = Field(description="Track ID")
    tn: str = Field(description="Track Name")
    tu: str = Field(description="Track URI")
    ms: int = Field(description="Duration in milliseconds")
    img: str = Field(description="Album Image URL")
    at: List[Artist] = Field(description="List of Artists")

class UserContext(TypedDict):
  location: Location
  goal: Goal
  decibel: Decibel

class AgentState(TypedDict):
  user_context: UserContext
  search_query: List[str]
  messages: Annotated[list, add_messages]
  candidate_tracks: Annotated[List[Track], operator.add]
  final_tracks: List[Track]
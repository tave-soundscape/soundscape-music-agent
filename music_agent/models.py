from enum import Enum
from pydantic import BaseModel, Field

# 1. 오타 방지를 위한 Enum 정의
class Location(str, Enum):
    GYM = "gym"
    CAFE = "cafe"
    LIBRARY = "library"
    HOME = "home"
    MOVING = "moving"
    PARK = "park"
    CO_WORKING = "co-working"

class Decibel(str, Enum):
    SILENT = "silent"      # 0-35dB
    QUIET = "quiet"        # 36-50dB
    MODERATE = "moderate"  # 51-65dB
    LOUD = "loud"          # 66-80dB
    VERY_LOUD = "very_loud" # 81dB+

class Goal(str, Enum):
    FOCUS = "focus"
    RELAX = "relax"
    SLEEP = "sleep"
    ACTIVE = "active"
    ANGER = "anger"
    CONSOLATION = "consolation"
    NEUTRAL = "neutral"

# 2. 사용자 입력 객체 (Java의 DTO 역할)
class UserContext(BaseModel):
    location: Location = Field(..., description="장소")
    decibel_level: Decibel = Field(..., description="소음도")
    goal: Goal = Field(..., description="목표")
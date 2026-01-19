# 순환 그래프 설정
MAX_ITERATION_COUNT = 2  # 최대 재시도 횟수

# 선곡 설정
TARGET_FINAL_TRACK_COUNT = 20  # 최종 추천 곡 수
SELECTION_BUFFER_COUNT = 25  # 필터링을 고려한 선곡 수 (여유분 포함)
PREFERENCE_TRACK_COUNT = 10  # 선호 아티스트 기반 선곡 목표 수
CONTEXT_TRACK_COUNT = 15  # 상황 기반 선곡 목표 수

# 품질 검증 기준
MAX_ARTIST_TRACK_COUNT = 4  # 한 아티스트당 최대 곡 수
MIN_RECENT_TRACK_RATIO = 0.2  # 최소 신곡 비율 (20%)
MIN_PREFERRED_ARTIST_COUNT = 2  # 최소 선호 아티스트 매칭 수 (3명 중 2명)
RECENT_TRACK_DAYS = 365  # 신곡 기준 (최근 1년)

# Spotify 검색 설정
PLAYLIST_SEARCH_LIMIT = 3  # 플레이리스트 검색 개수
MAX_TRACKS_PER_PLAYLIST = 150  # 플레이리스트당 최대 트랙 수
ARTIST_SEARCH_LIMIT = 1  # 아티스트 검색 개수, 검색 결과 최대 값
DEFAULT_TRACK_LIMIT = 15  # 아티스트 별 기본 트랙 검색 결과 개수
ENHANCED_TRACK_LIMIT = 20  # 재검색 시 트랙 개수

# 필터링 설정
EXCLUDE_TITLE_KEYWORDS = ["remix", "remaster", "mix", "master", "live"]
EXCLUDE_ARTIST_NAMES = ["한의 노래"]

# 기타 설정
DEFAULT_MARKET = "KR"  # 기본 시장 (한국)
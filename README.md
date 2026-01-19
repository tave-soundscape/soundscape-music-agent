# Music Recommendation Agent

사용자의 현재 컨텍스트(위치, 목적, 소음 수준)와 선호 아티스트를 기반으로 맞춤형 음악을 추천하는 LangGraph 기반 에이전트 시스템.

## 기능

- 사용자 컨텍스트 분석 (위치, 목적, 소음 수준)
- 사용자의 선호 아티스트 기반으로 취향 분석 및 페르소나 생성
- Spotify API 연동 음악 검색 및 추천
- 품질 검증 루프를 통한 추천 결과 최적화
  - 선호 아티스트 매칭률 검증
  - 신곡 비율 검증
  - 아티스트 다양성 검증
- 리믹스/커버곡 자동 필터링
- LLM 기반 추천 사유 생성

## 에이전트 구조

<img width="506" height="1000" alt="agent_graph" src="https://github.com/user-attachments/assets/3fdf6971-f992-4fb5-beb2-5ff1de0c680d" />

LangGraph를 사용한 순환형 에이전트 워크플로우:

1. **analyze_preference**: 선호 아티스트 분석 및 페르소나 생성
  <img width="657" height="313" alt="image" src="https://github.com/user-attachments/assets/de6f0864-6dda-45fb-9a11-673dc3e9e901" />

2. **context_agent**: 컨텍스트 기반 검색어 생성
3. **tools**: Spotify API를 통한 트랙 검색
4. **preference_search**: 선호 아티스트 관련 트랙 추가 검색
5. **selection**: 최종 20곡 선별
6. **remix_track_filter**: 리믹스/커버곡 필터링
7. **quality_validator**: 품질 검증 및 피드백 생성
8. **generate_reason**: 추천 사유 생성

품질 검증 실패 시 자동으로 이전 단계로 순환하여 재실행.

## 설치

```bash
pip install -r requirements.txt
```

## 환경 변수

`.env` 파일에 다음 변수들을 설정:

```
OPENAI_API_KEY=your_openai_api_key
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
```

## 사용법

### CLI 실행

```bash
python main.py
```

### FastAPI 서버 실행

```bash
python server.py
```

서버 실행 후 `http://localhost:8000/docs`에서 API 문서 확인.

### API 엔드포인트

**POST** `/music/invoke`

요청 예시:
```json
{
  "user_context": {
    "location": "cafe",
    "goal": "focus",
    "decibel": "loud",
    "preferred_artists": ["Drake", "NewJeans", "LE SSERAFIM"]
  },
  "messages": [
    {
      "type": "human",
      "content": "이 상황에 맞는 노래 찾아줘"
    }
  ]
}
```

응답 예시:
```json
{
  "final_tracks": [...],
  "recommendation_reason": "...",
  "search_query": [...],
  "user_persona": {...}
}
```

## 프로젝트 구조

```
music_agent/
├── graph.py              # LangGraph 워크플로우 정의
├── state.py              # 상태 관리 및 데이터 모델
├── llm.py                # LLM 설정
├── prompt.py             # 프롬프트 템플릿
├── config.py             # 환경 변수 로드
├── constants.py          # 상수 정의
├── nodes/                # 각 노드 구현
│   ├── preference_node.py
│   ├── model_node.py
│   ├── tool_node.py
│   ├── select_node.py
│   ├── filter_node.py
│   ├── quality_validator_node.py
│   └── reason_node.py
└── tools/
    └── spotify_tool.py   # Spotify API 통합
```

## 기술

- LangChain / LangGraph
- OpenAI GPT
- Spotipy
- FastAPI
- Pydantic

## 주요 검증 기준

- 선호 아티스트: 3명 중 최소 2명 매칭
- 신곡 비율: 최소 20% (최근 1년 이내)
- 선호 아티스트별 최대 곡 수: 2곡
- 최대 순환 횟수: 2회


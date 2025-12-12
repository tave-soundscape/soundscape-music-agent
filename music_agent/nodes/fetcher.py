from music_agent.state import AgentState
from music_agent.tools.lastfm import call_lastfm_api


def track_fetcher(state: AgentState):
    print("\n--- [Fetcher] 음악 수집 ---")

    # 기존에 모아둔 곡들은 유지해야 함
    existing_tracks = state.get("candidate_tracks", [])
    seen_ids = {f"{t['artist']}-{t['title']}".lower() for t in existing_tracks}

    new_tracks = []
    queries = state.get("search_queries", {})

    # 쿼리별 수집
    for region, tags in queries.items():
        if not tags: continue
        # region 이름 추출 (korea_tags -> korea)
        region_key = region.replace("_tags", "")

        for tag in tags:
            # 재시도 때는 더 많이 긁어오도록 limit 조절
            tracks = call_lastfm_api(tag, limit=50)
            for t in tracks:
                tid = f"{t['artist']}-{t['title']}".lower()
                if tid not in seen_ids:
                    seen_ids.add(tid)
                    t['region_tag'] = region_key
                    new_tracks.append(t)

    print(f"    신규 수집: {len(new_tracks)}곡 (누적 후보: {len(existing_tracks) + len(new_tracks)}곡)")

    # 기존 후보군 + 신규 후보군 합쳐서 반환
    return {"candidate_tracks": existing_tracks + new_tracks}
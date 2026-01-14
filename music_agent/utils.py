from datetime import datetime
from typing import Optional

def parse_release_date(release_date_str: str) -> Optional[datetime]:
    """
    Spotify release_date 문자열을 datetime 객체로 변환

    Args:
        release_date_str: "YYYY-MM-DD" 또는 "YYYY" 형식의 문자열

    Returns:
        Optional[datetime]: 변환된 datetime 객체, 실패 시 None
    """
    try:
        if len(release_date_str) == 4:  # "YYYY" 형식
            return datetime.strptime(release_date_str, "%Y")
        else:  # "YYYY-MM-DD" 형식
            return datetime.strptime(release_date_str[:10], "%Y-%m-%d")
    except Exception:
        return None


def format_artist_names(artists) -> str:
    """
    아티스트 목록을 쉼표로 구분된 문자열로 변환

    Args:
        artists: Artist 객체 리스트

    Returns:
        str: "Artist1, Artist2, Artist3" 형태의 문자열
    """
    return ", ".join([a.atn for a in artists])


def calculate_percentage(part: int, total: int) -> float:
    """
    백분율 계산 (0으로 나누기 방지)

    Args:
        part: 부분 값
        total: 전체 값

    Returns:
        float: 백분율 (0.0 ~ 1.0)
    """
    return part / total if total > 0 else 0.0


"""장르 카테고리 재정의 모듈.

Kaggle Spotify 데이터셋의 세분화된 ~90여 개 세부 장르(track_genre)는
프론트엔드 선택지로 노출하기엔 너무 많고 직관성이 떨어집니다.
이 모듈은 세부 장르들을 사용자가 고르기 쉬운 10개의 대분류 카테고리로
그룹화하고, 카테고리 ↔ 세부 장르 간 변환 헬퍼를 제공합니다.

- 프론트엔드: 아래 카테고리 `key`(예: "pop", "rock")를 selected_genre 로 전송
- 백엔드: 하드 필터링 시 카테고리를 세부 장르 리스트로 확장하여 조회
"""

# 대분류 카테고리 key -> {한글 라벨, 데이터셋 세부 장르 목록}
GENRE_CATEGORIES: dict[str, dict] = {
    "pop": {
        "label": "팝",
        "genres": [
            "pop", "power-pop", "indie-pop", "k-pop", "j-pop",
            "mandopop", "cantopop", "pop-film", "j-idol",
        ],
    },
    "rock": {
        "label": "록",
        "genres": [
            "rock", "alt-rock", "alternative", "rock-n-roll", "rockabilly",
            "psych-rock", "hard-rock", "grunge", "indie", "j-rock",
            "punk", "punk-rock", "garage", "guitar",
        ],
    },
    "metal": {
        "label": "메탈",
        "genres": [
            "metal", "black-metal", "death-metal", "heavy-metal",
            "metalcore", "hardcore", "industrial",
        ],
    },
    "electronic": {
        "label": "일렉트로닉/EDM",
        "genres": [
            "edm", "electro", "electronic", "house", "deep-house",
            "progressive-house", "chicago-house", "detroit-techno",
            "minimal-techno", "hardstyle", "dubstep", "drum-and-bass",
            "breakbeat", "idm", "club", "dance", "j-dance",
        ],
    },
    "hiphop_rnb": {
        "label": "힙합/R&B",
        "genres": ["hip-hop", "r-n-b", "funk", "groove"],
    },
    "jazz_classical": {
        "label": "재즈/클래식",
        "genres": ["jazz", "classical", "opera", "piano", "new-age"],
    },
    "acoustic_folk": {
        "label": "어쿠스틱/포크",
        "genres": [
            "folk", "country", "bluegrass", "honky-tonk",
            "singer-songwriter", "acoustic",
        ],
    },
    "world": {
        "label": "월드뮤직",
        "genres": [
            "afrobeat", "brazil", "latin", "latino", "salsa", "samba",
            "sertanejo", "pagode", "mpb", "forro", "indian", "iranian",
            "malay", "dub", "german", "french", "british",
        ],
    },
    "mood": {
        "label": "감성/무드",
        "genres": ["ambient", "chill", "happy", "sad", "romance", "party"],
    },
    "soundtrack": {
        "label": "사운드트랙/기타",
        "genres": [
            "anime", "gospel", "disney", "show-tunes",
            "children", "kids", "comedy",
        ],
    },
}

# 세부 장르 -> 카테고리 key 역방향 조회 테이블
_GENRE_TO_CATEGORY: dict[str, str] = {
    genre: key
    for key, info in GENRE_CATEGORIES.items()
    for genre in info["genres"]
}


def list_categories() -> list[dict]:
    """프론트엔드 장르 선택지 렌더링용 카테고리 목록을 반환합니다."""
    return [
        {"key": key, "label": info["label"], "genres": info["genres"]}
        for key, info in GENRE_CATEGORIES.items()
    ]


def resolve_genres(selected: str) -> list[str]:
    """사용자가 보낸 selected_genre 값을 실제 DB 조회용 세부 장르 리스트로 변환합니다.

    - 카테고리 key(예: "pop")  -> 해당 카테고리의 세부 장르 전체
    - 세부 장르(예: "k-pop")   -> 자기 자신만 담은 리스트 (하위 호환)
    - 알 수 없는 값            -> 자기 자신만 담은 리스트 (KNN 폴백에 위임)
    """
    if not selected:
        return []
    key = selected.strip().lower()
    if key in GENRE_CATEGORIES:
        return list(GENRE_CATEGORIES[key]["genres"])
    return [key]

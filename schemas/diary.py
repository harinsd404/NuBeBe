from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List

# 일기 생성 요청 스키마
class DiaryCreate(BaseModel):
    content: str
    selected_genre: str

# 추천 곡 정보 응답 스키마
class SongResponse(BaseModel):
    id: UUID
    spotify_track_id: str
    title: str
    artist: str
    genre: str
    valence: float
    energy: float
    rank: int
    distance: float

    class Config:
        from_attributes = True

# 일기 작성 및 조회 결과 응답 스키마
class DiaryResponse(BaseModel):
    id: UUID
    content: str
    emotion_label: str
    target_valence: float
    target_energy: float
    selected_genre: str
    created_at: datetime
    recommendations: List[SongResponse]

    class Config:
        from_attributes = True

# 아카이브용 일기 요약 응답 스키마
class DiarySummaryResponse(BaseModel):
    id: UUID
    content: str
    emotion_label: str
    created_at: datetime

    class Config:
        from_attributes = True

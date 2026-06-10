import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class MusicDiary(Base):
    __tablename__ = "music_diaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String, nullable=False)
    emotion_label = Column(String, nullable=False)
    target_valence = Column(Float, nullable=False)
    target_energy = Column(Float, nullable=False)
    selected_genre = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 1:N 관계 (일기 하나에 여러 곡이 추천됨)
    recommendations = relationship("DiaryRecommendation", back_populates="music_diary", cascade="all, delete-orphan")

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_track_id = Column(String, nullable=False, unique=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    valence = Column(Float, nullable=False)
    energy = Column(Float, nullable=False)
    
    # 1:N 관계 (한 곡이 여러 일기의 추천으로 등록될 수 있음)
    recommendations = relationship("DiaryRecommendation", back_populates="song")

class DiaryRecommendation(Base):
    __tablename__ = "diary_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diary_id = Column(UUID(as_uuid=True), ForeignKey("music_diaries.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)
    rank = Column(Integer, nullable=False)  # 1위 ~ 5위 순위
    distance = Column(Float, nullable=False)  # KNN 연산으로 계산된 유클리드 거리
    
    # N:1 관계
    music_diary = relationship("MusicDiary", back_populates="recommendations")
    song = relationship("Song", back_populates="recommendations")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from database import get_db
from models.models import MusicDiary, DiaryRecommendation, Song
from schemas.diary import DiaryCreate, DiaryResponse, DiarySummaryResponse, SongResponse
from services.nlp import nlp_service
from services.recommendation import recommendation_service
from services.genres import list_categories

router = APIRouter(tags=["Diaries"])

@router.get("/genres")
def get_genres():
    # 프론트엔드 장르 선택 UI 렌더링용 대분류 카테고리 목록 반환
    return list_categories()

@router.post("/diary", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED)
def create_diary(req: DiaryCreate, db: Session = Depends(get_db)):
    # 1. 자연어 처리(NLP) 및 감정 룰베이스 매핑 진행
    emotion_label, target_valence, target_energy = nlp_service.analyze_emotion(req.content)

    # 2. KNN 추천 서비스를 이용해 최단 거리 상위 5개 곡 추천 리스트 획득
    recommendations = recommendation_service.recommend_songs(
        db=db,
        selected_genre=req.selected_genre,
        target_valence=target_valence,
        target_energy=target_energy
    )

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추천할 음악 데이터를 찾을 수 없습니다. 데이터베이스를 확인해 주세요."
        )

    # 3. 데이터베이스에 일기 저장
    diary = MusicDiary(
        content=req.content,
        emotion_label=emotion_label,
        target_valence=target_valence,
        target_energy=target_energy,
        selected_genre=req.selected_genre
    )
    db.add(diary)
    db.flush()  # diary.id를 획득하기 위해 flush 수행

    # 4. 데이터베이스에 추천 매핑 정보 저장
    rec_models = []
    songs_response = []
    for song, rank, distance in recommendations:
        rec_entry = DiaryRecommendation(
            diary_id=diary.id,
            song_id=song.id,
            rank=rank,
            distance=distance
        )
        rec_models.append(rec_entry)
        db.add(rec_entry)
        
        # 응답 형식을 생성하기 위해 저장
        songs_response.append(
            SongResponse(
                id=song.id,
                spotify_track_id=song.spotify_track_id,
                title=song.title,
                artist=song.artist,
                genre=song.genre,
                valence=song.valence,
                energy=song.energy,
                rank=rank,
                distance=distance
            )
        )

    db.commit()
    db.refresh(diary)

    # 5. 최종 상세 응답 리턴
    return DiaryResponse(
        id=diary.id,
        content=diary.content,
        emotion_label=diary.emotion_label,
        target_valence=diary.target_valence,
        target_energy=diary.target_energy,
        selected_genre=diary.selected_genre,
        created_at=diary.created_at,
        recommendations=songs_response
    )

@router.get("/diary/{diary_id}", response_model=DiaryResponse)
def get_diary(diary_id: UUID, db: Session = Depends(get_db)):
    # 특정 과거 일기 내용 조회
    diary = db.query(MusicDiary).filter(MusicDiary.id == diary_id).first()
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요청하신 ID의 일기를 찾을 수 없습니다."
        )

    # 일기에 연동된 추천 곡 목록 구성
    songs_response = []
    for rec in diary.recommendations:
        songs_response.append(
            SongResponse(
                id=rec.song.id,
                spotify_track_id=rec.song.spotify_track_id,
                title=rec.song.title,
                artist=rec.song.artist,
                genre=rec.song.genre,
                valence=rec.song.valence,
                energy=rec.song.energy,
                rank=rec.rank,
                distance=rec.distance
            )
        )

    return DiaryResponse(
        id=diary.id,
        content=diary.content,
        emotion_label=diary.emotion_label,
        target_valence=diary.target_valence,
        target_energy=diary.target_energy,
        selected_genre=diary.selected_genre,
        created_at=diary.created_at,
        recommendations=songs_response
    )

@router.get("/archive", response_model=List[DiarySummaryResponse])
def get_archive(db: Session = Depends(get_db)):
    # 등록된 모든 일기 요약 정보를 최근 작성 순서대로 조회
    diaries = db.query(MusicDiary).order_by(MusicDiary.created_at.desc()).all()
    return diaries

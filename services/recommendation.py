import logging
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.models import Song
from services.genres import resolve_genres

logger = logging.getLogger(__name__)

class RecommendationService:
    def recommend_songs(self, db: Session, selected_genre: str, target_valence: float, target_energy: float) -> list:
        """
        1차 하드 필터링(장르 매칭) 후, 2차 소프트 필터링(KNN 거리 계산)을 통해
        감정 좌표에 가장 가까운 상위 5개의 곡을 추천합니다.
        반환값: [(Song, rank, distance), ...]
        """
        # 1. 1차 하드 필터링: 선택한 대분류 카테고리를 세부 장르 리스트로 확장하여 곡 선별
        target_genres = resolve_genres(selected_genre)
        candidates = (
            db.query(Song)
            .filter(func.lower(Song.genre).in_([g.lower() for g in target_genres]))
            .all()
        )
        logger.info(
            f"🔍 [Hard Filtering] 카테고리 '{selected_genre}' "
            f"(세부 장르 {len(target_genres)}종) 매칭 곡 수: {len(candidates)}개"
        )

        # 만약 해당 장르의 곡이 부족하다면(5곡 미만), 전체 곡 중에서 매칭되도록 폴백 적용
        if len(candidates) < 5:
            logger.warning(f"⚠️ 장르 '{selected_genre}'에 해당하는 곡이 너무 적습니다. 전체 곡 풀에서 추천을 진행합니다.")
            candidates = db.query(Song).all()

        if not candidates:
            logger.error("❌ 데이터베이스에 곡이 존재하지 않습니다.")
            return []

        # 2. 2차 소프트 필터링: KNN (NearestNeighbors) 수행
        # 오디오 특성 (Valence, Energy) 피처 행렬 구성
        features = np.array([[song.valence, song.energy] for song in candidates])
        
        # KNN 모델 학습 (최대 5개 이웃 설정)
        n_neighbors = min(5, len(candidates))
        knn = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto', metric='euclidean')
        knn.fit(features)

        # 타겟 벡터 설정
        target_vector = np.array([[target_valence, target_energy]])
        
        # 최단 거리 상위 5개 곡 탐색
        distances, indices = knn.kneighbors(target_vector)
        
        recommendations = []
        for i, idx in enumerate(indices[0]):
            song = candidates[idx]
            distance = float(distances[0][i])
            rank = i + 1
            recommendations.append((song, rank, distance))
            logger.info(f"🎵 [Recommended] Rank {rank}: {song.title} - {song.artist} (Genre: {song.genre}, Distance: {distance:.4f})")

        return recommendations

# 싱글톤 인스턴스 생성
recommendation_service = RecommendationService()

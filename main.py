from fastapi import FastAPI
from database import Base, engine
from models.models import MusicDiary, Song, DiaryRecommendation
from routers.diary import router as diary_router

app = FastAPI(title="Nube (누베) API", description="감정 일기 기반 초개인화 음악 추천 서비스 API")

# 테이블 생성
Base.metadata.create_all(bind=engine)

# API 라우터 추가
app.include_router(diary_router)

@app.get("/")
def root():
    return {"message": "Nube API"}
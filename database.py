import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 URL (기본값으로 SQLite 사용, .env에 DATABASE_URL이 있으면 그것을 사용)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# SQLite의 경우 대개 단일 스레드에서만 접근 가능하므로, 멀티스레드 환경(FastAPI)을 위해 check_same_thread 옵션 추가
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB 세션 의존성 주입을 위한 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

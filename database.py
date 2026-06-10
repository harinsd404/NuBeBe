import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# DATABASE_URL이 설정되어 있지 않으면 로컬 SQLite 사용
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./sql_app.db"

try:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
        # 연결 테스트를 수행하여 DB가 연결 가능한지 확인
        with engine.connect() as conn:
            pass
except Exception as e:
    print(f"⚠️ 데이터베이스 연결 실패: {e}")
    print("⚠️ 로컬 개발용 SQLite(sqlite:///./sql_app.db) 데이터베이스로 대체합니다.")
    DATABASE_URL = "sqlite:///./sql_app.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
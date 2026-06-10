import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import uuid
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models.models import Song


def seed():
    # 데이터베이스 테이블 생성 보장
    Base.metadata.create_all(bind=engine)

    print("📖 CSV 파일 읽는 중...")
    df = pd.read_csv("scripts/dataset.csv")

    # 필요한 컬럼만 추출
    df = df[["track_id", "track_name", "artists", "track_genre", "valence", "energy"]]

    # 결측값 제거
    df = df.dropna()
    
    # CSV 자체의 중복 track_id 제거
    df = df.drop_duplicates(subset=["track_id"])

    db: Session = SessionLocal()

    print("🔍 기존 데이터 확인 중...")
    # 기존에 적재된 track_id 목록을 가져옴
    existing_ids = set(r[0] for r in db.query(Song.spotify_track_id).all())

    new_songs = []
    print("⚡ 데이터 가공 중...")
    for _, row in df.iterrows():
        track_id = row["track_id"]
        if track_id in existing_ids:
            continue
            
        song = Song(
            id=uuid.uuid4(),
            spotify_track_id=track_id,
            title=row["track_name"],
            artist=row["artists"],
            genre=row["track_genre"],
            valence=float(row["valence"]),
            energy=float(row["energy"])
        )
        new_songs.append(song)
        existing_ids.add(track_id)

    if new_songs:
        print(f"🚀 {len(new_songs)}개의 곡 데이터를 DB에 적재 중 (Bulk Insert)...")
        batch_size = 5000
        for i in range(0, len(new_songs), batch_size):
            batch = new_songs[i : i + batch_size]
            db.bulk_save_objects(batch)
            db.commit()
            print(f"   - {i + len(batch)} / {len(new_songs)} 완료")
    else:
        print("✨ 새로 추가할 곡이 없습니다.")

    db.close()
    print("✅ 시드 완료")

if __name__ == "__main__":
    seed()
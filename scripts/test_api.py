import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("🚀 API 엔드포인트 통합 테스트 시작\n")

    # --- 1. 루트 엔드포인트 테스트 ---
    print("➡️ [GET /] 루트 엔드포인트 테스트 중...")
    response = client.get("/")
    assert response.status_code == 200, f"Error: {response.status_code}"
    assert response.json() == {"message": "Nube API"}
    print("✅ [GET /] 루트 엔드포인트 통과\n")

    # --- 2. 일기 작성 및 음악 추천 (행복) 테스트 ---
    print("➡️ [POST /diary] 감정 일기 작성 및 음악 추천 테스트 (행복)...")
    payload_happy = {
        "content": "오늘 친구들과 한강에 가서 피크닉을 했는데 너무 행복하고 신나는 하루였어!",
        "selected_genre": "indie"
    }
    response = client.post("/diary", json=payload_happy)
    assert response.status_code == 201, f"Error: {response.status_code} - {response.text}"
    
    data = response.json()
    diary_id = data["id"]
    print(f"   - 생성된 일기 ID: {diary_id}")
    print(f"   - 감정 분석 결과: {data['emotion_label']}")
    print(f"   - 목표 좌표: Valence={data['target_valence']}, Energy={data['target_energy']}")
    print(f"   - 추천받은 곡 개수: {len(data['recommendations'])}")
    
    assert data["emotion_label"] in ["행복 (Joy)", "슬픔 (Sadness)", "분노 (Anger)", "평온 (Neutral)"]
    assert len(data["recommendations"]) == 5
    for song in data["recommendations"]:
        print(f"     * [{song['rank']}위] {song['title']} - {song['artist']} (거리: {song['distance']:.4f})")
    print("✅ [POST /diary] 행복 일기 추천 통과\n")

    # --- 3. 일기 작성 및 음악 추천 (슬픔) 테스트 ---
    print("➡️ [POST /diary] 감정 일기 작성 및 음악 추천 테스트 (슬픔)...")
    payload_sad = {
        "content": "비가 많이 오는데 기분이 너무 우울하고 슬프다... 힘든 하루였어.",
        "selected_genre": "indie"
    }
    response = client.post("/diary", json=payload_sad)
    assert response.status_code == 201
    data_sad = response.json()
    print(f"   - 감정 분석 결과: {data_sad['emotion_label']}")
    print(f"   - 목표 좌표: Valence={data_sad['target_valence']}, Energy={data_sad['target_energy']}")
    print("✅ [POST /diary] 슬픔 일기 추천 통과\n")

    # --- 4. 특정 일기 조회 테스트 ---
    print(f"➡️ [GET /diary/{{diary_id}}] 특정 일기 상세 조회 테스트 (ID: {diary_id})...")
    response = client.get(f"/diary/{diary_id}")
    assert response.status_code == 200
    data_get = response.json()
    assert data_get["id"] == diary_id
    assert data_get["content"] == payload_happy["content"]
    assert len(data_get["recommendations"]) == 5
    print("✅ [GET /diary/{diary_id}] 상세 조회 통과\n")

    # --- 5. 아카이브 목록 조회 테스트 ---
    print("➡️ [GET /archive] 전체 일기 아카이브 조회 테스트...")
    response = client.get("/archive")
    assert response.status_code == 200
    archive_data = response.json()
    print(f"   - 아카이브 내 총 작성 일기 수: {len(archive_data)}개")
    assert len(archive_data) >= 2  # 방금 생성한 행복, 슬픔 일기 포함되어야 함
    print("✅ [GET /archive] 아카이브 조회 통과\n")

    print("🎉 모든 API 엔드포인트 통합 테스트를 성공적으로 통과했습니다!")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as ae:
        print(f"❌ 테스트 실패: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        sys.exit(1)

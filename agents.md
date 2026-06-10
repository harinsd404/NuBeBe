# ☁️ 프로젝트 누베 (Nube) - 시스템 에이전트 및 아키텍처 정의서 (agents.md)

본 문서는 사용자의 자연어 감정 일기 데이터를 기반으로 실시간 초개인화 음악 추천을 수행하는 웹 서비스 **'누베(Nube)'**의 시스템 모듈, 데이터 파이프라인, 그리고 핵심 처리 에이전트(Agents)들의 역할과 상호작용 메커니즘을 정의합니다.

---

## 1. 시스템 개요 및 아키텍처

'누베(Nube)'는 제한된 프로젝트 개발 기간(2주~한 달) 내에 데이터 처리 최적화와 인공지능 알고리즘 결합의 효율성을 극대화하기 위해 설계된 **하이브리드 필터링 추천 시스템**입니다. 무거운 오디오 파일(MP3)을 직접 가공하는 대신, Spotify 메타데이터 파이프라인과 자연어 처리(NLP) 모듈을 유기적으로 연결합니다.

### 시스템 아키텍처 다이어그램 흐름
1. **User** → 일기 작성 및 선호 장르 선택
2. **FastAPI Gateway** → 데이터 수신 및 파이프라인 제어
3. **Hugging Face NLP Agent** → 감정 라벨 분석 및 추출
4. **Vector Mapping Agent** → 감정 라벨을 (Valence, Energy) 타겟 벡터로 변환
5. **Supabase DB Agent** → 1차 SQL Hard Filtering (장르별 곡 선별)
6. **KNN Recommendation Agent** → 2차 Soft Filtering (유클리드 거리 연산 및 Top 5 추출)
7. **FastAPI Gateway** → 최종 결과 및 Spotify Track ID 반환 → **User** 재생

---

## 2. 핵심 에이전트(System Agents) 상세 정의

### 2.1. API 게이트웨이 및 오케스트레이터 (FastAPI Agent)
* **역할**: 클라이언트의 요청을 받아 전체 백엔드 추천 워크플로우를 제어하고 관리하는 중심 컨트롤러입니다.
* **주요 기능**:
  * 엔드포인트 라우팅 (`POST /diaries`, `GET /diaries`)
  * 각 하위 에이전트(Hugging Face, DB, KNN)로의 데이터 전달 및 실행 조율
  * 데이터 유효성 검증 및 예외 처리(Troubleshooting)
  * 비동기 처리를 통한 고성능 동시 요청 수용

### 2.2. 자연어 감성 분석 에이전트 (Hugging Face Agent)
* **역할**: 사용자가 입력한 비정형 텍스트(일기 데이터)에서 내포된 심리 상태와 감정 맥락을 정밀하게 추출합니다.
* **주요 기능**:
  * 사전 학습된 한국어/다국어 감성 분류 모델(예: KoBERT, Multilingual BERT 파이프라인) 로드 및 서빙
  * 일기 텍스트의 다중 클래스 분류 수행
  * **출력 데이터**: 특정 감정 카테고리 라벨 (예: `행복(Joy)`, `슬픔(Sadness)`, `분노(Anger)`, `평온(Neutral)`) 및 신뢰도 스코어

### 2.3. 벡터 매핑 및 차원 변환 에이전트 (Vector Mapping Agent)
* **역할**: NLP 에이전트가 추출한 추상적인 '감정 라벨'을 수학적 연산이 가능한 '다차원 오디오 특성 좌표(Target Vector)'로 매핑합니다.
* **매핑 메커니즘**:
  * **Valence**: 곡의 긍정적/부정적 정서 지수 ($0.0 \sim 1.0$)
  * **Energy**: 곡의 비트감, 빠르기 및 강렬함 지수 ($0.0 \sim 1.0$)
* **룰베이스 매핑 테이블**:
  | 감정 라벨 | Target Valence | Target Energy | 비고 |
  | :--- | :---: | :---: | :--- |
  | **행복 (Joy)** | 0.8 | 0.7 | 밝고 에너제틱한 사운드 매칭 |
  | **슬픔 (Sadness)**| 0.2 | 0.2 | 낮고 차분한 잔잔한 사운드 매칭 |
  | **분노 (Anger)** | 0.3 | 0.8 | 비트가 강하고 격렬한 사운드 매칭 |
  | **평온 (Neutral)** | 0.5 | 0.4 | 편안하고 무난한 배경음악 매칭 |

### 2.4. 데이터베이스 및 쿼리 필터링 에이전트 (Supabase & SQLAlchemy Agent)
* **역할**: 클라우드 인프라(Supabase PostgreSQL)와 SQLAlchemy ORM을 연동하여, 대용량 음악 데이터셋을 효율적으로 관리하고 실시간 조건절 필터링을 수행합니다.
* **주요 기능**:
  * **초기 적재 (Data Seeding)**: Kaggle의 Spotify 11만 곡 메타데이터(CSV)를 시스템 구축 단계에서 DB에 1회 적재하여 서버 파일 I/O 부하 방지.
  * **1차 하드 필터링 (Hard Filtering)**: 사용자가 선택한 음악 분류/장르(예: 힙합, 인디, 록 등)를 바탕으로 `WHERE track_genre = :genre` 쿼리를 수행하여 연산 대상 후보군을 대폭 압축 ($11\text{만 곡} \rightarrow \text{수천 곡 단위}$).
  * **사용자 데이터 영속성 관리**: 작성된 일기, 분석 감정, 추천 플레이리스트 이력을 데이터베이스에 안전하게 기록.

### 2.5. 거리 기반 근접 추천 에이전트 (Scikit-Learn KNN Agent)
* **역할**: 수치화된 감정 좌표와 1차 필터링된 곡들의 오디오 특성 좌표 간의 기하학적 거리를 연산하여, 사용자 기분에 가장 근접한 음악을 도출합니다.
* **주요 기능**:
  * `scikit-learn` 라이브러리의 `NearestNeighbors(n_neighbors=5, algorithm='auto')` 모델 인스턴스 활용
  * **유클리드 거리(Euclidean Distance) 연산 공식**:
    $$Distance = \sqrt{(Valence_{\text{target}} - Valence_{\text{song}})^2 + (Energy_{\text{target}} - Energy_{\text{song}})^2}$$
  * 최단 거리 상위 5개 곡의 인덱스를 계산하여 해당 곡들의 Spotify 고유 `track_id` 리스트 반환.

---

### 3. 데이터베이스 스키마 및 관계 정의 (SQLAlchemy 관계성)
요구사항을 충족하기 위해 `music_diaries`와 `songs` 테이블이 중간 테이블인 `diary_recommendations`를 통해 연결되는 구조로 명확하게 설정되어 있습니다.

 [music_diaries] (1)         [diary_recommendations] (N)         [songs] (1)
+-------------------+       +-----------------------+       +-------------------+
| id (PK, UUID)     |<------+ diary_id (FK)         |       | id (PK, UUID)     |
| content           |       | id (PK, UUID)         |       | spotify_track_id  |
| emotion_label     |       | song_id (FK)          +------>| title             |
| target_valence    |       | rank                  |       | artist            |
| target_energy     |       | distance              |       | genre             |
| selected_genre    |       +-----------------------+       | valence           |
| created_at        |                                       | energy            |
+-------------------+                                       +-------------------+

* **관계성 매커니즘**: 하나의 일기(music_diaries) 작성 시 5개의 맞춤 음악이 추천되므로 1:N 관계가 형성됩니다. 또한 특정 곡(songs)은 여러 추천 기록에 포함될 수 있으므로 이 역시 1:N 관계를 가집니다. `diary_recommendations `테이블이 `diary_id`와 `song_id`를 외래키(ForeignKey)로 참조하여 다대다(M:N) 관계를 해소하고 "어떤 일기에 어떤 곡이 몇 위로 추천되었는지"를 기록합니다.
* **백엔드 매핑**: SQLAlchemy의 relationship 기능을 활용해 music_diary.recommendations, song.recommendations 형태로 상호 참조(Back-populates)가 유기적으로 발생하도록 구현합니다.

---

## 4. 플레이리스트 렌더링 인터페이스 전략

* **MP3 파일 무처리 우회법**: 백엔드는 무거운 음원 바이너리 데이터 대신, 최종 선별된 5곡의 Spotify 고유 식별값(`track_id`)만을 JSON 포맷으로 전달합니다.
* **임베드 위젯(Embed Widget) 연동**: 프론트엔드 단에서 Spotify 공식 Iframe 플레이어 위젯 아키텍처를 호출하여 웹 화면 내에서 추가적인 API 연동 오버헤드 없이 스트리밍(또는 30초 미리듣기)을 원활하게 제공합니다.

---

## 65. API 엔드포인트 명세 (API Endpoints Specification)
본 프로젝트는 유저(User) 식별 과정을 생략하고, 기능의 즉각적인 처리와 데이터 조회에 집중하는 직관적인 REST API를 제공합니다.

### 5.1. 일기 작성 및 맞춤형 음악 추천
* **Method:** `POST`
* **URL:** `/diary`
* **Description:** 사용자의 일기 텍스트와 선호 장르를 입력받아 ML 파이프라인(감정 분석 및 KNN 추천)을 실행합니다. 결과를 DB에 저장함과 동시에 추천된 플레이리스트를 반환합니다.
* **Request Body (JSON):**
  ```json
  {
    "content": "오늘 너무 피곤하고 지치는 하루였어...",
    "selected_genre": "indie"
  }

### 5.2. 특정 일기 및 추천 기록 조회
*	**Method**: `GET`
*	**URL**: `/diary/{diary_id}`
*	**Description**: 발급된 고유 `diary_id`를 기반으로 특정 과거 일기 내용과 당시 추천받았던 음악 리스트(diary_recommendations 조인)를 조회합니다.

### 5.3. 전체 과거 기록 아카이브 조회
*	**Method**: `GET`
*	**URL**: `/archive`
*	**Description**: 서비스에 작성된 전체 과거 일기 기록 목록을 요약하여 반환합니다.
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

# 감정 라벨 매핑 테이블
EMOTION_MAPPING = {
    "기쁨": "행복 (Joy)",
    "슬픔": "슬픔 (Sadness)",
    "분노": "분노 (Anger)",
    "불안": "분노 (Anger)",
    "평온": "평온 (Neutral)",
    "당황": "평온 (Neutral)"
}

# (Valence, Energy) 매핑 테이블
VECTOR_MAPPING = {
    "행복 (Joy)": (0.8, 0.7),
    "슬픔 (Sadness)": (0.2, 0.2),
    "분노 (Anger)": (0.3, 0.8),
    "평온 (Neutral)": (0.5, 0.4)
}

class NLPService:
    def __init__(self):
        self.model_name = "Seonghaa/korean-emotion-classifier-roberta"
        self.classifier = None
        self._load_model()

    def _load_model(self):
        try:
            logger.info("⏳ Hugging Face 감성 분석 모델 로드 중...")
            # text-classification 파이프라인 로드
            self.classifier = pipeline("text-classification", model=self.model_name, device=-1) # CPU 실행 강제
            logger.info("✅ Hugging Face 감성 분석 모델 로드 완료")
        except Exception as e:
            logger.warning(f"⚠️ Hugging Face 모델 로드 실패: {e}")
            logger.warning("⚠️ 키워드 매칭 기반의 룰베이스 감정 분석 모드로 전환합니다.")
            self.classifier = None

    def analyze_emotion(self, content: str) -> tuple:
        """
        일기 텍스트를 받아 감정 라벨과 target (valence, energy) 좌표를 반환합니다.
        반환값: (emotion_label, valence, energy)
        """
        # 1. Hugging Face 모델이 있는 경우 모델을 이용해 추론
        if self.classifier:
            try:
                results = self.classifier(content)
                if results and len(results) > 0:
                    raw_label = results[0]["label"]
                    # 매핑된 감정 가져오기
                    mapped_emotion = EMOTION_MAPPING.get(raw_label, "평온 (Neutral)")
                    valence, energy = VECTOR_MAPPING[mapped_emotion]
                    logger.info(f"🔮 [HF Model] 감정 분석 결과: {raw_label} -> {mapped_emotion} (Valence: {valence}, Energy: {energy})")
                    return mapped_emotion, valence, energy
            except Exception as e:
                logger.error(f"❌ 추론 중 에러 발생: {e}. 룰베이스 매칭으로 전환합니다.")

        # 2. 룰베이스 감정 분석 (폴백)
        # 키워드 매칭
        joy_keywords = ["행복", "기쁨", "좋다", "신나", "즐거", "사랑", "감사", "최고"]
        sad_keywords = ["슬프", "우울", "눈물", "힘들", "지친", "피곤", "외롭", "속상"]
        anger_keywords = ["화나", "분노", "짜증", "스트레스", "미워", "싸웠", "답답"]
        
        content_lower = content.lower()
        
        # 키워드 카운트
        joy_count = sum(1 for kw in joy_keywords if kw in content_lower)
        sad_count = sum(1 for kw in sad_keywords if kw in content_lower)
        anger_count = sum(1 for kw in anger_keywords if kw in content_lower)
        
        if joy_count > sad_count and joy_count > anger_count:
            mapped_emotion = "행복 (Joy)"
        elif sad_count > joy_count and sad_count > anger_count:
            mapped_emotion = "슬픔 (Sadness)"
        elif anger_count > joy_count and anger_count > sad_count:
            mapped_emotion = "분노 (Anger)"
        else:
            mapped_emotion = "평온 (Neutral)"
            
        valence, energy = VECTOR_MAPPING[mapped_emotion]
        logger.info(f"🔮 [Rule-Base] 감정 분석 결과: {mapped_emotion} (Valence: {valence}, Energy: {energy})")
        return mapped_emotion, valence, energy

# 싱글톤 인스턴스 생성
nlp_service = NLPService()

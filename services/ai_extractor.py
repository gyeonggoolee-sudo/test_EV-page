import os
import json
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# .env 파일 로드
load_dotenv()

class AIExtractor:
    def __init__(self):
        # API 키 확인 및 클라이언트 초기화
        api_key = os.getenv("GEMINI_API")
        if not api_key:
            print("Warning: 'GEMINI_API' environment variable is not set.")
        
        # 최신 google-genai 라이브러리 클라이언트 초기화
        self.client = genai.Client(api_key=api_key)

    def extract_from_image(self, image_file):
        """
        이미지 파일(바이트)을 받아 Gemini 모델을 통해 텍스트를 추출합니다.
        """
        try:
            # 1. 이미지 처리 (PIL Image로 변환)
            image = Image.open(image_file)
            
            # 2. 샘플 데이터 정의 (프롬프트에 포함될 예시 - Plain Text)
            selected_sample_data = """
● 공통 : 지원신청서, 구매계약서
※ 개인, 개인사업자, 법인 등의 증빙자료는 신청일 기준 30일 이내 서류여야 함

① (개인) 주민등록등본 또는 초본(전입일 확인 가능한 서류)
② (개인사업자) 주민등록등본, 사업자등록증명원
③ (법인) 법인등기부등본
④ (외국인) 국내거소사실확인서 또는 외국인등록증 등(체류기간 2년 이상 확인 가능 서류)
"""
            
            # 3. 프롬프트 구성
            prompt = f"""이미지 내용을 아래 sample_data와 같은 형식으로 추출하세요.

중요 규칙:
1. '전기자동차 구매 지원신청서' 등 신청서류는 '지원신청서'로만 표기
2. '차량 구매계약서' 등 계약서류는 '구매계약서'로만 표기
3. 그 외 다른 서류들은 이미지에 있는 원래 이름 그대로 상세히 기재 (예: 주민등록등본 또는 초본, 법인등기부등본 등)
4. 응답할 때 "추출한 내용은 다음과 같습니다"와 같은 인사말, 부가 설명, 마크다운 기호를 절대 포함하지 마세요. 
5. 오직 아래 sample_data 포맷에 맞는 텍스트만 그대로 출력하세요.

sample_data:
{selected_sample_data}"""

            # 4. 모델 호출 (최신 라이브러리 문법 사용)
            # contents 리스트에 이미지 객체와 프롬프트 텍스트를 순서대로 전달
            response = self.client.models.generate_content(
                model="gemini-3-flash-preview", # 요청하신 gemini-3-flash-preview 대신 현재 사용 가능한 최신 모델 사용 (필요 시 변경 가능)
                contents=[image, prompt]
            )
            
            # 5. 결과 반환
            return {"status": "success", "text": response.text}

        except Exception as e:
            print(f"AI Extraction Error: {e}")
            return {"status": "error", "message": str(e)}
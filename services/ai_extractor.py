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

    def extract_from_image(self, image_file, doc_type='apply'):
        """
        이미지 파일(바이트)을 받아 Gemini 모델을 통해 텍스트를 추출합니다.
        :param image_file: 업로드된 이미지 파일
        :param doc_type: 'apply'(지원신청서) 또는 'priority'(우선순위)
        """
        try:
            # 1. 이미지 처리 (PIL Image로 변환)
            image = Image.open(image_file)
            
            prompt = ""
            
            if doc_type == 'priority':
                # [우선순위] 샘플 데이터 및 프롬프트
                sample_data_priority = """
● 다자녀가구(만 18세 이하 자녀 2명 이상) - 주민등록등본 또는 가족관계증명서
● 생애최초 차량 구매자 - 지방세 세목별 과세증명서 (조건: 전 생애 자동차세 과세 사실이 없어야 하며 취득세(차량), 등록세(차량), 자동차세(자동차) 세목 필수 선택)
● 취약계층(장애인) - 장애인증 사본
● 취약계층(차상위) - 차상위 계층 증명서, 기초생활 수급자 증명서
● 독립유공자(상이·독립유공자) - 국가유공자 등록증 또는 그 외 증빙가능한 서류
● 소상공인 - 사업자등록증, 소상공인 확인서 (발급처: 중소기업현황정보시스템)
● 노후경유차(이미지 내 노후 전기차) 대체 구매자 - 말소 사실 기재된 자동차등록원부(갑) 또는 자동차 말소등록사실증명서
● 전환지원금 - 차량등록원부(갑부), (폐차)자동차말소사실증명서, (매도)가족관계증명서
"""
                target_items = ['다자녀가구', '생애최초 차량 구매자', '취약계층(장애인)', '취약계층(차상위)', '독립유공자', '소상공인', '노후경유차 대체 구매자', '전환지원금']
                
                prompt = f"""이미지에서 오직 다음 항목들에 해당하는 정보만 추출하세요: {target_items}
각 항목에 대해 정확한 서류, 조건, 그리고 발급처가 명확히 보이도록 정리하세요.

중요 규칙:
1. 엑셀의 한 셀에 들어갈 정보이므로 '**'와 같은 마크다운 강조 기호나 특수 서식을 절대 사용하지 마세요.
2. 오직 평문(Plain Text)으로만 응답하세요. 인사말이나 부가 설명은 절대 포함하지 마세요.
3. 나머지 항목은 결과에 포함하지 마세요. 추출된 정보는 아래의 sample_data 형식을 참고하여 정리하세요:

sample_data:
{sample_data_priority}"""

            else:
                # [기본값: 지원신청서] 샘플 데이터 및 프롬프트
                sample_data_apply = """
● 공통 : 지원신청서, 구매계약서
※ 개인, 개인사업자, 법인 등의 증빙자료는 신청일 기준 30일 이내 서류여야 함

① (개인) 주민등록등본 또는 초본(전입일 확인 가능한 서류)
② (개인사업자) 주민등록등본, 사업자등록증명원
③ (법인) 법인등기부등본
④ (외국인) 국내거소사실확인서 또는 외국인등록증 등(체류기간 2년 이상 확인 가능 서류)
"""
                prompt = f"""이미지 내용을 아래 sample_data와 같은 형식으로 추출하세요.

중요 규칙:
1. '전기자동차 구매 지원신청서' 등 신청서류는 '지원신청서'로만 표기
2. '차량 구매계약서' 등 계약서류는 '구매계약서'로만 표기
3. 그 외 다른 서류들은 이미지에 있는 원래 이름 그대로 상세히 기재 (예: 주민등록등본 또는 초본, 법인등기부등본 등)
4. 응답할 때 "추출한 내용은 다음과 같습니다"와 같은 인사말, 부가 설명, 마크다운 기호를 절대 포함하지 마세요. 
5. 오직 아래 sample_data 포맷에 맞는 텍스트만 그대로 출력하세요.

sample_data:
{sample_data_apply}"""

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
import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API"))


sample_data_지원신청서 = """
● 공통 : 지원신청서, 구매계약서
※ 개인, 개인사업자, 법인 등의 증빙자료는 신청일 기준 30일 이내 서류여야 함

① (개인) 주민등록등본 또는 초본(전입일 확인 가능한 서류)
② (개인사업자) 주민등록등본, 사업자등록증명원
③ (법인) 법인등기부등본
④ (외국인) 국내거소사실확인서 또는 외국인등록증 등(체류기간 2년 이상 확인 가능 서류)
"""

sample_data_지급신청서 = """
1) 지급신청서(제조사) 2) 세금계산서 3) 자동차등록증 4) 통장사본(제조사) 5) 사업자등록증(제조사)
"""

sample_data_우선순위 = """
● 다자녀가구(만 18세 이하 자녀 2명 이상) - 주민등록등본 또는 가족관계증명서
● 생애최초 차량 구매자 - 지방세 세목별 과세증명서 (조건: 전 생애 자동차세 과세 사실이 없어야 하며 취득세(차량), 등록세(차량), 자동차세(자동차) 세목 필수 선택)
● 취약계층(장애인) - 장애인증 사본
● 취약계층(차상위) - 차상위 계층 증명서, 기초생활 수급자 증명서
● 독립유공자(상이·독립유공자) - 국가유공자 등록증 또는 그 외 증빙가능한 서류
● 소상공인 - 사업자등록증, 소상공인 확인서 (발급처: 중소기업현황정보시스템)
● 노후경유차(이미지 내 노후 전기차) 대체 구매자 - 말소 사실 기재된 자동차등록원부(갑) 또는 자동차 말소등록사실증명서
● 전환지원금 - 차량등록원부(갑부), (폐차)자동차말소사실증명서, (매도)가족관계증명서

"""

# 인자값에 따라 sample_data 및 프롬프트 선택
if len(sys.argv) > 1:
    try:
        index = int(sys.argv[1])
        if index == 1:
            selected_sample_data = sample_data_지원신청서
            doc_type = "지원신청서"
            prompt = f"""이미지 내용을 아래 sample_data와 같은 형식으로 추출하세요.
단, 서류 명칭은 다음 규칙을 반드시 따르세요:
1. '전기자동차 구매 지원신청서' 등 신청서류는 '지원신청서'로만 표기
2. '차량 구매계약서' 등 계약서류는 '구매계약서'로만 표기
3. 그 외 다른 서류들은 이미지에 있는 원래 이름 그대로 상세히 기재 (예: 주민등록등본 또는 초본, 법인등기부등본 등)

sample_data:
{selected_sample_data}"""
        elif index == 2:
            selected_sample_data = sample_data_지급신청서
            doc_type = "지급신청서"
            prompt = f"Extract the contents from the image in the same format as the sample_data:\n{selected_sample_data}"
        elif index == 3:
            selected_sample_data = sample_data_우선순위
            doc_type = "우선순위"
            target_items = ['다자녀가구', '생애최초 차량 구매자', '취약계층(장애인)', '취약계층(차상위)', '독립유공자', '소상공인', '노후경유차 대체 구매자', '전환지원금']
            prompt = f"""이미지에서 오직 다음 항목들에 해당하는 정보만 추출하세요: {target_items}
각 항목에 대해 정확한 서류, 조건, 그리고 발급처가 명확히 보이도록 정리하세요.
중요: 엑셀의 한 셀에 들어갈 정보이므로 '**'와 같은 마크다운 강조 기호나 특수 서식을 절대 사용하지 마세요. 오직 평문(Plain Text)으로만 응답하세요.
나머지 항목은 결과에 포함하지 마세요. 추출된 정보는 아래의 sample_data 형식을 참고하여 정리하세요:
{selected_sample_data}"""
        else:
            raise ValueError
    except ValueError:
        print("잘못된 입력입니다. 1(지원신청서), 2(지급신청서), 3(우선순위) 중 하나를 입력하세요.")
        sys.exit(1)
else:
    print("사용법: python main.py <1|2|3>")
    print("1: 지원신청서, 2: 지급신청서, 3: 우선순위")
    sys.exit(1)

print(f"선택된 문서 양식: {doc_type}")

image = Image.open("image.png")
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[image, prompt]
)

print(response.text)
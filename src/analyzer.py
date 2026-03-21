import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# notifier.py에서 get_secret 함수 가져오기
from notifier import get_secret
import os

# 로컬이면 .env에서, 클라우드면 Secret Manager에서 읽어오기
if os.getenv("IS_LOCAL", "true") == "true":
    api_key = os.getenv("OPENAI_API_KEY")
else:
    api_key = get_secret("openai-api-key")

client = OpenAI(api_key=api_key)


def analyze_bug_with_ai(bug_title, bug_description):
    """
    GPT에게 버그를 분석시키는 함수.

    Args:
        bug_title (str): 버그 제목
        bug_description (str): 버그 상세 설명

    Returns:
        dict: 분석 결과 {"severity", "type", "reason", "action"}
    """

    # 프롬프트 엔지니어링
    # GPT에게 역할과 출력 형식을 명확히 지정는 것이 중요
    prompt = f"""
    당신은 시니어 개발자입니다. 아래 버그를 분석하고 심각도를 판단해주세요.

    버그 제목: {bug_title}
    버그 설명: {bug_description}

    반드시 아래 JSON 형식으로만 답변해주세요. 다른 말은 하지 마세요:
    {{
        "severity": "Critical 또는 Major 또는 Minor 중 하나",
        "type": "버그 유형 (예: 결제 오류, UI 이슈, 성능 문제, 로그인 오류 등)",
        "reason": "이 심각도로 판단한 이유를 한 줄로",
        "action": "담당자에게 전달할 행동 지침"
    }}

    심각도 기준:
    - Critical: 서비스 중단, 결제 오류, 데이터 손실 등 즉시 해결 필요
    - Major: 주요 기능 오류, 오늘 중으로 해결 필요
    - Minor: UI 이슈, 사소한 오류, 시간 날 때 해결 가능
    """

    # GPT API 호출
    # 개념: messages 리스트
    # - system: GPT의 역할 설정 (배경 지식)
    # - user: 실제 질문 내용
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "당신은 버그 심각도를 분석하는 시니어 개발자입니다. 반드시 JSON 형식으로만 답변합니다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1  # 개념: temperature = 창의성 조절 (0에 가까울수록 일관된 답변)
    )

    # GPT 응답에서 텍스트 꺼내기
    result_text = response.choices[0].message.content

    # 개념: JSON 파싱
    # GPT가 문자열로 준 답변을 파이썬 딕셔너리로 변환
    result = json.loads(result_text)

    return result


def get_alert_format(analysis):
    """
    분석 결과에 따라 Discord 알림 형식을 결정하는 함수.

    Args:
        analysis (dict): analyze_bug_with_ai()의 반환값

    Returns:
        dict: Discord 알림 형식
            - color (int): 알림 색상 코드
            - title_prefix (str): 제목 앞에 붙는 심각도 표시
            - action_msg (str): 행동 지침 메시지
    """
    severity = analysis["severity"]

    if severity == "Critical":
        return {
            "color": 0xe74c3c,       # 빨간색
            "title_prefix": "🚨 [CRITICAL]",
            "action_msg": "⚡ 즉시 확인해주세요"
        }
    elif severity == "Major":
        return {
            "color": 0xf39c12,       # 주황색
            "title_prefix": "⚠️ [MAJOR]",
            "action_msg": "오늘 중으로 확인해주세요"
        }
    else:  # Minor
        return {
            "color": 0x3498db,       # 파란색
            "title_prefix": "ℹ️ [MINOR]",
            "action_msg": "급하진 않아요, 시간 날 때 확인해주세요~!"
        }
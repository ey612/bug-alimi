import sys
import os

# src 폴더 안에서 같은 폴더의 파일을 불러오기 위한 경로 설정
sys.path.append(os.path.dirname(__file__))

from analyzer import analyze_bug_with_ai, get_alert_format
from notifier import send_webhook_message


def run_bug_alert(bug_title, bug_description):
    """버그 분석부터 Discord 전송까지 전체 흐름을 실행하는 함수.

    Args:
        bug_title (str): 버그 제목
        bug_description (str): 버그 상세 설명

    Returns:
        None
    """
    print(f"\n 버그 분석 시작: {bug_title}")
    print("=" * 50)

    # 1. GPT로 버그 분석
    print("🤖 AI 분석 중...")
    analysis = analyze_bug_with_ai(bug_title, bug_description)

    print(f"✅ 분석 완료!")
    print(f"   심각도: {analysis['severity']}")
    print(f"   유형: {analysis['type']}")
    print(f"   이유: {analysis['reason']}")

    # 2. 알림 형식 결정
    alert_format = get_alert_format(analysis)

    # 3. Discord 전송
    send_webhook_message(
        title=f"{alert_format['title_prefix']} {bug_title}",
        description=f"**설명:** {bug_description}\n\n**AI 분석:** {analysis['reason']}",
        color=alert_format["color"],
        fields=[
            {
                "name": "🐛 버그 유형",
                "value": analysis["type"],
                "inline": True
            },
            {
                "name": "🕵🏻 행동 지침",
                "value": f"{alert_format['action_msg']}",
                "inline": True
            }
        ]
    )


if __name__ == "__main__":
    # 테스트용 버그 입력
    # 나중에 GitHub Issues 연동 시 여기서 데이터를 받아와요
    run_bug_alert(
        bug_title="결제 버튼 클릭 시 앱 크래시",
        bug_description="메인 화면에서 결제하기 버튼 클릭 시 앱이 강제 종료됨. 재현율 100%"
    )
import os
import sys
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# 같은 src 폴더의 파일 불러오기
sys.path.append(os.path.dirname(__file__))

from analyzer import analyze_bug_with_ai, get_alert_format
from notifier import send_webhook_message

# 개념: Flask 앱 생성
# Flask = 파이썬으로 만드는 웹 서버
# Jira가 우리 코드에 신호를 보낼 수 있도록 "문"을 열어주는 역할
app = Flask(__name__)


@app.route("/jira-webhook", methods=["POST"])
def jira_webhook():
    """Jira에서 신호가 오면 실행되는 함수.

    Args:
        없음 (Jira가 자동으로 데이터를 보내줘요)

    Returns:
        json: 처리 결과 메시지
    """
    # 개념: request.json
    # Jira가 보내준 데이터를 파이썬 딕셔너리로 받아요
    data = request.json
    print(f"\n 받은 데이터 전체: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if not data:
        return jsonify({"status": "error", "message": "데이터 없음"}), 400

    # Jira 이슈 데이터에서 필요한 정보 꺼내기
    issue = data.get("issue", data)
    fields = issue.get("fields", issue)

    bug_title = (
        fields.get("summary") or
        issue.get("summary") or
        data.get("summary", "제목 없음")
    )

    bug_description_raw = (
        fields.get("description") or
        issue.get("description") or
        data.get("description", "설명 없음")
    )

    # ADF 형식이면 텍스트 추출
    if isinstance(bug_description_raw, dict):
        bug_description = extract_text_from_adf(bug_description_raw)
    else:
        bug_description = bug_description_raw or "설명 없음"

    print(f"\n Jira 티켓 수신: {bug_title}")

    # GPT 분석
    print("🤖 AI 분석 중...")
    analysis = analyze_bug_with_ai(bug_title, bug_description)

    print(f"✅ 분석 완료! 심각도: {analysis['severity']}")

    # Discord 알림 형식 결정
    alert_format = get_alert_format(analysis)

    # Jira 티켓 URL 생성
    issue_key = issue.get("key", "")
    jira_domain = os.getenv("JIRA_DOMAIN")
    ticket_url = f"{jira_domain}/browse/{issue_key}"

    # Discord 알림 전송
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
                "name": "📋 행동 지침",
                "value": alert_format["action_msg"],
                "inline": True
            },
            {
                "name": "🔗 Jira 티켓",
                "value": ticket_url,
                "inline": False
            }
        ]
    )

    return jsonify({"status": "success"}), 200


def extract_text_from_adf(adf):
    """Jira ADF 형식에서 텍스트만 추출하는 함수.

    Args:
        adf (dict): Jira Atlassian Document Format 데이터

    Returns:
        str: 추출된 텍스트
    """
    # 개념: ADF (Atlassian Document Format)
    # Jira가 텍스트를 저장하는 특수 형식이에요
    # {"type": "doc", "content": [{"type": "paragraph", "content": [...]}]}
    texts = []

    def extract(node):
        if isinstance(node, dict):
            if node.get("type") == "text":
                texts.append(node.get("text", ""))
            for child in node.get("content", []):
                extract(child)

    extract(adf)
    return " ".join(texts)


if __name__ == "__main__":
    print("=" * 50)
    print(" 버그알리미 Jira Webhook 서버 시작!")
    print("=" * 50)
    # 개념: debug=True = 코드 수정 시 서버 자동 재시작
    # port=5000 = 5000번 문으로 신호를 받겠다는 의미
    app.run(debug=True, port=5000)
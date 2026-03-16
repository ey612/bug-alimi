import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# tests 폴더에서 src 폴더의 파일을 불러오기 위한 경로 설정
# 개념: sys.path.append = 파이썬에게 "여기서도 파일 찾아봐" 라고 알려주는 것
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzer import analyze_bug_with_ai, get_alert_format


class TestAnalyzeBugWithAI(unittest.TestCase):
    """analyze_bug_with_ai() 함수 테스트."""

    @patch("analyzer.client.chat.completions.create")
    def test_critical_bug(self, mock_create):
        """결제 오류 버그 → Critical 분류되는지 테스트."""

        # 가짜 GPT 응답 만들기 (가짜 == Mock)
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "severity": "Critical",
            "type": "결제 오류",
            "reason": "결제 시스템 장애는 매출에 직결됩니다",
            "action": "1시간 이내 해결 필요"
        })
        mock_create.return_value = mock_response

        result = analyze_bug_with_ai(
            bug_title="결제 버튼 클릭 시 앱 크래시",
            bug_description="결제 페이지에서 앱이 강제 종료됨. 재현율 100%"
        )

        # 개념: assertEqual = "이 값이 저 값과 같아야 테스트 통과"
        self.assertEqual(result["severity"], "Critical")
        self.assertEqual(result["type"], "결제 오류")

    @patch("analyzer.client.chat.completions.create")
    def test_minor_bug(self, mock_create):
        """UI 이슈 버그 → Minor 분류되는지 테스트."""

        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "severity": "Minor",
            "type": "UI 이슈",
            "reason": "기능에는 영향 없는 시각적 문제입니다",
            "action": "시간 날 때 확인해주세요"
        })
        mock_create.return_value = mock_response

        result = analyze_bug_with_ai(
            bug_title="버튼 색상이 디자인과 다름",
            bug_description="메인 화면 버튼 색상이 잘못됨"
        )

        self.assertEqual(result["severity"], "Minor")
        self.assertEqual(result["type"], "UI 이슈")

    @patch("analyzer.client.chat.completions.create")
    def test_invalid_json_response(self, mock_create):
        """GPT가 JSON이 아닌 답변을 줄 때 에러 처리되는지 테스트."""

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "죄송합니다, 분석할 수 없습니다. 파일 형식을 확인해주세요."
        mock_create.return_value = mock_response

        # 개념: assertRaises = "이 에러가 발생해야 테스트 통과"
        with self.assertRaises(Exception):
            analyze_bug_with_ai("테스트", "테스트 설명")


class TestGetAlertFormat(unittest.TestCase):
    """get_alert_format() 함수 테스트."""

    def test_critical_format(self):
        """Critical → 빨간색, 🚨 prefix 인지 테스트."""
        analysis = {"severity": "Critical"}
        result = get_alert_format(analysis)

        self.assertEqual(result["color"], 0xe74c3c)
        self.assertIn("CRITICAL", result["title_prefix"])

    def test_major_format(self):
        """Major → 주황색, ⚠️ prefix 인지 테스트."""
        analysis = {"severity": "Major"}
        result = get_alert_format(analysis)

        self.assertEqual(result["color"], 0xf39c12)
        self.assertIn("MAJOR", result["title_prefix"])

    def test_minor_format(self):
        """Minor → 파란색, ℹ️ prefix 인지 테스트."""
        analysis = {"severity": "Minor"}
        result = get_alert_format(analysis)

        self.assertEqual(result["color"], 0x3498db)
        self.assertIn("MINOR", result["title_prefix"])
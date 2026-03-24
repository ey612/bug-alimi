# 버그알리미 (Bug-Alimi)

> Jira에 버그 티켓이 등록되면 AI가 심각도를 자동 분석하고 Discord로 즉시 알림을 보내주는 자동화 시스템

## 주요 기능

- Jira 자동 감지: 버그 티켓 등록 즉시 Webhook으로 수신
- AI 심각도 분석: GPT-4o-mini가 제목·설명·우선순위를 바탕으로 자동 판단
- 3단계 심각도 분류: Critical / Major / Minor
- Discord 자동 알림: 심각도에 따라 색상과 행동 지침이 다른 알림 전송
- 24시간 운영: Google Cloud Run 서버리스 배포로 컴퓨터가 꺼져도 동작
- 안정적인 재시도: 네트워크 오류 시 최대 3번 재시도

## 심각도 기준

| 심각도 | 색상 | 기준 | 행동 지침 |
|--------|------|------|----------|
| Critical | 🔴 빨간색 | 서서비스 중단, 결제 오류, 데이터 손실 | 즉시 해결 |
| Major | 🟠 주황색 | 주요 기능 오류 | 오늘 중으로 해결 |
| Minor | 🔵 파란색 | UI 이슈, 사소한 오류 | 시간 날 때 해결 |

## 사용 기술

- **Python 3.11**
- **OpenAI API** (gpt-4o-mini) - 버그 심각도 분석
- **Discord Webhook API** - 알림 전송
- **이슈 트래커** - Jira Webhook
- **클라우드** - Google Cloud Run
- **환경 변수** - Google Cloud Secret Manager



## 프로젝트 구조
```
bug-alimi/
├── src/
│   ├── jira_webhook.py  # Flask 서버 — Jira Webhook 수신 및 파싱
│   ├── analyzer.py      # AI 분석 — GPT 심각도 판단
│   ├── notifier.py      # 알림 전송 — Discord Webhook
│   └── main.py          # 로컬 테스트용 진입점
├── tests/
│   └── test_analyzer.py # 단위 테스트
├── Dockerfile           # 컨테이너 빌드 설정
├── .env.example         # 로컬 환경변수 예시
├── requirements.txt     # 의존성 목록
└── README.md
```

# 🐛 버그알리미 (Bug-Alimi)

> AI가 버그를 분석하고 심각도에 따라 Discord로 자동 알림을 보내주는 봇

## ✨ 주요 기능

- **AI 버그 분석**: GPT-4o-mini가 버그 심각도를 자동 판단
- **3단계 심각도 분류**: Critical / Major / Minor
- **Discord 자동 알림**: 심각도에 따라 색상과 문구가 다른 알림 전송
- **안정적인 재시도**: 네트워크 오류 시 최대 3번 재시도

## 🚨 심각도 기준

| 심각도 | 색상 | 기준 | 행동 지침 |
|--------|------|------|----------|
| Critical | 🔴 빨간색 | 서비스 중단, 결제 오류, 데이터 손실 | 1시간 이내 해결 |
| Major | 🟠 주황색 | 주요 기능 오류 | 오늘 중으로 해결 |
| Minor | 🔵 파란색 | UI 이슈, 사소한 오류 | 시간 날 때 해결 |

## 🛠️ 사용 기술

- **Python 3.x**
- **OpenAI API** (gpt-4o-mini) - 버그 심각도 분석
- **Discord Webhook API** - 알림 전송
- **requests** - HTTP 통신
- **python-dotenv** - 환경변수 관리

## 📁 프로젝트 구조
```
bug-alimi/
├── src/
│   ├── analyzer.py      # GPT 버그 분석 함수
│   ├── notifier.py      # Discord 웹훅 전송 함수
│   └── main.py          # 전체 흐름 연결 진입점
├── tests/
│   └── test_analyzer.py # 단위 테스트
├── .env.example         # 환경변수 예시
├── requirements.txt     # 필요 라이브러리
└── README.md
```

## 📋 설치 및 실행

### 1. 레포지토리 클론
```bash
git clone https://github.com/본인아이디/bug-alimi.git
cd bug-alimi
```

### 2. 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env.example` 파일을 복사해서 `.env` 파일 생성 후 값 입력
```
DISCORD_WEBHOOK_URL=디스코드_웹훅_URL
OPENAI_API_KEY=오픈AI_API_키
```

### 4. 실행
```bash
python src/main.py
```

## 🧪 테스트 실행
```bash
pytest tests/test_analyzer.py -v
```

## 🔧 동작 흐름
```
버그 발생
    ↓
버그 제목 / 설명 입력
    ↓
GPT-4o-mini 심각도 분석
    ↓
Critical / Major / Minor 분류
    ↓
Discord 채널 알림 전송 🔔
```

## 🚀 향후 계획

- [ ] Jira 연동 - 티켓 등록 시 자동 분석 및 알림
- [ ] GitHub Issues 연동
- [ ] 웹 대시보드 추가

## ⚠️ 주의사항

- `.env` 파일은 절대 깃에 올리지 마세요
- OpenAI API 사용 시 소량의 비용이 발생합니다 (버그 1건당 약 1원 미만)

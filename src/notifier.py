import os
from dotenv import load_dotenv

load_dotenv()

import time
import requests
from datetime import datetime
import pytz

TEST_MODE = False
WEEKEND_OFF = True

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

if not WEBHOOK_URL:
    raise ValueError("오류: .env 파일에 DISCORD_WEBHOOK_URL이 없습니다!")


KST = pytz.timezone('Asia/Seoul')

MAX_RETRIES = 3
RETRY_DELAY = 5


def send_webhook_message(title, description, color, fields=None):
    
    # 주말 체크
    # weekday(): 월요일=0, 화요일=1, ... 토요일=5, 일요일=6
    if WEEKEND_OFF:
        today = datetime.now(KST).weekday()
        if today in [5, 6]:  # 토요일(5), 일요일(6)
            print(f"주말이라 알림 건너뜀: {title}")
            return
    
    if TEST_MODE:
        # 테스트 모드: 터미널에만 출력
        print("\n" + "="*60)
        print(f" [시뮬레이션] Discord 알림")
        print("="*60)
        print(f" 제목: {title}")
        print(f" 내용: {description}")
        print(f" 색상: {hex(color)}")
        print(f" 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}")
        if fields:
            print(f" 추가 필드:")
            for field in fields:
                print(f"   • {field['name']}: {field['value']}")
        print("="*60)
        print("(테스트 모드: 실제로는 전송 안 됨)")
        return True
    else:
        # 실제 모드: Discord에 전송 (재시도 로직 추가)
        # embed: Discord의 메시지 형식
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.now(KST).isoformat(),  # ISO 형식 시간
            "footer": {"text": "버그 알림 - Bug Alimi"}
        }
        
        if fields:
            embed["fields"] = fields
        
        # JSON 형식으로 데이터 준비
        data = {"embeds": [embed]}
        
        # 재시도 로직
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"\n 전송 시도 {attempt}/{MAX_RETRIES}: {title}")
                
                # HTTP POST 요청으로 Discord에 전송
                response = requests.post(WEBHOOK_URL, json=data, timeout=10)
                
                # 204: 성공 (No Content - Discord가 성공 시 보내는 코드)
                if response.status_code == 204:
                    print(f" 전송 완료!")
                    return True
                else:
                    print(f"  응답 코드: {response.status_code}")
                    
                    # 마지막 시도가 아니면 재시도
                    if attempt < MAX_RETRIES:
                        print(f"⏳ {RETRY_DELAY}초 후 재시도...")
                        time.sleep(RETRY_DELAY)
                    else:
                        print(f" {MAX_RETRIES}번 시도 후 실패")
                        return False
                        
            except requests.exceptions.Timeout:
                # 타임아웃: 서버 응답이 너무 느림
                print(f" 타임아웃 발생 (10초 초과)")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
            except requests.exceptions.ConnectionError:
                # 연결 오류: 인터넷 끊김 등
                print(f" 연결 오류 발생")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
            except Exception as e:
                # 기타 모든 오류
                print(f" 알 수 없는 오류: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
        
        return False

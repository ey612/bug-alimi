import os
from dotenv import load_dotenv

load_dotenv()

import time
import requests
from datetime import datetime
import pytz

from google.cloud import secretmanager

def get_secret(secret_id):
    """Secret Manager에서 비밀값을 가져오는 함수.
    
    Args:
        secret_id (str): Secret Manager에 등록한 이름
        
    Returns:
        str: 비밀값
    """
    # 개념: Secret Manager 클라이언트
    # GCP 금고와 대화하는 창구를 만드는 것
    client = secretmanager.SecretManagerServiceClient()
    
    # 개념: 프로젝트 ID를 환경변수로 읽어오기
    # 코드에 직접 쓰지 않아야 다른 프로젝트에서도 재사용 가능
    project_id = os.getenv("GCP_PROJECT_ID")
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    response = client.access_secret_version(request={"name": name})
    
    # 개념: .strip()
    # 앞뒤 공백/줄바꿈 제거
    return response.payload.data.decode("UTF-8").strip()

# 로컬이면 .env에서, 클라우드면 Secret Manager에서 읽어오기
# 개념: 환경변수 IS_LOCAL로 실행 환경을 구분
if os.getenv("IS_LOCAL", "true") == "true":
    WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
else:
    WEBHOOK_URL = get_secret("discord-webhook-url")

if not WEBHOOK_URL:
    raise ValueError("오류: DISCORD_WEBHOOK_URL을 찾을 수 없습니다!")


KST = pytz.timezone('Asia/Seoul')

MAX_RETRIES = 3
RETRY_DELAY = 5


def send_webhook_message(title, description, color, fields=None):

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

# test_connection.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "버그 분석 봇 테스트입니다. '연결 성공!'이라고만 답해주세요."}
    ]
)

print(response.choices[0].message.content)
# 출력: 연결 성공!
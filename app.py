from flask import Flask, redirect, request, session
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or "임시_비밀키"  # 세션 암호화용 키

# 환경 변수
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://llm-calender-app.onrender.com/oauth2callback"

@app.route("/")
def home():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=https://www.googleapis.com/auth/calendar.events"
        "&access_type=offline"
        "&prompt=consent"
    )
    return f'<a href="{google_auth_url}"> Google 계정으로 로그인하기</a>'

@app.route("/oauth2callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return "인증 코드가 없습니다"

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    r = requests.post(token_url, data=data)
    token_response = r.json()

    access_token = token_response.get("access_token")
    if not access_token:
        return f"토큰 요청 실패: {token_response}"

    # ✅ access_token을 Flask 세션에 저장
    session["access_token"] = access_token

    return "인증 성공! access_token이 세션에 저장되었습니다."

@app.route("/calendar")
def use_calendar():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/")  # 인증 안되어 있으면 로그인 페이지로

    # 예시: 캘린더 리스트 가져오기
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)
    
    if response.status_code == 200:
        return f"캘린더 목록: {response.json()}"
    else:
        return f"API 요청 실패: {response.text}"

from flask import Flask, redirect, request, session
from dotenv import load_dotenv
import os
import requests
import urllib.parse

if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv("Secret.env")

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
        return "인증 코드가 없습니다."

    print("🔍 CODE:", code)
    print("🔍 CLIENT_ID:", CLIENT_ID)
    print("🔍 CLIENT_SECRET:", CLIENT_SECRET)
    print("🔍 REDIRECT_URI:", REDIRECT_URI)

    if not CLIENT_ID or not CLIENT_SECRET:
        return "환경변수가 None입니다."

    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    body = urllib.parse.urlencode({
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    })

    try:
        r = requests.post("https://oauth2.googleapis.com/token", headers=headers, data=body, timeout=10)
        r.raise_for_status()
        token_response = r.json()
    except requests.exceptions.RequestException as e:
        return f"""
        토큰 요청 실패<br>
        에러: {e}<br>
        응답: {r.text if 'r' in locals() else '없음'}
        """

    return f"access_token: {token_response.get('access_token')}"



@app.route("/calendar")
def use_calendar():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/")  # 인증 안되어 있으면 로그인 페이지로

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)
    
    if response.status_code == 200:
        return f"캘린더 목록: {response.json()}"
    else:
        return f"API 요청 실패: {response.text}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

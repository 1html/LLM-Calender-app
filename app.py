from flask import Flask

app = Flask(__name__)

CLIENT_ID = os.environ.get("274904192004-eoe4u9qbl69ln215s3q4ragu9a7b04n8.apps.googleusercontent.com") or "너의 클라이언트 ID"
CLIENT_SECRET = os.environ.get("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") or "너의 클라이언트 Secret"
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
    return f'<a href="{google_auth_url}">📅 Google 계정으로 로그인하기</a>'

@app.route("/oauth2callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return "❌ 인증 코드가 없습니다"

    # 3. 코드로 Access Token 요청
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
        return f"❌ 토큰 요청 실패: {token_response}"

    return f"✅ 인증 성공! 액세스 토큰: {access_token}"

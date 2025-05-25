from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "서버가 정상적으로 작동 중입니다!"

@app.route("/oauth2callback")
def oauth_callback():
    return "여기가 Google 로그인 이후 리디렉션되는 콜백 주소입니다."

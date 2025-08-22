import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
from dotenv import load_dotenv

# load .env jika testing lokal
load_dotenv()

app = Flask(__name__)

# LINE credentials
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("2007965823")
LINE_CHANNEL_SECRET = os.getenv("94d4452f8935875e4c54dfdf3e7de9ab")

# DeepL API
DEEPL_API_KEY = os.getenv("96b1f3df-6814-4bfd-9607-903e9457b061:fx")
DEEPL_BASE = "https://api-free.deepl.com/v2/translate"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Fungsi translate DeepL
def translate_text(text, target_lang):
    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"}
    data = {"text": text, "target_lang": target_lang}
    resp = requests.post(DEEPL_BASE, headers=headers, data=data)
    result = resp.json()
    return result["translations"][0]["text"]

# Deteksi bahasa sederhana (Chinese vs EN/ID)
def detect_language(text):
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return "ZH"
    else:
        return "EN/ID"

# Endpoint webhook
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# Event handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    lang = detect_language(user_text)

    if lang == "ZH":
        translated = translate_text(user_text, "EN")
    else:
        translated = translate_text(user_text, "ZH")

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=translated)
    )

if __name__ == "__main__":
    app.run(port=5000)

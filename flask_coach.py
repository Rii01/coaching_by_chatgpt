import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
# import ngrok

# listener = ngrok.forward("localhost:8080")
# print(f"Ingress established at {listener.url()}")

app = Flask(__name__)

# SlackとOpenAIのAPIキーを環境変数から取得
slack_token = os.getenv("SLACK_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = WebClient(token=slack_token)

# Slackイベントを処理するエンドポイント
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    if "event" in data:
        event_data = data["event"]
        
        if event_data.get("type") == "message" and not event_data.get("bot_id"):
            user_message = event_data.get("text")
            channel_id = event_data.get("channel")
            
            # ChatGPTにメッセージを送信
            response_text = get_chatgpt_response(user_message)
            
            try:
                # Slackに返信
                client.chat_postMessage(channel=channel_id, text=response_text)
            except SlackApiError as e:
                print(f"Error posting message: {e.response['error']}")
    
    return "OK", 200

# ChatGPTからの応答を取得
def get_chatgpt_response(user_message):
    try:
        response = openai.Completion.create(
            #model="text-davinci-003",  # ここでモデルを指定
            model="GPT-3.5-Turbo-0125",
            prompt=user_message,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(port=3000)

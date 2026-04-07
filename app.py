from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__, static_folder='static')

client = OpenAI(
    api_key="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",
    base_url="https://integrate.api.nvidia.com/v1"
)

def get_bot_reply(message):
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": """You are a friendly gym assistant chatbot. Help users with:
- Membership plans (Basic ₹999/mo, Standard ₹1499/mo, Premium ₹1999/mo with personal training)
- Free 1-day trial booking (ask for name + phone)
- Location & timings (Mon-Sat 6AM-10PM, Sunday 8AM-2PM)
- Connecting with a trainer (goals: weight loss, muscle gain, fitness)
Keep responses concise, use emojis, and be enthusiastic about fitness! 💪"""
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Sorry, I'm having trouble right now. Please try again! (Error: {str(e)})"

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    reply = get_bot_reply(user_message)
    return jsonify({"reply": reply})

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg:
        reply = get_bot_reply(incoming_msg)
        msg.body(reply)
    else:
        msg.body("👋 Hey! Send me a message and I'll help you with gym info, memberships & more! 💪")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

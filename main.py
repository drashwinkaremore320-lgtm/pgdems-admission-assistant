from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import os
import requests

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "pgdems_verify_123")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v26.0")


@app.get("/")
def home():
    return {"status": "PGDEMS Admission Assistant is running"}


@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(default=None, alias="hub.mode"),
    hub_verify_token: str = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str = Query(default=None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("Verification failed", status_code=403)


@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    print("WhatsApp message received:")
    print(data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        sender = message["from"]

        reply_text = (
            "👋 Welcome to PGDEMS Admission Assistant!\n\n"
            "How can I help you?\n\n"
            "1️⃣ PGDEMS Course Details\n"
            "2️⃣ Eligibility\n"
            "3️⃣ Fees & Admission\n"
            "4️⃣ Course Duration\n"
            "5️⃣ Talk to a Counsellor\n\n"
            "Please reply with 1, 2, 3, 4 or 5."
        )

        url = (
            f"https://graph.facebook.com/"
            f"{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
        )

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": sender,
            "type": "text",
            "text": {
                "body": reply_text
            },
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=20,
        )

        print("WhatsApp reply status:", response.status_code)
        print("WhatsApp reply response:", response.text)

    except Exception as e:
        print("Error processing WhatsApp message:", str(e))

    return {"status": "received"}

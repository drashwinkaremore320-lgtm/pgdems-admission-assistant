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
    @app.get("/privacy-policy")
def privacy_policy():
    return PlainTextResponse(
        """
        PRIVACY POLICY – PGDEMS ADMISSION ASSISTANT

        This Privacy Policy explains how PGDEMS Admission Assistant handles information
        provided by users through WhatsApp.

        1. Information We May Collect
        We may receive information such as your name, WhatsApp phone number, messages,
        course preferences, eligibility information, and admission-related inquiries.

        2. How We Use Information
        Information is used only to respond to PGDEMS course inquiries, provide admission
        information, assist with counselling, and follow up regarding admission enquiries.

        3. Sharing of Information
        We do not sell personal information. Information may be accessed by authorised
        staff or service providers only when required to provide admission assistance
        and related services.

        4. Data Security
        Reasonable technical and organisational measures are used to protect information
        from unauthorised access, alteration, disclosure, or destruction.

        5. Data Retention
        Information is retained only for as long as reasonably necessary for admission
        assistance, counselling, administrative, or legal purposes.

        6. User Rights
        Users may request correction or deletion of information provided through the
        admission assistant, subject to applicable legal and administrative requirements.

        7. Contact
        For privacy-related questions or requests, please contact the PGDEMS Admission
        Assistant administration.

        8. Changes to this Policy
        This Privacy Policy may be updated from time to time. The latest version will
        be available at this URL.
        """
    )


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

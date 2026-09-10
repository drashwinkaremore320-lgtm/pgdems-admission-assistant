from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import os

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "pgdems_verify_123")


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

    return {"status": "received"}

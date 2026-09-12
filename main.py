from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import os
import requests

app = FastAPI()
user_state = {}

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
        message_text = message.get("text", {}).get("body", "").strip().lower()
    # Handle counsellor information submitted by the user
    if user_state.get(sender) == "counsellor":
        reply_text = (
            "✅ Thank you for sharing your details.\n\n"
            "Our admission counsellor will contact you shortly "
            "regarding PGDEMS course details, eligibility, fees and admission.\n\n"
            "📲 For direct assistance: 8830639520\n\n"
            "Type MENU to return to the main menu."
        )
        user_state.pop(sender, None)

    elif message_text in ["1", "course", "course details"]:
        reply_text = (
                "📚 PGDEMS Course Details\n\n"
                "Post Graduate Diploma in Emergency Medical Services (PGDEMS) "
                "is designed to provide structured learning in emergency medical care.\n\n"
                "For complete course details, please choose an option from the main menu "
                "or type MENU."
            )

        elif message_text in ["2", "eligibility"]:
            reply_text = (
                 "🎓 PGDEMS ELIGIBILITY\n\n"
                 "👨‍⚕️ ELIGIBLE CANDIDATES\n"
                 "Medical interns and doctors with any of the following qualifications:\n\n"
                 "• MBBS\n"
                 "• BAMS\n"
                 "• BHMS\n"
                 "• BUMS\n\n"
                 "✅ This eligibility applies to both learning pathways:\n\n"
                 "1️⃣ CCHR – 6-Month PGDCEMS\n"
                 "2️⃣ GIMER + Swaminarayan University – 12-Month PGDEMS\n\n"
                 "📌 For admission guidance, reply 6 to talk to a counsellor.\n\n"
                 "Type MENU to return to the main menu."
            )
        elif message_text in ["3", "fees", "admission"]:
            reply_text = (
                "💰 Fees & Admission\n\n"
                "For current fees, admission procedure and available batches, "
                "please connect with our admission counsellor.\n\n"
                "Reply 6 to request a counsellor.\n\n"
                "Type MENU to return to the main menu."
            )

        elif message_text in ["4", "duration"]:
            reply_text = (
                "⏱️ Course Duration\n\n"
                "Please select the PGDEMS learning pathway you are interested in "
                "for the applicable course duration and schedule.\n\n"
                "Reply 5 for Learning Pathways.\n\n"
                "Type MENU to return to the main menu."
            )

        elif message_text in ["5", "pathway", "pathways", "learning pathways"]:
            reply_text = (
                "🎓 PGDEMS LEARNING PATHWAYS\n\n"
                "We currently offer two learning pathways:\n\n"
                "1️⃣ CCHR – 6-Month PGDCEMS\n"
                "Vocational / skill-development pathway through "
                "Central Council of Health & Research.\n\n"
                "2️⃣ GIMER + SWAMINARAYAN UNIVERSITY – 12-Month PGDEMS\n"
                "PGDEMS pathway through Global Institute of Medical Education "
                "& Research in association with Swaminarayan University.\n\n"
                "Please reply:\n"
                "P1 – For complete details of CCHR 6-Month PGDCEMS\n"
                "P2 – For complete details of GIMER + Swaminarayan University PGDEMS\n\n"
                "Type MENU to return to the main menu."
            )  
        elif message_text in ["p1", "1"]:
            reply_text = (
                "🏥 CCHR – 6-MONTH PGDCEMS\n\n"
                "Post Graduate Diploma Certificate in Emergency Medical Services\n\n"
            "📚 PROGRAMME\n"
            "A 6-month vocational / skill-development pathway through "
            "Central Council of Health & Research.\n\n"
            "⏳ DURATION & SCHEDULE\n"
            "• 3 months theory\n"
            "• 3 months hospital orientation\n"
            "• Classes / training 4 days a week\n\n"
            "👨‍⚕️ ELIGIBILITY\n"
            "Medical interns and doctors with MBBS, BAMS, BHMS or BUMS qualification.\n\n"
            "📖 CURRICULUM\n"
            "A. Scene Safety, History Taking, Patient Assessment & Clinical Decision\n"
            "B. Airway Management & Mechanical Ventilation\n"
            "C. Basic Life Support (BLS) & Advanced Cardiac Life Support (ACLS)\n"
            "D. Various System Wise Emergencies & Their Management\n"
            "E. Polytrauma & Traumatic Emergencies\n"
            "F. Management of OBGY Emergencies\n"
            "G. Paediatric Emergencies & Management\n"
            "H. Environmental Emergencies & Management\n\n"
            "💰 INSTITUTE FEE\n"
            "Total: ₹35,000\n"
            "• Enrollment: ₹5,000\n"
            "• Balance: ₹30,000\n"
            "• Balance payable in 3 installments of ₹10,000/month\n\n"
            "🎓 CERTIFICATION\n"
            "PGDCEMS certificate is provided on successful completion of the programme.\n\n"
            "📍 Training Centre\n"
            "2nd Floor, Akshay Tower, Sakkardara Square, Nagpur.\n\n"
            "ℹ️ This is a vocational / skill-development pathway and is "
            "not a university programme or a programme awarded by a statutory body.\n\n"
            "For admission assistance, reply 6 to talk to a counsellor.\n"
            "Type MENU to return to the main menu."
            )   
        elif message_text in ["p2"]:
            reply_text = (
               "🎓 GIMER + SWAMINARAYAN UNIVERSITY – 12-MONTH PGDEMS\n\n"
               "Global Institute of Medical Education & Research (GIMER) "
                "in association with Swaminarayan University.\n\n"
                "⏳ PROGRAMME DURATION\n"
                "• Overall programme cycle: 12 months\n"
                "• GIMER training component: 6 months\n"
                "• 3 months classroom training\n"
                "• 3 months hospital posting\n\n"
                "📚 CLASSROOM SCHEDULE\n"
                "Tuesday to Friday – 4 days a week for 3 months.\n\n"
                "🏥 HOSPITAL POSTING\n"
                "3 months of hospital-based clinical orientation and practical exposure.\n\n"
                "📝 EXAMINATION\n"
                "University examination cycle: January / July.\n\n"
                "📅 INTAKES\n"
                "January / May / September.\n\n"
                "📖 CURRICULUM\n"
                "A. Scene Safety, History Taking, Patient Assessment & Clinical Decision\n"
                "B. Airway Management & Mechanical Ventilation\n"
                "C. Basic Life Support (BLS) & Advanced Cardiac Life Support (ACLS)\n"
                "D. Various System Wise Emergencies & Their Management\n"
                "E. Polytrauma & Traumatic Emergencies\n"
                "F. Management of OBGY Emergencies\n"
                "G. Paediatric Emergencies & Management\n"
                "H. Environmental Emergencies & Management\n\n"
                "💰 INSTITUTE FEE\n"
                "Total: ₹35,000\n"
                "• Enrollment: ₹5,000\n"
                "• ₹20,000 payable within 1 week of commencement of the batch\n"
                "• ₹10,000 payable in the next month\n\n"
                "🏛️ UNIVERSITY CHARGES\n"
                "University charges are separate from the ₹35,000 institute fee.\n"
                "Applicable charges may include examination, registration/enrollment, "
                "provisional certificate, marksheet, convocation and other "
                "certificates/documentation as per University regulations.\n"
                "Exact current university charges will be communicated separately.\n\n"
                "🎓 CERTIFICATION\n"
                "University marksheet, provisional certificate and diploma are issued "
                "as applicable after successful completion and fulfilment of "
                "University requirements.\n\n"
                "📍 Training Centre\n"
                "2nd Floor, Akshay Tower, Sakkardara Square, Nagpur.\n\n"
                "For admission assistance, reply 6 to talk to a counsellor.\n"
                "Type MENU to return to the main menu."
            )
       elif message_text in ["6", "counsellor", "counselor", "talk to a counsellor"]:
    user_state[sender] = "counsellor"
    reply_text = (
        "👨‍💼 Counsellor Assistance\n\n"
        "Sure! Our admission counsellor can assist you with the course, "
        "eligibility, fees and admission process.\n\n"
        "Please reply with your NAME and QUALIFICATION.\n\n"
        "Example:\n"
        "Rahul Sharma, MBBS\n\n"
        "📲 You may also call / WhatsApp: 8830639520"
    )

        else:
            reply_text = (
                "👋 Welcome to PGDEMS Admission Assistant!\n\n"
                "How may I help you?\n\n"
                "1️⃣ PGDEMS Course Details\n"
                "2️⃣ Eligibility\n"
                "3️⃣ Fees & Admission\n"
                "4️⃣ Course Duration\n"
                "5️⃣ Learning Pathways\n"
                "6️⃣ Talk to a Counsellor\n\n"
                "Please reply with 1, 2, 3, 4, 5 or 6."
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

from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from pydantic import BaseModel, EmailStr
import random
import smtplib
from email.mime.text import MIMEText
import os
import requests
from dotenv import load_dotenv
from google.cloud import firestore
from google.oauth2 import service_account
import threading
import time
from datetime import datetime, timedelta
import subprocess
from twilio.rest import Client
import shutil
from calendar_utils import create_event, delete_event

from ocr import extract_text
from ai_parser import extract_medicines
from langgraph_agent import agent
from llm_chat import llm_chat_response

from llm_chat import llm_chat_response
from ai_parser import parse_chat_query
from llm_parser import refine_medicines_llm

import json
def clean_medicines(meds):

    cleaned = []

    for med in meds:
        name = med.get("name", "").strip()

        # ❌ remove garbage entries
        if len(name) < 3:
            continue
        if "hospital" in name.lower():
            continue
        if "www" in name.lower():
            continue

        cleaned.append({
            "name": name,
            "dosage": med.get("dosage", "Not specified")
        })

    return cleaned[:5]


load_dotenv()

app = FastAPI()

# ---------------- ENV ---------------- #

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

ENABLE_SMS = os.getenv("ENABLE_SMS", "false").lower()
ENABLE_WHATSAPP = os.getenv("ENABLE_WHATSAPP", "false").lower()

# ---------------- FIRESTORE ---------------- #

cred = service_account.Credentials.from_service_account_file(
    os.path.join(os.path.dirname(__file__), "serviceAccount.json")
)

db = firestore.Client(credentials=cred, project=cred.project_id)

# ---------------- TWILIO ---------------- #

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
USER_NUMBER = os.getenv("USER_PHONE_NUMBER")

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
USER_WHATSAPP_NUMBER = os.getenv("USER_WHATSAPP_NUMBER")

# ---------------- NOTIFICATIONS ---------------- #

def send_sms(message):
    if ENABLE_SMS != "true":
        print("🚫 SMS DISABLED")
        return

    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=USER_NUMBER
        )
        print("✅ SMS SENT")
    except Exception as e:
        print("❌ SMS ERROR:", e)


def send_whatsapp(message):
    if ENABLE_WHATSAPP != "true":
        print("🚫 WHATSAPP DISABLED")
        return

    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=USER_WHATSAPP_NUMBER
        )
        print("✅ WHATSAPP SENT")
    except Exception as e:
        print("❌ WHATSAPP ERROR:", e)


def send_notification(title, message):
    try:
        subprocess.Popen([
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}"'
        ])
        print("🔔 Notification sent")
    except Exception as e:
        print("❌ Notification error:", e)

# ---------------- SCHEDULER ---------------- #

def scheduler():
    while True:

        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")

        print("⏰", current_time)

        docs = db.collection("medications").stream()

        for doc in docs:
            data = doc.to_dict()
            schedule = data.get("schedule", [])

            for dose in schedule:

                med_time = dose.get("time")
                last_taken_date = dose.get("last_taken_date")
                last_reminded = dose.get("last_reminded")
                snooze_until = dose.get("snooze_until")

                # ---------- DAILY RESET FIX ---------- #
                if last_taken_date and last_taken_date != today:
                    dose["taken"] = False
                    dose["last_taken_date"] = None

                is_taken = (
                    dose.get("taken", False)
                    and dose.get("last_taken_date") == today
                )

                # ---------- TIME PARSE FIX ---------- #
                try:
                    if "AM" in med_time or "PM" in med_time:
                        med_time_obj = datetime.strptime(med_time, "%I:%M %p")
                    else:
                        med_time_obj = datetime.strptime(med_time, "%H:%M")

                    med_time_obj = med_time_obj.replace(
                        year=now.year, month=now.month, day=now.day
                    )

                    is_due = med_time_obj <= now
                except:
                    continue

                # ---------- SNOOZE ---------- #
                if snooze_until and snooze_until == current_time and not is_taken:

                    send_notification("Snoozed Reminder", f"Take {data['name']}")
                    send_sms(f"Snoozed: Take {data['name']}")
                    send_whatsapp(f"Snoozed: Take {data['name']}")

                    dose["snooze_until"] = None
                    dose["last_reminded"] = current_time

                    db.collection("medications").document(doc.id).update({
                        "schedule": schedule
                    })

                # ---------- AUTO REMINDER ---------- #
                if is_due and not is_taken:

                    should_notify = False

                    if not last_reminded:
                        should_notify = True
                    else:
                        last_time = datetime.strptime(last_reminded, "%H:%M")
                        if (now - last_time) >= timedelta(minutes=2):
                            should_notify = True

                    if should_notify:

                        print("🔁 REMINDER:", data["name"])

                        send_notification(
                            "Medication Reminder",
                            f"Take {data['name']} ({data['dosage']})"
                        )

                        send_sms(f"Reminder: Take {data['name']}")
                        send_whatsapp(f"Reminder: Take {data['name']}")

                        dose["last_reminded"] = current_time

                        db.collection("medications").document(doc.id).update({
                            "schedule": schedule
                        })

        time.sleep(30)


threading.Thread(target=scheduler, daemon=True).start()

# ---------------- MODELS ---------------- #

class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Dose(BaseModel):
    time: str
    taken: bool = False


class Medication(BaseModel):
    name: str
    dosage: str
    user_email: EmailStr
    schedule: list[Dose]

# ---------------- OTP ---------------- #

otp_store = {}

def send_otp_email(receiver_email, otp):
    msg = MIMEText(f"Your MedGuard OTP is: {otp}")
    msg["Subject"] = "MedGuard OTP"
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ---------------- AUTH ---------------- #

@app.post("/auth/send-otp")
def send_otp(data: SignupRequest):
    otp = str(random.randint(100000, 999999))
    otp_store[data.email] = otp
    send_otp_email(data.email, otp)
    return {"message": "OTP sent"}


@app.post("/auth/verify-otp")
def verify_otp(data: VerifyOTPRequest):

    if otp_store.get(data.email) != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

    res = requests.post(url, json={
        "email": data.email,
        "password": data.password,
        "returnSecureToken": True
    })

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail=res.json())

    del otp_store[data.email]
    return {"message": "User created"}


@app.post("/auth/login")
def login(data: LoginRequest):

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

    res = requests.post(url, json={
        "email": data.email,
        "password": data.password,
        "returnSecureToken": True
    })

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return res.json()

# ---------------- CRUD ---------------- #

@app.post("/medications/add")
def add_medication(med: Medication):
    data = med.dict()
    data["user_email"] = data["user_email"].lower()

    # ---------- GOOGLE CALENDAR EVENTS ---------- #
    try:
        for dose in data.get("schedule", []):
            event_id = create_event(
                summary=f"Take {data['name']}",
                description=f"Dosage: {data['dosage']}",
                time_str=dose["time"]
            )

            # ✅ SAVE EVENT ID
            dose["event_id"] = event_id
    except Exception as e:
        print("❌ Calendar Error:", e)

    # ---------- SAVE TO FIRESTORE ---------- #
    db.collection("medications").document().set(data)

    return {"message": "Medication added"}

@app.get("/medications/{email}")
def get_medications(email: str):

    email = email.lower()

    docs = db.collection("medications").where("user_email", "==", email).stream()

    result = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)

    return result


@app.put("/medications/update/{doc_id}")
def update_medication(doc_id: str, data: dict = Body(...)):

    doc_ref = db.collection("medications").document(doc_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Medication not found")

    old_data = doc.to_dict()

    old_schedule = old_data.get("schedule", [])
    new_schedule = data.get("schedule", [])

    name = data.get("name", old_data.get("name"))
    dosage = data.get("dosage", old_data.get("dosage"))

    # ---------- DETECT FULL EDIT ---------- #
    is_full_edit = (
        "name" in data or
        "dosage" in data or
        len(new_schedule) != len(old_schedule)
    )

    # ---------- IF FULL EDIT → RESET CALENDAR ---------- #
    if is_full_edit:

        # DELETE OLD EVENTS
        for dose in old_schedule:
            event_id = dose.get("event_id")
            if event_id:
                try:
                    delete_event(event_id)
                except:
                    pass

        # CREATE NEW EVENTS
        for dose in new_schedule:
            try:
                event_id = create_event(
                    summary=f"Take {name}",
                    description=f"Dosage: {dosage}",
                    time_str=dose["time"]
                )
                dose["event_id"] = event_id
            except:
                pass

    else:
        # ---------- PARTIAL UPDATE (checkbox/snooze) ---------- #
        # KEEP EXISTING EVENT IDs
        for i in range(len(new_schedule)):
            if i < len(old_schedule):
                new_schedule[i]["event_id"] = old_schedule[i].get("event_id")

    # ---------- SAVE ---------- #
    data["name"] = name
    data["dosage"] = dosage

    doc_ref.update(data)

    return {"message": "Updated safely"}


@app.delete("/medications/delete/{doc_id}")
def delete_medication(doc_id: str):

    doc_ref = db.collection("medications").document(doc_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Not found")

    data = doc.to_dict()

    # ---------- DELETE CALENDAR EVENTS ---------- #
    for dose in data.get("schedule", []):
        event_id = dose.get("event_id")
        if event_id:
            try:
                delete_event(event_id)
            except Exception as e:
                print("❌ Event delete failed:", e)

    # ---------- DELETE FIRESTORE ---------- #
    doc_ref.delete()

    return {"message": "Deleted + Calendar cleaned"}

# ---------------- ANALYTICS ---------------- #

@app.get("/analytics/{email}")
def get_analytics(email: str):

    email = email.lower()

    docs = db.collection("medications").where("user_email", "==", email).stream()

    today = datetime.now().strftime("%Y-%m-%d")

    total_doses = 0
    taken_doses = 0

    meds_data = []

    for doc in docs:
        data = doc.to_dict()
        schedule = data.get("schedule", [])

        med_total = 0
        med_taken = 0

        for dose in schedule:
            med_total += 1
            total_doses += 1

            if dose.get("taken") and dose.get("last_taken_date") == today:
                med_taken += 1
                taken_doses += 1

        adherence = (med_taken / med_total * 100) if med_total else 0

        meds_data.append({
            "name": data.get("name"),
            "total": med_total,
            "taken": med_taken,
            "adherence": round(adherence, 2)
        })

    overall = (taken_doses / total_doses * 100) if total_doses else 0

    return {
        "overall": {
            "total": total_doses,
            "taken": taken_doses,
            "missed": total_doses - taken_doses,
            "adherence": round(overall, 2)
        },
        "medications": meds_data
    }

# ---------------- OCR ---------------- #

@app.post("/chat/save")
def save_chat(user_email: str, message: dict):

    db.collection("chat_history") \
        .document(user_email.lower()) \
        .set({
            "messages": firestore.ArrayUnion([message])
        }, merge=True)

    return {"status": "saved"}

@app.get("/chat/history/{user_email}")
def get_chat_history(user_email: str):

    doc = db.collection("chat_history").document(user_email.lower()).get()

    if doc.exists:
        return doc.to_dict().get("messages", [])

    return []

@app.post("/ocr/upload")
async def ocr_upload(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_path)

    print("\n===== OCR TEXT =====")
    print(text)

    # ---------- TRY LLM FIRST ---------- #
    try:
        from llm_parser import extract_medicines_llm
        import json

        meds_raw = extract_medicines_llm(text)

        # 🔥 CLEAN MARKDOWN
        meds_raw = meds_raw.strip()
        if meds_raw.startswith("```"):
            meds_raw = meds_raw.replace("```json", "").replace("```", "").strip()

        # ---------- FIRST LLM ----------
        meds_raw = extract_medicines_llm(text)

        meds_raw = meds_raw.strip()
        if meds_raw.startswith("```"):
            meds_raw = meds_raw.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(meds_raw)

        print("\n===== LLM PASS 1 =====")
        print(parsed)

        # ---------- SECOND LLM (FIXING) ----------
        refined_raw = refine_medicines_llm(parsed)

        refined_raw = refined_raw.strip()
        if refined_raw.startswith("```"):
            refined_raw = refined_raw.replace("```json", "").replace("```", "").strip()

        meds = json.loads(refined_raw)

        print("\n===== LLM PASS 2 =====")
        print(meds)

        # ---------- FINAL CLEAN ----------
        meds = clean_medicines(meds)

        # 🔥 SAFETY LIMIT
        if not isinstance(meds, list):
            raise Exception("Invalid format")

        meds = meds[:5]

        print("\n===== LLM PARSED =====")
        print(meds)

    # ---------- FALLBACK ---------- #
    except Exception as e:
        print("❌ LLM FAILED:", e)

        meds = extract_medicines(text)

        print("\n===== FALLBACK PARSER =====")
        print(meds)

    os.remove(file_path)

    return {
        "text": text,
        "medications": meds
    }

# ---------------- AI CHAT ---------------- #

from llm_chat import llm_chat_response
import json

@app.post("/chat")
def chat(user_email: str, query: str):

    q = query.lower().strip()

    # ---------- GREETING HANDLER ----------
    if q in ["hi", "hello", "hey", "hii", "yo"]:
        return {
            "response": "👋 Hey! I’m your AI health assistant.\n\nYou can ask me:\n• 'Add dolo 650 at 9 am'\n• 'What is my adherence?'\n• 'Delete paracetamol'\n\nHow can I help you today?"
        }

    docs = db.collection("medications").where("user_email", "==", user_email.lower()).stream()

    meds = []

    # ---------- GET CHAT HISTORY ----------
    chat_doc = db.collection("chat_history").document(user_email.lower()).get()

    if chat_doc.exists:
        history = chat_doc.to_dict().get("messages", [])
    else:
        history = []
    

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        meds.append(data)

    try:
        # ---------- STEP 0: SIMPLE QUERY → USE AGENT ----------
        simple_keywords = ["adherence", "taken", "pending", "missed", "progress"]

        if any(word in query.lower() for word in simple_keywords):
            agent_response = agent.invoke({
                "query": query,
                "medications": meds
            })

            return {
                "response": agent_response.get(
                    "response",
                    "🤖 Could not understand"
                )
            }

        # ---------- STEP 1: TRY LLM ----------
        formatted_history = "\n".join([
            f"{m['role']}: {m['content']}" for m in history[-10:]
        ])

        raw = llm_chat_response(query, meds, formatted_history)

        if not raw:
            raise Exception("Empty LLM response")

        raw = raw.strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(raw)
            # ---------- HANDLE ACTIONS FROM LLM ---------- #

            action = data.get("action")

            # ---------- ADD ----------
            if action == "add":

                times = data.get("times", [])

                if not times:
                    return {
                        "response": f"⚠️ You didn’t specify time for {data.get('name','medicine')}.\nSet default (09:00)?",
                        "pending": data
                    }

                schedule = []

                for t in times:
                    try:
                        event_id = create_event(
                            summary=f"Take {data.get('name')}",
                            description=f"Dosage: {data.get('dosage')}",
                            time_str=t
                        )
                    except:
                        event_id = None

                    schedule.append({
                        "time": t,
                        "taken": False,
                        "event_id": event_id
                    })

                new_med = {
                    "name": data.get("name", "Unknown"),
                    "dosage": data.get("dosage", "Not specified"),
                    "user_email": user_email.lower(),
                    "schedule": schedule
                }

                db.collection("medications").document().set(new_med)
                
                db.collection("chat_history").document(user_email.lower()).set({
                    "messages": firestore.ArrayUnion([
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": f"Added {new_med['name']}"}
                    ])
                }, merge=True)

                return {"response": f"✅ Added {new_med['name']} with reminders"}

            # ---------- DELETE ----------
            if action == "delete":

                meds_ref = db.collection("medications") \
                    .where("user_email", "==", user_email.lower()) \
                    .stream()

                for doc in meds_ref:
                    med = doc.to_dict()

                    if med["name"].lower() == data.get("name", "").lower():

                        for dose in med.get("schedule", []):
                            if "event_id" in dose:
                                delete_event(dose["event_id"])

                        db.collection("medications").document(doc.id).delete()

                        db.collection("chat_history").document(user_email.lower()).set({
                            "messages": firestore.ArrayUnion([
                                {"role": "user", "content": query},
                                {"role": "assistant", "content": f"Added {new_med['name']}"}
                            ])
                        }, merge=True)

                        return {"response": f"🗑 Deleted {med['name']}"}

                db.collection("chat_history").document(user_email.lower()).set({
                    "messages": firestore.ArrayUnion([
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": f"Added {new_med['name']}"}
                    ])
                }, merge=True)
                return {"response": "❌ Medicine not found"}
            
            # ---------- EDIT ----------
            if action == "edit":

                meds_ref = db.collection("medications") \
                    .where("user_email", "==", user_email.lower()) \
                    .stream()

                target = None

                for doc in meds_ref:
                    med = doc.to_dict()
                    if med["name"].lower() == data.get("name", "").lower():
                        target = (doc.id, med)
                        break

                if not target:
                    return {"response": "❌ Medicine not found"}

                doc_id, med = target

                # DELETE OLD EVENTS
                for dose in med.get("schedule", []):
                    if "event_id" in dose:
                        delete_event(dose["event_id"])

                times = data.get("times", [])

                if not times:
                    return {"response": "⚠️ Provide new times"}

                new_schedule = []

                for t in times:
                    try:
                        event_id = create_event(
                            summary=f"Take {data['name']}",
                            description=data.get("dosage", ""),
                            time_str=t
                        )
                    except:
                        event_id = None

                    new_schedule.append({
                        "time": t,
                        "taken": False,
                        "event_id": event_id
                    })

                db.collection("medications").document(doc_id).update({
                    "name": data.get("name"),
                    "dosage": data.get("dosage", med.get("dosage")),
                    "schedule": new_schedule
                })

                return {"response": f"✏️ Updated {data['name']}"}
            
            # ---------- NORMAL RESPONSE (CHATGPT MODE) ----------
            response_text = data.get("response", "⚠️ No response")

            # SAVE CHAT HISTORY
            db.collection("chat_history").document(user_email.lower()).set({
                "messages": firestore.ArrayUnion([
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response_text}
                ])
            }, merge=True)

            return {"response": response_text}

        except:
            print("❌ JSON FAILED:", raw)
            raise Exception("Invalid JSON from LLM")
            
    except Exception as e:
        print("❌ LLM FAILED:", e)

        # ---------- STEP 1: TRY SIMPLE ACTION DETECTION ----------
        q = query.lower()

        # ---------- ADD ----------
        if "add" in q:
            return {"response": "⚠️ AI failed to process add. Try: 'add dolo 650 at 9 am'"}

        # ---------- DELETE ----------
        if "delete" in q or "remove" in q:
            name = q.replace("delete", "").replace("remove", "").strip()

            meds_ref = db.collection("medications") \
                .where("user_email", "==", user_email.lower()) \
                .stream()

            for doc in meds_ref:
                med = doc.to_dict()

                if name in med["name"].lower():

                    for dose in med.get("schedule", []):
                        if "event_id" in dose:
                            delete_event(dose["event_id"])

                    db.collection("medications").document(doc.id).delete()

                    return {"response": f"🗑 Deleted {med['name']}"}

            return {"response": "❌ Medicine not found"}

        # ---------- OTHERWISE → AGENT ----------
        agent_response = agent.invoke({
            "query": query,
            "medications": meds
        })

        return {
            "response": agent_response.get(
                "response",
                "🤖 Could not understand your request"
            )
        }

    except Exception as e:
        print("❌ CHAT ERROR:", e)
        return {"response": "Something went wrong"}
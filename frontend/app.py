import streamlit as st
import requests
import datetime
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# ---------- SESSION INIT ---------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = None

# ---------- QUERY PARAM SESSION ---------- #
query_params = st.query_params

if "email" in query_params:
    st.session_state.logged_in = True
    st.session_state.email = query_params["email"]

st.set_page_config(page_title="MedGuard Omni", layout="wide")

# ---------- CSS ---------- #
st.markdown("""
<style>
.title {
    font-size: 40px;
    font-weight: bold;
    color: #2b7cff;
    text-align: center;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin: 10px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">MedGuard Omni</div>', unsafe_allow_html=True)

# ---------- DASHBOARD ---------- #
if st.session_state.logged_in:

    st.success(f"Logged in as {st.session_state.email}")

    # ================= DASHBOARD ================= #
    st.write("## 📊 Dashboard")

    res = requests.get(f"{API_URL}/analytics/{st.session_state.email}")

    if res.status_code == 200:
        data = res.json()

        overall = data["overall"]
        meds = data["medications"]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Doses", overall["total"])
        col2.metric("Taken", overall["taken"])
        col3.metric("Missed", overall["missed"])
        col4.metric("Adherence %", overall["adherence"])

        st.write("---")

        st.write("### 💊 Medication-wise Adherence")

        df = pd.DataFrame(meds)

        if not df.empty:
            st.dataframe(df, use_container_width=True)

            st.write("### 📊 Adherence Chart")
            chart_df = df.set_index("name")["adherence"]
            st.bar_chart(chart_df)
        else:
            st.info("No medication data yet")

    else:
        st.error("Failed to load analytics")

    st.write("---")

    # ================= OCR AUTO FILL ================= #
    st.write("## 📸 Upload Prescription")

    uploaded_file = st.file_uploader("Upload JPG or PDF", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file:

        files = {"file": uploaded_file}

        res = requests.post(f"{API_URL}/ocr/upload", files=files)

        if res.status_code == 200:
            data = res.json()
            extracted_meds = data.get("medications", [])

            st.success("Extraction Complete ✅")

            for med in extracted_meds:

                st.markdown("### 🤖 Auto-filled Medication")

                name = st.text_input("Medicine Name", value=med["name"], key=med["name"])
                dosage = st.text_input("Dosage", value=med["dosage"], key=med["name"] + "_dose")

                num_doses = st.number_input("Doses per day", 1, 5, 1, key=med["name"] + "_num")

                times = []
                for i in range(int(num_doses)):
                    t = st.time_input(f"Time {i+1}", key=f"{med['name']}_{i}")
                    times.append(t.strftime("%H:%M"))

                if st.button(f"Add {med['name']}"):

                    requests.post(f"{API_URL}/medications/add", json={
                        "name": name,
                        "dosage": dosage,
                        "schedule": [{"time": t, "taken": False, "last_taken_date": None} for t in times],
                        "user_email": st.session_state.email
                    })

                    st.success(f"{name} added ✅")
                    st.rerun()

    st.write("---")

    # ================= ADD MEDICATION ================= #
    st.write("### Add Medication")

    name = st.text_input("Medicine Name")
    dosage = st.text_input("Dosage")

    st.write("### Select Dosage Times")

    num_doses = st.number_input("Number of doses per day", min_value=1, max_value=5, value=1)

    times = []

    for i in range(int(num_doses)):
        t = st.time_input(f"Dose {i+1} time", key=f"time_{i}")
        times.append(t.strftime("%H:%M"))

    if st.button("Add Medication"):
        res = requests.post(f"{API_URL}/medications/add", json={
            "name": name,
            "dosage": dosage,
            "schedule": [{"time": t, "taken": False, "last_taken_date": None} for t in times],
            "user_email": st.session_state.email
        })

        if res.status_code == 200:
            st.success("Medication Added ✅")
            st.rerun()
        else:
            st.error("Failed to add medication")

    st.write("---")

    # ================= VIEW MEDICATIONS ================= #
    st.write("### Your Medications")

    res = requests.get(f"{API_URL}/medications/{st.session_state.email}")
    meds = res.json()

    for med in meds:
        edit_mode = st.checkbox("✏️ Edit", key=f"edit_{med['id']}")
        
        if edit_mode:

            new_name = st.text_input("Name", value=med["name"], key=f"name_{med['id']}")
            new_dosage = st.text_input("Dosage", value=med["dosage"], key=f"dose_{med['id']}")

            new_count = st.number_input(
                "Number of doses",
                min_value=1,
                max_value=5,
                value=len(med.get("schedule", [])),
                key=f"count_{med['id']}"
            )

            new_times = []

            for i in range(int(new_count)):
                default_time = med["schedule"][i]["time"] if i < len(med["schedule"]) else "09:00"

                t = st.time_input(
                    f"Time {i+1}",
                    value=datetime.datetime.strptime(default_time, "%H:%M").time(),
                    key=f"edit_time_{med['id']}_{i}"
                )

                new_times.append(t.strftime("%H:%M"))

            if st.button("💾 Save Changes", key=f"save_{med['id']}"):

                new_schedule = [
                    {
                        "time": t,
                        "taken": False,
                        "last_taken_date": ""
                    }
                    for t in new_times
                ]

                res = requests.put(
                    f"{API_URL}/medications/update/{med['id']}",
                    json={
                        "name": new_name,
                        "dosage": new_dosage,
                        "schedule": new_schedule
                    }
                )

                if res.status_code == 200:
                    st.success("Updated successfully")
                    st.rerun()
                else:
                    st.error("Update failed")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.write(f"### 💊 {med['name']} ({med['dosage']})")

        schedule = med.get("schedule", [])

        for idx, dose in enumerate(schedule):
            col1, col2, col3 = st.columns([3, 1, 1])

            today = datetime.datetime.now().strftime("%Y-%m-%d")

            # ---------- FIXED TAKEN LOGIC ---------- #
            is_taken_today = (
                dose.get("taken", False)
                and dose.get("last_taken_date") == today
            )

            with col1:
                st.write(f"🕒 {dose['time']}")

                if is_taken_today:
                    st.success("✅ Taken")
                else:
                    st.warning("⏳ Pending")

            with col2:
                new_taken = st.checkbox(
                    "Taken",
                    value=is_taken_today,
                    key=f"{med['id']}_{idx}"
                )

                if new_taken != is_taken_today:

                    if new_taken:
                        schedule[idx]["taken"] = True
                        schedule[idx]["last_taken_date"] = today
                    else:
                        schedule[idx]["taken"] = False
                        schedule[idx]["last_taken_date"] = None

                    requests.put(
                        f"{API_URL}/medications/update/{med['id']}",
                        json={"schedule": schedule}
                    )

                    st.rerun()

            with col3:
                if st.button("Snooze 5m", key=f"snooze_{med['id']}_{idx}"):

                    snooze_time = (
                        datetime.datetime.now() + datetime.timedelta(minutes=5)
                    ).strftime("%H:%M")

                    schedule[idx]["snooze_until"] = snooze_time
                    schedule[idx]["last_reminded"] = None

                    requests.put(
                        f"{API_URL}/medications/update/{med['id']}",
                        json={"schedule": schedule}
                    )

                    st.success(f"Snoozed till {snooze_time}")
                    st.rerun()

        if st.button("🗑 Delete", key=f"del_{med['id']}"):
            requests.delete(f"{API_URL}/medications/delete/{med['id']}")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")

    # ================= AI CHAT ================= #
    st.write("## 🤖 AI Health Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI:** {msg['content']}")

    query = st.text_input("Ask something about your medications")

    if st.button("Send") and query:

        st.session_state.chat_history.append({
            "role": "user",
            "content": query
        })

        res = requests.post(
            f"{API_URL}/chat",
            params={
                "user_email": st.session_state.email,
                "query": query
            }
        )

        if res.status_code == 200:
            reply = res.json()["response"]
        else:
            reply = "❌ Error talking to AI"

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply
        })

        st.rerun()

    # ================= LOGOUT ================= #
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.email = None
        st.query_params.clear()
        st.rerun()

# ================= AUTH ================= #
else:
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = requests.post(f"{API_URL}/auth/login", json={
                "email": email,
                "password": password
            })

            if res.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.email = email.lower()
                st.query_params["email"] = email.lower()
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Signup Email")
        password = st.text_input("Signup Password", type="password")

        if st.button("Send OTP"):
            requests.post(f"{API_URL}/auth/send-otp", json={
                "email": email,
                "password": password
            })
            st.success("OTP sent")

        otp = st.text_input("OTP")

        if st.button("Verify"):
            res = requests.post(f"{API_URL}/auth/verify-otp", json={
                "email": email,
                "otp": otp,
                "password": password
            })

            if res.status_code == 200:
                st.success("Account created")
            else:
                st.error(res.text)
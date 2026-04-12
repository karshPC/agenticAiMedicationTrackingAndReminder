import streamlit as st
import requests
import datetime
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go


API_URL = "http://127.0.0.1:8000"

from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")


# ---------- SESSION INIT ---------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = None

if "pending_med" not in st.session_state:
    st.session_state.pending_med = None

# ---------- QUERY PARAM SESSION ---------- #
query_params = st.query_params

if "email" in query_params:
    st.session_state.logged_in = True
    st.session_state.email = query_params["email"]

# ---------- CSS ---------- #
st.markdown("""
<style>
.section-card {
    background: #111827;
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid #1f2937;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 15px;
}

.primary-btn button {
    background: linear-gradient(135deg, #00D4FF, #007CF0);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
}

.success-box {
    background: #064e3b;
    padding: 15px;
    border-radius: 10px;
    color: #10b981;
    margin-top: 10px;
}

.chat-container {
    max-width: 800px;
    margin: auto;
}

.user-msg {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 8px 0;
    margin-left: auto;
    width: fit-content;
    max-width: 70%;
}

.ai-msg {
    background: #1f2937;
    color: #e5e7eb;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 8px 0;
    margin-right: auto;
    width: fit-content;
    max-width: 70%;
}

body {
    background: #0b0f19;
}

.stApp {
    background: radial-gradient(circle at 20% 20%, #1e293b, #020617);
}

/* subtle glow */
.stApp::before {
    content: "";
    position: fixed;
    top: -200px;
    left: -200px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(0,212,255,0.15), transparent);
    filter: blur(120px);
    z-index: -1;
}

.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-5px) scale(1.02);
}

.kpi-title {
    font-size: 14px;
    opacity: 0.7;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
}

button {
    transition: all 0.25s ease !important;
}

button:hover {
    transform: scale(1.04);
    box-shadow: 0 6px 20px rgba(0,212,255,0.3);
}

button:active {
    transform: scale(0.97);
}
                
</style>
""", unsafe_allow_html=True)

# ---------- DASHBOARD ---------- #
if st.session_state.logged_in:

    st.markdown("""
    <style>
    .navbar-glass {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(12px);
        padding: 10px;
        border-radius: 14px;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="navbar-glass">', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Home"

    selected = option_menu(
        menu_title=None,
        options=["Home", "Add Meds", "Dashboard", "Chat", "My Medications"],
        icons=["house", "plus-circle", "bar-chart", "chat", "capsule"],
        orientation="horizontal",
        default_index=["Home", "Add Meds", "Dashboard", "Chat", "My Medications"].index(
            st.session_state.selected_page
        ),
        key="main_navbar"   # ✅ ADD THIS LINE
    )

    st.session_state.selected_page = selected

    st.markdown("""
    <style>
    .fade-in {
        animation: fadeIn 0.4s ease-in-out;
    }

    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    col_nav, col_logout = st.columns([8,1])

    with col_logout:
        if st.button("Logout"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    # ================= HOME ================= #
    if selected == "Home":

        st.markdown("""
        <style>
        .hero {
            padding: 60px;
            border-radius: 20px;
            background: linear-gradient(135deg, #00D4FF, #090979);
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }
        .hero h1 {
            font-size: 48px;
            margin-bottom: 10px;
        }
        .hero p {
            font-size: 20px;
            opacity: 0.9;
        }
        </style>

        <div class="hero">
            <h1>💊 MedGuard Omni 💊</h1>
            <p>AI-powered medication tracking, reminders & adherence system</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

        if st.button("🚀 Go to Dashboard"):
            st.session_state.selected_page = "Dashboard"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # 🔥 LOAD CHAT FROM BACKEND
    if "chat_loaded" not in st.session_state or st.session_state.chat_loaded != st.session_state.email:

        res = requests.get(f"{API_URL}/chat/history/{st.session_state.email}")

        if res.status_code == 200:
            history = res.json()

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = {}

            st.session_state.chat_history[st.session_state.email] = history

        st.session_state.chat_loaded = st.session_state.email

    # ================= DASHBOARD ================= #
    if selected == "Dashboard":
        st.write("## 📊 Dashboard")

        res = requests.get(f"{API_URL}/analytics/{st.session_state.email}")

        if res.status_code == 200:
            data = res.json()

            overall = data["overall"]
            meds = data["medications"]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">💊 Total</div>
                    <div class="kpi-value">{overall["total"]}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">✅ Taken</div>
                    <div class="kpi-value" style="color:#10b981;">{overall["taken"]}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">❌ Missed</div>
                    <div class="kpi-value" style="color:#ef4444;">{overall["missed"]}</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">📊 Adherence</div>
                    <div class="kpi-value" style="color:#00D4FF;">{overall["adherence"]}%</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            st.write("### 📊 Overall Adherence")

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall["adherence"],
                title={'text': "🔥 Overall Adherence"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#00D4FF"},
                    'steps': [
                        {'range': [0, 50], 'color': '#7f1d1d'},
                        {'range': [50, 75], 'color': '#78350f'},
                        {'range': [75, 100], 'color': '#064e3b'}
                    ],
                }
            ))

            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5e7eb")
            )

            fig_gauge.update_layout(transition={'duration': 800})

            st.plotly_chart(fig_gauge, width="stretch")

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            st.write("### 💊 Medication-wise Adherence")

            df = pd.DataFrame(meds)

            if not df.empty:
                st.dataframe(df, width="stretch")

                st.write("### 📊 Adherence Chart")

                fig = px.bar(
                    df,
                    x="name",
                    y="adherence",
                    color="adherence",
                    color_continuous_scale=["#ef4444", "#facc15", "#10b981"],
                    text="adherence"
                )

                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    marker=dict(line=dict(width=0))
                )

                fig.update_layout(
                    title="💊 Medication-wise Adherence",
                    xaxis_title="Medicine",
                    yaxis_title="Adherence %",
                    yaxis=dict(range=[0, 100]),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e5e7eb"),
                    showlegend=False,
                    transition={'duration': 800}
                )

                st.plotly_chart(fig, width="stretch")

            else:
                st.info("No medication data yet")

            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.error("Failed to load analytics")

    # ================= ADD MEDS ================= #
    if selected == "Add Meds":

        st.write("## 💊 Add Medications")

        tab1, tab2 = st.tabs(["📸 OCR Upload", "✍️ Manual Entry"])

        # ================= OCR ================= #
        with tab1:

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Upload Prescription</div>', unsafe_allow_html=True)

            uploaded_file = st.file_uploader("Upload JPG/PDF")

            if uploaded_file:

                st.session_state.pop("ocr_meds", None)

                files = {"file": uploaded_file}
                res = requests.post(f"{API_URL}/ocr/upload", files=files)

                if res.status_code == 200:
                    data = res.json()

                    st.write("🔥 RAW OCR RESPONSE:", data)   # ✅ ADD THIS LINE HERE

                    st.markdown('<div class="success-box">Extraction Complete ✅</div>', unsafe_allow_html=True)

                    # HANDLE RESPONSE (FIXED)
                    if isinstance(data, dict):
                        extracted = data.get("medications", [])
                    else:
                        extracted = []

                    # STORE
                    if extracted:
                        st.session_state.ocr_meds = extracted

                    # SHOW COUNT
                    st.success(f"Detected {len(st.session_state.get('ocr_meds', []))} medicines")

                    # DEBUG
                    st.write("DEBUG OCR:", st.session_state.get("ocr_meds"))

                    # 🔥 NEW OCR UI USING SESSION STATE
                    if "ocr_meds" in st.session_state and st.session_state.ocr_meds:

                        st.write("### 🧾 Review & Add Medicines")

                        for i, med in enumerate(st.session_state.ocr_meds):

                            st.markdown('<div class="section-card">', unsafe_allow_html=True)

                            col1, col2 = st.columns(2)

                            with col1:
                                name = st.text_input(
                                    "Medicine Name",
                                    med.get("name", ""),
                                    key=f"ocr_name_{i}"
                                )

                                dosage = st.text_input(
                                    "Dosage",
                                    med.get("dosage", ""),
                                    key=f"ocr_dose_{i}"
                                )

                            with col2:
                                dose_count = st.number_input(
                                    "Doses per day",
                                    min_value=1,
                                    max_value=5,
                                    value=1,
                                    key=f"ocr_count_{i}"
                                )

                                times = []
                                for j in range(int(dose_count)):
                                    t = st.time_input(
                                        f"Time {j+1}",
                                        key=f"ocr_time_{i}_{j}"
                                    )
                                    times.append(t.strftime("%H:%M"))

                            if st.button("✅ Add This Medicine", key=f"ocr_add_{i}"):

                                requests.post(f"{API_URL}/medications/add", json={
                                    "name": name,
                                    "dosage": dosage,
                                    "schedule": [{"time": t, "taken": False} for t in times],
                                    "user_email": st.session_state.email
                                })

                                st.success(f"Added {name}")

                                # ✅ CLEAR AFTER ADD
                                st.session_state.ocr_meds.pop(i)
                                st.rerun()

                            st.markdown('</div>', unsafe_allow_html=True)

                    else:
                        st.warning("No medicines detected")

            st.markdown('</div>', unsafe_allow_html=True)

        # ================= MANUAL ================= #
        with tab2:

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Add Manually</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Medicine Name")

            with col2:
                dosage = st.text_input("Dosage")

            st.write("### ⏰ Schedule")

            st.markdown("#### Set Daily Schedule")

            dose_count = st.number_input(
                "Doses per day",
                min_value=1,
                max_value=5,
                value=1
            )

            times = []

            cols = st.columns(int(dose_count))

            for i in range(int(dose_count)):
                with cols[i]:
                    t = st.time_input(f"Time {i+1}", key=f"time_{i}")
                    times.append(t.strftime("%H:%M"))

            st.write("")

            if st.button("💊 Add Medication"):

                requests.post(f"{API_URL}/medications/add", json={
                    "name": name,
                    "dosage": dosage,
                    "schedule": [{"time": t, "taken": False} for t in times],
                    "user_email": st.session_state.email
                })

                st.success(f"Added {name}")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # ================= VIEW MEDICATIONS ================= #
    if selected == "My Medications":
        st.write("### Your Medications")

        res = requests.get(f"{API_URL}/medications/{st.session_state.email}")
        if res.status_code == 200:
            meds = res.json()
        else:
            meds = []
            st.error("Failed to load medications")

        for med in meds:
            edit_mode = st.checkbox("✏️ Edit", key=f"edit_{med['id']}")
            
            if edit_mode:

                new_name = st.text_input("Name", value=med["name"], key=f"name_{med['id']}")
                new_dosage = st.text_input("Dosage", value=med["dosage"], key=f"dose_{med['id']}")

                new_count = st.number_input(
                    "Number of doses",
                    min_value=1,
                    max_value=5,
                    value=max(1, len(med.get("schedule", []))),
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

            st.markdown(f"""
            <div style="
                background:#1c1c1c;
                padding:15px;
                border-radius:15px;
                margin-bottom:10px;
            ">
                <h3>💊 {med['name']}</h3>
                <p>{med['dosage']}</p>
            </div>
            """, unsafe_allow_html=True)

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

    # ================= AI CHAT ================= #
    if selected == "Chat":
        st.write("## 🤖 AI Health Assistant")

        user = st.session_state.email

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = {}

        if user not in st.session_state.chat_history:
            st.session_state.chat_history[user] = []

        chat_history = st.session_state.chat_history[user]

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for i, msg in enumerate(chat_history):

            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)

            else:
                # ONLY animate last message
                if i == len(chat_history) - 1:

                    placeholder = st.empty()
                    typed = ""

                    for char in msg["content"]:
                        typed += char
                        placeholder.markdown(f'<div class="ai-msg">{typed}</div>', unsafe_allow_html=True)
                        time.sleep(0.003)

                else:
                    st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        query = st.text_input(
            "💬 Ask anything...",
            placeholder="e.g. Add ibuprofen at 9 PM",
        )

        if st.button("Send") and query:

            # SAVE USER MESSAGE
            chat_history.append({
                "role": "user",
                "content": query
            })

            requests.post(
                f"{API_URL}/chat/save",
                params={"user_email": st.session_state.email},
                json={"role": "user", "content": query}
            )


            
            # ---------- IF WAITING FOR YES/NO ---------- #
            if st.session_state.pending_med:

                if query.lower() in ["yes", "y"]:

                    data = st.session_state.pending_med

                    new_med = {
                        "name": data.get("name", "Unknown"),
                        "dosage": data.get("dosage", "Not specified"),
                        "schedule": [{"time": "09:00", "taken": False}],
                        "user_email": st.session_state.email
                    }

                    requests.post(f"{API_URL}/medications/add", json=new_med)

                    reply = f"✅ Added {new_med['name']} with default time (09:00)"

                    st.session_state.pending_med = None

                else:
                    reply = "❌ Okay, please specify time like 'at 9 AM'"
                    st.session_state.pending_med = None

            # ---------- NORMAL CHAT ---------- #
            else:

                with st.spinner("🤖 AI is typing..."):
                    res = requests.post(
                        f"{API_URL}/chat",
                        params={
                            "user_email": st.session_state.email,
                            "query": query
                        }
                    )

                if res.status_code == 200:
                    try:
                        data = res.json()
                    except:
                        data = {"response": "⚠️ Invalid server response"}

                    if not data:
                        data = {"response": "⚠️ Empty response from backend"}

                    reply = data.get("response", "⚠️ No response field")

                    # 🔥 STORE PENDING MED FROM BACKEND
                    if "pending" in data:
                        st.session_state.pending_med = data["pending"]

                else:
                    reply = "❌ Error talking to AI"

            # SAVE AI RESPONSE
            chat_history.append({
                "role": "assistant",
                "content": reply
            })

            requests.post(
                f"{API_URL}/chat/save",
                params={"user_email": st.session_state.email},
                json={"role": "assistant", "content": reply}
            )

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
                st.session_state.chat_history = {}
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
# MedGuard – Agentic AI Medication Tracking & Reminder System

An AI-powered medication adherence platform that combines Agentic AI, prescription OCR, intelligent medication management, and multi-channel reminders into a single cloud-native healthcare application.

The system helps users manage medications by extracting prescription details automatically, scheduling reminders, tracking adherence, and providing conversational AI assistance for medication-related queries.

---

# Table of Contents

- Features
- Why MedGuard?
- System Overview
- Architecture
- Technology Stack
- Project Structure
- Core Modules
- OCR Pipeline
- Agentic AI Workflow
- Reminder System
- Dashboard & Analytics
- API Endpoints
- Running the Project
- Future Improvements

---

# Features

- AI-powered medication management
- Prescription OCR using Google Gemini Vision
- Agentic AI assistant built with LangGraph
- Natural language medication queries
- Smart adherence tracking
- Interactive analytics dashboard
- Multi-channel reminder system
- Google Calendar synchronization
- SMS notifications
- WhatsApp reminder escalation
- Firebase Authentication
- Cloud-native architecture

---

# Why MedGuard?

Medication non-adherence is one of the leading causes of poor treatment outcomes.

Many reminder applications simply notify users at scheduled times, but they cannot:

- Understand natural language
- Read prescriptions automatically
- Track adherence intelligently
- Escalate reminders across multiple channels
- Provide conversational assistance

MedGuard solves these problems by combining modern AI with cloud technologies into a single platform.

---

# System Overview

The project follows a three-layer cloud architecture.

```

Streamlit Frontend
│
▼
FastAPI Backend
│
├── LangGraph Agent
├── OCR Engine
├── Analytics
├── Scheduler
│
▼
Firebase Firestore

│
├── Google Gemini
├── Google Calendar
└── Twilio SMS + WhatsApp

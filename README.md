# MedGuard - Agentic AI Medication Tracking System

A cloud-native medication adherence platform that combines **Agentic AI**, **Prescription OCR**, **Intelligent Medication Scheduling**, **Real-Time Analytics**, and **Multi-Channel Reminder Escalation** into a single healthcare application.

Instead of acting as a simple reminder app, MedGuard assists users throughout the entire medication lifecycle—from reading prescriptions and organizing schedules to answering medication-related questions, monitoring adherence, and ensuring reminders reach users through multiple communication channels.

---

## Table of Contents

1. [What is MedGuard?](#1-what-is-medguard)
2. [Why Medication Adherence Matters](#2-why-medication-adherence-matters)
3. [Project Overview](#3-project-overview)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Project Structure](#6-project-structure)
7. [The Journey of a Medication](#7-the-journey-of-a-medication)
8. [Authentication Flow](#8-authentication-flow)
9. [Prescription OCR Pipeline](#9-prescription-ocr-pipeline)
10. [LangGraph Agentic AI Engine](#10-langgraph-agentic-ai-engine)
11. [Medication Reminder Engine](#11-medication-reminder-engine)
12. [Dashboard & Analytics](#12-dashboard--analytics)
13. [Database Design](#13-database-design)
14. [API Endpoints](#14-api-endpoints)
15. [Building and Running](#15-building-and-running)
16. [Future Improvements](#16-future-improvements)

---

# 1. What is MedGuard?

Medication adherence is one of the biggest challenges in healthcare.

Many patients forget medications, misunderstand prescriptions, or fail to complete treatment schedules. Existing reminder applications generally solve only one part of this problem by sending scheduled notifications.

MedGuard is designed to manage the **entire medication workflow**.

Instead of functioning as a timer, the platform can:

- Read prescriptions automatically
- Organize medication schedules
- Answer medication-related questions
- Track adherence history
- Generate analytics
- Synchronize reminders with Google Calendar
- Send SMS reminders
- Escalate reminders through WhatsApp
- Maintain conversational context using an Agentic AI architecture

Unlike traditional rule-based healthcare chatbots, MedGuard uses a **stateful AI workflow**, allowing conversations to continue naturally across multiple interactions.

---

## Traditional Reminder Apps

```
User
 │
 ▼
Create Reminder
 │
 ▼
Phone Notification
 │
 ▼
Done
```

These applications generally stop after sending a notification.

They do not understand medication information, provide conversational assistance, or monitor long-term adherence.

---

## What MedGuard Does

```
Prescription
      │
      ▼
 OCR Extraction
      │
      ▼
 Medication Database
      │
      ▼
 Intelligent Scheduling
      │
      ▼
 Calendar Events
      │
      ▼
 SMS Reminder
      │
(No Response)
      ▼
 WhatsApp Reminder
      │
      ▼
 User Confirmation
      │
      ▼
 Dashboard & Analytics
      │
      ▼
 AI Assistant
```

The platform continuously connects every component together rather than treating each feature independently.

---

# 2. Why Medication Adherence Matters

Medication adherence refers to how consistently a patient follows the treatment prescribed by a healthcare professional.

Poor adherence leads to

- Delayed recovery
- Treatment failure
- Increased hospitalization
- Higher healthcare costs
- Poor chronic disease management

Some common reasons include

- Forgetting medications
- Multiple medicines with different schedules
- Difficult-to-read prescriptions
- Lack of follow-up reminders
- No visibility into medication history

Many existing applications only notify users but cannot answer questions such as

```
Did I take my medicine today?

What medicines are pending?

Show my adherence this week.

How many doses have I missed?

When is my next medication?
```

MedGuard addresses these challenges by combining intelligent scheduling with conversational AI.

---

# 3. Project Overview

MedGuard follows a cloud-native architecture composed of three major layers.

```
                User
                  │
                  ▼
        Streamlit Web Interface
                  │
                  ▼
        FastAPI REST Backend
                  │
 ┌────────────────┼────────────────┐
 │                │                │
 ▼                ▼                ▼
OCR         LangGraph AI      Analytics
 │                │                │
 └────────────────┼────────────────┘
                  ▼
          Firebase Firestore
                  │
        ┌─────────┼───────────┐
        ▼         ▼           ▼
 Google Calendar Gemini      Twilio
                   OCR     SMS/WhatsApp
```

The frontend is responsible for

- Authentication
- Medication management
- Prescription upload
- Dashboard visualization
- AI chat interface

The backend performs

- Business logic
- Authentication verification
- Medication CRUD operations
- AI routing
- OCR processing
- Notification scheduling
- Analytics generation

External cloud services provide

- OCR
- Calendar synchronization
- SMS delivery
- WhatsApp messaging
- Secure authentication

---

## Overall Workflow

```
User
 │
 ▼
Login
 │
 ▼
Upload Prescription
 │
 ▼
OCR extracts medicines
 │
 ▼
Verify extracted information
 │
 ▼
Save medications
 │
 ▼
Calendar events created
 │
 ▼
Scheduler monitors medication time
 │
 ▼
SMS Reminder
 │
 ▼
WhatsApp Escalation
 │
 ▼
User confirms medicine
 │
 ▼
Adherence updated
 │
 ▼
Dashboard refreshed
```

Every module shares data through the backend rather than communicating directly with each other.

This keeps the architecture modular, secure, and scalable.

---

# 4. System Architecture

MedGuard follows a three-tier architecture.

```
                 PRESENTATION LAYER
┌────────────────────────────────────────────┐
│                                            │
│            Streamlit Frontend              │
│                                            │
│ Login                                      │
│ Dashboard                                  │
│ Medication Management                       │
│ OCR Upload                                 │
│ AI Chat                                    │
│ Analytics                                  │
│                                            │
└───────────────────┬────────────────────────┘
                    │ REST APIs
                    ▼

               APPLICATION LAYER

┌────────────────────────────────────────────┐
│                                            │
│             FastAPI Backend                │
│                                            │
│ Authentication                             │
│ Medication CRUD                            │
│ OCR Processing                             │
│ LangGraph Agent                            │
│ Analytics Engine                           │
│ APScheduler Jobs                           │
│ Calendar Synchronization                   │
│                                            │
└───────────────────┬────────────────────────┘
                    │
                    ▼

                  DATA LAYER

┌────────────────────────────────────────────┐
│ Firebase Firestore                         │
│ Firebase Authentication                    │
└────────────────────────────────────────────┘
                    │
                    ▼

             EXTERNAL SERVICES

      Google Gemini Vision
      Google Calendar API
      Twilio SMS
      Twilio WhatsApp
```

The architecture separates presentation, business logic, and data management, making the project easier to maintain and extend.

---

# 5. Technology Stack

| Layer | Technology | Purpose |
|--------|------------|---------|
| Frontend | Streamlit | User Interface |
| Backend | FastAPI | REST API |
| Database | Firebase Firestore | NoSQL Storage |
| Authentication | Firebase Auth | User Authentication |
| AI Workflow | LangGraph | Stateful Agent |
| LLM | Google Gemini | Natural Language Understanding |
| OCR | Gemini Vision | Prescription Recognition |
| Scheduler | APScheduler | Reminder Scheduling |
| Calendar | Google Calendar API | Native Device Reminders |
| Messaging | Twilio | SMS & WhatsApp Notifications |
| Visualization | Plotly | Dashboard Charts |

---

## Why These Technologies?

Rather than selecting technologies independently, each component was chosen to solve a specific problem.

| Problem | Technology Used |
|----------|-----------------|
| User Interface | Streamlit |
| REST Communication | FastAPI |
| Authentication | Firebase |
| Persistent Storage | Firestore |
| AI Conversation | LangGraph |
| OCR | Gemini Vision |
| Notifications | Twilio |
| Calendar Sync | Google Calendar |
| Scheduling | APScheduler |
| Analytics | Plotly |

Together these components create a fully cloud-native medication management platform.

---

# 6. Project Structure

The project follows a modular architecture where every major responsibility is isolated into its own component.

```
MedGuard/
│
├── frontend/
│   │
│   ├── app.py
│   ├── pages/
│   │   ├── Dashboard.py
│   │   ├── Medications.py
│   │   ├── Analytics.py
│   │   ├── OCR.py
│   │   └── AI_Assistant.py
│   │
│   └── components/
│
├── backend/
│   │
│   ├── main.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── medications.py
│   │   ├── analytics.py
│   │   └── ocr.py
│   │
│   ├── services/
│   │   ├── calendar.py
│   │   ├── scheduler.py
│   │   ├── twilio.py
│   │   └── firebase.py
│   │
│   ├── ai/
│   │   ├── langgraph_agent.py
│   │   ├── intent_classifier.py
│   │   ├── tools.py
│   │   └── gemini.py
│   │
│   └── models/
│
├── firebase/
│
├── requirements.txt
│
└── README.md
```

---

## Frontend

The Streamlit frontend provides the entire user experience.

It is responsible for

- User Authentication
- Dashboard
- Medication Management
- OCR Upload
- AI Chat
- Analytics
- Settings

The frontend **never communicates directly** with Firebase or external APIs.

Instead, every request is sent to the FastAPI backend.

```
Frontend

        │

        ▼

FastAPI REST API

        │

        ▼

Database / AI Services
```

This keeps authentication secure while centralizing all business logic.

---

## Backend

The FastAPI backend acts as the brain of the application.

It performs

- Authentication validation
- CRUD operations
- OCR requests
- LangGraph execution
- Calendar synchronization
- Reminder scheduling
- Analytics computation

Every frontend interaction eventually reaches the backend.

```
Frontend

      │

      ▼

Authentication

Medication APIs

OCR APIs

Analytics APIs

LangGraph

Scheduler

      │

      ▼

Firestore
```

---

## AI Layer

The AI module contains all intelligent functionality.

Instead of sending every user question directly to Gemini, the project first determines the user's intent.

```
User Question

        │

        ▼

Intent Classification

        │

        ├──────────────┐

        ▼              ▼

Tool A          Tool B

        │              │

        └──────┬───────┘

               ▼

      Natural Language Response
```

This design reduces hallucinations while allowing the AI to interact with real medication data.

---

## External Services

Several cloud services are integrated.

```
               FastAPI

                  │

     ┌────────────┼────────────┐

     ▼            ▼            ▼

 Firebase     Gemini      Google Calendar

                                │

                                ▼

                             Twilio
```

Each service has a dedicated responsibility.

| Service | Purpose |
|----------|---------|
| Firebase | Authentication & Database |
| Gemini | OCR + AI |
| Calendar API | Native reminders |
| Twilio | SMS & WhatsApp |

---

# 7. The Journey of a Medication

Understanding MedGuard becomes much easier by following **one medication** from the moment a prescription is uploaded until the medicine is marked as taken.

This section explains the complete lifecycle.

```
Prescription

      │

      ▼

OCR

      │

      ▼

Medicine Extraction

      │

      ▼

User Verification

      │

      ▼

Firestore Storage

      │

      ▼

Calendar Event

      │

      ▼

Scheduler

      │

      ▼

Reminder

      │

      ▼

User Confirmation

      │

      ▼

Analytics Update
```

---

## Step 1 — User Login

The workflow begins after the user logs in.

```
User

 │

 ▼

Login Screen

 │

 ▼

Firebase Authentication

 │

 ▼

JWT Token

 │

 ▼

Authenticated Session
```

Every subsequent API request contains the authentication token.

This ensures medications remain private to each user.

---

## Step 2 — Upload Prescription

The user uploads a prescription image.

Supported formats include

- JPG
- JPEG
- PNG

```
Prescription Image

        │

        ▼

Upload

        │

        ▼

FastAPI OCR Endpoint
```

Unlike manually typing every medicine, OCR significantly reduces data entry.

---

## Step 3 — Image Processing

The uploaded image is converted into Base64.

```
Image

 │

 ▼

Read Bytes

 │

 ▼

Base64 Encoding

 │

 ▼

Gemini Vision API
```

Gemini receives both

- the image
- a structured prompt

The prompt instructs the model to respond **only with JSON**.

Example response

```json
{
  "medication_name": "Paracetamol",
  "dosage": "500 mg",
  "frequency": "1-0-1",
  "duration": "5 Days"
}
```

Because the output is structured JSON, parsing becomes straightforward.

---

## Step 4 — User Verification

OCR is never assumed to be perfect.

The extracted values are shown to the user before saving.

```
OCR

 │

 ▼

Extracted Medicines

 │

 ▼

Editable Form

 │

 ▼

User Verification

 │

 ▼

Save
```

The user can

- edit medicine name
- change dosage
- modify frequency
- adjust duration

before submission.

---

## Step 5 — Medication Storage

After verification, the medication is saved.

```
User

 │

 ▼

POST /medications/add

 │

 ▼

FastAPI

 │

 ▼

Firestore
```

Each medication contains

```
Medication

├── Name

├── Dosage

├── Frequency

├── Scheduled Times

├── Start Date

├── End Date

└── Notes
```

This information becomes the single source of truth throughout the application.

---

## Step 6 — Calendar Synchronization

Immediately after saving, Google Calendar events are created.

```
Medication Saved

       │

       ▼

Calendar Service

       │

       ▼

Recurring Events

       │

       ▼

Native Device Notifications
```

This allows users to receive reminders even when the application is closed.

---

## Step 7 — APScheduler Monitoring

Creating calendar events alone is not enough.

A background scheduler continuously checks upcoming medications.

```
APScheduler

      │

      ▼

Runs Every Minute

      │

      ▼

Queries Firestore

      │

      ▼

Matches Current Time

      │

      ▼

Reminder Trigger
```

Instead of relying solely on Google Calendar, MedGuard independently verifies medication schedules.

---

## Step 8 — SMS Reminder

Once the scheduled time matches,

Twilio sends an SMS.

```
Medication Time

       │

       ▼

Scheduler

       │

       ▼

Twilio SMS

       │

       ▼

User
```

The reminder contains medication information so the user knows exactly which medicine to take.

---

## Step 9 — WhatsApp Escalation

If the medication remains unconfirmed,

a second reminder is sent.

```
SMS

 │

 ▼

No Response

 │

 ▼

WhatsApp

 │

 ▼

Reminder
```

This cascading strategy improves adherence compared to relying on a single notification channel.

---

## Step 10 — User Confirmation

The user confirms medication intake.

This can happen through

- Dashboard
- AI Chat
- Medication page

```
Medicine Taken

      │

      ▼

POST

/taken

      │

      ▼

Firestore Log
```

A new adherence record is created.

---

## Step 11 — Dashboard Update

After confirmation,

analytics automatically update.

```
Taken

 │

 ▼

Analytics Engine

 │

 ▼

Adherence %

Current Streak

Weekly Doses

Medication Count

 │

 ▼

Dashboard
```

No manual refresh is required.

The dashboard always reflects the latest medication history.

---

# Complete Workflow

Putting everything together,

```
Prescription

      │

      ▼

Upload

      │

      ▼

OCR

      │

      ▼

Verify

      │

      ▼

Firestore

      │

      ▼

Calendar Event

      │

      ▼

Scheduler

      │

      ▼

SMS

      │

(No Response)

      ▼

WhatsApp

      │

      ▼

Medicine Taken

      │

      ▼

Analytics

      │

      ▼

Dashboard

      │

      ▼

AI Assistant
```

This end-to-end workflow is what differentiates MedGuard from a traditional reminder application.

Rather than functioning as an isolated reminder tool, every component communicates through the backend to create a unified medication management platform.

---

---

# 8. Authentication Flow

Before a user can access medications, reminders, or analytics, the system verifies their identity using **Firebase Authentication**.

Unlike traditional applications that store passwords in a local database, MedGuard delegates authentication entirely to Firebase, ensuring secure credential management and token-based session handling.

---

## Authentication Workflow

```
User

 │

 ▼

Signup / Login

 │

 ▼

Firebase Authentication

 │

 ▼

ID Token

 │

 ▼

Streamlit Session

 │

 ▼

REST API Request

 │

 ▼

FastAPI

 │

 ▼

Token Verification

 │

 ▼

Firestore Access
```

Every request sent from the frontend includes the Firebase ID Token inside the Authorization header.

```
Authorization:

Bearer <Firebase Token>
```

The backend validates the token before executing any operation.

---

## User Registration

When a new user registers,

the following sequence occurs.

```
User Information

 │

 ▼

Signup Form

 │

 ▼

POST /auth/signup

 │

 ▼

Firebase Authentication

 │

 ▼

Create User

 │

 ▼

Firestore Profile

 │

 ▼

Registration Complete
```

The backend never stores passwords.

Only Firebase manages credentials.

---

## User Login

```
Email

Password

      │

      ▼

Firebase Login

      │

      ▼

ID Token

      │

      ▼

Stored in Session

      │

      ▼

Authenticated APIs
```

The session remains active until logout.

---

## Why Firebase?

Instead of implementing authentication from scratch,

Firebase provides

- Secure password hashing
- Email authentication
- Token generation
- Session management
- Identity verification

This significantly reduces security risks while simplifying backend development.

---

# 9. Prescription OCR Pipeline

One of MedGuard's primary features is automatic prescription reading.

Instead of manually typing medicine information, users simply upload an image.

The OCR pipeline extracts

- Medicine Name
- Dosage
- Frequency
- Duration

---

## OCR Workflow

```
Prescription Image

        │

        ▼

Image Upload

        │

        ▼

FastAPI

        │

        ▼

Base64 Encoding

        │

        ▼

Gemini Vision

        │

        ▼

JSON Response

        │

        ▼

Medication Form

        │

        ▼

Firestore
```

Unlike conventional OCR engines that return raw text,

Gemini Vision returns structured information ready for database storage.

---

## Why Base64?

Images cannot be directly embedded into JSON requests.

Therefore,

```
Image

 │

 ▼

Bytes

 │

 ▼

Base64 String

 │

 ▼

Gemini Request
```

The encoded image is transmitted together with a structured prompt.

---

## OCR Prompt Strategy

Rather than asking,

> "Read this prescription"

the system asks the model to return only structured JSON.

Example

```json
{
    "medication_name": "",
    "dosage": "",
    "frequency": "",
    "duration": ""
}
```

This makes parsing deterministic.

---

## OCR Decision Flow

```
Image

 │

 ▼

Gemini Vision

 │

 ▼

Medicine Found?

 │

 ├───────────────┐

 │Yes            │No

 ▼               ▼

JSON        Empty Response

 │               │

 ▼               ▼

Medication     Retry

Form
```

---

## Manual Entry Fallback

OCR should assist users,

not replace manual entry.

Therefore,

```
Add Medication

      │

      ├───────────────┐

      ▼               ▼

Manual          OCR Upload

      │               │

      └───────┬───────┘

              ▼

       Save Medication
```

This ensures every medication can be added,

regardless of prescription quality.

---

# 10. LangGraph Agentic AI Engine

Unlike a normal chatbot,

MedGuard uses an **Agentic AI architecture**.

Instead of asking Gemini to answer everything,

the application first decides

**what the user is trying to accomplish.**

---

## Traditional Chatbot

```
Question

 │

 ▼

LLM

 │

 ▼

Answer
```

Every request is handled the same way.

---

## MedGuard Agent

```
Question

 │

 ▼

Intent Classification

 │

 ├──────────────┐

 ▼              ▼

Tool A      Tool B

 │              │

 └──────┬───────┘

        ▼

 Response
```

Instead of one giant prompt,

multiple specialized tools perform specific tasks.

---

## Supported Intents

The AI currently recognizes four primary intents.

```
User Question

        │

        ▼

Intent Classifier

        │

 ┌──────┼─────────────┐

 ▼      ▼             ▼

Adherence

Pending

Taken

Drug Info
```

Each intent activates a different workflow.

---

## Adherence Tool

Example questions

```
How am I doing this week?

Show adherence.

Did I miss medicines?
```

Workflow

```
Question

 │

 ▼

Firestore

 │

 ▼

Compute %

 │

 ▼

Natural Response
```

---

## Pending Medicine Tool

Example

```
Which medicines are left today?
```

Workflow

```
Question

 │

 ▼

Today's Schedule

 │

 ▼

Pending Medicines

 │

 ▼

Response
```

---

## Dose Confirmation Tool

Example

```
I have taken my medicine.

Mark today's dose complete.
```

Workflow

```
Question

 │

 ▼

Firestore

 │

 ▼

Create Log

 │

 ▼

Confirmation
```

---

## Drug Information Tool

Example

```
What is Paracetamol?

What is this medicine used for?
```

Workflow

```
Question

 │

 ▼

Gemini

 │

 ▼

Explanation
```

Unlike the previous tools,

this one does not require Firestore.

---

## Why LangGraph?

Most chatbots are stateless.

```
Question 1

↓

Answer

Question 2

↓

Answer
```

Every interaction is isolated.

LangGraph maintains state.

```
Question

↓

History

↓

Current State

↓

Tool Selection

↓

Response
```

This enables

```
User:

Did I take Paracetamol?

Assistant:

No.

User:

What about the other one?
```

The AI understands that

"the other one"

refers to the previously discussed medication.

---

## Agent Decision Tree

```
                User Query

                     │

                     ▼

          Intent Classification

                     │

      ┌──────────────┼──────────────┐

      ▼              ▼              ▼

Adherence      Pending        Drug Info

      │              │              │

      ▼              ▼              ▼

Firestore     Firestore       Gemini

      │              │              │

      └──────────────┼──────────────┘

                     ▼

            Natural Language Reply
```

This routing strategy significantly reduces unnecessary LLM calls while allowing responses to be grounded in live medication data instead of model memory.

---

---

# 11. Medication Reminder Engine

Scheduling reminders is the core responsibility of MedGuard.

Unlike conventional reminder applications that rely on a single notification, MedGuard follows a **multi-channel cascading notification architecture**.

If one reminder is missed, another communication channel is automatically used.

This significantly improves medication adherence.

---

## Reminder Workflow

```
Medication Saved

       │

       ▼

Google Calendar Event

       │

       ▼

APScheduler

       │

       ▼

Scheduled Time Reached

       │

       ▼

SMS Reminder

       │

User Responded?

       │

   ┌───┴─────────────┐

   │Yes              │No

   ▼                 ▼

Update Logs     WhatsApp Reminder

   │                 │

   └────────┬────────┘

            ▼

      Dashboard Updated
```

Unlike simple reminder applications,

the scheduler continuously monitors medication schedules stored inside Firestore.

---

## Why APScheduler?

Google Calendar notifications alone are insufficient.

For example,

- User dismisses notification
- Device notifications disabled
- Calendar synchronization delayed

Therefore,

MedGuard runs an independent scheduler.

```
Application Starts

        │

        ▼

APScheduler

        │

        ▼

Every Minute

        │

        ▼

Query Firestore

        │

        ▼

Compare Current Time

        │

        ▼

Trigger Reminder
```

This provides an additional layer of reliability.

---

## Scheduler Logic

```
Current Time

      │

      ▼

09:00

      │

      ▼

Medication Collection

      │

      ▼

Medicine Scheduled?

      │

 ┌────┴─────────┐

 │Yes           │No

 ▼              ▼

SMS          Wait 1 Minute
```

Every medication stored in Firestore contains one or more scheduled times.

The scheduler compares each medication against the current system time.

---

## SMS Notification

Once a scheduled medication matches,

Twilio sends an SMS.

```
Medication

      │

      ▼

Twilio API

      │

      ▼

SMS Gateway

      │

      ▼

User Phone
```

The message contains medication information to reduce confusion.

Example

```
Reminder

Take

Amoxicillin

500 mg

at 9:00 AM
```

---

## WhatsApp Escalation

Missing one notification should not mean missing medication.

If the medicine is still unconfirmed,

the system sends another reminder.

```
SMS

 │

 ▼

No Confirmation

 │

 ▼

Twilio WhatsApp

 │

 ▼

WhatsApp Message

 │

 ▼

User
```

This cascading approach increases the probability that users receive the reminder.

---

## Three-Level Reminder Strategy

```
                  Medication Time

                         │

                         ▼

           Google Calendar Reminder

                         │

                         ▼

                 Twilio SMS

                         │

                No Confirmation

                         │

                         ▼

            WhatsApp Reminder
```

Each notification channel acts as a fallback for the previous one.

---

## Reminder Flow Summary

```
Medication

      │

      ▼

Firestore

      │

      ▼

Scheduler

      │

      ▼

Calendar

      │

      ▼

SMS

      │

      ▼

WhatsApp

      │

      ▼

Confirmation

      │

      ▼

Analytics
```

---

# 12. Dashboard & Analytics

Tracking medications is only useful if users can visualize their progress.

MedGuard provides an analytics dashboard that summarizes medication adherence in real time.

---

## Dashboard Overview

```
Dashboard

├── Overall Adherence

├── Current Streak

├── Weekly Doses

├── Registered Medicines

└── 30-Day Trend
```

Every statistic is generated directly from Firestore.

No values are manually maintained.

---

## Dashboard Workflow

```
Dashboard Opened

        │

        ▼

GET

/analytics/dashboard

        │

        ▼

FastAPI

        │

        ▼

Firestore

        │

        ▼

Analytics Engine

        │

        ▼

JSON Response

        │

        ▼

Plotly Charts
```

---

## Overall Adherence

The most important metric is

```
Overall Adherence %

=

Medicines Taken

───────────────

Medicines Scheduled
```

Example

```
Scheduled

10 Medicines

Taken

8 Medicines

Adherence

80%
```

---

## Current Streak

The streak measures

how many consecutive medication events have been completed.

```
✔

✔

✔

✔

✔

❌

Current Streak

5
```

This encourages users to maintain consistency.

---

## Weekly Dose Count

```
Monday

■■■

Tuesday

■■

Wednesday

■■■

Thursday

■

Friday

■■

Saturday

■■■

Sunday

■■
```

Users immediately see whether they are following their treatment schedule.

---

## Thirty-Day Trend

```
100 ┤                         ●

 90 ┤                     ●

 80 ┤                ●

 70 ┤          ●

 60 ┤    ●

 50 ┤●

    └──────────────────────────────

      Day1            Day30
```

Rather than displaying isolated numbers,

the dashboard shows long-term adherence behavior.

---

## Dashboard Metrics

The dashboard currently displays

| Metric | Description |
|---------|-------------|
| Overall Adherence | Percentage of completed medications |
| Current Streak | Consecutive successful doses |
| Weekly Doses | Medicines taken during current week |
| Registered Medicines | Total active medications |
| Daily Trend | Thirty-day adherence history |

---

# 13. Database Design

MedGuard stores application data inside Firebase Firestore.

Unlike SQL databases,

Firestore organizes information as collections and documents.

---

## Firestore Structure

```
Firestore

│

├── users

│      └── userID

│

├── medications

│      └── medicationID

│

└── adherence_logs

       └── logID
```

Each authenticated user owns their own medication documents.

---

## User Collection

```
users

│

└── uid

      ├── name

      ├── email

      └── phone
```

Authentication information is managed by Firebase Authentication,

while profile information is stored separately.

---

## Medication Collection

Each medication document stores

```
Medication

├── userId

├── medicineName

├── dosage

├── frequency

├── scheduledTimes

├── startDate

├── endDate

└── notes
```

This information drives

- Dashboard
- Scheduler
- Calendar
- AI Assistant

---

## Adherence Collection

Every completed medication creates an adherence log.

```
Adherence Log

├── medicationId

├── userId

├── status

├── timestamp

└── source
```

Example

```
status

=

taken
```

Source may indicate

```
Dashboard

Chat

Automatic
```

allowing future analytics to understand how medications were confirmed.

---

## Database Relationships

```
User

 │

 ▼

Medications

 │

 ▼

Adherence Logs

 │

 ▼

Analytics
```

Rather than duplicating data,

every component references the same Firestore documents.

This keeps the application consistent while reducing redundancy.

---

## Why Firestore?

Firestore provides several advantages.

- Real-time synchronization
- Cloud scalability
- Flexible NoSQL schema
- Firebase Authentication integration
- Fast document retrieval
- Minimal backend configuration

These characteristics make it well suited for cloud-native healthcare applications.

---

---

# 14. API Endpoints

The frontend never communicates directly with Firebase, Gemini, Twilio, or Google Calendar.

Instead, every operation passes through the FastAPI backend.

This architecture centralizes business logic, validation, security, and external API integrations.

```
Streamlit

     │

 REST Request

     │

     ▼

FastAPI

     │

 ┌───┼────────────────────────────┐

 ▼   ▼                            ▼

Firebase                  Gemini Vision

Calendar API              Twilio

     │

     ▼

 JSON Response

     │

     ▼

Frontend
```

---

## Authentication APIs

Authentication APIs manage user registration and login.

### Signup

```
POST

/auth/signup
```

Purpose

- Create Firebase account
- Generate user profile
- Initialize database record

---

### Login

```
POST

/auth/login
```

Purpose

- Verify credentials
- Generate Firebase ID Token
- Start authenticated session

---

## Medication APIs

Medication management revolves around four CRUD endpoints.

### Add Medication

```
POST

/medications/add
```

Workflow

```
Medication Form

       │

       ▼

Validation

       │

       ▼

Firestore

       │

       ▼

Calendar Sync

       │

       ▼

Success
```

---

### Get Medications

```
GET

/medications/list
```

Returns

- Active medicines
- Dosage
- Frequency
- Schedule
- Notes

---

### Update Medication

```
PUT

/medications/edit
```

Updates

- Dosage
- Frequency
- Time
- Notes
- End date

Calendar events are synchronized automatically after updates.

---

### Delete Medication

```
DELETE

/medications/delete
```

Deletes

- Firestore document
- Calendar events
- Scheduled reminders

---

## OCR API

```
POST

/ocr/parse
```

Workflow

```
Image

 │

 ▼

Gemini Vision

 │

 ▼

Structured JSON

 │

 ▼

Medication Form
```

---

## Analytics API

```
GET

/analytics/dashboard
```

Returns

```
Overall Adherence

Current Streak

Weekly Medicines

Registered Medicines

30-Day Trend
```

---

## AI APIs

The AI Assistant communicates through the backend.

```
Question

 │

 ▼

LangGraph

 │

 ▼

Tool Selection

 │

 ▼

Response
```

The frontend never communicates directly with Gemini.

---

## Overall API Flow

```
User

 │

 ▼

Frontend

 │

 ▼

REST API

 │

 ▼

Business Logic

 │

 ▼

Firestore

Gemini

Calendar

Twilio

 │

 ▼

JSON

 │

 ▼

Frontend
```

---

# 15. Building and Running

## Prerequisites

Install

- Python 3.10+
- Firebase Project
- Google Gemini API Key
- Google Calendar API Credentials
- Twilio Account

---

## Clone Repository

```bash
git clone https://github.com/karshPC/agenticAiMedicationTrackingAndReminder.git

cd agenticAiMedicationTrackingAndReminder
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create

```
.env
```

Example

```env
GEMINI_API_KEY=

FIREBASE_CREDENTIALS=

TWILIO_ACCOUNT_SID=

TWILIO_AUTH_TOKEN=

TWILIO_PHONE_NUMBER=

GOOGLE_CALENDAR_CLIENT_ID=

GOOGLE_CALENDAR_CLIENT_SECRET=
```

---

## Start FastAPI

```bash
uvicorn main:app --reload
```

Default

```
http://localhost:8000
```

---

## Start Streamlit

```bash
streamlit run app.py
```

Default

```
http://localhost:8501
```

---

## Application Startup

```
Start Backend

        │

        ▼

Initialize Firebase

        │

        ▼

Initialize Gemini

        │

        ▼

Initialize Scheduler

        │

        ▼

Start APIs

        │

        ▼

Ready
```

---

# 16. Future Improvements

Although MedGuard provides an end-to-end medication management platform, several enhancements can further improve usability and intelligence.

---

## Handwritten Prescription OCR

Current OCR focuses primarily on printed prescriptions.

Future versions can support

- Doctor handwriting
- Mixed handwriting
- Regional hospital prescriptions

```
Prescription

       │

       ▼

Handwritten OCR

       │

       ▼

Medicine Extraction
```

---

## Regional Language Support

Future OCR models can recognize

- Hindi

- Punjabi

- Tamil

- Telugu

- Bengali

- Marathi

allowing the application to support a much larger patient population.

---

## Local AI Models

Current implementation relies on cloud APIs.

Future versions may integrate

```
Llama

Mistral

Phi

Gemma
```

for offline medication assistance.

Benefits

- Better privacy

- Lower latency

- Offline support

---

## Adaptive Reminder Scheduling

Current reminders are time based.

Future versions can learn user behavior.

```
Reminder

 │

 ▼

User Response

 │

 ▼

Learning Algorithm

 │

 ▼

Better Reminder Time
```

Instead of always reminding at 9:00 AM,

the system could automatically adjust notification timing.

---

## Caregiver Portal

Future releases may include

```
Patient

      │

      ▼

Medication Data

      │

      ▼

Caregiver Dashboard
```

Caregivers could

- monitor adherence
- receive missed dose alerts
- review medication history

---

## Voice Assistant

Future versions could support

```
"Did I take my medicine?"

"When is my next dose?"

"Mark today's medicine as taken."
```

using speech recognition.

---

## Wearable Integration

Potential integrations include

- Smart Watches

- Health Bands

- Smart Speakers

providing medication reminders without opening the application.

---

# 17. What This Project Demonstrates

MedGuard combines several modern software engineering concepts into a single cloud-native healthcare platform.

The project demonstrates

- REST API Development
- Cloud-native Architecture
- Firebase Authentication
- NoSQL Database Design
- Agentic AI Workflows
- LangGraph State Management
- OCR Integration
- Google Calendar Synchronization
- APScheduler Background Jobs
- Twilio Communication APIs
- Interactive Analytics
- Streamlit Frontend Development
- FastAPI Backend Development
- Multi-Service Cloud Integration

---

## Complete System Overview

```
                   User

                     │

                     ▼

          Streamlit Frontend

                     │

                     ▼

              FastAPI Backend

                     │

 ┌───────────────────┼────────────────────┐

 ▼                   ▼                    ▼

Firestore       LangGraph AI       OCR Engine

 │                   │                    │

 ├──────────────┬────┘                    │

 ▼              ▼                         ▼

Analytics   Scheduler             Gemini Vision

 │              │

 ▼              ▼

Dashboard   Calendar API

                    │

                    ▼

             Twilio SMS

                    │

                    ▼

          WhatsApp Reminder
```

---

## Summary

MedGuard transforms traditional medication reminder systems into an intelligent medication management platform by combining conversational AI, prescription understanding, cloud-native architecture, and multi-channel notification delivery.

Rather than functioning as a standalone reminder application, the system creates a complete workflow that begins with prescription processing and continues through medication scheduling, adherence monitoring, conversational assistance, analytics generation, and intelligent reminder escalation.

By integrating Agentic AI, OCR, FastAPI, Firebase, Google Calendar, and Twilio into a unified architecture, MedGuard demonstrates how modern AI-powered software systems can improve medication management while providing a scalable foundation for future healthcare applications.

---

**Happy Coding! 🚀**

# Legal Intake System

> AI-powered WhatsApp bot for legal case intake with lawyer dashboard

A complete legal intake automation system that captures client details via WhatsApp, processes legal documents with AI, and provides lawyers with a real-time dashboard for case management.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Setup Guide](#setup-guide)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Security & Compliance](#security--compliance)

---

## 🎯 Overview

### What Problem Does It Solve?

Law firms receive countless inquiries via WhatsApp but lack structured intake processes. This leads to:
- Lost client information
- Inconsistent data collection
- Manual document processing
- Delayed response times

### The Solution

An automated WhatsApp bot that:
1. Greets clients and captures consent
2. Collects case details in a structured manner (English/Hindi/Hinglish)
3. Accepts document uploads (judgments, FIRs, notices)
4. Extracts key legal entities using AI (parties, sections, courts, dates)
5. Summarizes documents in layman's terms
6. Routes to lawyers with actionable next steps
7. Integrates scheduling and payments

---

## 🛠 Tech Stack

### **Frontend (Lawyer Dashboard)**

| Technology | Purpose | Version |
|------------|---------|---------|
| **Next.js 14** | React framework with App Router | 14.2.18 |
| **TypeScript** | Type-safe development | 5.6.3 |
| **Tailwind CSS** | Utility-first styling | 3.4.15 |
| **shadcn/ui** | Accessible UI components | Latest |
| **React Query** | Server state management | 5.59.16 |
| **Zustand** | Client state management | 5.0.1 |
| **react-pdf** | PDF viewing | 9.1.1 |
| **Recharts** | Data visualization | 2.13.3 |
| **Supabase JS** | Backend client | 2.45.6 |

### **Backend (API & Business Logic)**

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Async Python web framework | Latest |
| **Python** | Core language | 3.11+ |
| **Pydantic** | Data validation | Built-in |
| **Celery** | Background task queue | Latest |
| **Redis** | Caching & session storage | Latest |

### **Database & Storage**

| Technology | Purpose |
|------------|---------|
| **Supabase PostgreSQL** | Primary database with RLS |
| **Supabase Storage** | Encrypted document storage |
| **Supabase Auth** | Authentication & authorization |
| **Supabase Realtime** | Live updates to dashboard |
| **Qdrant** | Vector database for embeddings |

### **AI & NLP**

| Service | Purpose |
|---------|---------|
| **OpenAI GPT-4o** | Summarization, entity extraction, conversation |
| **Hugging Face Transformers** | IndicBERT for Hindi NLP |
| **Tesseract OCR** | Text extraction from images |
| **Google Document AI** | Advanced OCR (Hindi/English) |
| **Bhashini API** | Free Hindi ↔ English translation |

### **Communication & Integrations**

| Service | Purpose |
|---------|---------|
| **Meta Cloud API** | WhatsApp Business Platform |
| **Razorpay** | Indian payment gateway |
| **Stripe** | International payments |
| **Google Calendar API** | Appointment scheduling |
| **Microsoft Graph** | Outlook integration |

### **DevOps & Deployment**

| Tool | Purpose |
|------|---------|
| **Docker** | Containerization |
| **Vercel** | Frontend hosting |
| **Render** | Backend hosting |
| **GitHub Actions** | CI/CD pipeline |
| **Sentry** | Error tracking |

---

## 🏗 Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  User (WhatsApp) ←→ Meta Cloud API ←→ Webhook                  │
│  Lawyer (Browser) ←→ Next.js Dashboard                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌─────────────────────┐          │
│  │  FastAPI Backend │←───────→│  Next.js Frontend   │          │
│  │                  │         │  (Server Components)│          │
│  │  • WhatsApp Bot  │         │  • Live Inbox       │          │
│  │  • AI Processing │         │  • PDF Viewer       │          │
│  │  • OCR Pipeline  │         │  • Analytics        │          │
│  │  • Payments      │         │  • Quick Replies    │          │
│  └────────┬─────────┘         └──────────┬──────────┘          │
│           │                               │                      │
└───────────┼───────────────────────────────┼──────────────────────┘
            │                               │
            ↓                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Supabase         │  │    Redis     │  │    Qdrant       │   │
│  │                  │  │              │  │                 │   │
│  │ • PostgreSQL     │  │ • Sessions   │  │ • Embeddings    │   │
│  │ • Auth           │  │ • Cache      │  │ • Semantic      │   │
│  │ • Storage        │  │ • Queue      │  │   Search        │   │
│  │ • Realtime       │  │              │  │                 │   │
│  └──────────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                           │
├─────────────────────────────────────────────────────────────────┤
│  OpenAI • Bhashini • Razorpay • Google Calendar • Sentry       │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
WhatsApp Message → Meta Webhook → FastAPI
                                     ↓
                            Language Detection
                                     ↓
                            Conversation FSM
                                     ↓
                     ┌───────────────┴──────────────┐
                     ↓                              ↓
              Text Response                  Document Upload
                     ↓                              ↓
              Save to Supabase               OCR + AI Extraction
                     ↓                              ↓
              Realtime Update  ←─────────  Store + Summarize
                     ↓
              Dashboard Updates Live
```

---

## ⚙️ How It Works

### 1️⃣ **Client WhatsApp Interaction**

**Step 1: Greeting & Consent**
```
Bot: Hi! I'm the intake assistant for [Law Firm]. 
     I can collect basic details and share them with the lawyer. 
     Do I have your consent? (Yes/No)

User: Yes

Bot: Great! Let me help you. नमस्ते! मैं आपकी सहायता कर सकता हूँ। 
     Which language do you prefer? / आप किस भाषा में बात करना चाहेंगे?
     [English] [हिंदी]
```

**Step 2: Language Detection**
- Detects user language automatically (EN/HI/Hinglish)
- Persists choice for entire session
- User can switch via `/lang en` or `/lang hi`

**Step 3: Matter Type Selection**
```
Bot: What type of legal matter is this?

[Civil] [Criminal] [Family] 
[Corporate] [Property] [Employment] [Other]

User: Criminal

Bot: Please describe your situation briefly.
```

**Step 4: Details Collection**
```
Bot: Which court or jurisdiction? (e.g., Delhi High Court)

User: Saket District Court

Bot: Do you have any prior court orders, FIRs, or judgments? 
     You can upload a photo or PDF.
```

**Step 5: Document Processing**
```
[User uploads PDF judgment]

Bot: Processing your document... ⏳

Bot: ✅ Document analyzed!
     
     Summary: The court dismissed the petition under Section 482 CrPC 
     filed against FIR No. 123/2023. The petitioner was accused under 
     Sections 420, 406 IPC...
     
     Key Details:
     • Court: Saket District Court
     • Case: FIR 123/2023
     • Sections: 420, 406 IPC
     • Date: 15th March 2024
     
     ⚠️ Disclaimer: This is not legal advice.
     
     Suggested Next Steps:
     1. Book a 30-min consultation (₹500)
     2. File appeal within limitation period
     3. Collect additional evidence
     
     [Schedule Consultation] [Talk to Lawyer] [Share More Details]
```

### 2️⃣ **Backend AI Processing**

**Conversation State Machine**
```python
States: GREETING → CONSENT → LANGUAGE → MATTER_TYPE → 
        DESCRIPTION → JURISDICTION → DOCUMENT → CONTACT → SUMMARY
```

**Document Pipeline**
1. **Validate** file type (PDF/JPG/PNG, max 10MB)
2. **Store** in Supabase Storage (encrypted)
3. **Extract** text:
   - PDF: PyPDF2
   - Image: Tesseract OCR + Google Document AI
4. **Translate** (if Hindi) using Bhashini
5. **Summarize** using GPT-4o:
   ```
   Prompt: "Summarize this legal document in simple language 
            for a layperson. Extract: parties, court, sections, 
            key dates, disposition."
   ```
6. **Extract Entities** using NER:
   - Parties (petitioner/respondent)
   - Court name & bench
   - Case citation
   - Sections/Acts
   - Key dates
   - Disposition (dismissed/allowed/pending)
7. **Store** embeddings in Qdrant for semantic search
8. **Update** Supabase → triggers Realtime update to dashboard

### 3️⃣ **Lawyer Dashboard**

**Live Inbox**
- Real-time updates via Supabase Realtime
- Shows new conversations with unread count
- Click to view full conversation history

**Case View**
- PDF viewer (react-pdf) with annotations
- AI summary sidebar
- Extracted entities in structured format
- Conversation timeline

**Quick Actions**
- Send WhatsApp template messages
- Edit suggested next steps
- Mark as "Needs Review" / "Contacted" / "Converted"
- Assign to lawyer
- Flag for human handover

**Payment & Scheduling**
- Generate Razorpay payment link
- Send consultation booking link (Google Calendar)
- Track payment status

**Analytics Dashboard**
- Volume trends (daily/weekly/monthly)
- Matter type breakdown (pie chart)
- Conversion funnel (intake → consult → retainer)
- Average response time
- Top jurisdictions

### 4️⃣ **Background Workers (Celery)**

Async tasks for heavy operations:
- Document OCR processing
- AI summarization (can take 5-30 seconds)
- Batch translation
- Data retention cleanup (auto-delete after X days)
- Email/SMS notifications

---

## 📁 Project Structure

```
legal-intake-system/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── services/        # Business logic
│   │   │   ├── whatsapp/    # Bot logic
│   │   │   ├── ai/          # LLM, NER, translation
│   │   │   ├── document/    # OCR, parsing
│   │   │   ├── payment/     # Razorpay, Stripe
│   │   │   └── calendar/    # Scheduling
│   │   ├── core/            # Config, auth, DB
│   │   └── workers/         # Celery tasks
│   └── requirements.txt
│
├── frontend/                # Next.js dashboard
│   ├── src/
│   │   ├── app/            # Pages (App Router)
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities
│   │   │   └── supabase/   # DB client
│   │   └── hooks/          # Custom hooks
│   └── package.json
│
├── supabase/
│   ├── migrations/         # SQL migrations
│   └── config.toml
│
├── docker-compose.yml      # Local dev setup
└── README.md              # This file
```

---

## 🚀 Setup Guide

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Supabase account (free tier)
- Meta Developer account (WhatsApp Business)
- OpenAI API key

### 1. Clone Repository

```bash
git clone https://github.com/LamQam/legal-intake-system.git
cd legal-intake-system
```

### 2. Setup Supabase

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Init project
supabase init

# Link to cloud project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your keys

# Run migrations (if not using Supabase)
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local
# Edit with Supabase keys

# Start dev server
npm run dev
```

### 5. Setup WhatsApp Webhook

```bash
# Expose local backend (for testing)
ngrok http 8000

# Configure in Meta Developer Console:
# Webhook URL: https://your-ngrok-url.ngrok.io/api/v1/webhooks/whatsapp
# Verify Token: YOUR_VERIFY_TOKEN
```

### 6. Run with Docker (Alternative)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📚 API Documentation

### WhatsApp Webhook

**POST** `/api/v1/webhooks/whatsapp`

Receives messages from Meta Cloud API.

**GET** `/api/v1/webhooks/whatsapp`

Webhook verification endpoint.

### Cases API

**GET** `/api/v1/cases`
- List all cases
- Query params: `status`, `lawyer_id`, `matter_type`

**GET** `/api/v1/cases/{case_id}`
- Get case details with conversations

**PATCH** `/api/v1/cases/{case_id}`
- Update case (status, next steps, assigned lawyer)

### Documents API

**GET** `/api/v1/documents/{doc_id}`
- Download document

**GET** `/api/v1/documents/{doc_id}/summary`
- Get AI summary and extracted entities

### Payments API

**POST** `/api/v1/payments/create`
- Create Razorpay/Stripe payment link

**POST** `/api/v1/payments/webhook`
- Handle payment callbacks

---

## 🌐 Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Backend (Render)

1. Connect GitHub repo
2. Select `backend` folder
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Database (Supabase)

Will be already hosted - just use connection string.

---

## 🔒 Security & Compliance

### Data Protection

- **Encryption at Rest**: All documents encrypted via Supabase Storage
- **Encryption in Transit**: HTTPS/TLS 1.3
- **PII Handling**: Phone numbers hashed, minimal storage
- **Access Control**: Row-Level Security (RLS) in PostgreSQL

### Audit Trail

Every action logged:
```json
{
  "user_id": "uuid",
  "action": "document_viewed",
  "resource_type": "document",
  "resource_id": "doc_uuid",
  "timestamp": "2024-10-21T10:30:00Z",
  "ip_address": "1.2.3.4"
}
```

### Consent Management

- Explicit opt-in before data collection
- Stored in `consent` table with timestamp
- Can withdraw consent (deletes all data)

### Data Retention

- Configurable per-organization
- Default: 90 days for unconverted leads
- Permanent delete after retention period


---


**Built with ❤️ for the legal community in India**
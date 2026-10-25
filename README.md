# 🤖 VernaLedger AI (व्हर्ना लेजर ए आय)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vernaledger-ai.streamlit.app)
![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue?logo=python)
![Google Gemini](https://img.shields.io/badge/AI%20Engine-Google%20Gemini%20Vision%20%26%20Flash-orange?logo=google)
![Edge TTS](https://img.shields.io/badge/Voice-Microsoft%20Neural%20Edge--TTS-blueviolet)
![Database](https://img.shields.io/badge/Database-SQLite3%20(WAL%20Mode)-003B57?logo=sqlite)
![Status](https://img.shields.io/badge/Deployment-Live%20on%20Streamlit%20Cloud-success)

> **Next-Generation Vernacular Financial Assistant & Intelligent Khata Ledger for Indian Retailers, Kirana Stores, and MSMEs.**

---

## 🌟 Overview

**VernaLedger AI** bridges the digital divide for small Indian businesses by providing an intuitive, multilingual, and voice-enabled financial ledger system. Built specifically for the Indian commerce ecosystem, it understands handwritten regional receipts (Marathi, Hindi, English), processes spoken voice bills, manages customer credit (*Udhaari*), predicts inventory reorders, and answers business queries in real-time through an intelligent Context-Aware RAG AI Chatbot.

---

## 📸 Visual Showcase

<div align="center">
  <table>
    <tr>
      <td width="50%">
        <h4 align="center">🔐 Secure Glassmorphic Login</h4>
        <img src="assets/login.png" alt="Login Screen" width="100%"/>
      </td>
      <td width="50%">
        <h4 align="center">🧾 Smart OCR Receipt Scanner</h4>
        <img src="assets/ocr.png" alt="OCR Scanner" width="100%"/>
      </td>
    </tr>
    <tr>
      <td width="50%">
        <h4 align="center">📖 Customer Khata & Passbook</h4>
        <img src="assets/khata.png" alt="Customer Khata" width="100%"/>
      </td>
      <td width="50%">
        <h4 align="center">🤖 Context-Aware RAG AI Chatbot</h4>
        <img src="assets/rag.png" alt="RAG AI Chat" width="100%"/>
      </td>
    </tr>
    <tr>
      <td width="50%">
        <h4 align="center">📊 Analytics & Financial Overview</h4>
        <img src="assets/analytics.png" alt="Analytics Dashboard" width="100%"/>
      </td>
      <td width="50%">
        <h4 align="center">👥 Staff Roles & Audit Logs</h4>
        <img src="assets/staff.png" alt="Staff Management" width="100%"/>
      </td>
    </tr>
  </table>
</div>

---

## 🚀 Key Modules & Capabilities

### 1. 🧾 Smart Multilingual OCR Scanner
- **Regional Handwriting OCR:** Powered by Google Gemini Vision models to accurately extract item names, quantities, unit prices, and grand totals from handwritten or printed Devanagari (Marathi/Hindi) receipts.
- **58mm Pure Thermal Receipt:** Generates crisp POS slips ready for one-click printing or PDF download.
- **Smart Duplicate Prevention:** Automatically checks the database to prevent duplicate entries of the same bill.
- **One-Click Batch Inward:** Add all scanned receipt items directly into the shop's live inventory with a single tap.

### 2. 🎙️ Multi-Language Spoken Voice Billing
- **Hands-Free Billing:** Speak transaction details naturally in Marathi, Hindi, or English (e.g., *"रमेश कडून २ किलो साखर १०० रुपये आणि १ लिटर तेल १५० रुपये"*).
- **Auto-Parsing:** Converts natural spoken audio into structured itemized billing records instantaneously.

### 3. 📖 Customer Khata & Credit Ledger (*उधारी खाते*)
- **360° Customer Profiles:** Track customer balances, phone numbers, transaction timelines, and aging risk.
- **Direct Payment Collection:** Record payments instantly with automatic ledger passbook entries.
- **One-Click WhatsApp Reminders:** Generate personalized payment reminder messages with pre-filled customer details.

### 4. 🤖 Context-Aware RAG AI Chatbot with Neural Voice Output
- **Live Ledger Knowledge:** Asks analytical questions directly about sales, pending credit, customer debts, and stock availability (*"आज किती उधारी येणे बाकी आहे?", "साखर किती शिल्लक आहे?"*).
- **Neural Voice Output:** Natural speech responses powered by Microsoft Neural TTS (`mr-IN-AarohiNeural` for Marathi, `en-IN-NeerjaNeural` for English) with tuned regional pronunciation.

### 5. 📦 Business Operations & Inventory Management
- **Predictive Reorder System:** Real-time low-stock alerts with auto-calculated wholesale reorder suggestions.
- **Expense Tracking:** Monitor day-to-day shop operational costs with category breakdowns.

### 6. 🔐 Staff Management & Enterprise Security
- **Role-Based Access Control (RBAC):** Separate interfaces and permission levels for Store Owners (`Admin`) and Cashiers (`Staff`).
- **Cryptographic Security:** Passwords hashed with salted `PBKDF2-HMAC-SHA256`.
- **Immutable Audit Trail:** Comprehensive activity logging for financial compliance.

### 7. 🌐 Multilingual Text & Voice AI
- The AI Business Studio accepts typed and spoken questions in **Marathi, English, Hindi, Gujarati, Tamil, Telugu, Kannada, Bengali, Spanish, and French**.
- Speech recognition uses the selected locale and neural voice output uses a matching Edge-TTS voice where available.
- The application language selector persists the chosen language and the Kirana mode layout is optimized for desktop and mobile screens.

---

## 🛠️ Architecture & Tech Stack

```mermaid
flowchart TD
    A["User Input: Voice / Image / Text"] --> B["Streamlit Modern UI"]
    B --> C{"Input Routing"}
    C -->|"Receipt Image"| D["Gemini Vision OCR Engine"]
    C -->|"Voice Bill"| E["Speech Recognition & Gemini Parser"]
    C -->|"Analytical Query"| F["RAG AI Core (Gemini Flash)"]
    C -->|"Ledger Entry"| G["Transaction Controller"]
    
    D --> G
    E --> G
    G --> H[("SQLite Ledger DB (WAL Mode)")]
    H -->|"Database Context"| F
    F --> I["Microsoft Edge-TTS Engine"]
    I --> J["Aarohi / Neerja Audio Output"]
    G --> K["Live KPI & Analytics Dashboard"]
```

| Layer | Technologies |
| :--- | :--- |
| **Frontend & UI** | [Streamlit](https://streamlit.io), Custom HTML5/CSS3 (Glassmorphism), Vanilla JS Components |
| **AI & Multimodal Vision** | [Google Gemini 2.0 / 1.5 Flash](https://ai.google.dev/) via `google-generativeai` |
| **Voice & Speech Synthesis** | Microsoft Neural [Edge-TTS](https://github.com/rany2/edge-tts) (`mr-IN-AarohiNeural`, `en-IN-NeerjaNeural`) |
| **Database & Persistence** | [SQLite3](https://sqlite.org) with Write-Ahead Logging (WAL) & automated snapshots |
| **Security & Validation** | `pydantic` schemas, PBKDF2-HMAC password encryption, Role-based guards |

---

## 💻 Local Installation & Setup

### Prerequisites
- Python **3.11+** (Tested on Python 3.11, 3.12, 3.13)
- Git
- Google Gemini API Key ([Get one free from Google AI Studio](https://aistudio.google.com/))

### 1. Clone the Repository
```bash
git clone https://github.com/sanketkirdat08-cmd/vernaledger-ai.git
cd vernaledger-ai
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure API Keys
Create `.streamlit/secrets.toml` in the project root:
```toml
GEMINI_API_KEY = "your_google_gemini_api_key_here"
```

For the optional Smart Scanner fallback, enable the **Cloud Vision API** in the same
Google Cloud project, create a service account with the `Cloud Vision API User` role,
and configure Application Default Credentials. Do not commit the service-account JSON.

Windows PowerShell:
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\secure\google-cloud-service-account.json"
```

For serverless environments where a file is not available, provide the minified service
account JSON as `GOOGLE_CLOUD_CREDENTIALS_JSON`. Gemini remains the primary scanner;
Cloud Vision is called only when Gemini cannot return a result.

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

---

## ⚡ Deployment on Vercel (Production Serverless SPA)

VernaLedger.AI features a production-grade **FastAPI Serverless Backend** (`api/index.py`) and a responsive **Cyberpunk Dark Glassmorphic SPA** (`public/index.html`, `public/style.css`, `public/app.js`), fully pre-configured for 1-click deployment on [Vercel](https://vercel.com):

1. **Push to GitHub**:
   Ensure all changes are pushed to your GitHub repository `vernaledger-ai`.
2. **Import to Vercel**:
   - Go to [vercel.com](https://vercel.com) and log in.
   - Click **"Add New..."** -> **"Project"**.
   - Select your `vernaledger-ai` repository and click **Import**.
3. **Configure Environment Variables**:
   - Expand the **Environment Variables** section.
   - Key: `GEMINI_API_KEY`
   - Value: `your_google_gemini_api_key_here`
4. **Deploy**:
   - Click **Deploy**. Vercel will automatically build the Python serverless API and serve the high-speed static frontend at `https://your-project.vercel.app`.

### Install as a mobile or desktop app

The frontend includes a PWA manifest, install icons, and a service worker. Open the
HTTPS Vercel URL in Chrome or Edge, then choose **Install VernaLedger** from the
browser menu. Installation requires the deployed HTTPS URL; `localhost` is only for
local development.

### Production data persistence

Vercel serverless functions do not provide durable local SQLite storage. For
production use, configure a managed database such as Supabase and migrate the
ledger tables before relying on the app for permanent receipts or khata records.
Set `GEMINI_API_KEY` and the database connection variables in the Vercel project
Environment Variables for Production, Preview, and Development as appropriate.

---

## ☁️ Deployment on Streamlit Community Cloud (Legacy)

1. Fork or push this repository to your GitHub account.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Create a new app:
   - **Repository:** `your-username/vernaledger-ai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Under **Advanced settings** -> **Secrets**, paste your API key:
   ```toml
   GEMINI_API_KEY = "your_google_gemini_api_key_here"
   ```
5. Click **Deploy!** 🚀

---

## 👨‍💻 Project Team & Credits

This project was developed by the B.Tech Final Year Engineering Team at **Arvind Gavali College of Engineering, Satara (AGCE Satara)**, affiliated with **Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere**:

* 🎓 **Project Guide:** **Prof. Kaisar Atar Sir** (*प्रा. कैसर अत्तार सर*) — Department of AI & DS
* 💻 **Project Development Team:**
  * 👑 **Sanket Kirdat** (*संकेत किर्दत*) — **Roll No: 4060 | PRN: 24065451263508** — **Team Leader & AI Developer**
  * 🎨 **Sakshi Bhagat** (*साक्षी भगत*) — **Roll No: 4054 | PRN: 24065451263502** — **Frontend & UI Developer**
  * 🎙️ **Vaishnavi Dhavale** (*वैष्णवी ढवळे*) — **Roll No: 4056 | PRN: 24065451263504** — **Voice Billing & AI Developer**
  * 🗄️ **Rushikesh Mulik** (*ऋषिकेश मुळीक*) — **Roll No: 4004 | PRN: 23065451263005** — **Backend & Database Developer**
* 🏛️ **Institution:** **Arvind Gavali College of Engineering, Satara, Maharashtra**
* 📚 **Department:** **Artificial Intelligence & Data Science (AI & DS)**

---

## 📄 License

This project is developed for academic, retail empowerment, and research purposes. All rights reserved.

# VernaLedger.AI - Merchant Pro v7.5

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini%20AI-4285F4?logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Ledger-003B57?logo=sqlite&logoColor=white)
![PWA](https://img.shields.io/badge/PWA-Mobile%20Ready-5A0FC8)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?logo=vercel)

भारतीय किराणा दुकाने आणि लहान व्यापाऱ्यांसाठी बनवलेली एक बहुभाषिक AI लेजर, बिलिंग आणि स्टोअर व्यवस्थापन प्रणाली.

**VernaLedger.AI** FastAPI backend, responsive vanilla HTML/CSS/JavaScript PWA frontend आणि Google Gemini AI वापरते. स्मार्ट OCR, आवाजातून बिलिंग, ग्राहक उधारी (खाता), इन्व्हेंटरी, खर्च, dashboard आणि नेचरल-भाषिक AI सहाय्यक एकाच application मध्ये उपलब्ध आहेत.

## मुख्य वैशिष्ट्ये

- **बहुभाषिक स्मार्ट स्कॅनर** - मराठी, हिंदी आणि इंग्रजी पावत्या/हस्तलिखित बिलांमधील मजकूर Gemini Vision किंवा Google Cloud Vision वापरून वाचते.
- **आवाजातून बिलिंग** - बोललेली transaction तपशीलांमध्ये parser करते.
- **Customer Khata / उधारी खाते** - ग्राहकांचे debit, credit, payment आणि outstanding balance व्यवस्थापित करते.
- **Inventory व्यवस्थापन** - stock quantity, reorder/alert limit आणि selling price व्यवस्थापित करते.
- **Business expenses** - खर्चाचे प्रकार, रक्कम आणि नोंदी ठेवते.
- **AI Business Studio** - ledger context वापरून sales, stock, expenses आणि उधारीबद्दल प्रश्नांची उत्तरे देते.
- **Gemini Live voice chat** - browser PCM audio थेट Gemini Live WebSocket session ला bridge करते.
- **Neural TTS** - Edge-TTS वापरून मराठी आणि इतर समर्थित भाषांमध्ये आवाजात प्रतिसाद देते.
- **PWA support** - HTTPSवर installable आहे, theme आणि अनेक UI भाषांचा support आहे.
- **Offline-friendly local mode** - browser client data sync API द्वारे SQLite मध्ये restore करण्यास support करते.
- **GitOps auto-sync** - local server चालू असताना ledger snapshot तयार करते आणि changes GitHub वर push करते.

## उपलब्ध modules

| Module | कार्य |
|---|---|
| स्मार्ट स्कॅनर | receipt image OCR आणि bill/item extraction |
| ग्राहक खाते | customer credit, payments आणि khata passbook |
| स्टोअर ऑपरेशन्स | inventory आणि business expenses |
| लेजर व पावत्या | receipt search, save, delete आणि bulk actions |
| AI बिझनेस स्टुडिओ | ledger-aware RAG chat, voice chat आणि TTS |
| Dashboard | sales, pending उधारी, expenses, net profit आणि low stock |

## तंत्रज्ञान

| भाग | तंत्रज्ञान |
|---|---|
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| AI / OCR | Google Gemini, Google Cloud Vision fallback |
| Voice | Edge-TTS, Web Speech API, Gemini Live WebSocket |
| Database | SQLite3; local mode मध्ये `ledger.db` |
| Export | CSV आणि Excel/XLSX |
| Deployment | Vercel Serverless Functions; PWA |
| Local sync | `git_auto_sync.py` GitOps auto-sync |

## प्रोजेक्टची रचना

```text
vernaledger-ai/
├── api/
│   └── index.py             # FastAPI application, database, AI आणि API routes
├── public/
│   ├── index.html           # PWA application interface
│   ├── app.js               # frontend logic आणि API calls
│   ├── style.css            # responsive UI styles
│   ├── sw.js                # service worker
│   └── manifest.webmanifest # installable PWA metadata
├── assets/
│   └── vernaledger_bg.jpg
├── icons/
├── data/
│   └── live_ledger_snapshot.json
├── app.py                   # local unified server entry point
├── git_auto_sync.py         # offline-safe Git snapshot/push daemon
├── requirements.txt
├── vercel.json
├── .env.example
└── run_local.bat
```

## स्थानिक setup

### आवश्यकता

- Python 3.11 किंवा त्याहून नवे
- Git
- Google Gemini API key

### 1. Repository clone करा

```bash
git clone https://github.com/sanketkirdat08-cmd/vernaledger-ai.git
cd vernaledger-ai
```

### 2. Virtual environment तयार करा

Windows:

```bat
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependencies install करा

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment configuration

`.env.example` मधून `.env` तयार करा:

```env
GEMINI_API_KEY=your_gemini_api_key_here

# पर्यायी: Google Cloud Vision fallback
# GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
# GOOGLE_CLOUD_CREDENTIALS_JSON={"type":"service_account",...}
```

Gemini API key [Google AI Studio](https://aistudio.google.com/) वरून मिळू शकते.

Google Cloud Vision fallback वापरायचा असल्यास Google Cloud project मध्ये **Cloud Vision API** enable करा आणि service account ला आवश्यक read/OCR permissions द्या. Credential JSON किंवा त्याचा secret string repository मध्ये commit करू नका.

### 5. Application चालवा

```bash
python app.py
```

नंतर उघडा:

- Laptop: `http://127.0.0.1:8000`
- त्याच network वरील mobile: application console मध्ये दाखवलेला `http://<LAN-IP>:8000`

Windows वर `run_local.bat` देखील वापरता येते.

### Demo login

Frontend आणि API master/admin fallback म्हणून हे credentials देते:

```text
Username: admin
Password: admin123
```

`sanket` वापरकर्ता नाव आणि `verna123`, `pass123` या passwords सहही admin master fallback उपलब्ध आहे. Production deployment मध्ये हे predictable credentials बदलणे किंवा master fallback हटवणे आवश्यक आहे.

## API endpoints

मुख्य endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | application health |
| `POST /api/login` | user login |
| `POST /api/register` | नवीन account registration |
| `GET /api/dashboard` | business metrics |
| `POST /api/ocr` | receipt image OCR |
| `POST /api/voice-billing` | spoken bill parsing |
| `POST /api/rag-chat` | ledger-aware AI chat |
| `POST /api/tts` | neural text-to-speech |
| `WS /api/live-chat` | Gemini Live voice WebSocket |
| `GET/POST/DELETE /api/receipts` | receipts CRUD |
| `GET/POST/DELETE /api/khata` | customer khata CRUD |
| `GET/POST/DELETE /api/inventory` | inventory CRUD |
| `GET/POST/DELETE /api/expenses` | expenses CRUD |
| `POST /api/sync` | bi-directional client/server data sync |
| `GET /api/export/csv` | CSV export |
| `GET /api/export-excel` | Excel export |

FastAPI interactive documentation सामान्यतः `http://127.0.0.1:8000/docs` वर उपलब्ध असते.

## Vercel वर deployment

1. GitHub मधील repository Vercel project म्हणून import करा.
2. Vercel environment variables मध्ये `GEMINI_API_KEY` configure करा.
3. Optional Google Vision credentials तसेच secrets म्हणून configure करा.
4. Deploy करा.

Frontend आणि API दोन्ही `vercel.json` मधील routes/rewrites वापरतात. Serverless function चे timeout setting 60 seconds आहे.

### Production data persistence

Vercel फंक्शन्स ephemeral आहेत. Vercelमध्ये `/tmp/ledger.db` वापरला जातो; प्रत्येक serverless instance किंवा cold start नंतर database state टिकू शकत नाही.

Permanent data storage आणि वास्तविक production वापरासाठी managed database (उदा. Supabase/PostgreSQL) मध्ये schema migration करणे आवश्यक आहे. सधाची implementation खालील SQLite-backed features संदर्भित करते:

- receipts आणि deleted receipt tombstones
- customer khata आणि tombstones
- inventory
- expenses
- users आणि shop settings

## PWA install

Vercel किंवा HTTPS deployment उघडल्यानंतर Chrome किंवा Edge मधील browser menu मधून **Install VernaLedger** निवडा.

PWA manifest आणि service worker पुढील paths मधून serve केले जातात:

- `/manifest.webmanifest`
- `/sw.js`
- `/icons/`

## Local GitOps data sync

`python app.py` चालवल्यावर `git_auto_sync.py` मधील background daemon:

- प्रत्येक 4 सेकंदांनी SQLite data JSON snapshot मध्ये export करते;
- offline असताना local Git commit तयार करते;
- internet उपलब्ध असताना `origin/main` वर push करते;
- `ledger.db` आणि database sidecar files `.gitignore` मध्ये excluded आहेत.

`data/live_ledger_snapshot.json` tracked data file असू शकते. Customer आणि business data सार्वजनिक repository मध्ये commit होऊ शकत असल्याने ते production वापरात संवेदनशील मानून repository exposure आणि credentials तपासा.

## सुरक्षा सूचना

- API keys आणि `.env` मध्ये ठेवलेली credentials commit करू नका.
- demo/master credentials production मध्ये हटवा किंवा बदला.
- सर्व customer, staff आणि receipt data वर उत्पादनात secure authentication आणि authorization लागू करा.
- HTTPS आणि managed database वापरा.
- सार्वजनिक किंवा sample repositories मधून database snapshots किंवा identifiable customer data हटवा.

## Project team

**Arvind Gavali College of Engineering, Satara (AGCE Satara)**  
Department of Artificial Intelligence & Data Science  
Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere

- **Project Guide:** Mr. Kaisar Atar
- **Head of Department:** Dr. S. Y. Mulla
- **Team Leader & AI Developer:** Sanket Kirdat
- **Frontend & UI Developer:** Sakshi Bhagat
- **Voice Billing & AI Developer:** Vaishnavi Dhavale
- **Backend & Database Developer:** Rushikesh Mulik

## License

This project is developed for academic, retail empowerment and research purposes. Review the repository owner for specific usage and redistribution terms.

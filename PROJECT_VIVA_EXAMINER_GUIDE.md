# 🎓 VernaLedger.AI - परीक्षक व्हिवा आणि प्रोजेक्ट डायरेक्टरी गाईड
### (Examiner Viva Defense & Project Architecture Master Guide)

> [!IMPORTANT]
> **परीक्षकांनी कोणताही प्रश्न विचारल्यास हे पान उघडून तुम्ही क्षणात अचूक उत्तर, फाईलचे नाव आणि कोडची लाईन दाखवू शकता.**

---

## 🏛️ १. प्रकल्पाचे ३-टिअर तांत्रिक आर्किटेक्चर (3-Tier Architecture)

| टिअर (Tier) | तंत्रज्ञान व टूल्स (Tech Stack) | संबंधित फाईल्स (Files) | मुख्य जबाबदारी (Key Responsibilities) |
| :--- | :--- | :--- | :--- |
| **Tier 1: Client**<br>*(फ्रंटएंड ॲप)* | HTML5, Vanilla JavaScript (ES6+), CSS3 Glassmorphism, Web Speech API, MediaRecorder, PWA | [`index.html`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/index.html)<br>[`app.js`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/app.js)<br>[`style.css`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/style.css)<br>[`sw.js`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/sw.js) | • वापरकर्ता डॅशबोर्ड व सायबरपंक UI<br>• थेट कॅमेरा स्कॅनर व व्हॉइस रेकॉर्डिंग<br>• १-क्लिक WhatsApp स्मरणपत्र व बिल शेअरिंग<br>• थर्मल प्रिंटर बिल आणि ऑफलाइन कॅशिंग |
| **Tier 2: Backend**<br>*(सर्व्हरलेस AI इंजिन)* | Python 3.13 + FastAPI, Google Gemini 3.5 Flash Lite (REST Transport), Regex NLP Parser, Edge-TTS | [`api/index.py`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/api/index.py)<br>[`vercel.json`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/vercel.json)<br>[`requirements.txt`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/requirements.txt) | • हस्तलिखित पावतीचे Multimodal OCR स्कॅनिंग<br>• ग्रामीण मराठी ASR स्पीच-टू-टेक्स्ट बिलिंग<br>• Verna AI RAG फायनान्शियल चॅटबॉट<br>• व्यवसाय नफा-तोटा विश्लेषण व Excel एक्सपोर्ट |
| **Tier 3: Ledger**<br>*(हायब्रिड डेटाबेस)* | SQLite 3 (ACID WAL Mode), VernaStorage (लोकल-फर्स्ट झिरो-डेटा-लॉस इंजिन), Native XlsxWriter | [`ledger.db`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/ledger.db)<br>[`app.js`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/app.js) *(VernaStorage)* | • ग्राहक उधारी वही (Khata Ledger)<br>• दैनंदिन विक्री व इन्व्हॉइस नोंदी<br>• दुकानातील साठा (Inventory Management)<br>• सर्व्हरलेस कोल्ड-स्टार्ट डेटा संरक्षण व रिहायड्रेशन |

---

## 📂 २. फाईल डिरेक्टरी आणि कोड मॅपिंग (Where is What?)

कोणत्या वैशिष्ट्याचा कोड कुठे आहे हे दाखवणारा झटपट तक्ता:

| वैशिष्ट्य (Feature) | फाईल (File) | लाईन नंबर (Lines) | कोड फंक्शन / तपशील |
| :--- | :--- | :--- | :--- |
| **📸 Multimodal OCR स्कॅनर** | `api/index.py` | L. 903 – 1250 | `@app.post("/api/ocr")`<br>`_execute_ocr_bytes()`: Gemini 3.5 Flash Lite द्वारे हस्तलिखित मराठी पावती स्कॅनिंग. |
| **🎙️ व्हॉइस बिलिंग (Voice-to-Bill)** | `api/index.py`<br>`app.js` | L. 1359 – 1580<br>L. 2050 – 2300 | `@app.post("/api/voice-billing")`<br>मराठी आवाजातून थेट पावती व वस्तूंची विभागणी. |
| **📲 १-क्लिक WhatsApp तगादा** | `app.js` | L. 2690 – 2740<br>L. 4840 – 4880 | `wa.me/91...`<br>ग्राहकाला थेट UPI पेमेंट लिंकसह WhatsApp उधारी स्मरणपत्र पाठवणे. |
| **🤖 Verna AI RAG चॅटबॉट** | `api/index.py`<br>`app.js` | L. 2550 – 3700<br>L. 3800 – 4100 | `@app.post("/api/rag-chat")`<br>थेट SQLite डेटाबेसवरून नफा-तोटा व उधारी हिशोब उत्तर (No Hallucination). |
| **💾 झिरो डेटा लॉस (VernaStorage)** | `app.js`<br>`api/index.py` | L. 31 – 350<br>L. 2410 – 2545 | `const VernaStorage`<br>`@app.post("/api/sync")`: ऑफलाइन नोंदी सर्व्हर सुरू होताच ऑटो-सिंक होतात. |
| **🖨️ थर्मल प्रिंटर पावती** | `app.js` | L. 2550 – 2650 | `printReceipt()` / `window.print()`: ५८mm/८०mm थर्मल प्रिंटरसाठी कस्टमाईज्ड रिसिट. |
| **📊 १-क्लिक Excel एक्सपोर्ट** | `api/index.py` | L. 1813 – 2010 | `@app.get("/api/export-excel")`<br>`XlsxWriter` द्वारे संपूर्ण हिशोबाची एक्सेल शीट तयार होते. |
| **📦 साठा व्यवस्थापन (Inventory)** | `api/index.py`<br>`app.js` | L. 2353 – 2405<br>L. 3000 – 3150 | `@app.get("/api/inventory")`<br>कमी साठा (Low-Stock Alert) स्वयंचलित चेतावणी. |
| **🔒 सुरक्षा व ऑथेंटिकेशन** | `api/index.py` | L. 550 – 650 | `bcrypt` पासवर्ड हॅशिंग व युझर रोल मॅनेजमेंट (Admin/Staff). |
| **⚡ सर्व्हरलेस कॉन्फिगरेशन** | `vercel.json` | संपूर्ण फाईल | सर्व्हरलेस राऊटिंग, API रीराईट्स आणि ६० सेकंद टाइमआउट. |

---

## 🎯 ३. परीक्षकांचे संभाव्य १५ प्रश्न आणि अचूक उत्तरे (Top 15 Examiner Viva Q&A)

### प्रश्न १: "प्रोजेक्टचे मुख्य उद्दिष्ट (Problem Statement) काय आहे?"
> **उत्तर:** भारतातील विशेषतः महाराष्ट्रातील ९०% ग्रामीण व निमशहरी किराणा दुकानदार अजूनही कच्च्या कागदावर व वहीत उधारी आणि खरेदी लिहितात. अक्षरे अस्पष्ट असणे, गणित चुकणे, उधारी विसरणे आणि डेटा हरवणे या मोठ्या समस्या आहेत. **VernaLedger.AI** हे किराणा दुकानदारांसाठी खास प्रादेशिक (मराठी) भाषेतील AI लेजर आहे, जे १ सेकंदात हस्तलिखित पावती स्कॅन करते, आवाजावरून बिल बनवते आणि WhatsApp द्वारे उधारी वसूल करण्यास मदत करते.

### प्रश्न २: "पावतीवरील घाईत लिहिलेले मराठी अक्षर AI कसे वाचते (Multimodal OCR)?"
> **उत्तर:** आम्ही **Google Gemini 3.5 Flash Lite** हे Native Multimodal मॉडेल्स वापरत आहोत. हे मॉडेल **Vision Transformers (ViT)** आर्किटेक्चरवर काम करते. ते पावतीचा फोटो आणि भाषा एकाच न्यूरल नेटवर्कद्वारे थेट समजून घेते. अस्पष्ट अंक (उदा. १ की ७) हे आजूबाजूच्या शब्दांवरून आणि गणिताचा हिशोब (दर × वजन = एकूण रक्कम) तपासून अचूक ओळखले जातात.
> *(कोड पहा: `api/index.py` लाईन ९०३ - १०८०)*

### प्रश्न ३: "इंटरनेट नसेल किंवा सर्व्हर बंद झाला तर डेटा उडतो का (Data Loss)?"
> **उत्तर:** **नाही, १००% डेटा सुरक्षित राहतो.** आम्ही **Client-Side VernaStorage (Offline-First)** आर्किटेक्चर तयार केले आहे. इंटरनेट नसताना सर्व डेटा ब्राउझरच्या स्थानिक मेमरीत (IndexedDB / LocalStorage) सुरक्षित सेव्ह होतो. जेव्हा इंटरनेट येते, तेव्हा `/api/sync` एंडपॉईंटद्वारे सर्व डेटा बॅकएंड SQLite मध्ये ऑटो-सिंक (Auto-Rehydrate) होतो.
> *(कोड पहा: `app.js` लाईन ३१ आणि `api/index.py` लाईन २४१०)*

### प्रश्न ४: "व्हॉट्सॲप स्मरणपत्र (1-Click WhatsApp Reminder) कसे जाते?"
> **उत्तर:** आम्ही अधिकृत WhatsApp Web/API चा डीपलिंक प्रोटोकॉल (`https://wa.me/91<नंबर>?text=<मेसेज>`) वापरला आहे. यामध्ये दुकानदाराचे नाव, ग्राहकाचे नाव, थकीत रक्कम, शेवटच्या खरेदीची तारीख आणि थेट ऑनलाइन पैसे भरण्यासाठी **UPI Payment Link** स्वयंचलितपणे तयार होऊन ग्राहकाच्या WhatsApp वर १-क्लिकमध्ये जाते.
> *(कोड पहा: `app.js` लाईन २६९० आणि ४८४०)*

### प्रश्न ५: "Verna AI चॅटबॉट खोटे किंवा चुकीचे उत्तर (Hallucination) का देत नाही?"
> **उत्तर:** कारण आमचा चॅटबॉट हवेत उत्तरे देत नाही. तो **RAG (Retrieval-Augmented Generation)** आर्किटेक्चर वापरतो. जेव्हा युझर प्रश्न विचारतो (उदा. "या महिन्यात किती नफा झाला?"), तेव्हा सिस्टीम आधी स्थानिक **SQLite डेटाबेसवरून** प्रत्यक्ष विक्री आणि खर्चाची आकडेवारी काढते आणि त्या सत्य आकडेवारीच्या आधारावरच मराठीत अचूक उत्तर देते.
> *(कोड पहा: `api/index.py` लाईन २५५०)*

### प्रश्न ६: "डेटाबेस कोणता वापरला आहे आणि का?"
> **उत्तर:** आम्ही **SQLite 3** हे **WAL Mode (Write-Ahead Logging)** सह वापरले आहे. हे सर्व्हरलेस डिप्लॉयमेंट (Vercel / Local) साठी अत्यंत वेगवान, हलके आणि ACID कम्पलायंट आहे. यात `users`, `receipts`, `customer_khata`, `shop_inventory`, `business_expenses`, `audit_logs` आणि `shop_settings` अशी ७ सुव्यवस्थित टेबल्स आहेत.
> *(कोड पहा: `api/index.py` लाईन १५० - २५०)*

### प्रश्न ७: "प्रोजेक्टमध्ये सुरक्षा (Security) कशी ठेवली आहे?"
> **उत्तर:** 
> १. युझर पासवर्ड कधीही प्लेन टेक्स्टमध्ये साठवले जात नाहीत; ते **`bcrypt` क्रिप्टोग्राफिक हॅश** द्वारे सुरक्षित असतात.  
> २. दुहेरी भूमिका व्यवस्था (RBAC) - ॲडमिन (Admin) आणि कर्मचारी (Staff).  
> ३. संवेदनक्षम API की `.env` आणि `.streamlit/secrets.toml` मध्ये सुरक्षित ठेवल्या आहेत.

### प्रश्न ८: "प्रोजेक्ट स्थानिक पातळीवर (Locally) कसा रन करायचा?"
> **उत्तर:** 
> १. व्हर्च्युअल एन्व्हायरनमेंट ॲक्टिव्हेट करा: `.\venv\Scripts\Activate.ps1`  
> २. सर्व्हर सुरू करा: `uvicorn api.index:app --reload --port 8000`  
> ३. ब्राउझरमध्ये उघडा: `http://localhost:8000`

---

## 🚀 ४. डाव्या बाजूच्या फाईल्सचा झटपट परिचय (File Explorer Cheat Sheet)

- 📄 [`PROJECT_VIVA_EXAMINER_GUIDE.md`](file:///c:/Users/mahan/OneDrive/ドキュメント/Desktop/VernaLedger-AI/PROJECT_VIVA_EXAMINER_GUIDE.md) : **हा मुख्य गाईड (परीक्षकांसमोर उघडा ठेवायचा)**
- 📁 `api/` : **बॅकएंड AI आणि सर्व्हर** (`index.py` - ३७००+ लाईन्सचा मुख्य पायथन कोड)
- 📁 `public/` : **क्लाउड डिप्लॉयमेंट फाईल्स** (Vercel वर होस्ट होणाऱ्या मूळ फाईल्स)
- 📄 `index.html` : **फ्रंटएंड मांडणी (UI)**
- 📄 `app.js` : **फ्रंटएंड कार्यप्रणाली (JavaScript लॉजिक)**
- 📄 `style.css` : **रंगसंगती आणि सायबरपंक डिझाईन**
- 📄 `ledger.db` : **मुख्य डेटाबेस (SQLite)**
- 📄 `vercel.json` : **क्लाउड होस्टिंग कॉन्फिगरेशन**
- 📄 `requirements.txt` : **पायथन लायब्ररीज यादी**
- 📄 `run_local.bat` : **१-क्लिक स्थानिक रनर बॅच फाईल**
- 📁 `venv/` : **पायथन व्हर्च्युअल एन्व्हायरनमेंट (सर्व पॅकेजेस सुरक्षित)**
- 📁 `assets/` & `icons/` : **लोगो, चिन्हे आणि इमेजेस**


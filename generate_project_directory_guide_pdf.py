"""
VernaLedger.AI: Merchant Pro v7.5
System Architecture & Technical Project Guide PDF Generator (Updated & Enhanced Edition)
Features:
- New Clean Professional Name: VernaLedger_AI_System_Architecture_and_Technical_Guide.pdf
- Guide: Prof. Kaisar Atar sir | HOD: Dr. S. Y. Mulla mam | AGCE Satara (DBATU Lonere)
- Exact roles & technical contributions for all 4 developers:
  1. Sanket Kirdat (Team Leader & AI Architecture)
  2. Sakshi Bhagat (Frontend & UI/UX Developer)
  3. Vaishnavi Dhavale (Voice Billing & Multilingual AI)
  4. Rushikesh Mulik (Backend & Database Developer)
- Complete 23 Slides Presentation reference & companion Viva Script Guide
- 50 Kirana Items auto-stock deduction engine & API endpoints
- Playwright Chromium A4 multi-page PDF generation
"""

import os
import sys
import shutil
from playwright.sync_api import sync_playwright

OUTPUT_PDF_NEW = os.path.abspath("VernaLedger_AI_System_Architecture_and_Technical_Guide.pdf")
OUTPUT_PDF_OLD = os.path.abspath("VernaLedger_AI_Project_Architecture_and_File_Directory_Guide.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="utf-8">
<title>VernaLedger.AI: Merchant Pro v7.5 - संपूर्ण सिस्टीम आर्किटेक्चर व तांत्रिक गाईड</title>
<style>
  @page {
    size: A4;
    margin: 10mm 11mm 10mm 11mm;
    @bottom-right {
      content: counter(page);
    }
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  body {
    font-family: 'Segoe UI', 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
    color: #1e293b;
    background: #ffffff;
    font-size: 8.2pt;
    line-height: 1.40;
  }

  .page {
    page-break-after: always;
    position: relative;
    padding-bottom: 12px;
  }
  .page:last-child {
    page-break-after: avoid;
  }

  /* Header Bar */
  .header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2.5px solid #0284c7;
    padding-bottom: 7px;
    margin-bottom: 9px;
  }
  .brand-title {
    font-size: 15.5pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
    font-family: 'Segoe UI', sans-serif;
  }
  .brand-title span {
    color: #0284c7;
  }
  .brand-subtitle {
    font-size: 7.8pt;
    color: #475569;
    font-weight: 600;
    margin-top: 1px;
  }
  .badge-tag {
    background: linear-gradient(135deg, #0284c7, #0369a1);
    color: #ffffff;
    font-size: 7.2pt;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-family: 'Segoe UI', sans-serif;
  }

  /* Section Titles */
  .section-title {
    font-size: 9.6pt;
    font-weight: 800;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    margin-bottom: 5px;
    padding-bottom: 2px;
    border-bottom: 1.5px solid #e2e8f0;
  }
  .section-title .icon {
    font-size: 10.5pt;
  }

  /* Cards */
  .card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 6px 9px;
    margin-bottom: 6px;
  }
  .card-highlight {
    background: #f0f9ff;
    border-color: #bae6fd;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 6px;
    font-size: 7.8pt;
  }
  th {
    background: #0f172a;
    color: #ffffff;
    text-align: left;
    padding: 4px 6px;
    font-weight: 700;
    font-size: 7.8pt;
  }
  th.blue-th {
    background: #0284c7;
  }
  th.accent-th {
    background: #0f766e;
  }
  td {
    padding: 3.6px 6px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
    line-height: 1.35;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }
  tr:hover td {
    background: #f1f5f9;
  }

  /* Pills & Badges */
  .pill {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 7.1pt;
    font-family: 'Segoe UI', sans-serif;
  }
  .pill-blue { background: #e0f2fe; color: #0369a1; }
  .pill-green { background: #dcfce7; color: #15803d; }
  .pill-purple { background: #f3e8ff; color: #7e22ce; }
  .pill-amber { background: #fef3c7; color: #b45309; }
  .pill-slate { background: #f1f5f9; color: #334155; }
  .pill-red { background: #fee2e2; color: #b91c1c; }

  code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 7.5pt;
    background: #f1f5f9;
    padding: 1px 3px;
    border-radius: 3px;
    color: #0f172a;
    font-weight: 600;
  }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
  }

  /* Footer Note */
  .page-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    font-size: 7pt;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    padding-top: 3px;
    font-family: 'Segoe UI', sans-serif;
  }
</style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- PAGE 1: EXECUTIVE DOSSIER, ARCHITECTURE & CORE AI PILLARS             -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="header-bar">
      <div>
        <div class="brand-title">VernaLedger<span>.AI</span> <span style="font-size: 11pt; color: #0284c7; font-weight: 800;">Merchant Pro v7.5</span></div>
        <div class="brand-subtitle">स्थानिक किराणा व MSMEs साठी नेक्स्ट-जनरेशन AI बिलिंग, उधारी वही, ५० किराणा स्टॉक व व्हॉइस असिस्टंट प्रणाली</div>
      </div>
      <div>
        <span class="badge-tag">Technical Architecture Guide</span>
      </div>
    </div>

    <!-- Academic Dossier Banner -->
    <div class="card card-highlight">
      <table style="margin-bottom:0;">
        <tr>
          <td style="width:20%; font-weight:700; color:#0369a1; border:none; padding:2px 3px;">🏛️ महाविद्यालय:</td>
          <td style="width:80%; font-weight:600; border:none; padding:2px 3px;">अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (Arvind Gavali College of Engineering - AGCE Satara)</td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 3px;">🎓 विद्यापीठ:</td>
          <td style="font-weight:600; border:none; padding:2px 3px;">डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)</td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 3px;">📚 पदवी व विभाग:</td>
          <td style="font-weight:600; border:none; padding:2px 3px;">B.Tech (कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स - AI &amp; DS) | शैक्षणिक वर्ष: २०२६ – २०२७</td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 3px;">👨‍🏫 प्रकल्प मार्गदर्शक:</td>
          <td style="font-weight:700; color:#0f172a; border:none; padding:2px 3px;">प्रा. कैसर अत्तार सर (Prof. Kaisar Atar sir) <span class="pill pill-slate">Faculty Member &amp; Project Guide (Dept of AI &amp; DS)</span></td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 3px;">🏛️ विभागप्रमुख (HOD):</td>
          <td style="font-weight:700; color:#0f172a; border:none; padding:2px 3px;">डॉ. एस. वाय. मुल्ला मॅम (Dr. S. Y. Mulla mam) <span class="pill pill-slate">Head of Department (AI &amp; DS), AGCE Satara</span></td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:3px 3px; vertical-align:top;">👨‍💻 प्रकल्प डेव्हलपर्स (सर्व ४):</td>
          <td style="border:none; padding:3px 3px; line-height: 1.4;">
            <div style="margin-bottom: 3px;">
              <b>१. संकेत किर्दत</b> (Roll: 4060 | PRN: 24065451263508) &bull; <span class="pill pill-blue">Team Leader &amp; AI Architecture</span><br/>
              <span style="color:#475569; font-size:7.4pt;">↳ <b>प्रकल्पातील योगदान:</b> Google Gemini Multimodal OCR Vision Pipeline, ५० किराणा वस्तूंचे ऑटो-कपात अल्गोरिदम, Verna AI असिस्टंट (Gemini Stream &amp; Devanagari RAG), संपूर्ण सिस्टीम इंटिग्रेशन व प्रोजेक्ट नेतृत्व.</span>
            </div>
            <div style="margin-bottom: 3px;">
              <b>२. साक्षी भगत</b> (Roll: 4054 | PRN: 24065451263502) &bull; <span class="pill pill-green">Frontend &amp; UI/UX Experience</span><br/>
              <span style="color:#475569; font-size:7.4pt;">↳ <b>प्रकल्पातील काम:</b> HTML5/CSS3 आधारित ५ मुख्य ॲप व्ह्यूज, सायबरपंक निऑन ग्लास-मॉर्फिझम, १-क्लिक 'किराणा डे/नाईट मोड' थीम इंजिन, ५० वस्तूंचा लाइव्ह सर्च बार, व मोबाईल बॉटम नॅव्हिगेशन PWA.</span>
            </div>
            <div style="margin-bottom: 3px;">
              <b>३. वैष्णवी ढवळे</b> (Roll: 4056 | PRN: 24065451263504) &bull; <span class="pill pill-purple">Voice Billing &amp; Multilingual AI</span><br/>
              <span style="color:#475569; font-size:7.4pt;">↳ <b>प्रकल्पातील काम:</b> अस्खलित मराठी व्हॉइस बिलिंग इंजिन (Web Speech API mr-IN), पल्सिंग माइक बटन, पूर्ण वाक्य न अडखळता बोलणे (No premature cutoff), आणि मराठी-इंग्रजी भाषा ऑटो-डिटेक्शन.</span>
            </div>
            <div>
              <b>४. ऋषिकेश मुळीक</b> (Roll: 4004 | PRN: 23065451263005) &bull; <span class="pill pill-slate">Backend, Database &amp; Sync Engine</span><br/>
              <span style="color:#475569; font-size:7.4pt;">↳ <b>प्रकल्पातील काम:</b> SQLite ACID WAL हायब्रिड डेटाबेस, ग्राहक डिजिटल उधारी वही (Khata), १-क्लिक WhatsApp स्मरणपत्र लिंक, XlsxWriter द्वारे Excel (.xlsx) व CSV रिपोर्ट एक्सपोर्ट, ऑफलाइन सॉकेट रेझिलियन्स (0.3s timeout).</span>
            </div>
          </td>
        </tr>
      </table>
    </div>

    <!-- 3-Tier Architecture -->
    <div class="section-title"><span class="icon">🏗️</span> १. प्रकल्पाचे ३-टियर तांत्रिक आर्किटेक्चर (3-Tier System Architecture)</div>
    <table>
      <thead>
        <tr>
          <th style="width:17%;">टियर (Tier)</th>
          <th style="width:38%;">तंत्रज्ञान व टूल्स (Technology Stack)</th>
          <th style="width:45%;">मुख्य कार्यप्रणाली व जबाबदारी (Key Responsibilities)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span class="pill pill-blue">Tier 1: Client</span><br/><b>फ्रंटएंड SPA</b></td>
          <td>HTML5, Vanilla JavaScript (ES6+), CSS3 Glassmorphism, Web Speech API (mr-IN), PWA Service Worker</td>
          <td>५ ॲप व्ह्यूज (Scanner, Khata, Store/Stock, Ledger, Verna AI), कॅमेरा स्कॅनर, लाइव्ह माइक पल्सिंग, ५० स्टॉक सर्च बार, WhatsApp रिमाइंडर्स व ऑफलाइन कॅशिंग.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">Tier 2: Backend</span><br/><b>सर्व्हरलेस AI</b></td>
          <td>Python 3.13 + FastAPI, Google Gemini 2.5 Flash / Flash Lite, PIL Image Optimizer, Vernacular NLP Engine</td>
          <td>मल्टीमॉडल OCR पावती स्कॅनिंग, ASR स्पीच-टू-टेक्स्ट, Verna AI असिस्टंट (स्क्रिप्ट पर्सिस्टन्स व लाइव्ह SQL RAG), ५० किराणा स्टॉक ऑटो-कपात मॅचर.</td>
        </tr>
        <tr>
          <td><span class="pill pill-purple">Tier 3: Ledger</span><br/><b>हायब्रिड डेटाबेस</b></td>
          <td>SQLite 3 (ACID WAL Mode), Dexie IndexedDB Local-First, XlsxWriter Engine, Deletion Tombstones</td>
          <td>५० किराणा स्टॉक (shop_inventory), ग्राहक उधारी वही (customer_khata), पावत्या (receipts + stock_deducted फ्लॅग), खर्च नोंदी, आणि १-क्लिक Excel/CSV जनरेटर.</td>
        </tr>
      </tbody>
    </table>

    <!-- Core AI Pillars (2-column layout) -->
    <div class="section-title"><span class="icon">🧠</span> २. मुख्य AI तंत्रज्ञान पिलर्स (Core AI Foundations)</div>
    <div class="grid-2">
      <!-- Scanner 5 Pillars -->
      <div class="card" style="border-left: 3px solid #0284c7;">
        <div style="font-weight:700; color:#0369a1; margin-bottom:4px; font-size:8.2pt;">📸 स्मार्ट स्कॅनरचे मुख्य AI पिलर्स (Multimodal OCR)</div>
        <div style="font-size:7.6pt; line-height:1.38;">
          <b>१. Vision Transformers (ViT):</b> पावतीचे व्हिज्युअल पॅचेस बनवून तिरपे, घाईत लिहिलेले व अस्पष्ट मराठी हस्तलिखित अचूक वाचते.<br/>
          <b>२. Multimodal End-to-End:</b> इमेज पिक्सेल व देवनागरी भाषा थेट न्यूरल नेटवर्कद्वारे समजून अचूक वस्तू, वजन व दर काढते.<br/>
          <b>३. PIL Lanczos 960px Enhancement:</b> कॉन्ट्रास्ट (1.15x) व शार्पनेस (1.20x) वाढवून कमी प्रकाशातील फोटो सुस्पष्ट करते.<br/>
          <b>४. Devanagari Numeral Parser:</b> मराठी अंक (०-९) आपोआप आंतरराष्ट्रीय अंकांमध्ये बदलून गणिताचा हिशोब (वजन × दर) पडताळते.<br/>
          <b>५. Semantic Duplicate Shield:</b> इमेज हॅश व रक्कम तपासून एकाच पावतीची दुबार नोंद व दुबार स्टॉक कपात १००% रोखते.
        </div>
      </div>

      <!-- Chatbot 5 Pillars -->
      <div class="card" style="border-left: 3px solid #0f766e;">
        <div style="font-weight:700; color:#0f766e; margin-bottom:4px; font-size:8.2pt;">🤖 Verna AI असिस्टंट पिलर्स (Gemini Powered)</div>
        <div style="font-size:7.6pt; line-height:1.38;">
          <b>१. Official Gemini-Style Voice Mic:</b> इनपुट बारमध्ये स्लीक माइक बटन, थेट देवनागरी मराठी (mr-IN), हिंदी व इंग्रजी स्पीच-टू-टेक्स्ट.<br/>
          <b>२. Strict Script Persistence:</b> युझरने देवनागरी मराठी, रोमन मराठी किंवा इंग्रजीत विचारल्यास त्याच लिपीत व भाषेत सलग उत्तर.<br/>
          <b>३. Real-Time Word Streaming:</b> अधिकृत <code>sendMessageStream</code> द्वारे शब्दामागून शब्द गुगल ॲपप्रमाणे स्क्रीनवर उमटतात.<br/>
          <b>४. Zero-Hallucination SQL RAG:</b> थेट दुकानातील ५० वस्तूंचा साठा, विक्री, खर्च व उधारी पाहून १००% अचूक आकडेवारी सांगते.<br/>
          <b>५. Complete Sentence Speaking:</b> अकाली ऑटो-सेंड कटऑफ काढून टाकल्याने दुकानदार पूर्ण वाक्य न अडखळता बोलू शकतो.
        </div>
      </div>
    </div>

    <div class="page-footer">
      <span>VernaLedger.AI: Merchant Pro v7.5 • AGCE सातारा (DBATU Lonere) • AI &amp; DS Dept</span>
      <span>पान १ / ३</span>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 2: MASTER FILE DIRECTORY & APPLICATION WORKFLOW MAP              -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="header-bar">
      <div>
        <div class="brand-title">VernaLedger<span>.AI</span> — फाईल डिरेक्टरी व मोड्युल नकाशा</div>
        <div class="brand-subtitle">प्रकल्पातील प्रत्येक फाईलचे स्थान, आकार, उद्देश आणि ५ मुख्य ॲप व्ह्यूजचा आराखडा</div>
      </div>
      <div>
        <span class="badge-tag">Repository Structure</span>
      </div>
    </div>

    <!-- 5 App Views Card -->
    <div class="card card-highlight">
      <div style="font-weight:700; color:#0369a1; margin-bottom:3px; font-size:8.2pt;">📱 ॲप्लिकेशनचे ५ मुख्य व्ह्यूज (5-View Modular Architecture):</div>
      <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 5px; font-size:7.4pt;">
        <div style="background:#fff; padding:4px 6px; border-radius:4px; border:1px solid #bae6fd;">
          <b>१. 📷 AI Scanner</b><br/><span style="color:#64748b;">कॅमेरा स्कॅन, व्हॉइस बिलिंग व लाइव्ह डिजिटल पावती</span>
        </div>
        <div style="background:#fff; padding:4px 6px; border-radius:4px; border:1px solid #bae6fd;">
          <b>२. 👥 Khata Book</b><br/><span style="color:#64748b;">ग्राहक उधारी वही, WhatsApp स्मरणपत्र व UPI लिंक्स</span>
        </div>
        <div style="background:#fff; padding:4px 6px; border-radius:4px; border:1px solid #bae6fd;">
          <b>३. 🏬 Store &amp; Stock</b><br/><span style="color:#64748b;">५० किराणा माल साठा, ऑटो-कपात, सर्च बार व खर्च</span>
        </div>
        <div style="background:#fff; padding:4px 6px; border-radius:4px; border:1px solid #bae6fd;">
          <b>४. 📒 Ledger &amp; Excel</b><br/><span style="color:#64748b;">पावती इतिहास, थर्मल प्रिंट, .xlsx व CSV एक्सपोर्ट</span>
        </div>
        <div style="background:#fff; padding:4px 6px; border-radius:4px; border:1px solid #bae6fd;">
          <b>५. 🤖 Verna AI</b><br/><span style="color:#64748b;">मराठी AI असिस्टंट, लाइव्ह डेटा RAG व चॅट मेमरी</span>
        </div>
      </div>
    </div>

    <div class="section-title"><span class="icon">📁</span> ३. संपूर्ण प्रकल्प फाईल नकाशा (Master File Directory &amp; Component Map)</div>
    <table>
      <thead>
        <tr>
          <th class="blue-th" style="width:18%;">फाईलचे नाव</th>
          <th class="blue-th" style="width:23%;">स्थान (Repository Path)</th>
          <th class="blue-th" style="width:16%;">प्रकार व आकार</th>
          <th class="blue-th" style="width:43%;">त्यामध्ये काय महत्त्वाचे आहे व मुख्य कार्य (Core Role)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>index.py</b></td>
          <td><code>api/index.py</code></td>
          <td><span class="pill pill-green">FastAPI Backend</span><br/>246 KB</td>
          <td>प्रकल्पाचे <b>मुख्य AI इंजिन</b>. यात Gemini Vision OCR, Voice Billing NLP, Verna AI असिस्टंट (स्क्रिप्ट पर्सिस्टन्स), ५० किराणा स्टॉक ऑटो-कपात इंजिन (<code>deduct_inventory_stock</code>), SQLite WAL व्यवहार आणि Excel रिपोर्ट जनरेटर समाविष्ट आहे.</td>
        </tr>
        <tr>
          <td><b>app.py</b></td>
          <td><code>app.py</code></td>
          <td><span class="pill pill-blue">Server Runner</span><br/>2.8 KB</td>
          <td>स्थानिक संगणकावर पोर्ट ८००० वर Uvicorn सर्व्हर सुरू करतो. 0.3s सॉकेट टाइमआउटसह लॅपटॉप व मोबाईल IP ऑटो-डिटेक्ट करून ब्राऊझर आपोआप उघडतो.</td>
        </tr>
        <tr>
          <td><b>run_local.bat</b></td>
          <td><code>run_local.bat</code></td>
          <td><span class="pill pill-slate">Batch Script</span><br/>450 B</td>
          <td>विंडोजवर १-क्लिकमध्ये venv मधील Python द्वारे स्थानिक सर्व्हर सुरू करून डीफॉल्ट ब्राऊझरमध्ये <code>http://127.0.0.1:8000</code> उघडते.</td>
        </tr>
        <tr>
          <td><b>index.html</b></td>
          <td><code>public/index.html</code><br/>&amp; रूट <code>index.html</code></td>
          <td><span class="pill pill-amber">Frontend SPA</span><br/>90 KB</td>
          <td>५ व्ह्यूजचा संपूर्ण युझर इंटरफेस: स्मार्ट स्कॅनर, व्हॉइस बिलिंग, ग्राहक उधारी वही (Khata), ५० किराणा वस्तूंचा शोध बार, साठा तक्ता, आणि Verna AI असिस्टंट.</td>
        </tr>
        <tr>
          <td><b>app.js</b></td>
          <td><code>public/app.js</code><br/>&amp; रूट <code>app.js</code></td>
          <td><span class="pill pill-amber">Client Logic</span><br/>256 KB</td>
          <td>क्लायंट जावास्क्रिप्ट: Web Speech API देवनागरी व्हॉइस टायपिंग, कॅमेरा कॉम्प्रेशन, ऑटो-स्टॉक कपात लाइव्ह रीफ्रेश, WhatsApp ट्रिगर आणि स्टेट व्यवस्थापन.</td>
        </tr>
        <tr>
          <td><b>style.css</b></td>
          <td><code>public/style.css</code><br/>&amp; रूट <code>style.css</code></td>
          <td><span class="pill pill-purple">Stylesheets</span><br/>72 KB</td>
          <td>सायबरपंक ग्लासमोर्फिझम, निऑन-सायन ॲक्सेंट्स, १-क्लिक किराणा कम्फर्ट डे/नाईट मोड, मायक्रोफोन पल्सिंग ॲनिमेशन आणि मोबाईल बॉटम नॅव्हिगेशन मांडणी.</td>
        </tr>
        <tr>
          <td><b>ledger.db</b></td>
          <td><code>ledger.db</code></td>
          <td><span class="pill pill-green">SQLite 3 DB</span><br/>160 KB</td>
          <td>५० किराणा वस्तूंचा साठा (<code>shop_inventory</code>), ग्राहक उधारी वही (<code>customer_khata</code>), बिलांच्या नोंदी (<code>receipts</code> + <code>stock_deducted</code>), आणि व्यवसाय खर्च.</td>
        </tr>
        <tr>
          <td><b>sw.js &amp; manifest</b></td>
          <td><code>public/sw.js</code><br/><code>manifest.webmanifest</code></td>
          <td><span class="pill pill-blue">PWA Config</span><br/>2 KB</td>
          <td>प्रोग्रेसिव्ह वेब ॲप (PWA) सपोर्ट. मोबाईलवर ॲपप्रमाणे इन्स्टॉल होते आणि ऑफलाइन कॅशिंग प्रदान करते.</td>
        </tr>
        <tr>
          <td><b>Presentation.html</b></td>
          <td><code>VernaLedger_Presentation.html</code></td>
          <td><span class="pill pill-blue">3D Slideshow</span><br/>10.0 MB</td>
          <td>अंतिम वर्षाच्या प्रेझेंटेशन व व्हायव्हासाठी <b>२३ आधुनिक Reveal.js ३डी स्लाइड्स</b>. यात कॉलेज, गाईड, ४ डेव्हलपर्स आणि लाइव्ह स्क्रीनशॉट्स समाविष्ट आहेत.</td>
        </tr>
        <tr>
          <td><b>Script_Guide.pdf</b></td>
          <td><code>VernaLedger_AI_...Viva_Guide.pdf</code></td>
          <td><span class="pill pill-purple">Defense Guide</span><br/>800 KB</td>
          <td>२३ स्लाईड्सचे पाठ करायला अगदी सोपे इंग्रजी वाक्ये, सोप्या मराठीत अर्थ, ४ सदस्यांचे रोल वाटप आणि प्रत्येकी १ Viva प्रश्न-उत्तर देणारा अधिकृत गाईड.</td>
        </tr>
        <tr>
          <td><b>Project_Report.docx</b></td>
          <td><code>VernaLedger_AI_...Report.docx</code></td>
          <td><span class="pill pill-green">Final Report</span><br/>2.19 MB</td>
          <td>DBATU/AGCE च्या अधिकृत फॉरमॅटनुसार तयार केलेला सविस्तर <b>Final Year Project Report (Word Document)</b>, सर्व चॅप्टर्स, मॅथ्स व चाचण्यांसह.</td>
        </tr>
        <tr>
          <td><b>vercel.json</b></td>
          <td><code>vercel.json</code></td>
          <td><span class="pill pill-slate">Deployment</span><br/>1.2 KB</td>
          <td>Vercel सर्व्हरलेस फंक्शन राऊट्स (<code>/api/(.*) -&gt; api/index.py</code>), CORS हेडर, नो-कॅश नियम आणि टाइमआउट नियम.</td>
        </tr>
      </tbody>
    </table>

    <div class="page-footer">
      <span>VernaLedger.AI: Merchant Pro v7.5 • AGCE सातारा (DBATU Lonere) • AI &amp; DS Dept</span>
      <span>पान २ / ३</span>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 3: 50 KIRANA INVENTORY ENGINE, API & VIVA CHEAT SHEET           -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="header-bar">
      <div>
        <div class="brand-title">VernaLedger<span>.AI</span> — इन्व्हेंटरी इंजिन व API संदर्भावली</div>
        <div class="brand-subtitle">५० किराणा वस्तूंचा साठा कपात अल्गोरिदम, सर्व्हरलेस APIs आणि व्हायव्हा महत्त्वाचे मुद्दे</div>
      </div>
      <div>
        <span class="badge-tag">Inventory &amp; APIs</span>
      </div>
    </div>

    <!-- 50 Kirana Inventory Engine Highlight -->
    <div class="card card-highlight">
      <div style="font-weight:700; color:#0369a1; margin-bottom:3px; font-size:8.2pt;">📦 ५० किराणा वस्तूंचा साठा व स्वयंचलित कपात इंजिन (Auto Stock Deduction Engine):</div>
      <div style="font-size:7.5pt; line-height:1.4; color:#334155;">
        &bull; <b>५० अस्सल किराणा वस्तू:</b> गहू, बासमती/कोलम तांदूळ, ज्वारी, बाजरी, तूर/मूग/उडीद/चणा/मसूर डाळ, साखर, गूळ, रवा, पोहे, मैदा, बेसन, शेंगदाणा/सूर्यफूल/सोयाबीन/मोहरी तेल, तूप, मीठ, हळद, तिखट, मसाले, काजू, बदाम, चहा, कॉफी, बिस्किट्स, साबण, डिटर्जंट, टूथपेस्ट, विम बार.<br/>
        &bull; <b>स्वयंचलित कपात:</b> OCR स्कॅन, व्हॉइस बिल किंवा डिजिटल बिलातून वस्तू विकली जाताच <code>stock_qty = MAX(0, stock_qty - billed_qty)</code> द्वारे साठा तात्काळ कमी होतो.<br/>
        &bull; <b>युनिट व ग्रॅम कन्व्हर्जन:</b> <code>500 gm</code> दिल्यास आपोआप <code>0.5 kg</code> वजा होते. युनिट्स: <code>kg</code>, <code>लिटर</code>, <code>पॅकेट</code>, <code>नग</code>, <code>बाटली</code>.<br/>
        &bull; <b>कमी साठा अलर्ट (Low Stock Notice):</b> साठा अलर्ट मर्यादेखाली जाताच स्क्रीनवर <b>🚨 कमी साठा</b> चा इशारा येतो व Verna AI असिस्टंटलाही याची लाइव्ह माहिती असते.<br/>
        &bull; <b>१-क्लिक रिसेट:</b> <code>/api/inventory/reset-defaults</code> द्वारे दुकानातील सर्व ५० वस्तू त्यांच्या मूळ साठ्यासह पूर्ववत होतात.
      </div>
    </div>

    <!-- Core API Endpoints Table -->
    <div class="section-title"><span class="icon">🔌</span> ४. मुख्य सर्व्हरलेस API एंडपॉइंट्स (Core Serverless API Reference)</div>
    <table>
      <thead>
        <tr>
          <th class="accent-th" style="width:13%;">पद्धती</th>
          <th class="accent-th" style="width:25%;">एंडपॉइंट (API Route)</th>
          <th class="accent-th" style="width:24%;">इनपुट डेटा (Payload)</th>
          <th class="accent-th" style="width:38%;">कार्य व आउटपुट प्रतिसाद (Function &amp; Output)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/rag-chat</code></td>
          <td><code>{ message, chat_history }</code></td>
          <td><b>Verna AI असिस्टंट:</b> व्हॉइस/टेक्स्ट प्रश्न समजून देवनागरी लिपीत, लाइव्ह ५० वस्तूंचा साठा, विक्री व उधारी पाहून अचूक उत्तर.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/ocr</code></td>
          <td><code>multipart/form-data (file)</code></td>
          <td><b>स्मार्ट स्कॅनर:</b> पावतीच्या फोटोतून वस्तू, वजन, दर काढून डिजिटल बिल बनवते व ५० किराणा साठ्यातून वस्तू आपोआप वजा करते.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/voice-billing</code></td>
          <td><code>{ transcript, audio_data }</code></td>
          <td><b>व्हॉइस बिलिंग:</b> तोंडी आवाजाचे थेट बिलात रूपांतर, उधारी खात्यावर नोंद आणि साठ्यातून मालाची आपोआप कपात.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/receipts</code></td>
          <td><code>{ vendor_name, items, total }</code></td>
          <td><b>डिजिटल बिल सेव्ह:</b> पावती लेजरमध्ये सेव्ह करते, डुप्लिकेट तपासते व साठ्यातून विकलेल्या मालाची आपोआप वजावट करते.</td>
        </tr>
        <tr>
          <td><span class="pill pill-blue">GET</span></td>
          <td><code>/api/inventory</code></td>
          <td><i>None</i></td>
          <td><b>साठा यादी:</b> दुकानातील सर्व ५० किराणा वस्तू, शिल्लक प्रमाण, विक्री दर व कमी साठा (Low stock) स्थिती परत करते.</td>
        </tr>
        <tr>
          <td><span class="pill pill-purple">POST</span></td>
          <td><code>/api/inventory/reset-defaults</code></td>
          <td><i>None</i></td>
          <td><b>साठा रीसेट:</b> एका क्लिकवर सर्व ५० किराणा वस्तूंचा साठा त्यांच्या मूळ प्रमाणासह पूर्ववत (Reset Defaults) करते.</td>
        </tr>
        <tr>
          <td><span class="pill pill-blue">GET / POST</span></td>
          <td><code>/api/customers</code> / <code>/khata</code></td>
          <td><code>{ customer_name, amount... }</code></td>
          <td><b>ग्राहक उधारी वही:</b> ग्राहकांची उधारी यादी, नवीन उधारी नोंदवणे व १-क्लिक WhatsApp स्मरणपत्र लिंक.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/sync</code></td>
          <td><code>{ receipts, khata, expenses }</code></td>
          <td><b>लोकल-फर्स्ट ऑटो-सिंक:</b> ऑफलाइन किंवा रिफ्रेश झाल्यावर ब्राउझरमधील डेटा सर्व्हरलेस SQLite मध्ये सुरक्षित सिंक करतो.</td>
        </tr>
        <tr>
          <td><span class="pill pill-purple">GET</span></td>
          <td><code>/api/receipts/export-excel</code></td>
          <td><i>None (Direct Download)</i></td>
          <td><b>एक्सेल रिपोर्ट:</b> XlsxWriter द्वारे संपूर्ण व्यवसायाची सुंदर फॉरमॅट केलेली <code>.xlsx</code> फाईल थेट डाउनलोड होते.</td>
        </tr>
      </tbody>
    </table>

    <!-- Local Execution & Deployment Guide -->
    <div class="section-title"><span class="icon">🚀</span> ५. प्रकल्प कसा चालवायचा? (Execution &amp; Deployment Guide)</div>
    <table>
      <thead>
        <tr>
          <th style="width:20%;">वातावरण (Environment)</th>
          <th style="width:35%;">कमांड / पद्धत (Command / Action)</th>
          <th style="width:45%;">तपशील व महत्त्वाची माहिती (Details &amp; Instructions)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>स्थानिक संगणक</b><br/><span class="pill pill-blue">Localhost 8000</span></td>
          <td><code>run_local.bat</code> वर डबल-क्लिक करा<br/>किंवा <code>python app.py</code> रन करा</td>
          <td>Uvicorn सर्व्हर पोर्ट ८००० वर सुरू होतो (<code>http://127.0.0.1:8000</code>). मोबाईलवर पाहण्यासाठी एकाच वायफायवर लोकल आयपी वापरा.</td>
        </tr>
        <tr>
          <td><b>Vercel क्लाउड</b><br/><span class="pill pill-green">Production Live</span></td>
          <td><code>git add .</code><br/><code>git commit -m 'update'</code><br/><code>git push origin main</code></td>
          <td>GitHub <code>main</code> ब्रँचवर कोड पुश करताच Vercel आपोआप संपूर्ण ॲप व सर्व्हरलेस बॅकएंड क्लाउडवर लाईव्ह डिप्लॉय करते.</td>
        </tr>
        <tr>
          <td><b>ब्राऊझर कॅश क्लिअर</b><br/><span class="pill pill-amber">Hard Reload</span></td>
          <td>ब्राऊझरमध्ये <b>Ctrl + F5</b> दाबा<br/>किंवा DevTools मध्ये 'Empty Cache' करा</td>
          <td>कॅश व्हर्जनिंग पॅरामीटर <code>?v=75.0</code> वापरल्याने नवीन बदल ब्राऊझरमध्ये तात्काळ सक्रिय होतात.</td>
        </tr>
      </tbody>
    </table>

    <!-- Quick Reference Card -->
    <div class="card card-highlight" style="margin-top:6px;">
      <div style="font-weight:700; color:#0369a1; margin-bottom:2px; font-size:8.2pt;">💡 एक्सटर्नल परीक्षक (Examiner) व्हायव्हासाठी अत्यंत महत्त्वाचे मुद्दे:</div>
      <div style="font-size:7.5pt; line-height:1.4; color:#334155;">
        &bull; <b>मराठी-प्रथम (Vernacular-First):</b> स्थानिक सातारी/ग्रामीण उच्चार व हस्तलिखित पावत्या समजणारी पहिली AI बिलिंग सिस्टीम.<br/>
        &bull; <b>५० किराणा साठा ऑटो-कपात:</b> बिलात वस्तू नोंदवताच साठा आपोआप वजा होतो आणि कमी साठा झाल्यास लाल रंगात अलर्ट मिळतो.<br/>
        &bull; <b>Verna AI असिस्टंट:</b> अधिकृत जेमिनी स्टाईल व्हॉइस टायपिंग, लिपी पर्सिस्टन्स आणि झिरो-हॅल्युसिनेशन SQL लाइव्ह डेटा RAG.
      </div>
    </div>

    <div class="page-footer">
      <span>VernaLedger.AI: Merchant Pro v7.5 • AGCE सातारा (DBATU Lonere) • AI &amp; DS Dept</span>
      <span>पान ३ / ३</span>
    </div>
  </div>

</body>
</html>
"""

def generate_pdf():
    temp_html = os.path.abspath("temp_technical_guide_render.html")

    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print("=" * 70)
    print("🚀 Generating Updated System Architecture & Technical Project Guide PDF...")
    print("=" * 70)
    
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    with sync_playwright() as p:
        try:
            if os.path.exists(edge_path):
                browser = p.chromium.launch(executable_path=edge_path, headless=True)
            else:
                browser = p.chromium.launch(headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto(f"file:///{temp_html.replace(os.sep, '/')}", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(800)
        
        # 1. Generate primary new PDF
        page.pdf(
            path=OUTPUT_PDF_NEW,
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        
        # 2. Also generate/update the legacy filename so no link or examiner document breaks
        page.pdf(
            path=OUTPUT_PDF_OLD,
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    # Sync both PDFs to public/ folder
    public_dir = os.path.abspath("public")
    if os.path.exists(public_dir):
        shutil.copy2(OUTPUT_PDF_NEW, os.path.join(public_dir, os.path.basename(OUTPUT_PDF_NEW)))
        shutil.copy2(OUTPUT_PDF_OLD, os.path.join(public_dir, os.path.basename(OUTPUT_PDF_OLD)))
        print(f"✅ Synced both PDFs to public/ folder.")

    print(f"✅ SUCCESS: New Guide PDF: {OUTPUT_PDF_NEW}")
    print(f"📊 File Size: {os.path.getsize(OUTPUT_PDF_NEW):,} bytes")
    print(f"✅ Also preserved legacy filename: {OUTPUT_PDF_OLD}")
    print("=" * 70)

if __name__ == "__main__":
    generate_pdf()

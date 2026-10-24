import os, sys
from playwright.sync_api import sync_playwright

HTML_CONTENT = """<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="utf-8">
<title>VernaLedger.AI - संपूर्ण प्रकल्प निर्देशिका व आर्किटेक्चर गाईड</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

  @page {
    size: A4;
    margin: 14mm 14mm 14mm 14mm;
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
    font-family: 'Noto Sans Devanagari', 'Nirmala UI', 'Segoe UI', -apple-system, sans-serif;
    color: #1e293b;
    background: #ffffff;
    font-size: 8.5pt;
    line-height: 1.45;
  }

  .page {
    page-break-after: always;
    position: relative;
    padding-bottom: 10px;
  }
  .page:last-child {
    page-break-after: avoid;
  }

  /* Header Bar */
  .header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 8px;
    margin-bottom: 12px;
  }
  .brand-title {
    font-size: 17pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
  }
  .brand-title span {
    color: #0284c7;
  }
  .brand-subtitle {
    font-size: 8pt;
    color: #64748b;
    font-weight: 500;
    margin-top: 2px;
  }
  .badge-tag {
    background: linear-gradient(135deg, #0284c7, #0369a1);
    color: #ffffff;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Section Titles */
  .section-title {
    font-size: 10.5pt;
    font-weight: 700;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    margin-bottom: 6px;
    padding-bottom: 3px;
    border-bottom: 1px solid #e2e8f0;
  }
  .section-title .icon {
    font-size: 11pt;
  }

  /* Cards */
  .card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 8px;
  }
  .card-highlight {
    background: #f0f9ff;
    border-color: #bae6fd;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
    font-size: 8pt;
  }
  th {
    background: #0f172a;
    color: #ffffff;
    text-align: left;
    padding: 5px 7px;
    font-weight: 600;
    font-size: 8pt;
  }
  th.blue-th {
    background: #0284c7;
  }
  th.accent-th {
    background: #0f766e;
  }
  td {
    padding: 4.5px 7px;
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

  /* Pills & Code Badges */
  .pill {
    display: inline-block;
    padding: 1.5px 6px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 7.5pt;
  }
  .pill-blue { background: #e0f2fe; color: #0369a1; }
  .pill-green { background: #dcfce7; color: #15803d; }
  .pill-purple { background: #f3e8ff; color: #7e22ce; }
  .pill-amber { background: #fef3c7; color: #b45309; }
  .pill-slate { background: #f1f5f9; color: #334155; }

  code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 7.8pt;
    background: #f1f5f9;
    padding: 1px 4px;
    border-radius: 3px;
    color: #0f172a;
    font-weight: 600;
  }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
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
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
    padding-top: 4px;
  }
</style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- PAGE 1: EXECUTIVE DOSSIER & 3-TIER ARCHITECTURE                       -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="header-bar">
      <div>
        <div class="brand-title">VernaLedger<span>.AI</span></div>
        <div class="brand-subtitle">स्थानिक किराणा व MSMEs साठी नेक्स्ट-जनरेशन AI बिलिंग, लेजर व चॅटबॉट प्रणाली</div>
      </div>
      <div>
        <span class="badge-tag">Merchant Pro v7.5 • Official Guide</span>
      </div>
    </div>

    <!-- Academic Dossier Banner -->
    <div class="card card-highlight">
      <table style="margin-bottom:0;">
        <tr>
          <td style="width:20%; font-weight:700; color:#0369a1; border:none; padding:2px 4px;">🏛️ महाविद्यालय:</td>
          <td style="width:80%; font-weight:600; border:none; padding:2px 4px;">अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (Arvind Gavali College of Engineering - AGCE)</td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 4px;">🎓 विद्यापीठ:</td>
          <td style="font-weight:600; border:none; padding:2px 4px;">डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)</td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 4px;">📚 पदवी व विभाग:</td>
          <td style="font-weight:600; border:none; padding:2px 4px;">B.Tech (कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स - AI & DS) | शैक्षणिक वर्ष: २०२६ – २०२७</td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 4px;">👨‍🏫 प्रकल्प मार्गदर्शक:</td>
          <td style="font-weight:700; color:#0f172a; border:none; padding:2px 4px;">प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir) <span class="pill pill-slate">Dept of AI & DS, AGCE Satara</span></td>
        </tr>
        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 4px;">👨‍💻 प्रकल्प डेव्हलपर्स:</td>
          <td style="border:none; padding:2px 4px;">
            <b>१. संकेत किर्दत</b> (Lead Full-Stack AI) &bull; 
            <b>२. साक्षी भगत</b> (UI/UX Design) &bull; 
            <b>३. वैष्णवी ढवळे</b> (Data Pipeline) &bull; 
            <b>४. ऋषिकेश मुळीक</b> (Database & Ledger)
          </td>
        </tr>
      </table>
    </div>

    <!-- 3-Tier Architecture -->
    <div class="section-title"><span class="icon">🏗️</span> १. प्रकल्पाचे ३-टियर तांत्रिक आर्किटेक्चर (3-Tier System Architecture)</div>
    <table>
      <thead>
        <tr>
          <th style="width:18%;">टियर (Tier)</th>
          <th style="width:40%;">तंत्रज्ञान व टूल्स (Technology Stack)</th>
          <th style="width:42%;">मुख्य कार्यप्रणाली व जबाबदारी (Key Responsibilities)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span class="pill pill-blue">Tier 1: Client</span><br/><b>फ्रंटएंड ॲप</b></td>
          <td>HTML5, Vanilla JavaScript (ES6+), CSS3 Glassmorphism, Web Speech API, MediaRecorder, Service Worker (PWA)</td>
          <td>वापरकर्ता डॅशबोर्ड, रिअल-टाइम व्हॉइस रेकॉर्डिंग, कॅमेरा स्कॅनर, १-क्लिक WhatsApp स्मरणपत्र, थर्मल प्रिंटर बिल व ऑफलाइन कॅशिंग.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">Tier 2: Backend</span><br/><b>सर्व्हरलेस AI</b></td>
          <td>Python 3.13 + FastAPI, Google Gemini 3.1 Flash Lite (REST Transport), Google Cloud Vision API, Regex NLP Parser</td>
          <td>पावतीचे OCR स्कॅनिंग, ASR स्पीच-टू-टेक्स्ट, Verna AI RAG चॅटबॉट, डायनॅमिक लांबी नियंत्रण, आणि व्यवसाय नफा-तोटा विश्लेषण.</td>
        </tr>
        <tr>
          <td><span class="pill pill-purple">Tier 3: Ledger</span><br/><b>हायब्रिड लेजर</b></td>
          <td>SQLite 3 (ACID WAL), VernaStorage (लोकल-फर्स्ट झिरो-डेटा लॉस इंजिन), /api/sync ऑटो-रिहायड्रेशन, Native XlsxWriter Engine</td>
          <td>ग्राहक उधारी वही, दैनंदिन विक्री नोंदी, साठा (Inventory), सर्व्हरलेस कोल्ड-स्टार्ट डेटा संरक्षण आणि १-क्लिक Excel एक्सपोर्ट.</td>
        </tr>
      </tbody>
    </table>

    <!-- Core AI Pillars (2-column layout) -->
    <div class="section-title"><span class="icon">🧠</span> २. मुख्य AI तंत्रज्ञान पिलर्स (Core AI Foundations)</div>
    <div class="grid-2">
      <!-- Scanner 5 Pillars -->
      <div class="card" style="border-left: 3px solid #0284c7;">
        <div style="font-weight:700; color:#0369a1; margin-bottom:5px; font-size:8.5pt;">📸 स्मार्ट स्कॅनरचे ५ मुख्य AI पिलर्स (Multimodal OCR)</div>
        <div style="font-size:7.8pt; line-height:1.4;">
          <b>१. Vision Transformers (ViT):</b> पावतीचे लहान व्हिज्युअल पॅचेस बनवून तिरपे, घाईत लिहिलेले व अस्पष्ट मराठी हस्तलिखित अचूक वाचते.<br/>
          <b>२. Native Multimodal AI:</b> फोटोचे पिक्सेल आणि भाषा एकाच न्यूरल नेटवर्कद्वारे थेट (End-to-End) समजून घेते.<br/>
          <b>३. Google TPU Cloud:</b> क्लाउडवरील Tensor Processing Units वर मॉडेल चालल्यामुळे अवघ्या ०.९ ते १.२ सेकंदात निकाल मिळतो.<br/>
          <b>४. Context-Aware Attention:</b> अस्पष्ट अंक (उदा. १ की ७) आजूबाजूच्या शब्दांवरून आणि गणिताचा हिशोब (दर × वजन) तपासून ओळखते.<br/>
          <b>५. Document AI Fallback:</b> अडथळा आल्यास गुगलच्या Document Text Detection API द्वारे अखंड फॉलबॅक.
        </div>
      </div>

      <!-- Chatbot 4 Pillars -->
      <div class="card" style="border-left: 3px solid #0f766e;">
        <div style="font-weight:700; color:#0f766e; margin-bottom:5px; font-size:8.5pt;">🤖 Verna AI चॅटबॉटचे ४ मुख्य पिलर्स (Universal Engine)</div>
        <div style="font-size:7.8pt; line-height:1.4;">
          <b>१. Native Multimodal Architecture:</b> आवाज आणि मजकूर एकाच न्यूरल नेटवर्कद्वारे अखंडपणे समजून घेते.<br/>
          <b>२. High-Accuracy Vernacular ASR:</b> दुकानातील गोंगाट गाळून सातारी, कोल्हापुरी, पुणेरी व ग्रामीण मराठी उच्चार अचूक ओळखते.<br/>
          <b>३. Transformer LLM Reasoning:</b> दुकानाच्या थेट SQLite डेटाबेसमधील हिशोब तपासून १००% अचूक उत्तरे देते (No Hallucination).<br/>
          <b>४. Real-Time Low Latency Engine:</b> सब-मिलिसेकंद (१०-१५ ms) इन-मेमरी मेमरी ॲक्सेस आणि Google Gemini द्वारे जागतिक ज्ञान.
        </div>
      </div>
    </div>

    <div class="page-footer">
      <span>VernaLedger.AI • AGCE सातारा (DBATU University) • AI & DS Department</span>
      <span>पान १ / ३</span>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 2: MASTER FILE DIRECTORY MAP (कोणती फाईल कुठे आहे आणि काय करते)   -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="header-bar">
      <div>
        <div class="brand-title">VernaLedger<span>.AI</span> — फाईल डिरेक्टरी नकाशा</div>
        <div class="brand-subtitle">प्रकल्पातील प्रत्येक महत्त्वाच्या फाईलचे स्थान, उद्देश आणि त्यामधील महत्त्वाचे घटक</div>
      </div>
      <div>
        <span class="badge-tag">Repository Structure</span>
      </div>
    </div>

    <div class="section-title"><span class="icon">📁</span> ३. संपूर्ण प्रकल्प फाईल नकाशा (Master File Directory & Component Map)</div>
    <table>
      <thead>
        <tr>
          <th class="blue-th" style="width:18%;">फाईलचे नाव</th>
          <th class="blue-th" style="width:22%;">स्थान (Repository Path)</th>
          <th class="blue-th" style="width:16%;">प्रकार व आकार</th>
          <th class="blue-th" style="width:44%;">त्यामध्ये काय महत्त्वाचे आहे व मुख्य कार्य (Core Role)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>index.py</b></td>
          <td><code>api/index.py</code></td>
          <td><span class="pill pill-green">FastAPI Backend</span><br/>110 KB</td>
          <td>प्रकल्पाचे <b>मुख्य AI इंजिन</b>. यात Gemini 3.1 Flash Lite RAG चॅटबॉट, व्हॉइस ट्रान्सक्रिप्शन, डायनॅमिक लांबी नियंत्रण, OCR पावती स्कॅनिंग, SQLite WAL व्यवहार आणि Excel रिपोर्ट जनरेटर समाविष्ट आहे.</td>
        </tr>
        <tr>
          <td><b>app.py</b></td>
          <td><code>app.py</code></td>
          <td><span class="pill pill-blue">Server Runner</span><br/>916 B</td>
          <td>स्थानिक संगणकावर पोर्ट ८००० वर Uvicorn सर्व्हर सुरू करतो. यात <code>reload=True</code> असल्याने कोडमध्ये बदल करताच ॲप तात्काळ आपोआप रीलोड होते.</td>
        </tr>
        <tr>
          <td><b>run_local.bat</b></td>
          <td><code>run_local.bat</code></td>
          <td><span class="pill pill-slate">Batch Script</span><br/>328 B</td>
          <td>विंडोजवर १-क्लिकमध्ये स्थानिक सर्व्हर सुरू करून डीफॉल्ट ब्राऊझरमध्ये <code>http://127.0.0.1:8000</code> उघडते.</td>
        </tr>
        <tr>
          <td><b>index.html</b></td>
          <td><code>public/index.html</code><br/>& रूट <code>index.html</code></td>
          <td><span class="pill pill-amber">Frontend SPA</span><br/>63 KB</td>
          <td>डॅशबोर्ड, स्मार्ट स्कॅनर कॅमेरा व्ह्यू, व्हॉइस बिलिंग माइक स्पेक्ट्रम, ग्राहक उधारी वही (Khata), साठा व्यवस्थापन आणि Verna AI स्टुडिओ चॅटबॉटचा संपूर्ण युझर इंटरफेस.</td>
        </tr>
        <tr>
          <td><b>app.js</b></td>
          <td><code>public/app.js</code><br/>& रूट <code>app.js</code></td>
          <td><span class="pill pill-amber">Client Logic</span><br/>117 KB</td>
          <td>फ्रंटएंड जावास्क्रिप्ट, MediaRecorder द्वारे ऑडिओ रेकॉर्डिंग, बेस६४ एन्कोडिंग, API कॉल्स, थर्मल प्रिंट जनरेशन, कॅल्क्युलेटर, व्हॉट्सॲप स्मरणपत्र ट्रिगर आणि स्टेट मॅनेजमेंट.</td>
        </tr>
        <tr>
          <td><b>style.css</b></td>
          <td><code>public/style.css</code><br/>& रूट <code>style.css</code></td>
          <td><span class="pill pill-purple">Stylesheets</span><br/>64 KB</td>
          <td>मॉडर्न डार्क सायबरपंक / किराणा कम्फर्ट थीम, ग्लासमोर्फिझम कार्ड्स, हाय-कॉन्ट्रास्ट फॉन्ट्स, निऑन अ‍ॅक्सेंट बार, आणि मोबाईल रिस्पॉन्सिव्ह ग्रिड मांडणी.</td>
        </tr>
        <tr>
          <td><b>sw.js & manifest</b></td>
          <td><code>public/sw.js</code><br/><code>manifest.webmanifest</code></td>
          <td><span class="pill pill-blue">PWA Config</span><br/>1.8 KB</td>
          <td>प्रोग्रेसिव्ह वेब ॲप (PWA) सपोर्ट. ॲप मोबाईलवर नेटिव्ह ॲपप्रमाणे इन्स्टॉल करता येते आणि नेटवर्क खंडित झाल्यास ऑफलाइन कॅशिंग प्रदान करते.</td>
        </tr>
        <tr>
          <td><b>ledger.db</b></td>
          <td><code>ledger.db</code></td>
          <td><span class="pill pill-green">SQLite 3 DB</span><br/>135 KB</td>
          <td>ग्राहकांची माहिती (customers), उधारी वही (customer_khata), किराणा साठा (inventory), बिलांचे व्यवहार (transactions) आणि व्यवसाय खर्च (expenses) सुरक्षित साठवते.</td>
        </tr>
        <tr>
          <td><b>backups/</b></td>
          <td><code>backups/*.db</code></td>
          <td><span class="pill pill-slate">Database Backups</span></td>
          <td>डेटाबेसमधील माहितीचे टाइमस्टॅम्पसह स्वयंचलित सुरक्षित बॅकअप्स (Auto-Snapshots), जेणेकरून डेटा गहाळ होण्याची भीती नसते.</td>
        </tr>
        <tr>
          <td><b>secrets.toml</b></td>
          <td><code>.streamlit/secrets.toml</code></td>
          <td><span class="pill pill-amber">Local Secrets</span><br/>149 B</td>
          <td>स्थानिक वातावरणातील गुगल जेमिनी API चावी (<code>GEMINI_API_KEY</code>) सुरक्षित ठेवण्याचे ठिकाण. गिटवर ही फाईल सुरक्षितपणे दुर्लक्षित केली जाते.</td>
        </tr>
        <tr>
          <td><b>vercel.json</b></td>
          <td><code>vercel.json</code></td>
          <td><span class="pill pill-purple">Deployment</span><br/>369 B</td>
          <td>Vercel सर्व्हरलेस फंक्शन राऊट्स (<code>/api/(.*) -> api/index.py</code>), CORS हेडर, मेमरी अलोकेशन आणि ६० सेकंद टाइमआउट नियम.</td>
        </tr>
        <tr>
          <td><b>Presentation.html</b></td>
          <td><code>VernaLedger_Presentation.html</code></td>
          <td><span class="pill pill-blue">3D Slideshow</span><br/>140 KB</td>
          <td>अंतिम वर्षाच्या सेमिनार व व्हायव्हासाठी तयार केलेले आधुनिक ३डी स्लाइडशो. यात कॉलेजचे नाव, विद्यापीठ, गाईड, ४ डेव्हलपर्स आणि लाइव्ह स्क्रीनशॉट्स समाविष्ट आहेत.</td>
        </tr>
        <tr>
          <td><b>Project_Report.docx</b></td>
          <td><code>VernaLedger_AI_...Report.docx</code></td>
          <td><span class="pill pill-green">Final Report</span><br/>2.19 MB</td>
          <td>DBATU/AGCE च्या अधिकृत फॉरमॅटनुसार तयार केलेला सविस्तर <b>Final Year Project Report (Word Document)</b>, ज्यात सर्व चॅप्टर्स, मॅथ्स आणि आर्किटेक्चर आहे.</td>
        </tr>
        <tr>
          <td><b>Project_Synopsis.docx</b></td>
          <td><code>VernaLedger_AI_...Synopsis.docx</code></td>
          <td><span class="pill pill-slate">Official Synopsis</span><br/>216 KB</td>
          <td>प्रकल्पाचा अधिकृत सिनॉप्सिस (Synopsis), ज्यामध्ये समस्या विधान, प्रस्तावित पद्धती, उद्दिष्टे आणि संभाव्य निकाल दिले आहेत.</td>
        </tr>
      </tbody>
    </table>

    <div class="page-footer">
      <span>VernaLedger.AI • AGCE सातारा (DBATU University) • AI & DS Department</span>
      <span>पान २ / ३</span>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 3: API ENDPOINTS & EXECUTION GUIDE                               -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="header-bar">
      <div>
        <div class="brand-title">VernaLedger<span>.AI</span> — API व डिप्लॉयमेंट गाईड</div>
        <div class="brand-subtitle">सर्व्हरलेस API संदर्भावली, स्थानिक वापर आणि क्लाउड डिप्लॉयमेंट नियम</div>
      </div>
      <div>
        <span class="badge-tag">API & Deployment</span>
      </div>
    </div>

    <!-- Core API Endpoints Table -->
    <div class="section-title"><span class="icon">🔌</span> ४. मुख्य सर्व्हरलेस API एंडपॉइंट्स (Core Serverless API Reference)</div>
    <table>
      <thead>
        <tr>
          <th class="accent-th" style="width:12%;">पद्धती</th>
          <th class="accent-th" style="width:24%;">एंडपॉइंट (API Route)</th>
          <th class="accent-th" style="width:26%;">इनपुट डेटा (Payload)</th>
          <th class="accent-th" style="width:38%;">कार्य व आउटपुट प्रतिसाद (Function & Output)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/rag-chat</code></td>
          <td><code>{ message, audio_data, lang }</code></td>
          <td><b>Verna AI चॅटबॉट:</b> व्हॉइस/टेक्स्ट प्रश्न समजून Google Gemini 3.1 द्वारे दुकान हिशोब किंवा जागतिक ज्ञानाचे अचूक मराठीत उत्तर देते.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/scan-receipt</code></td>
          <td><code>{ image_data, language }</code></td>
          <td><b>स्मार्ट स्कॅनर:</b> ५ AI पिलर्सद्वारे हस्तलिखित मराठी पावतीतील वस्तू, वजन, दर व एकूण रकमांचा अचूक डिजिटल डेटा काढते.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/voice-billing</code></td>
          <td><code>{ audio_data, mime_type }</code></td>
          <td><b>व्हॉइस बिलिंग:</b> दुकानातील आवाजाचे थेट बिलात रूपांतर करते व ग्राहकाच्या खात्यावर व्यवहार नोंदवते.</td>
        </tr>
        <tr>
          <td><span class="pill pill-blue">GET / POST</span></td>
          <td><code>/api/customers</code></td>
          <td><code>{ customer_name, phone }</code></td>
          <td><b>ग्राहक उधारी वही:</b> ग्राहकांची यादी, एकूण उधारी, नवीन ग्राहक जोडणे व १-क्लिक WhatsApp स्मरणपत्र लिंक.</td>
        </tr>
        <tr>
          <td><span class="pill pill-blue">GET / POST</span></td>
          <td><code>/api/inventory</code></td>
          <td><code>{ item_name, stock_qty... }</code></td>
          <td><b>साठा व्यवस्थापन:</b> किराणा वस्तूंचा साठा, विक्री दर आणि कमी साठा (Low stock) अलर्ट व्यवस्थापन.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/sync</code></td>
          <td><code>{ receipts, customers, expenses }</code></td>
          <td><b>लोकल-फर्स्ट ऑटो-सिंक:</b> ब्राउझरमधील डेटा सर्व्हरलेस SQLite <code>/tmp/ledger.db</code> मध्ये आपोआप रि-हायड्रेट व सिंक करतो.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/sync</code></td>
          <td><code>{ receipts, customers, expenses }</code></td>
          <td><b>लोकल-फर्स्ट ऑटो-सिंक:</b> ब्राउझरमधील डेटा सर्व्हरलेस SQLite <code>/tmp/ledger.db</code> मध्ये आपोआप रि-हायड्रेट व सिंक करतो.</td>
        </tr>
        <tr>
          <td><span class="pill pill-green">POST</span></td>
          <td><code>/api/sync</code></td>
          <td><code>{ receipts, customers, expenses }</code></td>
          <td><b>लोकल-फर्स्ट ऑटो-सिंक:</b> ब्राउझरमधील डेटा सर्व्हरलेस SQLite <code>/tmp/ledger.db</code> मध्ये आपोआप रि-हायड्रेट व सिंक करतो.</td>
        </tr>
        <tr>
          <td><span class="pill pill-purple">GET</span></td>
          <td><code>/api/export-excel</code></td>
          <td><i>None (Direct Download)</i></td>
          <td><b>एक्सेल रिपोर्ट:</b> <code>xlsxwriter</code> द्वारे संपूर्ण व्यवसायाची सुंदर फॉरमॅट केलेली <code>.xlsx</code> फाईल डाउनलोड होते.</td>
        </tr>
      </tbody>
    </table>

    <!-- Local Execution & Deployment Guide -->
    <div class="section-title"><span class="icon">🚀</span> ५. प्रकल्प कसा चालवायचा व डिप्लॉय करायचा? (Execution & Deployment Guide)</div>
    <table>
      <thead>
        <tr>
          <th style="width:20%;">वातावरण (Environment)</th>
          <th style="width:35%;">कमांड / पद्धत (Command / Action)</th>
          <th style="width:45%;">तपशील व महत्त्वाची माहिती (Details & Instructions)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>स्थानिक संगणक</b><br/><span class="pill pill-blue">Localhost 8000</span></td>
          <td><code>run_local.bat</code> वर डबल-क्लिक करा<br/>किंवा <code>python app.py</code> रन करा</td>
          <td>Uvicorn सर्व्हर पोर्ट ८००० वर सुरू होतो (<code>http://127.0.0.1:8000</code>). <code>reload=True</code> सक्षम असल्याने कोड बदलताच आपोआप रीलोड होतो.</td>
        </tr>
        <tr>
          <td><b>Vercel क्लाउड</b><br/><span class="pill pill-green">Production Live</span></td>
          <td><code>git add .</code><br/><code>git commit -m 'update'</code><br/><code>git push origin main</code></td>
          <td>GitHub <code>main</code> ब्रँचवर कोड पुश करताच Vercel आपोआप संपूर्ण ॲप व सर्व्हरलेस फंक्शन्स क्लाउडवर लाईव्ह डिप्लॉय करते.</td>
        </tr>
        <tr>
          <td><b>ब्राऊझर कॅश क्लिअर</b><br/><span class="pill pill-amber">Hard Reload</span></td>
          <td>ब्राऊझरमध्ये <b>Ctrl + F5</b> दाबा<br/>किंवा DevTools मध्ये 'Empty Cache' करा</td>
          <td>वेब ब्राऊझर जुन्या जावास्क्रिप्ट फाईल्स कॅशमध्ये ठेवू नयेत म्हणून व्हर्जनिंग पॅरामीटर (उदा. <code>?v=31.0</code>) वापरले आहे.</td>
        </tr>
      </tbody>
    </table>

    <!-- Quick Reference Card -->
    <div class="card card-highlight" style="margin-top:10px;">
      <div style="font-weight:700; color:#0369a1; margin-bottom:4px; font-size:8.5pt;">💡 व्हायव्हा आणि प्रेझेंटेशनसाठी महत्त्वाचे मुद्दे (Key Highlights for External Viva):</div>
      <div style="font-size:7.8pt; line-height:1.45; color:#334155;">
        &bull; <b>मराठी-प्रथम (Vernacular-First):</b> ग्रामीण व सातारी भाषेतील उच्चार व हस्तलिखित पावत्या समजणारी पहिली एकात्मिक AI बिलिंग सिस्टीम.<br/>
        &bull; <b>झिरो हॅल्युसिनेशन (Zero Hallucination):</b> दुकानाचे आकडे थेट SQLite डेटाबेसमधून पडताळून दिले जातात, ज्यामुळे चुकीचा हिशोब होणे अशक्य आहे.<br/>
        &bull; <b>सब-सेकंड परफॉर्मन्स:</b> Google Gemini 3.1 Flash Lite आणि Google TPU Cloud मुळे ०.९ ते १.२ सेकंदात निकाल मिळतो.
      </div>
    </div>

    <div class="page-footer">
      <span>VernaLedger.AI • AGCE सातारा (DBATU University) • AI & DS Department</span>
      <span>पान ३ / ३</span>
    </div>
  </div>

</body>
</html>
"""

def generate_pdf():
    output_pdf = os.path.abspath("VernaLedger_AI_Project_Architecture_and_File_Directory_Guide.pdf")
    temp_html = os.path.abspath("temp_guide_render.html")

    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print("Rendering PDF using Playwright + Blink / DirectWrite Engine...")
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=edge_path, headless=True)
        page = browser.new_page()
        page.goto(f"file:///{temp_html.replace(os.sep, '/')}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        page.pdf(
            path=output_pdf,
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    print(f"SUCCESS: Perfect guide PDF generated at: {output_pdf}")
    print(f"Size: {os.path.getsize(output_pdf):,} bytes")

if __name__ == "__main__":
    generate_pdf()

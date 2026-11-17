"""
VernaLedger.AI: Merchant Pro v7.5
Presentation Script & Role-Wise Defense Guide (12-Slide Streamlined Edition: Exactly 3 Slides Per Member)
Features:
- Exactly 3 role-specific slides per member (4 members × 3 slides = 12 slides) + 1 team conclusion slide
- Prominently displays: Guide: Prof. Kaisar Atar | HOD: Dr. S. Y. Mulla | AGCE Satara (DBATU Lonere)
- Exact technical contribution (प्रकल्पातील नक्की योगदान) detailed right next to each member's name
- Prominent Speaker Badges on EVERY slide: Sanket (1-3), Sakshi (4-6), Vaishnavi (7-9), Rushikesh (10-12), Team (13)
- Crisp spoken English (3-4 punchy sentences, 45-60s speech), concise Marathi meaning, 1 direct Viva Q&A, and handover cue
"""

import os
import sys
from playwright.sync_api import sync_playwright

OUTPUT_PDF = os.path.abspath("VernaLedger_AI_Presentation_Team_Script_and_Viva_Guide.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="utf-8">
<title>VernaLedger.AI - 3-Slide Per Member Defense Guide</title>
<style>
  @page {
    size: A4;
    margin: 8mm 8mm 8mm 8mm;
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
    color: #0f172a;
    background: #ffffff;
    font-size: 8.8pt;
    line-height: 1.36;
  }

  /* Header Box */
  .hero-box {
    background: linear-gradient(135deg, #050b14 0%, #0d2859 60%, #0a1128 100%);
    color: #ffffff;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    border-left: 5px solid #00f2fe;
  }

  .hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3px;
  }

  .badge-inst {
    background: rgba(0, 242, 254, 0.18);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.4);
    font-size: 7pt;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    text-transform: uppercase;
  }

  .badge-guide {
    background: rgba(0, 255, 135, 0.18);
    color: #00ff87;
    border: 1px solid rgba(0, 255, 135, 0.4);
    font-size: 7.5pt;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 12px;
  }

  .hero-title {
    font-size: 15pt;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 2px;
  }
  .hero-title span { color: #00f2fe; }

  .hero-desc {
    font-size: 8.2pt;
    color: #cbd5e1;
    margin-bottom: 6px;
  }

  .guide-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    background: rgba(255, 255, 255, 0.08);
    padding: 5px 10px;
    border-radius: 5px;
    font-size: 7.6pt;
  }
  .guide-strip strong { color: #38bdf8; }

  /* Contributions Table */
  .sec-heading {
    font-size: 10pt;
    font-weight: 800;
    color: #0f172a;
    border-left: 4px solid #0284c7;
    padding-left: 6px;
    margin: 8px 0 5px 0;
    text-transform: uppercase;
    display: flex;
    justify-content: space-between;
  }

  .table-contrib {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 7.8pt;
  }
  .table-contrib th {
    background: #0f172a;
    color: #ffffff;
    padding: 5px 7px;
    text-align: left;
    border: 1px solid #1e293b;
    font-weight: 700;
  }
  .table-contrib td {
    padding: 5px 7px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }
  .table-contrib tr:nth-child(even) td { background: #f8fafc; }

  .tag-member {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 700;
    font-size: 6.8pt;
    color: #ffffff;
  }
  .tag-sanket { background: #0284c7; }
  .tag-sakshi { background: #d97706; }
  .tag-vaishnavi { background: #7c3aed; }
  .tag-rushikesh { background: #059669; }

  /* Slide Presentation Cards */
  .slide-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    margin-bottom: 7px;
    page-break-inside: avoid;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  }

  .slide-topbar {
    padding: 4px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
  }
  .topbar-sanket { background: #f0f9ff; border-left: 5px solid #0284c7; }
  .topbar-sakshi { background: #fffbeb; border-left: 5px solid #d97706; }
  .topbar-vaishnavi { background: #faf5ff; border-left: 5px solid #7c3aed; }
  .topbar-rushikesh { background: #f0fdf4; border-left: 5px solid #059669; }
  .topbar-team { background: #ecfdf5; border-left: 5px solid #10b981; }

  .slide-id-title {
    font-size: 8.5pt;
    font-weight: 800;
    color: #0f172a;
  }
  .slide-pill {
    background: #0f172a;
    color: #ffffff;
    padding: 1px 5px;
    border-radius: 10px;
    font-size: 6.8pt;
    font-weight: 700;
    margin-right: 4px;
  }

  .speaker-badge {
    font-size: 7.2pt;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 10px;
  }
  .spk-sanket { background: #0284c7; color: #fff; }
  .spk-sakshi { background: #d97706; color: #fff; }
  .spk-vaishnavi { background: #7c3aed; color: #fff; }
  .spk-rushikesh { background: #059669; color: #fff; }
  .spk-team { background: #10b981; color: #fff; }

  .card-body {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 7px;
    padding: 6px 8px;
  }

  .box-en {
    background: #ffffff;
    border: 1px solid #bae6fd;
    border-left: 3px solid #0284c7;
    border-radius: 4px;
    padding: 5px 7px;
  }
  .box-mr {
    background: #fcfbf9;
    border: 1px solid #a7f3d0;
    border-left: 3px solid #10b981;
    border-radius: 4px;
    padding: 5px 7px;
  }

  .box-label {
    font-size: 6.6pt;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 2px;
  }
  .lbl-en { color: #0369a1; }
  .lbl-mr { color: #047857; }

  .text-en {
    font-size: 7.8pt;
    line-height: 1.33;
    color: #1e293b;
  }
  .text-en strong { color: #0f172a; }

  .text-mr {
    font-size: 7.8pt;
    line-height: 1.33;
    color: #334155;
  }
  .text-mr strong { color: #065f46; }

  .bottom-row {
    grid-column: span 2;
    display: grid;
    grid-template-columns: 1.3fr 0.7fr;
    gap: 5px;
    margin-top: 2px;
  }

  .qa-mini {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 4px;
    padding: 4px 6px;
    font-size: 7.1pt;
    color: #9a3412;
    line-height: 1.25;
  }
  .qa-mini strong { color: #c2410c; }

  .handover-mini {
    background: #f1f5f9;
    border-radius: 4px;
    padding: 4px 6px;
    font-size: 7pt;
    color: #475569;
    border-left: 3px solid #64748b;
    line-height: 1.25;
    display: flex;
    align-items: center;
  }
  .handover-mini strong { color: #0f172a; }

  .page-break { page-break-after: always; }
</style>
</head>
<body>

  <!-- ==================== HEADER ==================== -->
  <div class="hero-box">
    <div class="hero-top">
      <span class="badge-inst">Arvind Gavali College of Engineering, Satara • DBATU Lonere</span>
      <span class="badge-guide">Project Guide: Prof. Kaisar Atar | HOD: Dr. S. Y. Mulla</span>
    </div>
    <div class="hero-title">VernaLedger.AI <span>Merchant Pro v7.5</span></div>
    <div class="hero-desc">Role-Wise Presentation Defense Guide • Exactly 3 Slides Per Member (4 Members × 3 Slides = 12 Slides + Conclusion)</div>
    
    <div class="guide-strip">
      <div><strong>प्रकल्प मार्गदर्शक (Guide):</strong> Prof. Kaisar Atar</div>
      <div><strong>विभागप्रमुख (HOD):</strong> Dr. S. Y. Mulla</div>
      <div><strong>Department:</strong> Artificial Intelligence & Data Science (2026-2027)</div>
      <div><strong>Deck Format:</strong> 13 High-Impact Slides in VernaLedger_Presentation.html</div>
    </div>
  </div>

  <!-- ==================== MEMBER CONTRIBUTIONS ==================== -->
  <div class="sec-heading">
    <span>1. टीम सदस्यांचे वाटप आणि प्रकल्पातील नक्की तांत्रिक योगदान (Role & Exact Technical Contributions)</span>
    <span style="font-size: 7.2pt; font-weight: normal; color: #64748b;">प्रत्येकी बरोबर ३ स्लाईड्स (Exactly 3 Slides Each)</span>
  </div>

  <table class="table-contrib">
    <thead>
      <tr>
        <th style="width: 22%;">विद्यार्थ्याचे नाव व भूमिका</th>
        <th style="width: 14%;">रोल / PRN</th>
        <th style="width: 48%;">प्रकल्पातील नक्की तांत्रिक योगदान (Exact Technical Contribution)</th>
        <th style="width: 16%;">वाटून दिलेल्या ३ स्लाईड्स</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Sanket Kirdat</strong><br><span class="tag-member tag-sanket">Team Leader & AI</span></td>
        <td>Roll: 4060<br><span style="font-size: 7pt; color: #64748b;">24065451263508</span></td>
        <td>
          • <strong>AI Vision OCR इंजिन:</strong> गुगल Gemini 3.1 Flash द्वारे कागदी हस्तलिखित पावत्यांचे <1.5s मध्ये डिजिटायझेशन (`/api/ocr`).<br>
          • <strong>इमेज प्री-प्रोसेसिंग:</strong> 960px Lanczos कॉन्ट्रास्ट फिल्टर आणि SHA-256 हॅश द्वारे डुप्लिकेट पावती प्रतिबंध.<br>
          • <strong>प्रकल्प नेतृत्व:</strong> सिस्टीम एकत्रीकरण, आर्किटेक्चर फ्लो आणि अंतिम ओपन डिफेन्स (Q&A).
        </td>
        <td><strong>Slides: 01, 02, 03</strong><br><span style="color: #0284c7; font-weight: 700;">(३ स्लाईड्स)</span></td>
      </tr>
      <tr>
        <td><strong>Sakshi Bhagat</strong><br><span class="tag-member tag-sakshi">Frontend & UI/UX</span></td>
        <td>Roll: 4054<br><span style="font-size: 7pt; color: #64748b;">24065451263502</span></td>
        <td>
          • <strong>UI/UX आर्किटेक्चर:</strong> व्हॅनिला JavaScript आधारित जलद सिंगल पेज ॲप्लिकेशन (SPA) इंटरफेस.<br>
          • <strong>उधारी खातेवही (Khata):</strong> 'उधारी दिली' व 'जमा मिळाले' ऑटो-कॅल्क्युलेशन आणि 1-क्लिक व्हॉट्सॲप UPI पेमेंट लिंक.<br>
          • <strong>किराणा मोड व PWA:</strong> थेट उन्हात स्पष्ट दिसणारा किराणा मोड आणि मोबाईलसाठी 5-टॅब बॉटम टच बार.
        </td>
        <td><strong>Slides: 04, 05, 06</strong><br><span style="color: #d97706; font-weight: 700;">(३ स्लाईड्स)</span></td>
      </tr>
      <tr>
        <td><strong>Vaishnavi Dhavale</strong><br><span class="tag-member tag-vaishnavi">Voice Billing & AI</span></td>
        <td>Roll: 4056<br><span style="font-size: 7pt; color: #64748b;">24065451263504</span></td>
        <td>
          • <strong>मराठी व्हॉइस बिलिंग:</strong> Web Speech API (`mr-IN`) द्वारे सलग अखंड आवाजातून बिल तयार करणे (`/api/voice-billing`).<br>
          • <strong>प्रादेशिक भाषा NLP पार्सर:</strong> 'पाव किलो', 'अर्धा लिटर' अशा स्थानिक मराठी बोलीभाषेचे थेट अंकांमध्ये रूपांतर.<br>
          • <strong>Verna AI जेमिनी असिस्टंट:</strong> माईक पल्स ॲनिमेशन, वर्ड-बाय-वर्ड स्ट्रीमिंग आणि देवनागरी स्क्रिप्ट पर्सिस्टन्स.
        </td>
        <td><strong>Slides: 07, 08, 09</strong><br><span style="color: #7c3aed; font-weight: 700;">(३ स्लाईड्स)</span></td>
      </tr>
      <tr>
        <td><strong>Rushikesh Mulik</strong><br><span class="tag-member tag-rushikesh">Backend & Database</span></td>
        <td>Roll: 4004<br><span style="font-size: 7pt; color: #64748b;">23065451263005</span></td>
        <td>
          • <strong>FastAPI सर्व्हरलेस बॅकएंड:</strong> हाय-स्पीड ASGI गेटवे आणि multi-key failover rotation पूल (`api/index.py`).<br>
          • <strong>SQLite ACID डेटाबेस:</strong> Write-Ahead Logging (WAL) मोडमध्ये <2ms लेटन्सीसह 5 टेबल्सचे व्यवस्थापन.<br>
          • <strong>50 किराणा माल साठा इंजिन:</strong> 50 वस्तूंचा साठा, रिअल-टाइम सर्च आणि बिलांनंतर स्वयंचलित स्टॉक वजावट.<br>
          • <strong>एक्सेल एक्सपोर्ट इंजिन:</strong> XlsxWriter द्वारे देवनागरी मराठी फॉन्टसह थेट `.xlsx` स्प्रेडशीट जनरेशन.
        </td>
        <td><strong>Slides: 10, 11, 12</strong><br><span style="color: #059669; font-weight: 700;">(३ स्लाईड्स)</span></td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== MEMBER 1: SANKET KIRDAT (Slides 1 to 3) ==================== -->
  <div class="sec-heading">
    <span>2. सदस्य १: SANKET KIRDAT (स्लाईड्स ०१ ते ०३ • एकूण ३ स्लाईड्स)</span>
    <span style="font-size: 7.2pt; font-weight: normal; color: #0284c7;">Team Leader & AI Architecture</span>
  </div>

  <!-- SLIDE 01 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 01</span> Project Title, Objectives & Executive Vision</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT • Slide 1/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Respected Project Guide <strong>Prof. Kaisar Atar sir</strong>, HOD <strong>Dr. S. Y. Mulla sir</strong>, and external examiners, a very good morning. I am <strong>Sanket Kirdat</strong>, leading our team consisting of Sakshi Bhagat, Vaishnavi Dhavale, and Rushikesh Mulik from AGCE Satara. We present <strong>'VernaLedger.AI: Merchant Pro v7.5'</strong> — an offline-first vernacular POS suite tailored for India's 63 million kirana merchants to digitize handwritten bills and manage finances with zero English dependency."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          मार्गदर्शक <strong>अतार सर</strong>, विभागप्रमुख <strong>मुल्ला सर</strong> आणि परीक्षकांना नमस्कार करून स्वतःची व टीमची ओळख करून द्या. प्रकल्पाचे नाव सांगा: हा स्थानिक किराणा दुकानदारांसाठी बनवलेला मराठी AI बिलिंग प्लॅटफॉर्म आहे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is the main USP? <strong>Ans:</strong> Zero English barrier: merchants can scan paper bills with camera and speak in Marathi to generate instant bills.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us examine our 4-stage system pipeline on Slide 2."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 02 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 02</span> Proposed Multimodal System Pipeline</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT • Slide 2/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Our system runs in four closed-loop stages: <strong>1. Ingestion</strong> via camera receipt capture, Marathi voice prompt, or manual entry. <strong>2. AI Intelligence</strong> using Gemini Flash Vision and regex NLP to normalize tokens into structured JSON with math verification. <strong>3. ACID Commit</strong> to local SQLite within 2ms, auto-deducting inventory stock count. <strong>4. Output</strong> via thermal receipts, WhatsApp UPI bills, Excel (.xlsx), and Gemini chat."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          4 टप्पे सांगा: इनपुट (कॅमेरा/आवाज) -> AI द्वारे अक्षरे व आकडे ओळखणे -> SQLite डेटाबेसमध्ये सेव्ह व 50 मालातून साठा वजावट -> आउटपुट (पावती/व्हॉट्सॲप/एक्सेल/चॅटबॉट).
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How is pricing math verified? <strong>Ans:</strong> System automatically validates quantity × unit rate = total before committing to the database.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us now witness live Result 1: Smart Scanner on Slide 3."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 03 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 03</span> Result 1: Smart Multimodal Scanner & POS</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT • Slide 3/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 1 shows our live Multimodal Scanner. Photographing a physical Marathi bill segments items, weights, and prices into an editable POS grid in under 1.5 seconds with over 96% accuracy. Crucially, the moment the bill is saved, all billed commodities are automatically deducted from the store's 50 Kirana inventory items (`stock_qty = MAX(0, stock_qty - billed_qty)`)."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          स्क्रीनशॉट दाखवून सांगा: पावतीचा फोटो काढताच 1.5 सेकंदात डिजिटल बिल तयार झाले. 'सेव्ह' दाबताच 50 किराणा साठ्यातून साखर किंवा तेलाचे प्रमाण आपोआप कमी होते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you handle faint thermal receipts? <strong>Ans:</strong> Client canvas applies 960px Lanczos contrast sharpening and CLAHE histogram equalization before cloud OCR.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sakshi:</strong> "I now hand over to Sakshi Bhagat to present the market problems and UI."</div>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== MEMBER 2: SAKSHI BHAGAT (Slides 4 to 6) ==================== -->
  <div class="sec-heading">
    <span>3. सदस्य २: SAKSHI BHAGAT (स्लाईड्स ०४ ते ०६ • एकूण ३ स्लाईड्स)</span>
    <span style="font-size: 7.2pt; font-weight: normal; color: #d97706;">Frontend, UI/UX & Responsive PWA</span>
  </div>

  <!-- SLIDE 04 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 04</span> Problem Statement & Kirana Motivation</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT • Slide 1/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Thank you Sanket. Over 85% of small retailers still rely on manual paper notebooks ('बही-खाते') prone to damage, page loss, and math errors. Unrecorded customer credit ties up working capital, resulting in bad debts. Existing apps are complex and English-heavy. Our motivation is to provide zero digital literacy friction, enabling shopkeepers to operate via photo and voice while recovering credit 60% faster."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          85% दुकानदार वही वापरतात, ज्यामुळे हिशोबाच्या चुका होतात आणि उधारी अडकते. दुकानदाराला टायपिंग किंवा संगणक न येताही फक्त फोटो काढून किंवा बोलून 60% वेगाने उधारी वसूल करता यावी हा हेतू आहे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why WhatsApp over SMS? <strong>Ans:</strong> WhatsApp has 98% open rate in India and allows clickable UPI payment links (PhonePe/GPay) directly in Marathi.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us see Result 3: Customer Khata on Slide 5."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 05 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 05</span> Result 3: Customer Khata & 1-Click WhatsApp UPI</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT • Slide 2/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 3 is our Khatabook-beating Customer Khata Ledger. Merchants record 'उधारी दिली' and 'जमा मिळाले' with live running balances. To eliminate awkward debt follow-ups, one click on the green WhatsApp icon dispatches a polite Marathi reminder with an embedded dynamic UPI link, allowing customers to settle balances in 10 seconds."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          उधारी आणि जमा रकमेचा हिशोब. व्हॉट्सॲप आयकॉनवर क्लिक करताच ग्राहकाला नम्र मराठी मेसेज आणि थेट Google Pay/PhonePe ची UPI लिंक जाते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Does this need a paid WhatsApp API? <strong>Ans:</strong> No, uses native URI scheme `wa.me/{phone}?text=...` launching the installed app directly at zero cost.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Next, let us look at Kirana Light Mode and PWA on Slide 6."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 06 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 06</span> Result 7 & 8: Kirana Light Mode & Mobile PWA</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT • Slide 3/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Kirana stores operate under harsh roadside sunlight where dark mode is unreadable. Our High-Contrast Kirana Light Mode ensures 100% legibility under direct sunlight. Furthermore, VernaLedger is a Mobile-First PWA: on smartphones, the desktop sidebar converts into an intuitive 5-tab bottom navigation bar (`Scanner`, `Khata`, `Store`, `Ledger`, `Verna AI`), installable on Android homescreens like a native app."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          कडक उन्हात डार्क मोड दिसत नाही, म्हणून पांढऱ्या पार्श्वभूमीचा 'किराणा लाईट मोड' बनवला आहे. तसेच मोबाईलवर खाली 5 सोपे टॅब मिळतात आणि हे ॲप थेट मोबाईल स्क्रीनवर इन्स्टॉल करता येते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How is theme persisted? <strong>Ans:</strong> Saved in `localStorage.getItem('verna_theme')` for instant zero-flicker restoration.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Vaishnavi will now present gap analysis and voice billing."</div>
      </div>
    </div>
  </div>

  <!-- ==================== MEMBER 3: VAISHNAVI DHAVALE (Slides 7 to 9) ==================== -->
  <div class="sec-heading">
    <span>4. सदस्य ३: VAISHNAVI DHAVALE (स्लाईड्स ०७ ते ०९ • एकूण ३ स्लाईड्स)</span>
    <span style="font-size: 7.2pt; font-weight: normal; color: #7c3aed;">Voice Billing & Conversational AI</span>
  </div>

  <!-- SLIDE 07 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 07</span> Gap Analysis & Competitive Benchmarks</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE • Slide 1/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Thank you Sakshi. On Slide 7, we compare VernaLedger against Vyapar, Khatabook, and OKCredit. While commercial apps rely on English and manual typing, VernaLedger uniquely provides Multimodal Marathi Bill OCR, continuous Devanagari Voice Billing, an official Gemini store assistant, and 50 pre-seeded Kirana commodities with auto stock deduction at zero recurring fee."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          इतर ॲप्समध्ये कागदी बिल स्कॅनर नाही, मराठी व्हॉइस बिलिंग नाही आणि AI असिस्टंट नाही. VernaLedger मध्ये 50 किराणा माल आधीच लोड केलेला असून बिलासोबत साठा आपोआप वजा होतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Is VernaLedger subscription-based? <strong>Ans:</strong> No, it is open, self-hosted, and zero-subscription, keeping merchant data 100% private.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us see Result 2: Voice Billing on Slide 8."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 08 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 08</span> Result 2: Vernacular Voice Billing Engine</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE • Slide 2/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 2 is our Vernacular Voice Billing Engine. During rush hours, typing causes massive delays. With VernaLedger, the shopkeeper speaks naturally: 'सागरला २ किलो साखर ८४ रुपये आणि १ तेल १८५ रुपये'. The Web Speech API captures speech continuously without premature cutoff. Our NLP parser parses customer names, weights, and prices, slashes checkout delays by 85%."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          दुकानदार माईक दाबून बोलेल: 'सागरला २ किलो साखर ८४ रुपये...'. वाक्य पूर्ण होईपर्यंत माइक चालू राहतो आणि थेट बिल बनते, ज्यामुळे दुकानातील गर्दीत 85% वेळ वाचतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you handle 'पाव किलो'? <strong>Ans:</strong> Custom regex maps vernacular fractions ('पाव' = 0.25kg, 'अर्धा' = 0.5kg) to standard numeric floats.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Next, let us see Result 5: Verna AI Assistant on Slide 9."</div>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SLIDE 09 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 09</span> Result 5: Verna AI Multilingual Voice Assistant</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE • Slide 3/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 5 is our official Gemini-style Verna AI Assistant. It features a pulsing mic button (`#chatVoiceBtn`), word-by-word streaming (`sendMessageStream`), strict script persistence (replies strictly in the user's spoken language and script), and zero-hallucination store SQL context RAG to answer queries on daily revenue, credit, and 50-item inventory stock levels."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          गुगल जेमिनीसारखा AI चॅटबॉट: माईक पल्स ॲनिमेशन, शब्द न् शब्द थेट स्क्रीनवर येणे, मराठीत विचारल्यास मराठीतच उत्तर, आणि दुकानातील खरा साठा व विक्री तपासून उत्तर देणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How is zero-hallucination ensured? <strong>Ans:</strong> Exact SQL metrics are injected into system instruction; the LLM is restricted to database ground truth.</div>
        <div class="handover-mini"><strong>➡️ Handover to Rushikesh:</strong> "Rushikesh will now present backend architecture, inventory, and Excel."</div>
      </div>
    </div>
  </div>

  <!-- ==================== MEMBER 4: RUSHIKESH MULIK (Slides 10 to 12) ==================== -->
  <div class="sec-heading">
    <span>5. सदस्य ४: RUSHIKESH MULIK (स्लाईड्स १० ते १२ • एकूण ३ स्लाईड्स)</span>
    <span style="font-size: 7.2pt; font-weight: normal; color: #059669;">Backend, Database & Storage Engine</span>
  </div>

  <!-- SLIDE 10 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 10</span> 3-Tier System Architecture & Tech Stack</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK • Slide 1/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Thank you Vaishnavi. Our engineering stack is built for zero latency: <strong>FastAPI & Uvicorn</strong> universal ASGI backend, vanilla JS reactive client, Web Speech API (`mr-IN`), and Gemini 3.1 Flash. We follow a modular 3-tier architecture: Presentation (Client UI), Intelligence (FastAPI routing & failover API key pool), and Persistence (SQLite in WAL mode for sub-2ms ACID commits across 5 tables)."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          रचना सांगा: बॅकएंडला FastAPI, फ्रंटएंडला व्हॅनिला JS, AI साठी जेमिनी, आणि 2ms मध्ये सेव्ह होणारा सुरक्षित SQLite WAL डेटाबेस.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why SQLite over MongoDB? <strong>Ans:</strong> Relational ACID integrity is essential for running debt balance calculations; NoSQL lacks atomic joins.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us examine Result 4: 50 Kirana Inventory Items on Slide 11."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 11 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 11</span> Result 4: Store Operations & 50 Kirana Inventory Items</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK • Slide 2/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 4 showcases our 50 Pre-Seeded Kirana Commodities (grains, pulses, oils, sugar, tea, spices) across metric units (`kg`, `ltr`, `packet`). Key technical capabilities include: real-time search filtering, automatic stock deduction on all sales (`stock_qty = MAX(0, stock_qty - billed_qty)`), low-stock '🚨 कमी साठा' alert badges, and a 1-click default reset button."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          50 मूळ किराणा वस्तू आधीच सेव्ह आहेत. सर्च बारने वस्तू शोधता येते, बिलासोबत साठा आपोआप कमी होतो आणि माल संपत आला की लाल रंगाचा 'कमी साठा' इशारा मिळतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Can merchants add new items? <strong>Ans:</strong> Yes, via the Add Item form with custom units (`kg`, `ltr`, `packet`) and alert thresholds.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Next, let us see Result 6: Digital Ledger and Excel Export on Slide 12."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 12 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 12</span> Result 6: Digital Ledger & Native Excel Export</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK • Slide 3/3</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 6 is our Digital Ledger and Excel Export. All transactions are logged with dynamic search and thermal POS reprint. A prominent green button exports professional OpenXML `.xlsx` spreadsheets with auto-fitted columns and full Devanagari UTF-8 font fidelity for CAs and banks via XlsxWriter, maintaining complete ACID referential integrity."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          सर्व बिलांचा कायमस्वरूपी रेकॉर्ड. हिरवे एक्सेल बटण दाबताच मराठी नावांसह सुटसुटीत `.xlsx` फाईल डाऊनलोड होते, जी CA किंवा बँकेला दाखवता येते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why not just export CSV? <strong>Ans:</strong> CSV files corrupt Devanagari UTF-8 fonts in Microsoft Excel; XlsxWriter embeds native XML encoding and auto column widths.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sanket:</strong> "Our Team Leader Sanket will now deliver the conclusion on Slide 13."</div>
      </div>
    </div>
  </div>

  <!-- ==================== TEAM OPEN DEFENSE: SLIDE 13 ==================== -->
  <div class="sec-heading">
    <span>6. अंतिम स्लाईड: निष्कर्ष आणि ओपन डिफेन्स (Slide 13 • Team Open Defense)</span>
    <span style="font-size: 7.2pt; font-weight: normal; color: #10b981;">Led by Sanket • All 4 Members Answer Questions</span>
  </div>

  <!-- SLIDE 13 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-team">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 13</span> Conclusion, Summary & Open Viva Defense</div>
      <span class="speaker-badge spk-team">👥 सर्व ४ सदस्य (Team Open Defense)</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "To conclude: VernaLedger.AI bridges the digital divide for India's 63M+ kirana merchants by uniting Gemini 3.1 Vision OCR, continuous Marathi voice billing, a 50-item inventory auto-deduction engine, official Gemini voice assistant, and SQLite ACID ledger with native Excel export. We express our deepest gratitude to our guide <strong>Prof. Kaisar Atar sir</strong>, our HOD <strong>Dr. S. Y. Mulla sir</strong>, and all faculty of AGCE Satara. Our entire team stands ready for your questions!"
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          समारोप: वर्णा-लेजर AI ने ग्रामीण दुकानदारांना सर्वात आधुनिक AI तंत्रज्ञान दिले आहे. मार्गदर्शक <strong>अतार सर</strong>, विभागप्रमुख <strong>मुल्ला सर</strong> आणि परीक्षकांचे आभार मानून तांत्रिक प्रश्नांसाठी आत्मविश्वासाने सज्ज व्हा.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is each member's core contribution? <strong>Ans:</strong> Sanket (AI vision & lead), Sakshi (UI/UX & Khata WhatsApp), Vaishnavi (Voice billing & Gemini assistant), Rushikesh (FastAPI, SQLite WAL, 50-item inventory & Excel).</div>
        <div class="handover-mini"><strong>🏁 Open Defense:</strong> <strong>"All 4 members stand ready for Examiner Questions."</strong></div>
      </div>
    </div>
  </div>

  <!-- ==================== VIVA EXAMINATION TIPS ==================== -->
  <div class="sec-heading" style="margin-top: 6px;">
    <span>7. परीक्षेत पूर्ण गुण मिळवण्यासाठी ५ सुवर्ण नियम (Top 5 Golden Viva Defense Rules)</span>
  </div>

  <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 5px; padding: 6px 10px; font-size: 7.4pt; line-height: 1.35;">
    <ol style="padding-left: 14px;">
      <li><strong>नेहमी आय-कॉन्टॅक्ट ठेवा:</strong> स्लाईडकडे पाठ करून वाचू नका; परीक्षक आणि अतार सरांकडे पाहून आत्मविश्वासाने बोला.</li>
      <li><strong>स्क्रीनवर बोट दाखवा:</strong> 50 आयटम्स किंवा स्क्रीनशॉट सांगताना स्क्रीनवरील घटकावर हात दाखवून बोला (उदा. "As seen here...").</li>
      <li><strong>हँडओव्हर व्यवस्थित करा:</strong> स्वतःच्या ३ स्लाईड्स संपताच पुढील सहकाऱ्याचे नाव घेऊन हँडओव्हर करा, यामुळे टीमवर्कचे गुण वाढतात.</li>
      <li><strong>प्रश्न ज्याचा त्यानेच हाताळावा:</strong> AI साठी संकेत, UI साठी साक्षी, आवाजासाठी वैष्णवी, आणि बॅकएंड/डेटाबेससाठी ऋषिकेशने उत्तरे द्यावीत.</li>
      <li><strong>लाइव्ह डेमो सज्ज ठेवा:</strong> लॅपटॉपवर `http://127.0.0.1:8000` चालू ठेवा; प्रत्यक्ष काम करून दाखवल्यास परीक्षक 100% प्रभावित होतात.</li>
    </ol>
  </div>

</body>
</html>
"""

def generate_pdf():
    print("=" * 70)
    print("🚀 Generating 3-Slide Per Member Defense Guide PDF")
    print("=" * 70)

    html_file = os.path.abspath("temp_presentation_script_12slides.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        file_url = "file:///" + html_file.replace("\\", "/")
        print(f"Loading: {file_url}")
        page.goto(file_url, wait_until="networkidle")
        
        print("Rendering compact PDF...")
        page.pdf(
            path=OUTPUT_PDF,
            format="A4",
            print_background=True,
            margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"},
            display_header_footer=True,
            header_template='<div style="font-size: 6.8pt; color: #64748b; width: 100%; text-align: right; padding-right: 10mm; font-family: Segoe UI, sans-serif;">VernaLedger.AI: Merchant Pro v7.5 • Guide: Prof. Kaisar Atar • HOD: Dr. S. Y. Mulla • AGCE Satara</div>',
            footer_template='<div style="font-size: 6.8pt; color: #64748b; width: 100%; display: flex; justify-content: space-between; padding: 0 10mm; font-family: Segoe UI, sans-serif;"><span>Arvind Gavali College of Engineering, Satara (DBATU Lonere)</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        )
        browser.close()

    if os.path.exists(html_file):
        os.remove(html_file)

    if os.path.exists(OUTPUT_PDF):
        size_bytes = os.path.getsize(OUTPUT_PDF)
        print("=" * 70)
        print(f"✅ SUCCESS: PDF generated at: {OUTPUT_PDF}")
        print(f"📊 PDF File Size: {size_bytes:,} bytes")
        print("=" * 70)
    else:
        print("❌ ERROR: Output PDF was not created!")
        sys.exit(1)

if __name__ == "__main__":
    generate_pdf()

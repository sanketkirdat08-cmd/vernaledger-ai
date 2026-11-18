"""
VernaLedger.AI: Merchant Pro v7.5
Presentation Script & Role-Wise Defense Guide Generator (Super Simple & Memorable Edition)
Features:
- Complete 23 slides matching VernaLedger_Presentation.html
- Super simple, easy-to-memorize English (2-4 punchy sentences per slide, no tongue-twisters)
- Simple, clear Marathi explanation (2 lines of plain everyday Marathi)
- 1 targeted Examiner Viva Question & simple direct answer per slide
- Smooth English handover cue to next presenter
- Prominently displays: Guide: Prof. Kaisar Atar sir | HOD: Dr. S. Y. Mulla mam | AGCE Satara (DBATU Lonere)
- Exact technical contribution (प्रकल्पातील नक्की योगदान) detailed for all 4 members
- Speaker badges with slide counts: Sanket (6), Sakshi (6), Vaishnavi (5), Rushikesh (6)
"""

import os
import sys
from playwright.sync_api import sync_playwright

OUTPUT_PDF = os.path.abspath("VernaLedger_AI_Presentation_Team_Script_and_Viva_Guide.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="utf-8">
<title>VernaLedger.AI - सोपे प्रेझेंटेशन स्क्रिप्ट व डिफेन्स गाईड</title>
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
    font-size: 8.6pt;
    line-height: 1.34;
  }

  /* Compact Hero Header */
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
    font-size: 9.8pt;
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
    margin-bottom: 6px;
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

  .card-body {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 7px;
    padding: 5px 8px;
  }

  .box-en {
    background: #ffffff;
    border: 1px solid #bae6fd;
    border-left: 3px solid #0284c7;
    border-radius: 4px;
    padding: 4px 7px;
  }
  .box-mr {
    background: #fcfbf9;
    border: 1px solid #a7f3d0;
    border-left: 3px solid #10b981;
    border-radius: 4px;
    padding: 4px 7px;
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
    line-height: 1.32;
    color: #1e293b;
  }
  .text-en strong { color: #0f172a; }

  .text-mr {
    font-size: 7.8pt;
    line-height: 1.32;
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
    padding: 3px 6px;
    font-size: 7.1pt;
    color: #9a3412;
    line-height: 1.25;
  }
  .qa-mini strong { color: #c2410c; }

  .handover-mini {
    background: #f1f5f9;
    border-radius: 4px;
    padding: 3px 6px;
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
      <span class="badge-guide">Guide: Prof. Kaisar Atar | HOD: Dr. S. Y. Mulla mam</span>
    </div>
    <div class="hero-title">VernaLedger.AI <span>Merchant Pro v7.5</span></div>
    <div class="hero-desc">सोपे व सुटसुटीत प्रेझेंटेशन स्क्रिप्ट आणि डिफेन्स गाईड • पाठ करायला व बोलायला अगदी सोपे</div>
    
    <div class="guide-strip">
      <div><strong>प्रकल्प मार्गदर्शक (Guide):</strong> Prof. Kaisar Atar sir</div>
      <div><strong>विभागप्रमुख (HOD):</strong> Dr. S. Y. Mulla mam</div>
      <div><strong>Department:</strong> Artificial Intelligence & Data Science (2026-2027)</div>
      <div><strong>Deck Presentation:</strong> VernaLedger_Presentation.html (23 Slides)</div>
    </div>
  </div>

  <!-- ==================== MEMBER CONTRIBUTIONS ==================== -->
  <div class="sec-heading">
    <span>1. टीम सदस्यांचे वाटप आणि प्रकल्पातील नक्की तांत्रिक योगदान (Role & Exact Technical Contributions)</span>
    <span style="font-size: 7.2pt; font-weight: normal; color: #64748b;">4 Members • 23 Slides</span>
  </div>

  <table class="table-contrib">
    <thead>
      <tr>
        <th style="width: 22%;">विद्यार्थ्याचे नाव व भूमिका</th>
        <th style="width: 14%;">रोल / PRN</th>
        <th style="width: 48%;">प्रकल्पातील नक्की तांत्रिक योगदान (Exact Technical Contribution)</th>
        <th style="width: 16%;">वाटून दिलेल्या स्लाईड्स</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Sanket Kirdat</strong><br><span class="tag-member tag-sanket">Team Leader & AI</span></td>
        <td>Roll: 4060<br><span style="font-size: 7pt; color: #64748b;">24065451263508</span></td>
        <td>
          • <strong>AI Vision OCR इंजिन:</strong> गुगल Gemini 3.1 Flash द्वारे कागदी हस्तलिखित पावत्यांचे <1.5s मध्ये डिजिटायझेशन (`/api/ocr`).<br>
          • <strong>इमेज प्री-प्रोसेसिंग:</strong> ९६०px Lanczos कॉन्ट्रास्ट फिल्टर आणि SHA-256 हॅश द्वारे डुप्लिकेट पावती प्रतिबंध.<br>
          • <strong>प्रकल्प नेतृत्व:</strong> सिस्टीम एकत्रीकरण, उद्दिष्टे, पाईपलाईन आणि अंतिम ओपन डिफेन्स (Q&A).
        </td>
        <td><strong>Slides: 01, 02, 06, 07, 12, 23</strong><br><span style="color: #0284c7; font-weight: 700;">(६ स्लाईड्स)</span></td>
      </tr>
      <tr>
        <td><strong>Sakshi Bhagat</strong><br><span class="tag-member tag-sakshi">Frontend & UI/UX</span></td>
        <td>Roll: 4054<br><span style="font-size: 7pt; color: #64748b;">24065451263502</span></td>
        <td>
          • <strong>UI/UX आर्किटेक्चर:</strong> व्हॅनिला JavaScript आधारित जलद सिंगल पेज ॲप्लिकेशन (SPA) इंटरफेस.<br>
          • <strong>उधारी खातेवही (Khata):</strong> 'उधारी दिली' व 'जमा मिळाले' ऑटो-कॅल्क्युलेशन आणि १-क्लिक व्हॉट्सॲप UPI पेमेंट लिंक.<br>
          • <strong>किराणा मोड व PWA:</strong> थेट उन्हात स्पष्ट दिसणारा किराणा मोड आणि मोबाईलसाठी ५-टॅब बॉटम टच बार.
        </td>
        <td><strong>Slides: 03, 04, 14, 18, 19, 20</strong><br><span style="color: #d97706; font-weight: 700;">(६ स्लाईड्स)</span></td>
      </tr>
      <tr>
        <td><strong>Vaishnavi Dhavale</strong><br><span class="tag-member tag-vaishnavi">Voice Billing & AI</span></td>
        <td>Roll: 4056<br><span style="font-size: 7pt; color: #64748b;">24065451263504</span></td>
        <td>
          • <strong>मराठी व्हॉइस बिलिंग:</strong> Web Speech API (`mr-IN`) द्वारे सलग अखंड आवाजातून बिल तयार करणे (`/api/voice-billing`).<br>
          • <strong>प्रादेशिक भाषा NLP पार्सर:</strong> 'पाव किलो', 'अर्धा लिटर' अशा स्थानिक मराठी बोलीभाषेचे थेट अंकांमध्ये रूपांतर.<br>
          • <strong>Verna AI जेमिनी असिस्टंट:</strong> माईक पल्स ॲनिमेशन, वर्ड-बाय-वर्ड स्ट्रीमिंग आणि देवनागरी स्क्रिप्ट पर्सिस्टन्स.
        </td>
        <td><strong>Slides: 05, 13, 16, 21, 22</strong><br><span style="color: #7c3aed; font-weight: 700;">(५ स्लाईड्स)</span></td>
      </tr>
      <tr>
        <td><strong>Rushikesh Mulik</strong><br><span class="tag-member tag-rushikesh">Backend & Database</span></td>
        <td>Roll: 4004<br><span style="font-size: 7pt; color: #64748b;">23065451263005</span></td>
        <td>
          • <strong>FastAPI सर्व्हरलेस बॅकएंड:</strong> हाय-स्पीड ASGI गेटवे आणि multi-key failover rotation पूल (`api/index.py`).<br>
          • <strong>SQLite ACID डेटाबेस:</strong> Write-Ahead Logging (WAL) मोडमध्ये <2ms लेटन्सीसह 5 टेबल्सचे व्यवस्थापन.<br>
          • <strong>५० किराणा माल साठा इंजिन:</strong> ५० वस्तूंचा साठा, रिअल-टाइम सर्च आणि बिलांनंतर स्वयंचलित स्टॉक वजावट.<br>
          • <strong>एक्सेल एक्सपोर्ट इंजिन:</strong> XlsxWriter द्वारे देवनागरी मराठी फॉन्टसह थेट `.xlsx` स्प्रेडशीट जनरेशन.
        </td>
        <td><strong>Slides: 08, 09, 10, 11, 15, 17</strong><br><span style="color: #059669; font-weight: 700;">(६ स्लाईड्स)</span></td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== ALL 23 SLIDES (Super Simple Edition) ==================== -->
  <div class="sec-heading">
    <span>2. सर्व २३ स्लाईड्सचे सोपे स्क्रिप्ट (Simple Spoken English + Marathi Meaning)</span>
  </div>

  <!-- SLIDE 01 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 01</span> Cover Page: VernaLedger.AI: Merchant Pro v7.5</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader & AI) • Slide 1/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Good morning respected guide <strong>Prof. Kaisar Atar sir</strong>, HOD <strong>Dr. S. Y. Mulla mam</strong>, and examiners. I am <strong>Sanket Kirdat</strong>, leading our team with Sakshi, Vaishnavi, and Rushikesh. Today, we present <strong>'VernaLedger.AI'</strong> — an AI billing and bookkeeping system made specially for local Indian kirana stores."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          सुरुवात करताना <strong>अतार सर</strong>, <strong>मुल्ला मॅम</strong> आणि परीक्षकांना आदरपूर्वक नमस्कार करा. स्वतःची व सहकाऱ्यांची ओळख करून देऊन सांगा: "हा किराणा दुकानदारांसाठी बनवलेला सोपा मराठी AI बिलिंग प्लॅटफॉर्म आहे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is the main goal of your project? <strong>Ans:</strong> To help local kirana shopkeepers make bills by camera photo or Marathi voice, without typing or English.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us look at the project overview on Slide 2."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 02 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 02</span> Introduction: VernaLedger.AI Suite</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader & AI) • Slide 2/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "VernaLedger.AI does three main things: <strong>First</strong>, it scans paper bills using camera AI in under 2 seconds. <strong>Second</strong>, shopkeepers can create bills simply by speaking in Marathi. <strong>Third</strong>, it tracks customer udhari and sends WhatsApp payment links with Google Pay and PhonePe."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          ३ मुख्य कामे सांगा: १. कागदी पावती २ सेकंदात स्कॅन करणे, २. मराठीत बोलून बिल बनवणे, आणि ३. उधारीचा हिशोब ठेवून ग्राहकांना व्हॉट्सॲपवर UPI लिंक पाठवणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why does it work offline? <strong>Ans:</strong> In villages, internet is slow; so our database saves all bills locally in under 2 milliseconds.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sakshi:</strong> "Now Sakshi will explain the real problems shopkeepers face on Slide 3."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 03 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 03</span> Problem Statement: Market Reality</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend & UI) • Slide 1/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Thank you Sanket. Today, 85% of local kirana stores still use paper notebooks. These notebooks get torn, wet, or lost, and math mistakes happen easily. Also, customers buy on credit, but shopkeepers forget to collect money on time, losing cash. Existing software is in English and too hard to use."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          किराणा दुकानांच्या ३ अडचणी सांगा: १. कागदी वह्या खराब होतात व हिशोबात चुका होतात. २. उधारीचे पैसे वेळेवर न मागितल्याने बुडतात. ३. सध्याची ॲप्स इंग्रजीत असल्याने अवघड आहेत.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How does paper ledger cause loss? <strong>Ans:</strong> Shopkeepers lose 15-20% working capital because forgotten credit records are never recovered.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us see our motivation on Slide 4."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 04 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 04</span> Motivation & Purpose</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend & UI) • Slide 2/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Our main goal is to remove typing and language barriers. If a shopkeeper can take a photo or speak Marathi, they can easily make bills. Sending 1-click WhatsApp payment reminders helps them recover money 60% faster, without any awkward phone calls."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          आमचा हेतू: दुकानदाराला इंग्रजी किंवा टायपिंग न येताही फक्त फोटो काढून किंवा बोलून बिलिंग करता यावी आणि व्हॉट्सॲपमुळे उधारीचे पैसे ६०% जलद परत मिळावेत.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why send WhatsApp messages? <strong>Ans:</strong> WhatsApp is used by everyone in India, and customers can directly click the UPI link to pay via PhonePe or Google Pay.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Now Vaishnavi will compare existing market apps on Slide 5."</div>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SLIDE 05 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 05</span> Gap Analysis & Competitive Benchmarks</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing & AI) • Slide 1/5</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Thank you Sakshi. On Slide 5, we compare VernaLedger with Vyapar and Khatabook. Other apps do not have paper bill scanning, do not support Marathi voice billing, and do not have an AI assistant. VernaLedger provides all these features completely free and offline-ready."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          खाताबुक किंवा व्यापार ॲपमध्ये कागदी बिल स्कॅनर नाही, मराठी व्हॉइस बिलिंग नाही आणि AI चॅटबॉट नाही. आपल्या सिस्टीममध्ये हे सर्व मोफत आणि ऑफलाइन उपलब्ध आहे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why is VernaLedger better than Khatabook? <strong>Ans:</strong> Khatabook requires typing everything in English; VernaLedger lets merchants speak in Marathi or scan paper bills.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sanket:</strong> "Sanket will now present our project objectives on Slide 6."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 06 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 06</span> Project Objectives</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader & AI) • Slide 3/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "We had four clear goals: 1. Scan handwritten bills accurately in 1.5 seconds. 2. Support continuous Marathi voice billing without stopping. 3. Track customer credit and send 1-click WhatsApp payment links. 4. Pre-load 50 kirana items and auto-deduct stock on every sale."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          ४ उद्दिष्टे सांगा: १. पावती जलद स्कॅन करणे, २. सलग मराठी आवाज ऐकून बिल बनवणे, ३. व्हॉट्सॲपवर उधारी लिंक पाठवणे, आणि ४. ५० किराणा साठ्यातून माल आपोआप कमी होणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What happens if stock becomes zero? <strong>Ans:</strong> System shows a red '🚨 कमी साठा' alert and prevents negative stock using `MAX(0, stock - qty)`.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us see how the system works step-by-step on Slide 7."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 07 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 07</span> Proposed System Pipeline</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader & AI) • Slide 4/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Our system works in 4 simple steps: <strong>Step 1:</strong> Input from camera photo, Marathi voice, or keyboard. <strong>Step 2:</strong> Gemini AI reads items, weights, and prices. <strong>Step 3:</strong> SQLite database saves the bill and auto-deducts inventory stock. <strong>Step 4:</strong> Output bill as thermal print, WhatsApp message, or Excel file."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          कामाचे ४ टप्पे: १. इनपुट (फोटो किंवा आवाज) -> २. AI द्वारे वाचन -> ३. डेटाबेस सेव्ह व साठा वजावट -> ४. आउटपुट (पावती प्रिंट, व्हॉट्सॲप किंवा एक्सेल).
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you check if bill calculation is correct? <strong>Ans:</strong> The system automatically checks `quantity × rate = total` before saving to database.</div>
        <div class="handover-mini"><strong>➡️ Handover to Rushikesh:</strong> "Now Rushikesh will explain our technology stack on Slide 8."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 08 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 08</span> Technologies & Tools (Engineering Stack)</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend & Database) • Slide 1/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Thank you Sanket. Our backend is built using <strong>FastAPI and Python</strong>, which is extremely fast. The frontend is built in pure JavaScript with zero heavy frameworks. We use Google Gemini for AI vision, Web Speech API for voice, and local <strong>SQLite database</strong> which saves bills in under 2 milliseconds."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          तंत्रज्ञान सांगा: बॅकएंडला वेगवान FastAPI व Python, फ्रंटएंडला हलके व्हॅनिला JS, AI साठी गुगल Gemini, आवाजासाठी Web Speech API, आणि २ मिलिसेकंदात सेव्ह होणारा SQLite डेटाबेस.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why SQLite instead of MySQL? <strong>Ans:</strong> SQLite is serverless and zero-setup; it runs inside a single file without needing expensive server hardware.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 9 shows our 3-tier architecture."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 09 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 09</span> System Architecture (Modular 3-Tier)</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend & Database) • Slide 2/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "We use a clean 3-tier architecture: 1. <strong>Presentation Layer:</strong> The mobile and desktop web UI with Kirana Light mode. 2. <strong>Application Layer:</strong> FastAPI server handling OCR, voice billing, and database queries. 3. <strong>Database Layer:</strong> SQLite database storing bills, customer khata, 50 inventory items, and expenses."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          ३ लेअर्स: १. प्रेझेंटेशन (स्क्रीन व कॅमेरा), २. ॲप्लिकेशन (FastAPI सर्व्हर जो AI आणि डेटाबेस जोडतो), आणि ३. डेटाबेस (बिलांचे, उधारीचे, आणि ५० मालाचे टेबल्स).
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How is merchant data kept safe? <strong>Ans:</strong> All sales and customer credit data are stored locally on the shopkeeper's device, not shared with third parties.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 10 details our working flow."</div>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SLIDE 10 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 10</span> Working Flow & Execution Pipeline</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend & Database) • Slide 3/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "The billing flow takes 5 steps: 1. Take a bill photo or speak in Marathi. 2. Image is compressed to 960px to speed up upload. 3. Gemini AI extracts items into a clean bill. 4. Shopkeeper checks the items on screen. 5. On clicking Save, the database commits and stock auto-deducts immediately."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          कामाची पायरी: १. फोटो किंवा आवाज -> २. ९६०px इमेज कॉम्प्रेशन -> ३. AI द्वारे बिल तयार -> ४. स्क्रीनवर खात्री करणे -> ५. 'सेव्ह' दाबताच डेटाबेसमध्ये नोंद व साठा वजावट.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you stop scanning the same bill twice? <strong>Ans:</strong> We compute a SHA-256 digital hash of the image; if scanned twice, the system shows an instant duplicate warning.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us review our performance benchmarks on Slide 11."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 11 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 11</span> Performance Analysis & Benchmarks</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend & Database) • Slide 4/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "We tested our system on real kirana bills: 1. Bill scanning takes under 1.5 seconds. 2. Marathi word recognition is 96.8% accurate across 120 test bills. 3. AI chat responds in 10 milliseconds from local memory. 4. Database commits take less than 2 milliseconds."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          आकडेवारी सांगा: १. पावती १.५ सेकंदात स्कॅन होते. २. मराठी अक्षरे ९६.८% अचूक ओळखली जातात. ३. स्थानिक डेटाबेसमधून १०ms मध्ये उत्तर मिळते. ४. २ मिलिसेकंदात बिल सेव्ह होते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is SQLite WAL mode? <strong>Ans:</strong> Write-Ahead Logging allows reading and writing at the same time, so the billing screen never freezes.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sanket:</strong> "Sanket will now demonstrate Result 1: Smart Scanner on Slide 12."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 12 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 12</span> Result 1: Smart Multimodal Scanner & POS</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader & AI) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "This is Result 1: Our Smart Bill Scanner. When the shopkeeper takes a photo of a paper receipt, Google Gemini AI reads all item names, quantities, and rates into a clean bill on screen. When saved, all sold items are automatically deducted from store inventory."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          स्क्रीन दाखवून सांगा: कागदी पावतीचा फोटो काढताच स्क्रीनवर सुंदर बिल तयार होते. 'सेव्ह' दाबताच दुकानातील ५० साठ्यामधून तेवढा माल आपोआप कमी होतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What if handwriting is bad or faded? <strong>Ans:</strong> Our app sharpens the image first, and allows the shopkeeper to edit any item on screen before saving.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Next, Vaishnavi will show our voice billing engine on Slide 13."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 13 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 13</span> Result 2: Vernacular Voice Billing Engine</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing & AI) • Slide 2/5</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "This is Result 2: Voice Billing. When there is a crowd of customers, typing is impossible. The shopkeeper simply speaks: 'सागरला २ किलो साखर ८४ रुपये आणि १ तेल १८५ रुपये'. The app listens continuously, creates the bill, updates customer credit, and cuts down counter wait time by 85%."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          गर्दी असताना टायपिंग करायला वेळ नसतो. दुकानदार फक्त माईक दाबून मराठीत बोलेल: 'सागरला २ किलो साखर ८४ रुपये...'. सिस्टीम वाक्य पूर्ण होईपर्यंत ऐकून थेट बिल बनवते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How does it understand words like 'पाव किलो'? <strong>Ans:</strong> Our regex parser automatically converts 'पाव' to 0.25 kg, 'अर्धा' to 0.5 kg, and 'दीड' to 1.5 kg.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sakshi:</strong> "Now Sakshi will present Customer Khata on Slide 14."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 14 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 14</span> Result 3: Customer Khata & Udhar Ledger</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend & UI) • Slide 3/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "This is Result 3: Customer Khata Book. Shopkeepers can record 'उधारी दिली' (credit given) and 'जमा मिळाले' (payment received) with one click. Clicking the green WhatsApp button sends a polite Marathi reminder with a direct UPI payment link to the customer's phone."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          उधारी खातेवही: उधारी आणि जमा रकमेची नोंद एका सेकंदात होते. हिरवे व्हॉट्सॲप बटण दाबताच ग्राहकाला 'आपली बाकी ₹५०० आहे' असा मेसेज आणि थेट PhonePe/GPay ची लिंक जाते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Does WhatsApp messaging cost any money? <strong>Ans:</strong> No, it uses the free WhatsApp web intent (`wa.me`) to open the shopkeeper's WhatsApp directly.</div>
        <div class="handover-mini"><strong>➡️ Handover to Rushikesh:</strong> "Now Rushikesh will explain 50 Kirana Inventory Items on Slide 15."</div>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SLIDE 15 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 15</span> Result 4: Store Operations & 50 Kirana Inventory Items</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend & Database) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Result 4 is Store Operations. We pre-loaded 50 authentic Kirana items (wheat, rice, dals, sugar, oil, tea, spices) with units like kg, liter, and packet. When bills are saved, stock is automatically deducted (`stock = MAX(0, stock - qty)`). Items running low display a bright '🚨 कमी साठा' badge."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          ५० मूळ किराणा वस्तू आधीच भरलेल्या आहेत. सर्च बारने वस्तू शोधता येते, बिलासोबत गोदामातील साठा आपोआप कमी होतो आणि माल संपत आला की लाल रंगाचा '🚨 कमी साठा' इशारा मिळतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Can shopkeepers add their own items? <strong>Ans:</strong> Yes, they can add new items with custom units and rates, or click reset to restore original 50 items.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Now Vaishnavi will showcase Verna AI Assistant on Slide 16."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 16 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 16</span> Result 5: Verna AI Multilingual Voice Assistant</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing & AI) • Slide 3/5</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Result 5 is our Verna AI Assistant, designed like the official Google Gemini app. It has a pulsing mic button, answers word-by-word smoothly, and speaks strictly in the same language. It checks our real database to answer: 'How much sugar is left?' or 'What is today's total sale?' with 100% accuracy."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          गुगल जेमिनीसारखा AI असिस्टंट: बोलताना माईक पल्स होतो, शब्द न् शब्द समोर उमटतात, आणि मराठीत विचारल्यास मराठीतच उत्तर मिळते. दुकानातील खरा साठा तपासून अगदी अचूक उत्तर देतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Does the AI give fake numbers? <strong>Ans:</strong> No, we inject real database numbers into the prompt, so it answers only from verified store data.</div>
        <div class="handover-mini"><strong>➡️ Handover to Rushikesh:</strong> "Rushikesh will now show our digital ledger and Excel export on Slide 17."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 17 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 17</span> Result 6: Digital Ledger & Excel Export</div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend & Database) • Slide 6/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Result 6 is our Digital Ledger and Excel Export. All old bills can be searched instantly by bill number or customer name. Clicking the big green button downloads a formatted Microsoft Excel (`.xlsx`) sheet with clean Marathi fonts, ready to show to chartered accountants (CAs) or banks."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          सर्व जुन्या बिलांचा कायमस्वरूपी रेकॉर्ड. हिरवे एक्सेल बटण दाबताच मराठी नावांसह सुटसुटीत `.xlsx` फाईल डाऊनलोड होते, जी CA किंवा बँकेला दाखवता येते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is your personal contribution? <strong>Ans:</strong> I built the FastAPI backend, SQLite WAL database, 50 Kirana item inventory auto-deduction, and the Excel export generator.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sakshi:</strong> "Sakshi will now present Kirana Light Mode and Mobile PWA on Slide 18."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 18 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 18</span> Result 7: High-Contrast Kirana Light Mode</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend & UI) • Slide 4/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Kirana shops are on the roadside with bright sunlight entering the counter. On cheap mobile screens, dark mode cannot be seen under bright sunlight. So we made 'Kirana Light Mode' with a clean white background and dark navy text, so shopkeepers can read numbers easily in full sunlight."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          दुकानात दुपारच्या कडक उन्हामध्ये डार्क मोड दिसत नाही. म्हणून आम्ही 'किराणा लाईट मोड' बनवला; पांढऱ्या पार्श्वभूमीवर गडद अक्षरे असल्यामुळे उन्हातही सर्व आकडे अगदी स्पष्ट दिसतात.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you switch themes? <strong>Ans:</strong> Click the sun/moon button on top; the setting is saved in browser localStorage.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 19 shows our Mobile App interface."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 19 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 19</span> Result 8: Mobile-First Responsive PWA</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend & UI) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Most shopkeepers do not have computers; they only use budget Android phones. So we built VernaLedger as a Mobile PWA. On phones, it shows 5 easy bottom tabs: Scanner, Khata, Store, Ledger, and AI. It can be installed directly on the phone home screen like a normal app."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          दुकानदारांकडे कॉम्प्युटर नसतो, फक्त फोन असतो. म्हणून आम्ही मोबाईलसाठी खाली ५ सोपे टॅब दिले आहेत आणि हे ॲप क्रोममधून थेट मोबाईल स्क्रीनवर ॲपसारखे इन्स्टॉल करता येते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Can it take photos using mobile camera? <strong>Ans:</strong> Yes, it directly opens the phone's back camera when clicking the scan button.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 20 summarizes our system advantages."</div>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SLIDE 20 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 20</span> Advantages & Strategic Strengths</div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend & UI) • Slide 6/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Our 4 biggest advantages are: 1. Works in Marathi so anyone can use it without training. 2. 60% faster credit recovery via WhatsApp UPI links. 3. Works on existing phones with zero extra hardware cost. 4. Works offline so billing never stops when internet is down."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          ४ मोठे फायदे: १. मराठीत असल्याने कोणीही वापरू शकते. २. उधारी ६०% लवकर वसूल होते. ३. नवीन महागडे मशीन लागत नाही. ४. इंटरनेट नसले तरी सुरक्षित चालते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is your personal contribution? <strong>Ans:</strong> I designed the complete user interface, the Khata WhatsApp system, Kirana Light mode, and mobile PWA.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Now Vaishnavi will explain system limitations on Slide 21."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 21 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 21</span> System Limitations (Engineering Constraints)</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing & AI) • Slide 4/5</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "Here are our honest system limitations: 1. Core billing and database work 100% offline, but Gemini AI bill scanning and chat require an internet connection. 2. If a paper receipt is very oily, torn, or completely faded, the merchant must double-check the items on screen before saving."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          सिस्टीमच्या २ मर्यादा: १. बिलिंग आणि डेटाबेस ऑफलाइन चालतो, पण AI स्कॅनर व चॅटसाठी इंटरनेट लागते. २. जर पावतीवर तेल सांडले असेल किंवा शाई उडाली असेल, तर स्क्रीनवर तपासून खात्री करावी लागते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How will you make bill scanning work without internet? <strong>Ans:</strong> In future, we can run a small lightweight offline OCR model like MobileNet directly on the mobile device.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 22 shows our future enhancements."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 22 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 22</span> Future Enhancements (Scalability Roadmap)</div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing & AI) • Slide 5/5</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "In the future, we plan four additions: 1. A standalone offline Android APK. 2. A Bluetooth UPI Soundbox that announces payments in Marathi: 'PhonePe वर ₹२५० प्राप्त झाले'. 3. Multi-counter syncing across the shop. 4. One-click GST tax report generation."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          भविष्यातील ४ योजना: १. फोनसाठी ऑफलाइन ॲप (APK), २. 'PhonePe वर ₹२५० मिळाले' असा मराठी आवाज देणारा UPI साऊंडबॉक्स, ३. दुकानातील इतर काऊंटर जोडणे, आणि ४. GST टॅक्स रिपोर्ट बनवणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is your personal contribution? <strong>Ans:</strong> I developed the Marathi voice billing system, the regional dialect NLP parser, and the Gemini AI assistant.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sanket:</strong> "Now our leader Sanket will conclude our presentation on Slide 23."</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 23 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 23</span> Conclusion & Open Defense (Q&A)</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader & AI) • Slide 6/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (सोपे इंग्रजी वाक्ये)</div>
        <div class="text-en">
          "To conclude: VernaLedger.AI brings modern AI to local kirana stores. It combines paper bill scanning, Marathi voice billing, 50 kirana items inventory, and WhatsApp payment recovery. We thank our guide <strong>Prof. Kaisar Atar sir</strong>, HOD <strong>Dr. S. Y. Mulla mam</strong>, and our college. We are now ready for your questions. Thank you!"
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात काय सांगायचे)</div>
        <div class="text-mr">
          समारोप करा: "वर्णा-लेजर AI मुळे लहान दुकानदारांना बिलिंग करणे सोपे झाले आहे." <strong>अतार सर</strong>, <strong>मुल्ला मॅम</strong> आणि परीक्षकांचे आभार माना आणि तांत्रिक प्रश्नांसाठी सज्ज व्हा.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is your personal contribution? <strong>Ans:</strong> I led the project, built the Gemini Vision OCR scanner, and integrated the complete system.</div>
        <div class="handover-mini"><strong>🏁 Open Defense:</strong> <strong>"All 4 members stand ready for Examiner Questions."</strong></div>
      </div>
    </div>
  </div>

  <!-- ==================== VIVA EXAMINATION TIPS ==================== -->
  <div class="sec-heading" style="margin-top: 6px;">
    <span>3. परीक्षेत पूर्ण गुण मिळवण्यासाठी ५ सुवर्ण नियम (Top 5 Golden Viva Defense Rules)</span>
  </div>

  <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 5px; padding: 6px 10px; font-size: 7.4pt; line-height: 1.35;">
    <ol style="padding-left: 14px;">
      <li><strong>नेहमी आय-कॉन्टॅक्ट ठेवा:</strong> स्लाईडकडे पाठ करून वाचू नका; परीक्षक, अतार सर आणि मुल्ला मॅम यांच्याकडे पाहून आत्मविश्वासाने बोला.</li>
      <li><strong>स्क्रीनवर बोट दाखवा:</strong> ५० आयटम्स किंवा स्क्रीनशॉट सांगताना स्क्रीनवरील घटकावर हात दाखवून बोला (उदा. "As seen here...").</li>
      <li><strong>हँडओव्हर व्यवस्थित करा:</strong> स्वतःच्या स्लाईड्स संपताच पुढील सहकाऱ्याचे नाव घेऊन हँडओव्हर करा, यामुळे टीमवर्कचे गुण वाढतात.</li>
      <li><strong>प्रश्न ज्याचा त्यानेच हाताळावा:</strong> AI साठी संकेत, UI साठी साक्षी, आवाजासाठी वैष्णवी, आणि बॅकएंड/डेटाबेससाठी ऋषिकेशने उत्तरे द्यावीत.</li>
      <li><strong>लाइव्ह डेमो सज्ज ठेवा:</strong> लॅपटॉपवर `http://127.0.0.1:8000` चालू ठेवा; प्रत्यक्ष काम करून दाखवल्यास परीक्षक १००% प्रभावित होतात.</li>
    </ol>
  </div>

</body>
</html>
"""

def generate_pdf():
    print("=" * 70)
    print("🚀 Generating Super Simple 23-Slide Presentation Script & Defense Guide PDF")
    print("=" * 70)

    html_file = os.path.abspath("temp_presentation_script_simple.html")
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
            header_template='<div style="font-size: 6.8pt; color: #64748b; width: 100%; text-align: right; padding-right: 10mm; font-family: Segoe UI, sans-serif;">VernaLedger.AI: Merchant Pro v7.5 • Guide: Prof. Kaisar Atar • HOD: Dr. S. Y. Mulla mam • AGCE Satara</div>',
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

"""
VernaLedger.AI: Merchant Pro v7.5
Presentation Script & Role-Wise Defense Guide Generator (100% Slide-by-Slide Exact Match Edition)
Features:
- Complete 23 slides matching VernaLedger_Presentation.html 1:1
- 📌 Exact On-Screen Slide Content (स्लाईडवरील नक्की मुद्दे व दृश्य) listed for every single slide
- 🗣️ Super simple, easy-to-memorize Spoken English Script (2-4 punchy active sentences)
- 📝 Simple, plain everyday Marathi explanation (२ ओळींत सोपा अर्थ)
- 🎯 1 targeted Examiner Viva Question & simple direct answer per slide
- ➡️ Smooth English handover cue to next presenter
- Prominently displays: Guide: Prof. Kaisar Atar sir | HOD: Dr. S. Y. Mulla mam | AGCE Satara (DBATU Lonere)
- Exact technical contributions detailed for all 4 team members
- Speaker badges with slide counts: Sanket (6), Sakshi (6), Vaishnavi (5), Rushikesh (6)
"""

import os
import sys
import shutil
from playwright.sync_api import sync_playwright

OUTPUT_PDF = os.path.abspath("VernaLedger_AI_Presentation_Team_Script_and_Viva_Guide.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="utf-8">
<title>VernaLedger.AI - स्लाईडनुसार अचूक प्रेझेंटेशन स्क्रिप्ट व डिफेन्स गाईड</title>
<style>
  @page {
    size: A4;
    margin: 7mm 7mm 7mm 7mm;
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
    font-size: 8.2pt;
    line-height: 1.32;
  }

  /* Compact Hero Header */
  .hero-box {
    background: linear-gradient(135deg, #050b14 0%, #0d2859 60%, #0a1128 100%);
    color: #ffffff;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 7px;
    border: 1px solid rgba(0, 242, 254, 0.4);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  .hero-top-badge {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 6.8pt;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 700;
    margin-bottom: 2px;
  }
  .hero-title {
    font-size: 13.5pt;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .hero-title .tag {
    font-size: 7.2pt;
    background: rgba(0, 242, 254, 0.18);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.45);
    padding: 2px 7px;
    border-radius: 10px;
    font-weight: 700;
  }
  .hero-sub {
    font-size: 7.6pt;
    color: #cbd5e1;
    margin-top: 1px;
  }
  .hero-meta-grid {
    display: grid;
    grid-template-columns: 1.15fr 1.05fr 1.8fr;
    gap: 4px;
    margin-top: 5px;
    padding-top: 4px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    font-size: 7.1pt;
  }
  .meta-item b {
    color: #00f2fe;
  }

  /* Team Roster Grid */
  .team-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
    margin-bottom: 8px;
  }
  .team-card {
    border-radius: 6px;
    padding: 5px 7px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    font-size: 7.2pt;
    line-height: 1.25;
  }
  .team-card.sanket { border-top: 3px solid #0284c7; background: #f0f9ff; }
  .team-card.sakshi { border-top: 3px solid #059669; background: #ecfdf5; }
  .team-card.vaishnavi { border-top: 3px solid #7c3aed; background: #f5f3ff; }
  .team-card.rushikesh { border-top: 3px solid #d97706; background: #fffbeb; }

  .team-name {
    font-weight: 800;
    font-size: 7.8pt;
    color: #0f172a;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .team-badge-pill {
    font-size: 6.2pt;
    font-weight: 800;
    padding: 1px 5px;
    border-radius: 6px;
    color: #fff;
  }
  .badge-sanket { background: #0284c7; }
  .badge-sakshi { background: #059669; }
  .badge-vaishnavi { background: #7c3aed; }
  .badge-rushikesh { background: #d97706; }

  .team-role {
    color: #475569;
    font-weight: 700;
    font-size: 6.8pt;
    margin-top: 1px;
  }
  .team-contrib {
    color: #64748b;
    font-size: 6.6pt;
    margin-top: 2px;
  }

  /* Slide Cards Layout */
  .slide-card {
    border-radius: 6px;
    border: 1.2px solid #cbd5e1;
    margin-bottom: 7px;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    page-break-inside: avoid;
    overflow: hidden;
  }
  .slide-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 8px;
    font-size: 7.5pt;
    font-weight: 800;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  }
  .topbar-sanket { background: #e0f2fe; color: #0369a1; border-left: 4px solid #0284c7; }
  .topbar-sakshi { background: #d1fae5; color: #047857; border-left: 4px solid #059669; }
  .topbar-vaishnavi { background: #ede9fe; color: #6d28d9; border-left: 4px solid #7c3aed; }
  .topbar-rushikesh { background: #fef3c7; color: #b45309; border-left: 4px solid #d97706; }

  .slide-id-title {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .slide-pill {
    background: #0f172a;
    color: #ffffff;
    font-size: 6.6pt;
    padding: 1.5px 6px;
    border-radius: 4px;
    font-weight: 800;
    letter-spacing: 0.5px;
  }
  .speaker-badge {
    font-size: 6.8pt;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .spk-sanket { background: #bae6fd; color: #0369a1; }
  .spk-sakshi { background: #a7f3d0; color: #065f46; }
  .spk-vaishnavi { background: #ddd6fe; color: #5b21b6; }
  .spk-rushikesh { background: #fde68a; color: #92400e; }

  .card-body {
    padding: 5px 8px;
  }

  /* 1. On-Screen Content Box (Exact match with presentation slide) */
  .box-onscreen {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #64748b;
    border-radius: 4px;
    padding: 3px 6px;
    margin-bottom: 4px;
  }
  .lbl-onscreen {
    color: #334155;
    font-weight: 800;
    font-size: 6.7pt;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .text-onscreen {
    font-size: 7.2pt;
    line-height: 1.28;
    color: #334155;
  }
  .text-onscreen b {
    color: #0f172a;
  }
  .text-onscreen .pill-item {
    display: inline-block;
    background: #e2e8f0;
    color: #0f172a;
    padding: 0px 4px;
    border-radius: 3px;
    font-weight: 700;
    margin-right: 3px;
    font-size: 6.8pt;
  }

  /* 2. Spoken English Script Box */
  .box-en {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 3px solid #16a34a;
    border-radius: 4px;
    padding: 4px 7px;
    margin-bottom: 4px;
  }
  .lbl-en {
    color: #15803d;
    font-weight: 800;
    font-size: 6.8pt;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 1.5px;
  }
  .text-en {
    font-size: 7.5pt;
    line-height: 1.30;
    color: #14532d;
    font-weight: 600;
  }

  /* 3. Marathi Translation Box */
  .box-mr {
    background: #fefce8;
    border: 1px solid #fef08a;
    border-left: 3px solid #ca8a04;
    border-radius: 4px;
    padding: 3.5px 7px;
    margin-bottom: 4px;
  }
  .lbl-mr {
    color: #854d0e;
    font-weight: 800;
    font-size: 6.8pt;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 1px;
  }
  .text-mr {
    font-size: 7.3pt;
    line-height: 1.28;
    color: #713f12;
  }

  /* Bottom Row: Viva QA & Handover */
  .bottom-row {
    display: grid;
    grid-template-columns: 1.25fr 0.95fr;
    gap: 5px;
    font-size: 6.9pt;
  }
  .qa-mini {
    background: #fdf2f8;
    border: 1px solid #fbcfe8;
    border-radius: 4px;
    padding: 2.5px 5px;
    color: #831843;
    line-height: 1.22;
  }
  .qa-mini b { color: #9d174d; }
  .handover-mini {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2.5px 5px;
    color: #334155;
    font-style: italic;
    line-height: 1.22;
  }
  .handover-mini b { color: #0f172a; font-style: normal; }

  /* Page Break Styling */
  .page-divider {
    page-break-after: always;
  }
</style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- HERO HEADER & TEAM ROSTER                                             -->
  <!-- ===================================================================== -->
  <div class="hero-box">
    <div class="hero-top-badge">
      <span>ARVIND GAVALI COLLEGE OF ENGINEERING, SATARA • DBATU LONERE</span>
      <span>Guide: Prof. Kaisar Atar sir | HOD: Dr. S. Y. Mulla mam</span>
    </div>
    <div class="hero-title">
      VernaLedger.AI Merchant Pro v7.5
      <span class="tag">२३ Slides Exact Match Defense Guide</span>
    </div>
    <div class="hero-sub">
      स्लाईडवरील नक्की मजकूर, पाठ करायला सोपे इंग्रजी वाक्ये, मराठी अर्थ आणि संभाव्य Viva प्रश्न-उत्तरे
    </div>
    <div class="hero-meta-grid">
      <div class="meta-item">👨‍🏫 <b>प्रकल्प मार्गदर्शक:</b> Prof. Kaisar Atar sir</div>
      <div class="meta-item">🏛️ <b>विभागप्रमुख (HOD):</b> Dr. S. Y. Mulla mam</div>
      <div class="meta-item">📚 <b>विभाग:</b> Artificial Intelligence &amp; Data Science (2026-2027)</div>
    </div>
  </div>

  <!-- 4 Team Members Exact Role & Slide Allocation Table -->
  <div class="team-grid">
    <div class="team-card sanket">
      <div class="team-name">
        <span>१. संकेत किर्दत</span>
        <span class="team-badge-pill badge-sanket">६ Slides</span>
      </div>
      <div class="team-role">Team Leader &amp; AI Architecture</div>
      <div class="team-contrib">
        <b>योगदान:</b> Gemini Vision OCR, Pipeline, 50-Item Logic, Leader Defense.<br/>
        <b>Slides:</b> 01, 02, 06, 07, 12, 23
      </div>
    </div>
    <div class="team-card sakshi">
      <div class="team-name">
        <span>२. साक्षी भगत</span>
        <span class="team-badge-pill badge-sakshi">६ Slides</span>
      </div>
      <div class="team-role">Frontend &amp; UI/UX Experience</div>
      <div class="team-contrib">
        <b>योगदान:</b> Cyberpunk &amp; Light Themes, Khata UI, PWA, 5 App Views.<br/>
        <b>Slides:</b> 03, 04, 14, 18, 19, 20
      </div>
    </div>
    <div class="team-card vaishnavi">
      <div class="team-name">
        <span>३. वैष्णवी ढवळे</span>
        <span class="team-badge-pill badge-vaishnavi">५ Slides</span>
      </div>
      <div class="team-role">Voice Billing &amp; Multilingual AI</div>
      <div class="team-contrib">
        <b>योगदान:</b> Web Speech API mr-IN, Verna AI Chatbot, Limitations &amp; Scope.<br/>
        <b>Slides:</b> 05, 13, 16, 21, 22
      </div>
    </div>
    <div class="team-card rushikesh">
      <div class="team-name">
        <span>४. ऋषिकेश मुळीक</span>
        <span class="team-badge-pill badge-rushikesh">६ Slides</span>
      </div>
      <div class="team-role">Backend, Database &amp; Sync Engine</div>
      <div class="team-contrib">
        <b>योगदान:</b> SQLite WAL, 50 Kirana Stock DB, Excel Export, Performance.<br/>
        <b>Slides:</b> 08, 09, 10, 11, 15, 17
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 01: COVER PAGE                                                  -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 01</span>
        VernaLedger.AI Merchant Pro v7.5 (Cover Page)
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 1/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Title:</b> VernaLedger.AI Merchant Pro v7.5 • <b>Badge:</b> B.Tech Artificial Intelligence &amp; Data Science • Major Project Final Defense<br/>
          <b>Subtitle:</b> Next-Gen Vernacular Retail Point of Sale &amp; Financial Suite with Gemini 3.1 Flash Vision OCR, Continuous Marathi Voice Billing, 50-Item Kirana Inventory Engine &amp; SQLite ACID Ledger<br/>
          <b>Team Strip:</b> 1. Sanket Kirdat (4060), 2. Sakshi Bhagat (4054), 3. Vaishnavi Dhavale (4056), 4. Rushikesh Mulik (4004)<br/>
          <b>Guide:</b> Prof. Kaisar Atar sir • <b>HOD:</b> Dr. S. Y. Mulla mam • <b>Institute:</b> AGCE Satara (DBATU Lonere)
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Good morning respected guide <b>Prof. Kaisar Atar sir</b>, HOD <b>Dr. S. Y. Mulla mam</b>, and external examiners. I am Sanket Kirdat, leading our team. Today we present <b>VernaLedger.AI: Merchant Pro v7.5</b> — a next-generation AI-powered vernacular retail billing and bookkeeping suite for local kirana merchants."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          सुरुवात करताना अत्तार सर, मुल्ला मॅम आणि परीक्षकांना नमस्कार करा. स्वतःची व तिन्ही सहकाऱ्यांची ओळख करून द्या आणि सांगा: "हा प्रोजेक्ट स्थानिक किराणा दुकानदारांसाठी बनवलेली आधुनिक AI बिलिंग प्रणाली आहे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What is the main problem your project solves?<br/>
          <b>Ans:</b> It allows rural kirana merchants to make bills using Marathi voice or camera photos, without English or computer training.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "Let us now look at the overview of VernaLedger suite on Slide 2."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 02: INTRODUCTION: VERNLEDGER.AI SUITE                           -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 02</span>
        Introduction: VernaLedger.AI Suite
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 2/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4 On-Screen Feature Cards:</b><br/>
          <span class="pill-item">🏪 What is VernaLedger.AI?</span> Offline-first, vernacular POS &amp; bookkeeping suite for 63M+ Indian MSMEs.<br/>
          <span class="pill-item">🗣️ Vernacular First Design</span> Regional voice recognition and UI rendering in authentic Marathi &amp; Hindi.<br/>
          <span class="pill-item">📸 Multimodal OCR Vision</span> Converts messy handwritten receipts into verified digital line items in sub-2 seconds.<br/>
          <span class="pill-item">💾 ACID Ledger Persistence</span> SQLite 3 WAL mode with zero data loss and native offline speed.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 2, you see the four core pillars of VernaLedger.AI. First, it is designed for 63 million Indian MSMEs. Second, it is <b>vernacular-first</b>, supporting native Marathi speech. Third, it reads handwritten receipts using multimodal AI. And fourth, it stores all bills safely in an ACID-compliant local database."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          स्लाईडवरील चारही चौकोन दाखवून सांगा: "भारतातील ६.३ कोटी लहान दुकानदारांसाठी ही पहिली मराठी-प्रथम बिलिंग प्रणाली आहे; यात कॅमेरा OCR, व्हॉइस बिलिंग आणि सुरक्षित डेटाबेस आहे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Why is it called 'Vernacular-first'?<br/>
          <b>Ans:</b> Because the UI, voice commands, bills, and WhatsApp reminders work directly in local Marathi and Hindi languages.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Sakshi:</b> "Sakshi Bhagat will now present the problem statement on Slide 3."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 03: PROBLEM STATEMENT                                           -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 03</span>
        Problem Statement: Ground Realities of Kirana Stores
      </div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend &amp; UI) • Slide 1/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4 On-Screen Problem Cards:</b><br/>
          <span class="pill-item">📓 1. Paper Ledger Vulnerability</span> Over 85% of retailers use paper notebooks ('बही-खाते') prone to water damage, fire, and page tearing.<br/>
          <span class="pill-item">⏳ 2. Severe Bad Debt Delinquency</span> Unrecorded informal credit ('उधारी') freezes working capital; merchants lack polite automated reminders.<br/>
          <span class="pill-item">🚫 3. Complex Enterprise POS Software</span> Tally and Vyapar are expensive, desktop-bound, and English-only with high complexity.<br/>
          <span class="pill-item">🔍 4. No Visual Audit Trail</span> Verbal agreements cause disputes over payment dates and exact balances.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Thank you Sanket. Respected examiners, Slide 3 highlights the four major problems kirana stores face today: Over 85% still use paper khata books that get torn or lost. Unrecorded credit causes bad debts. Existing software like Tally is in English and very complex. And there is no digital proof when customers dispute balances."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          दुकानदारांच्या ४ अडचणी सांगा: कागदी वही भिजून किंवा फाटून हिशोब हरवतो, लोकांकडे उधारी अडकून राहते, टॅली सारखे ॲप्स इंग्रजीत आणि चालवायला अवघड असतात, आणि उधारीवरून वाद होतात.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How big is the unrecorded credit problem?<br/>
          <b>Ans:</b> Over 60% of rural kirana transactions are on credit ('उधारी'), leading to severe working capital shortages.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "On Slide 4, I will explain the motivation and purpose behind VernaLedger."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 04: MOTIVATION & PURPOSE                                        -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 04</span>
        Motivation &amp; Purpose: Digital India for Bharat
      </div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend &amp; UI) • Slide 2/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4 On-Screen Purpose Cards:</b><br/>
          <span class="pill-item">🇮🇳 Digital India for Bharat</span> Bringing enterprise AI analytics to unorganized grassroots kirana stores.<br/>
          <span class="pill-item">⚡ Eliminating Manual Burden</span> Reducing bill entry time from 2 minutes per paper bill to under 2 seconds (60x faster).<br/>
          <span class="pill-item">📈 Formalizing Rural Credit</span> Transforming informal notebook scribbles into verifiable digital ledger history.<br/>
          <span class="pill-item">🌉 Bridging The Digital Divide</span> Voice-first Marathi interface requires zero training for elder shopkeepers.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Our motivation on Slide 4 is clear: We want to empower local Bharat merchants under Digital India. By replacing slow manual bill entry with sub-2-second AI scanning, we save 60 times the merchant's time. We formalize rural credit so shopkeepers can recover money faster with polite WhatsApp reminders."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          आपला हेतू स्पष्ट करा: "डिजिटल इंडिया' अंतर्गत ग्रामीण दुकानदारांना AI देणे, बिलाचा वेळ २ मिनिटांवरून २ सेकंदांवर आणणे, आणि उधारीचे डिजिटल पुरावे तयार करणे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How does your app save time?<br/>
          <b>Ans:</b> Taking a photo of a receipt or speaking the items takes only 2 seconds, compared to 2-3 minutes of manual ledger writing.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi Dhavale will now present the Gap Analysis on Slide 5."
        </div>
      </div>
    </div>
  </div>

  

  <!-- ===================================================================== -->
  <!-- SLIDE 05: GAP ANALYSIS & BENCHMARKS                                   -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 05</span>
        Gap Analysis &amp; Competitive Benchmarks
      </div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing &amp; AI) • Slide 1/5</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>On-Screen Comparison Table (5 Features Across 5 Platforms):</b><br/>
          • <b>Marathi/Hindi Voice Billing:</b> Khatabook ❌, OkCredit ❌, Vyapar ❌, Tally ❌, <b>VernaLedger: ✔ Native Voice NLP</b><br/>
          • <b>Multimodal AI OCR Receipt Parsing:</b> Khatabook ❌, OkCredit ❌, Vyapar ❌, Tally ❌, <b>VernaLedger: ✔ Gemini Flash (&lt;2s)</b><br/>
          • <b>50-Item Kirana Auto Stock Deduction:</b> Khatabook ❌, OkCredit ❌, Vyapar (Manual), Tally (Complex), <b>VernaLedger: ✔ Auto-Deduct</b><br/>
          • <b>Context-Aware SQL RAG AI Studio:</b> Khatabook ❌, OkCredit ❌, Vyapar ❌, Tally ❌, <b>VernaLedger: ✔ Gemini Assistant</b>
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Thank you Sakshi. On Slide 5, we compare VernaLedger with Khatabook, OkCredit, Vyapar, and TallyPrime. Existing apps require manual English typing and lack paper bill scanning. VernaLedger.AI is the only system offering native Marathi voice billing, multimodal OCR scanning, 50 pre-loaded kirana items with auto-deduction, and a built-in AI assistant."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          तक्ता दाखवून सांगा: "खाताबुक किंवा व्यापार ॲपमध्ये मराठी व्हॉइस बिलिंग नाही, कागदी पावती स्कॅनर नाही आणि ५० किराणा वस्तूंचा ऑटो-साठा कपात नाही; आपल्या सिस्टीममध्ये हे सर्व एकाच मोफत ॲपमध्ये उपलब्ध आहे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Why don't existing apps have Marathi OCR?<br/>
          <b>Ans:</b> Traditional OCR only works on typed English text; we used Google Gemini Multimodal Vision which understands handwritten regional Devanagari.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Sanket:</b> "Sanket will now present our project objectives on Slide 6."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 06: PROJECT OBJECTIVES                                          -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 06</span>
        Project Objectives: 4 Core Engineering Goals
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 3/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4 On-Screen Objective Cards:</b><br/>
          <span class="pill-item">🎯 1. Sub-2s Vision Token Extraction</span> Multimodal pipeline reading handwritten receipts (vendor, line items, prices) in under 2 seconds.<br/>
          <span class="pill-item">🎙️ 2. Regional Marathi/Hindi Voice POS</span> Hands-free audio billing converting Devanagari speech directly into structured line items.<br/>
          <span class="pill-item">💳 3. Intelligent Khata &amp; WhatsApp Links</span> Automated customer debt ledger with color-coded aging and 1-click WhatsApp payment links.<br/>
          <span class="pill-item">🤖 4. SQL-Grounded RAG Business Studio</span> AI assistant answering store revenue, stock, and credit queries with 100% verified DB truth.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 6, we defined four measurable engineering objectives: First, extract items from paper receipts in under 2 seconds. Second, enable hands-free Marathi voice billing. Third, track customer udhar with 1-click WhatsApp payment reminders. And fourth, build a zero-hallucination AI assistant connected directly to real store data."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          चारही उद्दिष्टे सांगा: "२ सेकंदात पावती स्कॅन करणे, मराठीत बोलून बिल तयार करणे, ग्राहकांना व्हॉट्सॲपवर उधारी आठवण पाठवणे, आणि दुकानाच्या खऱ्या डेटावर चालणारा AI असिस्टंट तयार करणे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What do you mean by 'zero hallucination'?<br/>
          <b>Ans:</b> The AI is strictly fed live numbers from our SQLite database, so it never invents fake sales or inventory quantities.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "Slide 7 shows our proposed end-to-end system pipeline."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 07: PROPOSED SYSTEM PIPELINE                                    -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 07</span>
        Proposed System Pipeline: End-to-End Architecture
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 4/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4-Stage Pipeline Cards:</b><br/>
          <span class="pill-item">🧑‍💼 1. Merchant Ingestion</span> Live camera receipt capture, Marathi voice speech prompt, or fast manual billing.<br/>
          <span class="pill-item">🧠 2. AI Intelligence</span> Gemini Flash Vision &amp; NLP normalizes raw input into strictly validated JSON schema.<br/>
          <span class="pill-item">💾 3. ACID Commit</span> Atomic transactional commits to SQLite WAL, updating khata balance and deducting 50 kirana stock.<br/>
          <span class="pill-item">🖨️ 4. Multi-Channel Output</span> Thermal POS receipt preview, dynamic UPI QR code, and pre-filled WhatsApp recovery link.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Slide 7 illustrates our 4-stage pipeline: Stage 1 takes input via camera, voice, or manual entry. Stage 2 parses this raw data using Gemini AI into structured JSON. Stage 3 saves the bill to our local SQLite database and automatically deducts stock. Stage 4 produces a thermal bill, dynamic UPI QR, and WhatsApp reminder link."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          पायपलाईन दाखवून सांगा: "पायरी १: इनपुट (कॅमेरा/आवाज), पायरी २: AI द्वारे विश्लेषण, पायरी ३: डेटाबेसमध्ये सेव्ह व साठा कपात, आणि पायरी ४: थर्मल बिल, QR कोड व व्हॉट्सॲप मेसेज."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What if camera photo is taken in bad light?<br/>
          <b>Ans:</b> We run a PIL Lanczos image enhancement pass that boosts sharpness by 20% and contrast by 15% before sending to Gemini.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Rushikesh:</b> "Rushikesh Mulik will now present our technology stack on Slide 8."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 08: TECHNOLOGIES & TOOLS                                        -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 08</span>
        Technologies &amp; Tools: Modern Engineering Stack
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 1/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>3 Core Tech Stacks On-Screen:</b><br/>
          <span class="pill-item">⚡ Frontend &amp; SPA</span> FastAPI &amp; Uvicorn backend • Pure JavaScript (ES6+) responsive SPA • Web Speech API • PWA Service Worker.<br/>
          <span class="pill-item">🤖 AI &amp; Audio</span> Google Gemini 3.5 Flash Lite &amp; 2.5 Flash Vision OCR • Edge-TTS Regional Audio • PIL Image Enhancer.<br/>
          <span class="pill-item">💽 Persistence &amp; Export</span> SQLite 3 with Write-Ahead Logging (WAL) • Dexie.js IndexedDB local-first cache • XlsxWriter Excel engine.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Thank you Sanket. Respected examiners, Slide 8 outlines our engineering stack: On the frontend, we built a lightweight vanilla JavaScript SPA with PWA support. On the backend, we use FastAPI with Google Gemini Multimodal AI. For data storage, we use high-speed SQLite 3 in WAL mode, paired with XlsxWriter for professional Excel reports."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          तंत्रज्ञान समजावून सांगा: "फ्रंटएंडसाठी हलकेफुलके जावास्क्रिप्ट PWA, बॅकएंडसाठी वेगवान FastAPI आणि गुगल जेमिनी AI, आणि डेटा सुरक्षित राहण्यासाठी जलद SQLite डेटाबेस व Excel लायब्ररी वापरली आहे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Why choose SQLite over MongoDB?<br/>
          <b>Ans:</b> SQLite requires zero server setup, runs natively on local devices, has ACID transactions, and responds in under 2 milliseconds.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "Slide 9 explains our modular 3-tier system architecture."
        </div>
      </div>
    </div>
  </div>

  

  <!-- ===================================================================== -->
  <!-- SLIDE 09: SYSTEM ARCHITECTURE                                         -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 09</span>
        System Architecture: Modular 3-Tier Design
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 2/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>3-Tier Architecture Diagram &amp; Flow:</b><br/>
          • <b>Presentation Tier:</b> Responsive Web SPA (HTML5/CSS3), Cyberpunk &amp; Kirana Light Mode, Web Speech API, Service Worker PWA.<br/>
          • <b>Application &amp; AI Tier:</b> FastAPI Universal ASGI gateway, Gemini 2.5 Flash Multimodal OCR, Vernacular NLP Engine, SQL RAG.<br/>
          • <b>Database Tier:</b> Hybrid Local-First engine (Dexie IndexedDB) paired with SQLite 3 ACID WAL database (ledger.db).
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 9, you see our 3-tier architecture: Tier 1 is the client layer running in the merchant's browser with voice and camera support. Tier 2 is the FastAPI backend handling Gemini AI OCR, speech transcription, and business logic. Tier 3 is our ACID ledger database ensuring that offline bills sync reliably without data loss."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          आर्किटेक्चर दाखवून सांगा: "पहिली पायरी: दुकानदाराच्या मोबाईल/लॅपटॉपचा ब्राऊझर, दुसरी पायरी: AI आणि प्रक्रिया करणारा पायथन सर्व्हर, आणि तिसरी पायरी: बिलांचा कायमस्वरूपी डेटाबेस."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What is the benefit of a 3-tier architecture?<br/>
          <b>Ans:</b> Clean separation of concerns: UI updates do not disturb the database, and AI models can be upgraded without changing the frontend.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "Slide 10 details the execution workflow from input to receipt."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 10: WORKING FLOW & EXECUTION PIPELINE                           -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 10</span>
        Working Flow &amp; Execution Pipeline: 4 Steps
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 3/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4-Step Detailed Execution Flow:</b><br/>
          • <b>Step 1: Input Ingestion:</b> Shopkeeper captures a paper receipt via camera, uploads an image, or speaks transaction details naturally.<br/>
          • <b>Step 2: AI Parsing:</b> Gemini Flash processes handwritten Devanagari text, extracts items, and validates math (quantity × rate = total).<br/>
          • <b>Step 3: Database Commit:</b> SQLite commits data to ledger.db in &lt;2ms, updates customer balance, and auto-deducts 50 kirana items.<br/>
          • <b>Step 4: Output Generation:</b> Generates formatted thermal POS receipt with dynamic UPI QR and 1-click WhatsApp reminder.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Slide 10 shows the complete working flow in 4 simple steps: Step 1: The merchant speaks or takes a photo. Step 2: Gemini AI parses the items and checks the math. Step 3: SQLite writes the bill and auto-deducts stock in less than 2 milliseconds. Step 4: The bill is printed, and a WhatsApp reminder link is created."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          काम करण्याची पद्धत सांगा: "दुकानदाराने फोटो काढला किंवा तोंडातून बोलला की AI पावती वाचते, गणिताची खात्री करते, दुकानातील साठ्यामधून माल वजा करते, आणि लगेच पक्के बिल तयार होते."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What happens if stock quantity becomes zero?<br/>
          <b>Ans:</b> Stock never goes below zero due to `MAX(0, stock - billed)`. A red 'Low Stock Alert' badge immediately appears on the screen.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "Slide 11 presents our performance benchmarks."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 11: PERFORMANCE ANALYSIS & BENCHMARKS                           -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 11</span>
        Performance Analysis &amp; Speed Benchmarks
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 4/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4 Benchmarked Performance Metric Cards:</b><br/>
          <span class="pill-item">&lt; 1.5s Latency</span> Sub-1.5s Gemini 3.5 Flash Lite multimodal vision OCR with client-side canvas compression.<br/>
          <span class="pill-item">96.8% Accuracy</span> High-precision token extraction across Marathi and Hindi handwritten receipts.<br/>
          <span class="pill-item">&lt; 2ms WAL Write</span> Ultra-low commit latency with SQLite 3 Write-Ahead Logging preventing lockups.<br/>
          <span class="pill-item">&lt; 1.2 MB Bundle</span> Lightweight Progressive Web App with zero installation friction on budget smartphones.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 11, we verified system performance: OCR takes under 1.5 seconds. Marathi speech accuracy reached 96.8%. SQLite database commits take under 2 milliseconds. And the entire application is under 1.2 megabytes, allowing it to run smoothly on budget Android phones."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          आकडेवारी ठामपणे सांगा: "पावती स्कॅन १.५ सेकंदात होते, मराठी बोलण्याची अचूकता ९६.८% आहे, डेटाबेस नोंद अवघ्या २ मिलिसेकंदात होते, आणि ॲपची साईझ १.२ एमबी इतकी हलकी आहे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How did you measure 96.8% voice accuracy?<br/>
          <b>Ans:</b> We tested 150 regional Marathi voice prompts across kirana grocery items and compared recognized tokens with spoken words.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Sanket:</b> "Sanket will now demonstrate Result 1: Smart Bill Scanner on Slide 12."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 12: RESULT 1: SMART MULTIMODAL SCANNER & POS                    -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 12</span>
        Result 1: Smart Multimodal Scanner &amp; POS
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Capabilities On-Screen:</b><br/>
          • Live camera capture of paper receipts with instant canvas preview and Lanczos image sharpening.<br/>
          • Google Gemini reads Marathi and English handwriting, extracting items, quantities, and rates.<br/>
          • Populates an editable on-screen table where the merchant can adjust quantities or prices before saving.<br/>
          • Clicking 'Save' registers the bill, updates customer khata, and deducts sold items from the 50 inventory items.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Respected examiners, Slide 12 showcases Result 1: Our Smart Bill Scanner. When the merchant captures a photo of a handwritten paper receipt, Gemini AI reads all item names, weights, and rates in under 1.5 seconds. The shopkeeper can edit any row on screen, and upon saving, stock is deducted automatically."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          स्क्रीन दाखवून सांगा: "कागदी पावतीचा फोटो काढताच स्क्रीनवर सुंदर टेबल तयार होते. दुकानदाराला बदल करायचा असल्यास करू शकतो, आणि 'सेव्ह' दाबताच दुकानातील ५० साठ्यामधून तेवढा माल आपोआप कमी होतो."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Can the merchant edit items before saving?<br/>
          <b>Ans:</b> Yes, every detected row has editable input fields for item name, quantity, and rate before final confirmation.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi will now demonstrate our voice billing engine on Slide 13."
        </div>
      </div>
    </div>
  </div>

  

  <!-- ===================================================================== -->
  <!-- SLIDE 13: RESULT 2: VERNACULAR VOICE BILLING ENGINE                   -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 13</span>
        Result 2: Vernacular Voice Billing Engine
      </div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing &amp; AI) • Slide 2/5</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Audio Features On-Screen:</b><br/>
          • Pulsing microphone button with live audio waveform animation using Web Speech API (mr-IN).<br/>
          • Natural Devanagari speech recognition supporting colloquial Marathi (e.g., '२ किलो साखर, १ लिटर तेल').<br/>
          • Automatic quantity and unit extraction (kg, ltr, packet, nos) directly mapping to the billing cart.<br/>
          • Handles voice credit commands (e.g., 'रमेश पाटील ५०० रुपये उधारी') recording directly to Khata ledger.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Thank you Sanket. Slide 13 presents Result 2: Vernacular Voice Billing. The shopkeeper simply taps the microphone and speaks naturally in Marathi, like '२ किलो साखर, १ लिटर शेंगदाणा तेल'. Our system extracts the item and quantity, adds them to the bill, and computes the grand total automatically."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          माइक दाखवून सांगा: "दुकानदाराला टाईप करायची गरज नाही; त्याने फक्त '२ किलो साखर, १ लिटर तेल' असे मराठीत बोलताच स्क्रीनवर आपोआप बिल तयार होते आणि उधारीही आवाजाने नोंदवता येते."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Which API powers the voice recognition?<br/>
          <b>Ans:</b> We use the browser's native Web Speech API configured for the `mr-IN` (Indian Marathi) Devanagari locale.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Sakshi:</b> "Sakshi will now present Customer Khata and Udhar Ledger on Slide 14."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 14: RESULT 3: CUSTOMER KHATA & UDHAR LEDGER                     -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 14</span>
        Result 3: Customer Khata &amp; Udhar Ledger
      </div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend &amp; UI) • Slide 3/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Credit Tracking Features On-Screen:</b><br/>
          • Comprehensive customer credit tracker with running balances and individual customer account cards.<br/>
          • Clear distinction between 'उधारी दिली' (Credit Given) and 'जमा मिळाले' (Payment Received).<br/>
          • Color-coded delinquency indicators: Green for paid balances, Red warning for overdue credit.<br/>
          • 1-Click WhatsApp payment reminder button generating pre-filled polite Marathi messages with UPI payment links.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 14, Result 3 shows our Customer Khata Book. It tracks every customer's credit and payment history. Overdue balances are highlighted with red alert badges. With a single click, the merchant can send a polite WhatsApp reminder with their shop's UPI QR link, ensuring faster debt recovery."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          खाता स्क्रीन दाखवून सांगा: "कोणाकडे किती उधारी बाकी आहे हे लाल रंगात दिसते. एका क्लिकवर ग्राहकाला व्हॉट्सॲपवर नम्र मेसेज आणि दुकानाचा UPI QR कोड जातो, ज्यामुळे उधारीचे पैसे वेळेवर वसूल होतात."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Does the WhatsApp reminder cost money?<br/>
          <b>Ans:</b> No, it uses WhatsApp deep-linking via browser URL (`wa.me/`), making it 100% free with zero API charges.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Rushikesh:</b> "Rushikesh will now showcase 50 Kirana Inventory Items on Slide 15."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 15: RESULT 4: STORE OPERATIONS & 50 KIRANA ITEMS                -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 15</span>
        Result 4: Store Operations &amp; 50 Kirana Inventory Items
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Inventory Capabilities On-Screen:</b><br/>
          • 50 pre-loaded authentic Indian kirana items: wheat, rice, dals, sugar, gul, rawa, oils, ghee, tea, spices, soaps.<br/>
          • Real-time search bar by item name or category, with metric unit conversion (e.g., 500 gm = 0.5 kg).<br/>
          • Automatic stock deduction: Scanning a bill or voice billing auto-deducts sold items (`MAX(0, stock - billed)`).<br/>
          • Red '🚨 कमी साठा' (Low Stock) alert badge when items drop below threshold, plus 1-click 'Reset Defaults' button.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Slide 15 presents Result 4: Store Operations with 50 authentic pre-loaded kirana items. We have grains, dals, oils, spices, and soaps. Whenever a bill is saved, our backend matches the item name and automatically deducts the quantity from stock. If stock drops below threshold, a red 'Low Stock' badge warns the merchant."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          साठा तक्ता दाखवून सांगा: "दुकानातील ५० मूळ किराणा वस्तू आधीच भरलेल्या आहेत. बिल सेव्ह होताच गोदामातील साठा आपोआप कमी होतो, आणि माल संपत आला की लाल अलर्ट मिळतो. १-क्लिकमध्ये साठा पूर्ववत करता येतो."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How does it match spoken item names to database?<br/>
          <b>Ans:</b> Our backend normalizes Marathi and English names, performing token-based fuzzy matching against inventory items.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi will now demonstrate our Verna AI Assistant on Slide 16."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 16: RESULT 5: VERNA AI MULTILINGUAL VOICE ASSISTANT             -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 16</span>
        Result 5: Verna AI Multilingual Voice Assistant
      </div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing &amp; AI) • Slide 3/5</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; AI Assistant Features On-Screen:</b><br/>
          • Official Google Gemini app design with sleek pulsing microphone button and live listening status.<br/>
          • Real-time word-by-word streaming answers via `sendMessageStream` with zero delay.<br/>
          • Multilingual script persistence: Automatically detects Marathi Devanagari, Roman Marathi, Hindi, or English.<br/>
          • Live SQLite RAG context: Directly queries today's sales, pending credit, 50 stock items, and expenses with 100% accuracy.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 16, Result 5 is our Verna AI Assistant, styled after Google Gemini. The merchant can type or tap the microphone to ask questions like 'आजची विक्री किती आहे?' or 'कोणत्या वस्तूंचा साठा कमी आहे?'. The assistant streams answers word-by-word, answering accurately from verified database records."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          AI असिस्टंट दाखवून सांगा: "गुगल जेमिनीसारखा AI असिस्टंट: बोलताना माईक पल्स होतो, शब्द न् शब्द समोर उमटतात, आणि मराठीत विचारल्यास मराठीतच उत्तर मिळते. दुकानातील विक्री, उधारी व साठ्याची सर्व खरी उत्तरे मिळतात."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Does the chatbot require voice output?<br/>
          <b>Ans:</b> No, text streaming is cleaner and faster in noisy kirana shops, though voice input is fully supported.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Rushikesh:</b> "Rushikesh will now show our digital ledger and Excel export on Slide 17."
        </div>
      </div>
    </div>
  </div>

  

  <!-- ===================================================================== -->
  <!-- SLIDE 17: RESULT 6: DIGITAL LEDGER & EXCEL EXPORT                     -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 17</span>
        Result 6: Digital Ledger &amp; Excel Export Engine
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 6/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Ledger Capabilities On-Screen:</b><br/>
          • Searchable historical transaction ledger with dynamic search by Bill ID (#VL-XX), customer, or date.<br/>
          • Dedicated emerald green 'Excel Export' button generating styled OpenXML `.xlsx` spreadsheets in 1 click.<br/>
          • Powered by Python's XlsxWriter with auto-fitted columns and UTF-8 Devanagari text support.<br/>
          • Thermal POS reprint preview and controlled deletion workflow maintaining database referential integrity.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Slide 17 showcases Result 6: Digital Ledger and Excel Export. All historical bills are listed with dynamic search. Clicking the green 'Excel Export' button instantly generates a beautifully formatted `.xlsx` spreadsheet using Python's XlsxWriter library, ready for the merchant's accountant or CA."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          लेजर दाखवून सांगा: "सर्व बिलांचा इतिहास येथे सुरक्षित असतो. हिरवे 'Excel Export' बटण दाबताच संपूर्ण हिशोबाची एक्सेल फाईल डाऊनलोड होते, जी दुकानदार आपल्या सीए (CA) कडे ऑडिटसाठी देऊ शकतो."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Why use XlsxWriter instead of CSV?<br/>
          <b>Ans:</b> XlsxWriter creates styled Excel workbooks with column widths, currency formats, and bold headers without character corruption.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Sakshi:</b> "Sakshi will now present Kirana Light Mode on Slide 18."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 18: RESULT 7: HIGH-CONTRAST KIRANA LIGHT MODE                   -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 18</span>
        Result 7: High-Contrast Kirana Light Mode UI
      </div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend &amp; UI) • Slide 4/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Outdoor Theme Features On-Screen:</b><br/>
          • High-contrast, glare-resistant light theme engineered specifically for outdoor storefronts and sunlit counters.<br/>
          • Ultra-crisp dark slate typography on clean porcelain backgrounds guaranteeing readability for elder merchants.<br/>
          • Invoice preview mirrors traditional physical retail paper receipts, increasing customer trust and familiarity.<br/>
          • 1-Click theme toggle (`☀️ / 🌙`) with state persistence across browser sessions and device reboots.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 18, Result 7 presents our High-Contrast Kirana Light Mode. Small shops operate in bright sunlight where dark screens cause glare. Our light mode features crisp dark typography on a clean white background, designed like a physical paper receipt so elderly shopkeepers can read with zero eye strain."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          लाईट मोड दाखवून सांगा: "दुकान उन्हात किंवा प्रकाशात असताना काळी स्क्रीन दिसत नाही; म्हणून आम्ही १-क्लिक 'किराणा कम्फर्ट डे मोड' दिला आहे. कागदी पावतीसारखी स्वच्छ पांढरी स्क्रीन वयस्कर दुकानदारांनाही सहज वाचता येते."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How is theme state persisted?<br/>
          <b>Ans:</b> We store the merchant's theme choice in `localStorage`, so their preference remains saved even after closing the browser.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "Slide 19 demonstrates our mobile-first responsive PWA."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 19: RESULT 8: MOBILE-FIRST RESPONSIVE PWA                       -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 19</span>
        Result 8: Mobile-First Responsive PWA
      </div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend &amp; UI) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Mobile Screenshot &amp; PWA Capabilities On-Screen:</b><br/>
          • Ergonomic bottom navigation rail designed for 1-handed thumb reach on standard 6.5-inch Android smartphones.<br/>
          • Native camera hardware hook for instant receipt capture and built-in mobile microphone for voice billing.<br/>
          • Deep-links directly into the WhatsApp Android application without third-party API dependencies or recurring fees.<br/>
          • Web manifest and service worker caching allows 1-tap installation onto merchant home screen like a native APK.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Slide 19 highlights Result 8: Our Mobile-First Responsive PWA. Most shopkeepers do not own computers; they use budget Android smartphones. Our app features a bottom navigation rail for easy one-handed thumb reach, hooks into the mobile camera and mic, and can be installed on the home screen with one tap."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          मोबाईल स्क्रीन दाखवून सांगा: "किराणा दुकानदारांकडे कम्प्युटर नसतो; म्हणून हे ॲप मोबाईलवर अंगठ्याने सहज वापरता येईल असे बनवले आहे. मोबाईलच्या कॅमेरा, माइकशी जोडले जाते आणि प्लेस्टोअरशिवाय १-क्लिकमध्ये इन्स्टॉल होते."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What makes it a Progressive Web App (PWA)?<br/>
          <b>Ans:</b> It includes `manifest.webmanifest` and `sw.js` service worker, enabling home-screen installation and offline file caching.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "On Slide 20, I will present the strategic advantages and strengths of VernaLedger."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 20: ADVANTAGES & STRENGTHS                                      -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sakshi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 20</span>
        Advantages &amp; Strategic Strengths
      </div>
      <span class="speaker-badge spk-sakshi">👤 वक्ता: SAKSHI BHAGAT (Frontend &amp; UI) • Slide 6/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>3 Core Strategic Advantages On-Screen:</b><br/>
          <span class="pill-item">🇮🇳 True Vernacular Accessibility</span> Voice assistant with continuous speech typing (mr-IN) eliminates the English literacy barrier; zero training curve.<br/>
          <span class="pill-item">⚡ 60% Faster Debt Recovery</span> Direct WhatsApp payment reminders accelerate customer khata repayments and prevent awkward verbal confrontations.<br/>
          <span class="pill-item">🛡️ Enterprise-Grade Security</span> Local SQLite database ensures instant responsiveness, zero downtime, and complete merchant data privacy.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 20, our key advantages are: First, true vernacular accessibility — merchants speak in their mother tongue with zero training. Second, 60% faster credit recovery through automated WhatsApp reminders. And third, enterprise-grade security with an offline-first local database that guarantees complete merchant privacy."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          फायदे ठामपणे सांगा: "पहिली गोष्ट: मातृभाषेत असल्याने कोणत्याही ट्रेनिंगची गरज नाही. दुसरी: ६०% वेगाने उधारी जमा होते. तिसरी: डेटा स्वतःच्या डिव्हाइसवर सुरक्षित राहतो, खाजगी माहिती चोरीला जात नाही."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How does it achieve 60% faster debt recovery?<br/>
          <b>Ans:</b> Sending polite automated WhatsApp payment links prevents awkward verbal confrontations and speeds up customer repayments.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi Dhavale will now discuss system limitations on Slide 21."
        </div>
      </div>
    </div>
  </div>

  

  <!-- ===================================================================== -->
  <!-- SLIDE 21: SYSTEM LIMITATIONS                                          -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 21</span>
        System Limitations: Engineering Realism
      </div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing &amp; AI) • Slide 4/5</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>2 On-Screen Engineering Constraints:</b><br/>
          <span class="pill-item">🌐 1. AI Internet Dependency</span> While manual POS billing, 50-stock updates, and ledger work offline, multimodal Gemini Flash OCR requires cloud connectivity.<br/>
          <span class="pill-item">📸 2. Severe Image Distortion</span> Extremely crumpled, oil-stained, or faint thermal receipts with severe ink fading can occasionally require manual correction.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Thank you Sakshi. On Slide 21, as honest engineers, we acknowledge two real-world limitations: First, while offline billing and stock work without internet, Gemini Vision OCR needs active connectivity. Second, if a paper bill is extremely torn, oily, or faded, manual editing on screen may be required."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          मर्यादा प्रामाणिकपणे सांगा: "पहिली मर्यादा: स्थानिक बिलिंग इंटरनेटशिवाय चालते, पण कॅमेरा AI स्कॅनिंगसाठी इंटरनेट लागते. दुसरी मर्यादा: पावतीवर तेल सांडले असेल किंवा खूप चुरगळलेली असेल तर स्क्रीनवर थोडे बदल करावे लागतात."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What if the shop loses internet during the day?<br/>
          <b>Ans:</b> The shopkeeper can still perform manual POS billing, customer khata updates, and stock tracking offline without interruption.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover:</b> "On Slide 22, I will outline our roadmap for future enhancements."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 22: FUTURE ENHANCEMENTS                                         -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-vaishnavi">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 22</span>
        Future Enhancements: Scalability Roadmap
      </div>
      <span class="speaker-badge spk-vaishnavi">👤 वक्ता: VAISHNAVI DHAVALE (Voice Billing &amp; AI) • Slide 5/5</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>4 On-Screen Future Roadmap Cards:</b><br/>
          <span class="pill-item">📱 1. Native Android APK</span> Packaging with quantized on-device Edge-AI models for 100% offline OCR scanning.<br/>
          <span class="pill-item">💸 2. Dynamic UPI QR Soundbox</span> Generating transaction-specific UPI QR codes on invoices with audio payment confirmation soundbox.<br/>
          <span class="pill-item">☁️ 3. Multi-Device Sync</span> Encrypted peer-to-peer cloud replication for multi-counter billing across devices.<br/>
          <span class="pill-item">📊 4. Automated GST Filing</span> 1-Click ready-to-file GSTR-1 and GSTR-3B tax compliance summaries.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "On Slide 22, our future scope includes: Packaging as a native Android APK with quantized on-device Edge AI for offline OCR. Integrating a dynamic UPI Soundbox for audio payment alerts. Adding peer-to-peer multi-counter sync. And building one-click GST GSTR-1 filing."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          भविष्यातील योजना सांगा: "१. इंटरनेटशिवाय चालणारे ऑन-डिव्हाइस AI मॉडेल आणणे, २. पेटीएमसारखा व्हॉइस साऊंडबॉक्स जोडणे, ३. एकाच दुकानातील अनेक काऊंटर्स सिंक करणे, आणि ४. जीएसटी (GST) टॅक्स रिटर्न एका क्लिकवर तयार करणे."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How can you run AI models offline on a phone?<br/>
          <b>Ans:</b> By quantizing lightweight Vision Transformers (e.g., MobileNet or Gemma 2B INT4) to execute via ONNX Runtime directly on smartphone chips.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Sanket:</b> "Team leader Sanket Kirdat will now conclude our presentation on Slide 23."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 23: CONCLUSION & Q&A                                            -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 23</span>
        Conclusion &amp; Open Defense (Q&amp;A)
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 6/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Concluding Screen &amp; Executive Summary:</b><br/>
          • <b>Executive Summary:</b> VernaLedger.AI bridges the technological divide for India's 63M+ grassroots kirana merchants. Combining Gemini 3.1 Flash vision OCR, continuous Marathi voice billing, a 50-item kirana auto-deduction engine, Verna AI voice assistant, and SQLite ACID ledger.<br/>
          • <b>Thank You &amp; Acknowledgment:</b> Dept of AI &amp; DS • Arvind Gavali College of Engineering, Satara • DBATU Lonere.<br/>
          • <b>Special Thanks:</b> Guide Prof. Kaisar Atar sir &amp; HOD Dr. S. Y. Mulla mam. Open for questions!
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "To conclude on Slide 23: VernaLedger.AI brings cutting-edge artificial intelligence into the hands of local Bharat kirana stores. We sincerely express our heartfelt gratitude to our respected guide <b>Prof. Kaisar Atar sir</b>, our HOD <b>Dr. S. Y. Mulla mam</b>, and the entire AI &amp; DS faculty. The floor is now open for your valuable questions. Thank you!"
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          अंतिम समारोप करा: "वर्णा-लेजर AI मुळे लहान किराणा दुकानदारांचे जीवन सुलभ झाले आहे. अत्तार सर, मुल्ला मॅम आणि सर्व शिक्षकांचे मनःपूर्वक आभार! आता आम्ही सर्व ४ सदस्य परीक्षकांच्या प्रश्नांची उत्तरे देण्यास तयार आहोत."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> What was your team's greatest technical achievement?<br/>
          <b>Ans:</b> Integrating multimodal Gemini AI OCR and Marathi voice recognition with instant SQLite database synchronization in a lightweight PWA.
        </div>
        <div class="handover-mini">
          🏁 <b>Open Defense:</b> "All 4 members stand ready for Examiner Questions."
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- GOLDEN VIVA DEFENSE RULES                                             -->
  <!-- ===================================================================== -->
  <div style="background: #f8fafc; border: 1.5px solid #0284c7; border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 7.2pt; page-break-inside: avoid;">
    <div style="font-weight: 800; color: #0284c7; font-size: 8.2pt; margin-bottom: 2px;">
      🏆 अंतिम वर्षाच्या Viva डिफेन्ससाठी परीक्षकांसमोर ५ सुवर्ण नियम (Top 5 Golden Rules):
    </div>
    <div style="color: #334155; line-height: 1.35;">
      १. <b>स्क्रीनवर जे दिसतेय त्यावर बोट ठेवा (Point to the screen):</b> स्लाईडवर जे ४ मुद्दे, आकडे किंवा स्क्रीनशॉट दिसतात तेच सांगा; गोंधळ होणार नाही.<br/>
      २. <b>थेट आणि नेमके उत्तर द्या (Crisp &amp; Direct):</b> परीक्षकाने 'डेटाबेस कोणता?' विचारल्यास थेट सांगा: "SQLite 3 with Write-Ahead Logging (WAL)."<br/>
      ३. <b>स्वतःच्या भूमिकेवर ठाम राहा (Own your role):</b> संकेत AI वर बोलेल, साक्षी UI वर बोलेल, वैष्णवी व्हॉइस इंजिनवर बोलेल, आणि ऋषिकेश बॅकएंडवर बोलेल.<br/>
      ४. <b>तांत्रिक संज्ञा अचूक उच्चारा (Accurate Tech Terms):</b> Multimodal Vision, Gemini 3.1 Flash, Web Speech API mr-IN, SQLite ACID WAL, XlsxWriter.<br/>
      ५. <b>शांत, हसतमुख आणि आदरपूर्वक बोला (Calm &amp; Confident):</b> अत्तार सर आणि मुल्ला मॅम यांनी दिलेल्या मार्गदर्शनाचा अभिमानाने उल्लेख करा.
    </div>
  </div>

</body>
</html>
"""

def generate_pdf():
    temp_html = os.path.abspath("temp_presentation_script_render.html")

    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print("=" * 70)
    print("🚀 Generating Exact 23-Slide Presentation Script & Viva Defense Guide PDF...")
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

        page.pdf(
            path=OUTPUT_PDF,
            format="A4",
            print_background=True,
            margin={"top": "7mm", "bottom": "7mm", "left": "7mm", "right": "7mm"},
            display_header_footer=True,
            header_template='<div style="font-size: 6.8pt; color: #64748b; width: 100%; text-align: right; padding-right: 8mm; font-family: Segoe UI, sans-serif;">VernaLedger.AI Merchant Pro v7.5 • Guide: Prof. Kaisar Atar sir • HOD: Dr. S. Y. Mulla mam • AGCE Satara (DBATU Lonere)</div>',
            footer_template='<div style="font-size: 6.8pt; color: #64748b; width: 100%; display: flex; justify-content: space-between; padding: 0 8mm; font-family: Segoe UI, sans-serif;"><span>Arvind Gavali College of Engineering, Satara • B.Tech AI & DS (2026-2027)</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        )
        browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    # Sync to public/
    public_dir = os.path.abspath("public")
    if os.path.exists(public_dir):
        shutil.copy2(OUTPUT_PDF, os.path.join(public_dir, os.path.basename(OUTPUT_PDF)))
        print(f"✅ Synced PDF to public/ folder.")

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

"""
VernaLedger.AI: Merchant Pro v7.5
Presentation Script & Role-Wise Defense Guide Generator
Generates a comprehensive, professional, dual-language (Spoken English + Marathi Explanation)
PDF guide for the 4-member final year project presentation defense.
"""

import os
import sys
from playwright.sync_api import sync_playwright

OUTPUT_PDF = os.path.abspath("VernaLedger_AI_Presentation_Team_Script_and_Viva_Guide.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="utf-8">
<title>VernaLedger.AI - Presentation Script & Defense Guide</title>
<style>
  @page {
    size: A4;
    margin: 10mm 10mm 10mm 10mm;
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
    font-size: 9.5pt;
    line-height: 1.45;
  }

  .cover-banner {
    background: linear-gradient(135deg, #050b14 0%, #0d2859 60%, #0a1128 100%);
    color: #ffffff;
    padding: 22px 24px;
    border-radius: 12px;
    margin-bottom: 16px;
    border-left: 6px solid #00f2fe;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  }

  .college-badge {
    display: inline-block;
    background: rgba(0, 242, 254, 0.15);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.4);
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .cover-title {
    font-size: 20pt;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 4px;
    color: #ffffff;
  }

  .cover-title span {
    color: #00f2fe;
  }

  .cover-subtitle {
    font-size: 10.5pt;
    color: #94a3b8;
    margin-bottom: 12px;
    font-weight: 500;
  }

  .dossier-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    background: rgba(255, 255, 255, 0.06);
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 8pt;
  }

  .dossier-item strong {
    color: #38bdf8;
  }

  /* Member Summary Table */
  .section-title {
    font-size: 12.5pt;
    font-weight: 800;
    color: #0f172a;
    border-left: 4px solid #0284c7;
    padding-left: 8px;
    margin: 14px 0 8px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .table-roles {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;
    font-size: 8.5pt;
  }

  .table-roles th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 7px 10px;
    border: 1px solid #1e293b;
  }

  .table-roles td {
    padding: 6px 10px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }

  .table-roles tr:nth-child(even) td {
    background: #f8fafc;
  }

  .badge-role {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 7.5pt;
    color: #ffffff;
  }
  .role-sanket { background: #0284c7; }
  .role-sakshi { background: #d97706; }
  .role-vaishnavi { background: #7c3aed; }
  .role-rushikesh { background: #059669; }

  /* Flow Table */
  .flow-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 18px;
    font-size: 8pt;
  }
  .flow-table th {
    background: #1e293b;
    color: #38bdf8;
    font-weight: 700;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #334155;
  }
  .flow-table td {
    padding: 5px 8px;
    border: 1px solid #cbd5e1;
    vertical-align: middle;
  }
  .flow-table tr:nth-child(even) td {
    background: #f8fafc;
  }

  /* Slide Presentation Cards */
  .slide-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    margin-bottom: 14px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    page-break-inside: avoid;
    overflow: hidden;
  }

  .slide-card-header {
    background: #f1f5f9;
    padding: 8px 12px;
    border-bottom: 2px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .slide-card-header.sanket-header {
    border-left: 5px solid #0284c7;
    background: #f0f9ff;
  }
  .slide-card-header.sakshi-header {
    border-left: 5px solid #d97706;
    background: #fffbeb;
  }
  .slide-card-header.vaishnavi-header {
    border-left: 5px solid #7c3aed;
    background: #faf5ff;
  }
  .slide-card-header.rushikesh-header {
    border-left: 5px solid #059669;
    background: #f0fdf4;
  }

  .slide-num-title {
    font-weight: 800;
    font-size: 10pt;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .slide-pill {
    background: #0f172a;
    color: #ffffff;
    font-size: 7.5pt;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 12px;
  }

  .presenter-pill {
    font-size: 8pt;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
  }

  .slide-content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    padding: 10px 12px;
  }

  .script-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 10px;
  }

  .script-box.english-box {
    border-left: 3px solid #0284c7;
  }

  .script-box.marathi-box {
    border-left: 3px solid #10b981;
    background: #fafaf9;
  }

  .box-tag {
    font-size: 7.5pt;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .tag-en { color: #0369a1; }
  .tag-mr { color: #047857; }

  .spoken-text {
    font-size: 8.5pt;
    line-height: 1.45;
    color: #1e293b;
    font-style: italic;
  }

  .spoken-text strong {
    color: #0f172a;
    font-style: normal;
    font-weight: 700;
  }

  .marathi-text {
    font-size: 8.5pt;
    line-height: 1.5;
    color: #334155;
  }

  .marathi-text strong {
    color: #065f46;
    font-weight: 700;
  }

  .qa-box {
    grid-column: span 2;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 8pt;
    margin-top: 2px;
  }

  .qa-title {
    font-weight: 800;
    color: #c2410c;
    font-size: 8pt;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .qa-content {
    color: #7c2d12;
    line-height: 1.4;
  }

  .handover-banner {
    grid-column: span 2;
    background: #f1f5f9;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 8pt;
    font-weight: 600;
    color: #475569;
    border-left: 3px solid #64748b;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .handover-banner span.cue {
    color: #0f172a;
    font-style: italic;
  }

  .page-break {
    page-break-after: always;
  }

  .viva-tips-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 10px;
    font-size: 8.5pt;
  }

  .viva-tips-box h4 {
    color: #0f172a;
    font-size: 9.5pt;
    margin-bottom: 6px;
  }

  .viva-tips-box ul {
    padding-left: 18px;
    line-height: 1.5;
    color: #334155;
  }
</style>
</head>
<body>

  <!-- ==================== HEADER COVER ==================== -->
  <div class="cover-banner">
    <div class="college-badge">B.Tech AI & Data Science • Project Presentation Script</div>
    <div class="cover-title">VernaLedger.AI <span>Merchant Pro v7.5</span></div>
    <div class="cover-subtitle">Complete Spoken English Presentation Script & Marathi Translation Guide for 4 Team Members</div>
    
    <div class="dossier-grid">
      <div class="dossier-item"><strong>Institute:</strong> Arvind Gavali College of Engineering, Satara (AGCE)</div>
      <div class="dossier-item"><strong>Affiliation:</strong> Dr. Babasaheb Ambedkar Tech University, Lonere (DBATU)</div>
      <div class="dossier-item"><strong>Internal Guide:</strong> Mr. Kaisar Atar</div>
      <div class="dossier-item"><strong>Head of Department:</strong> Dr. S. Y. Mulla</div>
      <div class="dossier-item"><strong>Total Presentation Slides:</strong> 23 Slides (Full Deck in VernaLedger_Presentation.html)</div>
      <div class="dossier-item"><strong>Defense Date / Target:</strong> Academic Year 2026-2027 Final Evaluation</div>
    </div>
  </div>

  <!-- ==================== TEAM DIVISION SUMMARY ==================== -->
  <div class="section-title">
    <span>1. टीम सदस्यांचे वाटप (Team Roles & Slide Allocation)</span>
    <span style="font-size: 8pt; font-weight: normal; color: #64748b;">4 Members • 23 Slides</span>
  </div>

  <table class="table-roles">
    <thead>
      <tr>
        <th style="width: 24%;">विद्यार्थ्याचे नाव (Student)</th>
        <th style="width: 14%;">रोल / PRN</th>
        <th style="width: 24%;">प्रकल्पातील तांत्रिक भूमिका (Role)</th>
        <th style="width: 20%;">वाटून दिलेल्या स्लाईड्स (Slides)</th>
        <th style="width: 18%;">एकूण स्लाईड्स (Count)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Sanket Kirdat</strong><br><span style="font-size: 7.5pt; color: #0284c7;">(Team Leader)</span></td>
        <td>Roll: 4060<br><span style="font-size: 7pt; color: #64748b;">24065451263508</span></td>
        <td><span class="badge-role role-sanket">Project Lead & AI Vision</span><br><span style="font-size: 7pt; color: #475569;">Introduction, Objectives, Multimodal OCR, Conclusion</span></td>
        <td><strong>Slides: 01, 02, 06, 07, 12, 23</strong></td>
        <td><strong>6 Slides</strong><br><span style="font-size: 7pt; color: #059669;">Opening & Close</span></td>
      </tr>
      <tr>
        <td><strong>Sakshi Bhagat</strong></td>
        <td>Roll: 4054<br><span style="font-size: 7pt; color: #64748b;">24065451263502</span></td>
        <td><span class="badge-role role-sakshi">Frontend & UI/UX Design</span><br><span style="font-size: 7pt; color: #475569;">Problems, Motivation, Customer Khata, Light Mode, PWA</span></td>
        <td><strong>Slides: 03, 04, 14, 18, 19, 20</strong></td>
        <td><strong>6 Slides</strong><br><span style="font-size: 7pt; color: #059669;">UI / UX / Khata</span></td>
      </tr>
      <tr>
        <td><strong>Vaishnavi Dhavale</strong></td>
        <td>Roll: 4056<br><span style="font-size: 7pt; color: #64748b;">24065451263504</span></td>
        <td><span class="badge-role role-vaishnavi">Voice Billing & AI Assistant</span><br><span style="font-size: 7pt; color: #475569;">Gap Analysis, Continuous Speech ASR, Verna AI Assistant</span></td>
        <td><strong>Slides: 05, 13, 16, 21, 22</strong></td>
        <td><strong>5 Slides</strong><br><span style="font-size: 7pt; color: #059669;">Voice & Conversational AI</span></td>
      </tr>
      <tr>
        <td><strong>Rushikesh Mulik</strong></td>
        <td>Roll: 4004<br><span style="font-size: 7pt; color: #64748b;">23065451263005</span></td>
        <td><span class="badge-role role-rushikesh">Backend & Database Engine</span><br><span style="font-size: 7pt; color: #475569;">Tech Stack, 3-Tier Arch, Benchmarks, 50-Item Inventory, Excel</span></td>
        <td><strong>Slides: 08, 09, 10, 11, 15, 17</strong></td>
        <td><strong>6 Slides</strong><br><span style="font-size: 7pt; color: #059669;">Core Backend & Data</span></td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== FLOW SEQUENCE TIMELINE ==================== -->
  <div class="section-title">
    <span>2. सादरीकरणाचा नैसर्गिक क्रम (Chronological Presentation Handover Flow)</span>
  </div>

  <table class="flow-table">
    <thead>
      <tr>
        <th style="width: 8%;">टप्पा</th>
        <th style="width: 22%;">सादरकर्ता (Presenter)</th>
        <th style="width: 25%;">स्लाईड क्रमांक व विषय</th>
        <th style="width: 15%;">अंदाजे वेळ (Time)</th>
        <th style="width: 30%;">हँडओव्हर वाक्य (Next Speaker Handover Cue)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Stage 1</strong></td>
        <td><strong style="color: #0284c7;">Sanket Kirdat</strong></td>
        <td><strong>Slide 01 & 02:</strong> Cover Title & Introduction</td>
        <td>~1.5 मिनिटे</td>
        <td>"Now, I invite Sakshi to present the ground-level problems..."</td>
      </tr>
      <tr>
        <td><strong>Stage 2</strong></td>
        <td><strong style="color: #d97706;">Sakshi Bhagat</strong></td>
        <td><strong>Slide 03 & 04:</strong> Problem Statement & Motivation</td>
        <td>~1.5 मिनिटे</td>
        <td>"I now hand over to Vaishnavi to present the market gap analysis..."</td>
      </tr>
      <tr>
        <td><strong>Stage 3</strong></td>
        <td><strong style="color: #7c3aed;">Vaishnavi Dhavale</strong></td>
        <td><strong>Slide 05:</strong> Gap Analysis & Competitive Matrix</td>
        <td>~1.0 मिनिट</td>
        <td>"Now our project leader Sanket will explain the core objectives..."</td>
      </tr>
      <tr>
        <td><strong>Stage 4</strong></td>
        <td><strong style="color: #0284c7;">Sanket Kirdat</strong></td>
        <td><strong>Slide 06 & 07:</strong> Project Objectives & Proposed Pipeline</td>
        <td>~1.5 मिनिटे</td>
        <td>"I now invite Rushikesh to explain our engineering stack & architecture..."</td>
      </tr>
      <tr>
        <td><strong>Stage 5</strong></td>
        <td><strong style="color: #059669;">Rushikesh Mulik</strong></td>
        <td><strong>Slide 08, 09, 10, 11:</strong> Stack, Architecture, Flow & Benchmarks</td>
        <td>~3.0 मिनिटे</td>
        <td>"Let us now witness the live results; Sanket will show Result 1: Scanner..."</td>
      </tr>
      <tr>
        <td><strong>Stage 6</strong></td>
        <td><strong style="color: #0284c7;">Sanket Kirdat</strong></td>
        <td><strong>Slide 12:</strong> Result 1: Multimodal Vision Scanner & POS</td>
        <td>~1.0 मिनिट</td>
        <td>"Next, Vaishnavi will demonstrate Result 2: Voice Billing Engine..."</td>
      </tr>
      <tr>
        <td><strong>Stage 7</strong></td>
        <td><strong style="color: #7c3aed;">Vaishnavi Dhavale</strong></td>
        <td><strong>Slide 13:</strong> Result 2: Vernacular Voice Billing Engine</td>
        <td>~1.0 मिनिट</td>
        <td>"Sakshi will now present Result 3: Customer Khata & WhatsApp links..."</td>
      </tr>
      <tr>
        <td><strong>Stage 8</strong></td>
        <td><strong style="color: #d97706;">Sakshi Bhagat</strong></td>
        <td><strong>Slide 14:</strong> Result 3: Customer Khata & Udhar Ledger</td>
        <td>~1.0 मिनिट</td>
        <td>"Next, Rushikesh will explain Result 4: 50 Kirana Inventory Engine..."</td>
      </tr>
      <tr>
        <td><strong>Stage 9</strong></td>
        <td><strong style="color: #059669;">Rushikesh Mulik</strong></td>
        <td><strong>Slide 15:</strong> Result 4: Store Operations & 50 Kirana Items</td>
        <td>~1.0 मिनिट</td>
        <td>"Now Vaishnavi will showcase Result 5: Verna AI Gemini Assistant..."</td>
      </tr>
      <tr>
        <td><strong>Stage 10</strong></td>
        <td><strong style="color: #7c3aed;">Vaishnavi Dhavale</strong></td>
        <td><strong>Slide 16:</strong> Result 5: Verna AI Multilingual Voice Assistant</td>
        <td>~1.0 मिनिट</td>
        <td>"Rushikesh will now demonstrate Result 6: Digital Ledger & Excel Export..."</td>
      </tr>
      <tr>
        <td><strong>Stage 11</strong></td>
        <td><strong style="color: #059669;">Rushikesh Mulik</strong></td>
        <td><strong>Slide 17:</strong> Result 6: Digital Ledger & Excel Generator</td>
        <td>~1.0 मिनिट</td>
        <td>"Sakshi will now walk through Kirana Light Mode and PWA UI..."</td>
      </tr>
      <tr>
        <td><strong>Stage 12</strong></td>
        <td><strong style="color: #d97706;">Sakshi Bhagat</strong></td>
        <td><strong>Slide 18, 19, 20:</strong> Light Mode, Mobile PWA & Advantages</td>
        <td>~2.0 मिनिटे</td>
        <td>"I hand over to Vaishnavi for system limitations and future scope..."</td>
      </tr>
      <tr>
        <td><strong>Stage 13</strong></td>
        <td><strong style="color: #7c3aed;">Vaishnavi Dhavale</strong></td>
        <td><strong>Slide 21 & 22:</strong> Limitations & Future Enhancements</td>
        <td>~1.5 मिनिटे</td>
        <td>"Finally, our Team Leader Sanket will deliver the concluding remarks..."</td>
      </tr>
      <tr>
        <td><strong>Stage 14</strong></td>
        <td><strong style="color: #0284c7;">Sanket Kirdat</strong></td>
        <td><strong>Slide 23:</strong> Conclusion, Executive Summary & Open Defense</td>
        <td>~1.5 मिनिटे</td>
        <td>"We are now open for queries. Thank you respected examiners!"</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- ==================== DETAILED SLIDE-BY-SLIDE SCRIPTS ==================== -->
  <div class="section-title">
    <span>3. प्रत्येक स्लाईडचे सादरीकरण स्क्रिप्ट (Detailed Slide-by-Slide Scripts)</span>
    <span style="font-size: 8pt; font-weight: normal; color: #64748b;">English Spoken + Marathi Meaning + Viva Q&A</span>
  </div>

  <!-- ==================== SLIDE 01 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sanket-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 01</span>
        <span>Cover Page: VernaLedger.AI: Merchant Pro v7.5</span>
      </div>
      <span class="badge-role role-sanket presenter-pill">Presenter: Sanket Kirdat (Team Leader)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Respected Project Guide <strong>Prof. Kaisar Atar sir</strong>, Head of Department <strong>Dr. S. Y. Mulla sir</strong>, and respected External Examiners. A very warm good morning to everyone.<br><br>
          I am <strong>Sanket Kirdat</strong>, leading our final year project team consisting of Sakshi Bhagat, Vaishnavi Dhavale, and Rushikesh Mulik from the Department of Artificial Intelligence and Data Science at Arvind Gavali College of Engineering, Satara.<br><br>
          Today, we are honored to defend our major project: <strong>'VernaLedger.AI: Merchant Pro v7.5'</strong> — a Next-Gen Vernacular Retail Point of Sale and Financial Intelligence Suite tailored specifically for India's 63 million local kirana merchants."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>सुरुवात कशी करावी:</strong><br>
          "सर्वप्रथम मार्गदर्शक सर, विभागप्रमुख सर आणि परीक्षकांना आदरपूर्वक नमस्कार करा. आपले नाव, रोल नंबर आणि टीममधील सर्व सदस्यांची (साक्षी, वैष्णवी, ऋषिकेश) ओळख करून द्या.<br><br>
          आपल्या प्रकल्पाचे नाव <strong>'वर्णा-लेजर AI: मर्चंट प्रो व्हर्जन 7.5'</strong> आहे. हा भारतातील 6 कोटी 30 लाखांपेक्षा जास्त स्थानिक किराणा आणि सूक्ष्म व्यापाऱ्यांसाठी बनवलेला खास प्रादेशिक (मराठी) AI बिलिंग आणि फायनान्शियल प्लॅटफॉर्म आहे."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "What does 'Vernacular' in VernaLedger mean?"<br>
          <strong>A (उत्तर):</strong> "'Vernacular' means native regional languages. Local Indian shopkeepers struggle with English-only software; VernaLedger allows them to scan bills, speak in Marathi, and manage accounts in their mother tongue with zero English dependency."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 02:</span>
        <span class="cue">"Let us begin with an overview of what makes VernaLedger.AI uniquely impactful..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 02 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sanket-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 02</span>
        <span>Introduction: VernaLedger.AI Suite</span>
      </div>
      <span class="badge-role role-sanket presenter-pill">Presenter: Sanket Kirdat (Team Leader)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Moving to Slide 2: <strong>What exactly is VernaLedger.AI?</strong><br><br>
          VernaLedger.AI is an <strong>offline-first, vernacular-native Point of Sale (POS) and smart bookkeeping suite</strong> engineered to empower grassroots Indian retail.<br><br>
          Our platform unites three transformative technologies: First, <strong>Multimodal Vision OCR</strong> that digitizes crumpled Marathi paper bills in under 1.5 seconds. Second, <strong>Regional Marathi Voice Billing</strong> allowing shopkeepers to create bills simply by speaking during rush hours. Third, an <strong>ACID-compliant SQLite Ledger</strong> with 1-click WhatsApp payment reminders with dynamic UPI links and instant Microsoft Excel exports.<br><br>
          In short, we transform any low-cost smartphone or laptop into an enterprise-grade retail terminal."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>मुख्य मुद्दे काय आहेत:</strong><br>
          "1. हे एक <strong>ऑफलाइन-फर्स्ट</strong> सॉफ्टवेअर आहे जे इंटरनेट नसले तरी सुरळीत चालते.<br>
          2. यामध्ये <strong>3 मुख्य घटक</strong> आहेत: (अ) कागदी पावत्यांचे फोटो काढून 1.5 सेकंदात बिल बनवणारे व्हिजन OCR, (ब) दुकानात गर्दी असताना थेट मराठीत बोलून बिल बनवणारे व्हॉइस बिलिंग, (क) सुरक्षित SQLite डेटाबेस, ज्यातून ग्राहकांना व्हॉट्सॲपवर UPI पेमेंट लिंक पाठवता येते आणि एक्सेल शीट डाऊनलोड करता येते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Why not just use a traditional desktop POS like Tally or Marg?"<br>
          <strong>A (उत्तर):</strong> "Tally requires formal accounting training, English fluency, and expensive hardware. A kirana store owner cannot type ledger entries while weighing sugar; they need hands-free voice billing and instant camera receipt scanning."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Sakshi:</span>
        <span class="cue">"I now invite Sakshi Bhagat to present the ground reality and critical problems local merchants face daily."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 03 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sakshi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 03</span>
        <span>Problem Statement: Market Reality</span>
      </div>
      <span class="badge-role role-sakshi presenter-pill">Presenter: Sakshi Bhagat (Frontend & UI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Thank you Sanket. Respected examiners, on Slide 3, we highlight the <strong>critical operational pain points</strong> crippling India's grassroots kirana economy.<br><br>
          <strong>First is Paper Ledger Vulnerability:</strong> Over 85% of small retailers still record transactions in physical paper notebooks known as 'बही-खाते'. These books are highly vulnerable to water spills, tearing, page loss, and mathematical calculation errors.<br><br>
          <strong>Second is Severe Bad Debt Delinquency:</strong> Retailers extend 15 to 45 days of credit to neighborhood customers. Because of manual tracking, payment follow-ups are delayed or forgotten, tying up working capital and resulting in severe bad debt.<br><br>
          <strong>Third is the High Friction of Existing Apps:</strong> Existing apps are either English-centric, full of intrusive advertisements, or require constant typing that disrupts busy checkout counters."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>साक्षीने हे समजावून सांगावे:</strong><br>
          "1. <strong>वही-खात्यांचे नुकसान:</strong> 85% दुकानदार अजूनही कागदी वह्या वापरतात. चहा किंवा पाणी सांडल्याने, पाने फाटल्याने किंवा बेरजेच्या चुकांमुळे पैशांचे मोठे नुकसान होते.<br>
          2. <strong>बुडीत उधारी (Bad Debt):</strong> ग्राहकांना उधारी दिली जाते पण वेळेवर आठवण न केल्याने पैसे अडकून पडतात.<br>
          3. <strong>सध्याच्या ॲप्समधील अडचणी:</strong> बाजारात असलेली ॲप्स इंग्रजीत आहेत, जाहिरातींनी भरलेली आहेत आणि सतत टाईप करावे लागते, जे ग्रामीण दुकानदाराला जमत नाही."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Did you conduct any real field survey to identify these problems?"<br>
          <strong>A (उत्तर):</strong> "Yes, we observed local kirana merchants in Satara district. During morning and evening peak hours, shopkeepers cannot operate complex smartphone keyboards while managing counter transactions."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 04:</span>
        <span class="cue">"Seeing these harsh operational realities, let us examine our core motivation on Slide 4..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 04 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sakshi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 04</span>
        <span>Motivation & Purpose</span>
      </div>
      <span class="badge-role role-sakshi presenter-pill">Presenter: Sakshi Bhagat (Frontend & UI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 4, our primary motivation is to <strong>democratize AI for grassroots merchants</strong>.<br><br>
          While massive tier-1 supermarkets enjoy advanced SAP or POS software with barcode scanners and cloud analytics, local kirana store owners have been completely left behind.<br><br>
          Our purpose is threefold:<br>
          1. <strong>Zero Digital Literacy Barrier:</strong> If a merchant can click a photograph or speak a sentence in Marathi, they can operate VernaLedger.AI without typing a single letter.<br>
          2. <strong>Financial Inclusion:</strong> By automatically calculating credit balances and enabling 1-click WhatsApp payment reminders with UPI links, we accelerate debt recovery by over 60%.<br>
          3. <strong>Offline-First Resilience:</strong> A shopkeeper's business cannot stop when rural internet fluctuates; our system commits transactions locally within 2 milliseconds."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>प्रकल्पाची प्रेरणा काय आहे:</strong><br>
          "मोठ्या डी-मार्ट किंवा मॉलमध्ये कोट्यवधी रुपयांची बिलिंग सिस्टीम असते, पण आपल्या गल्लीतील किराणा दुकानदाराकडे फक्त वही असते.<br>
          आमचा हेतू असा आहे की दुकानदाराला जर फक्त फोटो काढता येत असेल किंवा मराठीत बोलता येत असेल, तरीही तो हे आधुनिक AI सॉफ्टवेअर सहज वापरू शकेल. यामुळे डिजिटल साक्षरतेची अट उरत नाही आणि उधारीचे पैसे 60% वेगाने परत मिळतात."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Why did you prioritize WhatsApp payment reminders over SMS?"<br>
          <strong>A (उत्तर):</strong> "SMS open rates in rural India have dropped below 15% due to spam filters. WhatsApp has a 98% open rate and allows direct clickable UPI payment links (Google Pay / PhonePe) right in Marathi."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Vaishnavi:</span>
        <span class="cue">"I now invite Vaishnavi Dhavale to present the comparative gap analysis against current market solutions."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 05 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header vaishnavi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 05</span>
        <span>Gap Analysis & Competitive Benchmarks</span>
      </div>
      <span class="badge-role role-vaishnavi presenter-pill">Presenter: Vaishnavi Dhavale (Voice & AI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Thank you Sakshi. On Slide 5, we present a rigorous <strong>Gap Analysis</strong> comparing VernaLedger.AI against leading commercial applications: Vyapar, Khatabook, and OKCredit.<br><br>
          As seen in our benchmark matrix:<br>
          • <strong>Multimodal Paper Bill OCR:</strong> Competitors lack handwritten bill digitization. VernaLedger extracts items, weights, and rates in under 1.5 seconds.<br>
          • <strong>Regional Marathi Voice Billing:</strong> None of the commercial apps support continuous Marathi speech recognition. VernaLedger allows complete Devanagari voice billing.<br>
          • <strong>Conversational Store Intelligence (RAG):</strong> Existing apps only display static lists. VernaLedger features an official Gemini AI assistant answering inventory and sales queries with zero hallucination.<br>
          • <strong>50 Pre-Seeded Kirana Commodities with Auto Stock Deduction:</strong> Unlike generic software requiring tedious manual master data entry, VernaLedger comes pre-loaded with 50 authentic staples that automatically deduct on sales."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>वैष्णवीने तक्त्याची तुलना सांगावी:</strong><br>
          "खाताबुक आणि व्यापार ॲप्स चांगले असले तरी त्यामध्ये खालील 4 मोठ्या कमतरता आहेत:<br>
          1. त्यामध्ये <strong>हस्तलिखित पावत्या स्कॅन करण्याची सोय नाही</strong>, जी आपल्याकडे गुगल व्हिजन AI द्वारे आहे.<br>
          2. त्यामध्ये <strong>मराठी व्हॉइस बिलिंग नाही</strong>, आपल्याकडे थेट आवाजातून बिल बनते.<br>
          3. त्यामध्ये <strong>AI असिस्टंट नाही</strong>, आपल्याकडे जेमिनी चॅटबॉट आहे जो दुकानातील साठा व उधारी सांगतो.<br>
          4. इतर ॲप्समध्ये 500 वस्तू मॅन्युअली भरावा लागतात, आपल्याकडे <strong>50 मूळ किराणा वस्तू आधीच लोड केलेल्या आहेत</strong> आणि बिलासोबत साठा आपोआप वजा होतो."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Is VernaLedger free or subscription based compared to Khatabook?"<br>
          <strong>A (उत्तर):</strong> "Khatabook has shifted to aggressive paid subscriptions and merchant loans. VernaLedger is an open, self-hosted, offline-resilient architecture that puts data ownership 100% in the merchant's hands."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Sanket:</span>
        <span class="cue">"I now request our team leader Sanket to articulate our core technical objectives and system pipeline."</span>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== SLIDE 06 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sanket-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 06</span>
        <span>Project Objectives</span>
      </div>
      <span class="badge-role role-sanket presenter-pill">Presenter: Sanket Kirdat (Team Leader)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 6, we define the four concrete <strong>engineering objectives</strong> successfully accomplished in VernaLedger.AI:<br><br>
          <strong>1. Sub-1.5s Vision Token Extraction:</strong> We architected a multimodal pipeline ingesting physical receipts with client-side 960px Lanczos contrast pre-processing, achieving over 96% token extraction accuracy.<br><br>
          <strong>2. Regional Marathi Voice POS & Continuous Voice Typing:</strong> We implemented the Web Speech API configured for regional Devanagari dialects (`mr-IN`), allowing hands-free checkout with zero premature cutoffs.<br><br>
          <strong>3. Intelligent Khata with Automated WhatsApp UPI Hooks:</strong> We built automated running balance computation with overdue indicators and single-click personalized payment recovery messages.<br><br>
          <strong>4. 50 Kirana Item Auto-Deduction Engine & SQL RAG Assistant:</strong> We integrated 50 authentic pre-seeded Kirana staples with instant filter search, automated stock deduction on sales (`stock_qty = MAX(0, stock_qty - billed_qty)`), and zero-hallucination store SQL queries."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>संकेतने सांगावयाची 4 मुख्य उद्दिष्टे:</strong><br>
          "1. <strong>1.5 सेकंदाच्या आत स्कॅनिंग:</strong> कागदी पावतीचा फोटो घेताच त्यातील वस्तू, प्रमाण आणि किंमत 96% अचूकतेने ओळखणे.<br>
          2. <strong>अखंड मराठी व्हॉइस इनपुट:</strong> वाक्य पूर्ण होईपर्यंत माइक बंद न होता सलग मराठी बोलणे ऐकून घेणे.<br>
          3. <strong>स्मार्ट उधारी खातेवही:</strong> ग्राहकाची उधारी एका क्लिकवर अपडेट होणे आणि व्हॉट्सॲपवर UPI लिंक जाणे.<br>
          4. <strong>50 किराणा वस्तूंचा साठा व AI सल्लागार:</strong> 50 जीवनावश्यक वस्तूंचा साठा आपोआप वजा होणे आणि दुकानाचा हिशोब सांगणारा जेमिनी AI असिस्टंट तयार करणे."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How do you prevent negative stock when an item is oversold?"<br>
          <strong>A (उत्तर):</strong> "In our SQLite backend, we use the constraint `stock_qty = MAX(0, stock_qty - billed_qty)`. If stock is insufficient, the system flags a visual '🚨 कमी साठा' alert while gracefully capping stock at zero rather than throwing a runtime error."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 07:</span>
        <span class="cue">"Let us examine how these objectives come together in our end-to-end system pipeline on Slide 7..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 07 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sanket-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 07</span>
        <span>Proposed System Pipeline</span>
      </div>
      <span class="badge-role role-sanket presenter-pill">Presenter: Sanket Kirdat (Team Leader)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Slide 7 depicts our <strong>Four-Stage Closed-Loop Transaction Lifecycle</strong>:<br><br>
          <strong>Stage 1 - Merchant Ingestion:</strong> Ingests inputs through three channels: live camera receipt capture, continuous regional speech prompt, or manual POS keyboard entry.<br><br>
          <strong>Stage 2 - AI Intelligence & Normalization:</strong> Google Gemini Vision and regex NLP normalize raw unstructured tokens into a strictly typed, validated JSON schema while verifying item math (quantity × rate = total).<br><br>
          <strong>Stage 3 - ACID Commit & Auto Stock Deduction:</strong> Executes transactional commits to SQLite within 2 milliseconds, updates customer khata, and instantly deducts inventory stock count.<br><br>
          <strong>Stage 4 - Omnichannel Delivery & Gemini AI:</strong> Generates thermal POS print receipts, sends WhatsApp bills with dynamic UPI links, provides native Excel (.xlsx) exports, and empowers interactive conversational AI."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>प्रणाली कशी काम करते (4 टप्पे):</strong><br>
          "1. <strong>डेटा इनपुट:</strong> पावतीचा फोटो, व्हॉइस किंवा कीबोर्डने माहिती सिस्टीममध्ये जाते.<br>
          2. <strong>AI प्रोसेसिंग:</strong> जेमिनी मॉडेल हस्तलिखित मजकुराचे JSON डेटा मध्ये रूपांतर करते आणि किंमतींची बेरीज तपासते.<br>
          3. <strong>डेटाबेस सेव्ह व स्टॉक वजावट:</strong> 2 मिलिसेकंदात SQLite डेटाबेसमध्ये नोंद होते, उधारी अपडेट होते आणि 50 किराणा मालातून साठा वजा होतो.<br>
          4. <strong>आउटपुट:</strong> थर्मल प्रिंटर पावती, व्हॉट्सॲप मेसेज, एक्सेल फाईल आणि जेमिनी AI चॅटबॉटद्वारे माहिती मिळते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "What if the user's speech contains slang or regional Marathi words?"<br>
          <strong>A (उत्तर):</strong> "We built custom Marathi dialect normalizers: words like 'शंभर', 'दीडशे', 'पाव किलो', 'अर्धा लिटर' are mapped to standard metric units and numerical values using regex and Gemini NLP."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Rushikesh:</span>
        <span class="cue">"I now invite Rushikesh Mulik to explain our underlying technologies, system architecture, and empirical benchmarks."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 08 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header rushikesh-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 08</span>
        <span>Technologies & Tools (Engineering Stack)</span>
      </div>
      <span class="badge-role role-rushikesh presenter-pill">Presenter: Rushikesh Mulik (Backend & DB)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Thank you Sanket. Respected examiners, on Slide 8, I present our <strong>Full-Stack Engineering Architecture</strong> engineered for zero-latency local performance.<br><br>
          • <strong>Application Layer:</strong> We use <strong>FastAPI with Uvicorn</strong> as a high-throughput universal ASGI serverless backend. The client is a reactive single-page application built in vanilla JavaScript, avoiding bulky framework dependencies.<br><br>
          • <strong>Artificial Intelligence & Audio:</strong> Powered by <strong>Google Gemini 3.1 Flash Lite and 3.8</strong> for sub-1.5s vision OCR and zero-hallucination RAG reasoning. The speech layer utilizes the native <strong>Web Speech API (`mr-IN`)</strong> for uninterrupted speech recognition with word-by-word streaming (`sendMessageStream`).<br><br>
          • <strong>Persistence & Data Integrity:</strong> Local <strong>SQLite with Write-Ahead Logging (WAL)</strong> ensures atomic ACID transactions. Microsoft Excel generation is powered by <strong>XlsxWriter</strong> with automatic column fitting and full UTF-8 Devanagari font rendering."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>ऋषिकेशने तांत्रिक टूल्स सांगावीत:</strong><br>
          "1. <strong>बॅकएंड:</strong> पायथनचा <strong>FastAPI आणि Uvicorn</strong> सर्व्हर, जो अतिशय वेगवान आहे.<br>
          2. <strong>फ्रंटएंड:</strong> शुद्ध व्हॅनिला जावास्क्रिप्ट (कोणताही हेवी फ्रेमवर्क नाही, त्यामुळे लो-कॉस्ट फोनवरही जलद चालते).<br>
          3. <strong>AI मॉडेल्स:</strong> गुगलचे <strong>Gemini 3.1 Flash Lite</strong> मॉडेल आणि ब्राउझरची <strong>Web Speech API</strong> (मराठी आवाजासाठी).<br>
          4. <strong>डेटाबेस:</strong> <strong>SQLite WAL मोड</strong>, जो इंटरनेट नसतानाही अखंड चालतो, आणि <strong>XlsxWriter</strong> ज्यामुळे मराठी फॉन्टसह एक्सेल फाईल तयार होते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Why did you choose SQLite over MySQL or PostgreSQL?"<br>
          <strong>A (उत्तर):</strong> "Local kirana stores operate in low-resource environments. Running a separate MySQL or Postgres service consumes memory and requires administrative setup. SQLite is serverless, zero-configuration, resides in a single file (`ledger.db`), and supports ACID transactions with sub-2ms latency in WAL mode."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 09:</span>
        <span class="cue">"Moving to Slide 9, let us review our 3-Tier Layered Architecture..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 09 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header rushikesh-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 09</span>
        <span>System Architecture (Modular 3-Tier)</span>
      </div>
      <span class="badge-role role-rushikesh presenter-pill">Presenter: Rushikesh Mulik (Backend & DB)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 9, we illustrate our <strong>Modular 3-Tier Layered Architecture</strong> ensuring full decoupling and fault isolation:<br><br>
          <strong>1. Presentation Layer (Client):</strong> Responsive SPA rendering Cyberpunk Dark and Kirana Light modes, handling canvas image compression, speech mic capture, and reactive DOM updates.<br><br>
          <strong>2. Intelligence & Application Layer (FastAPI Gateway):</strong> Hosts RESTful endpoints (`/api/ocr`, `/api/voice-billing`, `/api/rag-chat`, `/api/inventory/reset-defaults`, `/api/sync`). It coordinates API key failover pools, image pre-processing, and RAG context building.<br><br>
          <strong>3. Persistence Layer (Storage Engine):</strong> Local SQLite database maintaining structured relational tables (`receipts`, `customer_khata`, `shop_inventory`, `business_expenses`, and `audit_logs`) with full ACID compliance."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>3-स्तरीय रचना समजावून सांगा:</strong><br>
          "1. <strong>प्रेझेंटेशन लेअर (UI):</strong> वापरकर्त्याला दिसणारा स्क्रीन, कॅमेरा इनपुट आणि माईक बटण.<br>
          2. <strong>ॲप्लिकेशन व इंटेलिजन्स लेअर (FastAPI):</strong> सर्व्हर जो क्लायंट आणि AI मॉडेल्समध्ये दुवा साधतो; यामध्ये सुरक्षितता, की-रोटेशन आणि डेटा व्हॅलिडेशन होते.<br>
          3. <strong>डेटाबेस लेअर (SQLite):</strong> यामध्ये बिलांचा डेटा (`receipts`), ग्राहकांची उधारी (`customer_khata`), 50 किराणा मालाचा साठा (`shop_inventory`) आणि दैनंदिन खर्च सुरक्षितपणे साठवले जातात."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "What happens if the Gemini API key runs out of quota?"<br>
          <strong>A (उत्तर):</strong> "We implemented an API key failover pool in `api/index.py` (`get_api_keys_pool()`). If the primary key receives a 429 quota error, the system automatically rotates to the secondary key without crashing."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 10:</span>
        <span class="cue">"On Slide 10, let us trace the sequential execution pipeline from input capture to storage..."</span>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== SLIDE 10 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header rushikesh-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 10</span>
        <span>Working Flow & Execution Pipeline</span>
      </div>
      <span class="badge-role role-rushikesh presenter-pill">Presenter: Rushikesh Mulik (Backend & DB)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 10, we display the <strong>step-by-step Execution Lifecycle</strong>:<br><br>
          1. <strong>Capture:</strong> The shopkeeper photographs a receipt or speaks a Marathi phrase.<br>
          2. <strong>Client-Side Optimization:</strong> If an image is captured, our client canvas compresses it to 960px with Lanczos filter and computes a SHA-256 hash to prevent duplicate entries.<br>
          3. <strong>AI Inference:</strong> Ingested into Gemini Flash Vision, which parses vendor name, date, items, quantities, and totals into strongly typed JSON.<br>
          4. <strong>Operator Verification:</strong> Items appear in an editable interactive grid on screen, allowing instantaneous manual adjustments if necessary.<br>
          5. <strong>Atomic Commit:</strong> On clicking Save, the transaction is committed to SQLite, customer debt balances are updated, and inventory stock is automatically deducted (`stock_qty = MAX(0, stock_qty - billed_qty)`)."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>सॉफ्टवेअरची कार्यपद्धती:</strong><br>
          "1. फोटो काढला किंवा आवाज दिला जातो.<br>
          2. फोटो ब्राऊझरमध्येच ऑप्टिमाइझ केला जातो आणि डुप्लिकेट बिल टाळण्यासाठी SHA-256 हॅश तपासला जातो.<br>
          3. गुगल जेमिनी मॉडेल बिलातील अक्षरे आणि आकडे JSON फॉरमॅटमध्ये आणते.<br>
          4. स्क्रीनवर दुकानदाराला बदल करण्यासाठी टेबल दिसते.<br>
          5. 'सेव्ह' दाबताच 2 सेकंदांत पावती सेव्ह होते, ग्राहकाच्या नावावर उधारी नोंदवली जाते आणि गोदामातील साठा आपोआप कमी होतो."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How do you detect duplicate receipts?"<br>
          <strong>A (उत्तर):</strong> "We compute a cryptographic image hash and store it in SQLite index `idx_receipts_image_hash`. If a merchant accidentally scans the same paper bill twice, the system flags a duplicate warning immediately."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 11:</span>
        <span class="cue">"Next, let us look at our empirical performance benchmarks on Slide 11..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 11 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header rushikesh-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 11</span>
        <span>Performance Analysis & Empirical Benchmarks</span>
      </div>
      <span class="badge-role role-rushikesh presenter-pill">Presenter: Rushikesh Mulik (Backend & DB)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Slide 11 highlights our <strong>Quantitative Performance Benchmarks</strong> rigorously tested under real-world kirana workloads:<br><br>
          • <strong>Sub-1.5s OCR Latency:</strong> Through client-side 960px compression and Gemini 3.1 Flash Lite inference, end-to-end receipt digitization completes in under 1.5 seconds.<br><br>
          • <strong>96.8% Devanagari Extraction Accuracy:</strong> Tested across handwritten Marathi bills and faint thermal paper receipts, maintaining exceptional mathematical integrity.<br><br>
          • <strong>10ms Chatbot Dispatch:</strong> Instant in-memory state dispatch for store inventory and ~1.2s deep Gemini LLM reasoning with zero audio delay.<br><br>
          • <strong>Sub-2ms ACID Commit Latency:</strong> Local SQLite commits in Write-Ahead Logging mode guarantee zero checkout lag even during massive transaction bursts."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>ऋषिकेशने ही आकडेवारी स्पष्ट सांगावी:</strong><br>
          "1. <strong>OCR लेटन्सी:</strong> दीड सेकंदापेक्षा कमी वेळात कागदी पावती डिजिटल होते.<br>
          2. <strong>मराठी अचूकता:</strong> 96.8% अचूकतेने मराठी हस्तलिखित अक्षरे आणि आकडे ओळखले जातात.<br>
          3. <strong>चॅटबॉट रिस्पॉन्स:</strong> फक्त 10 मिलिसेकंदात स्थानिक डेटाबेसमधून माहिती मिळवून AI उत्तर देते.<br>
          4. <strong>डेटाबेस स्पीड:</strong> 2 मिलिसेकंदांच्या आत प्रत्येक बिल डेटाबेसमध्ये सेव्ह होते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How many receipts did you test to calculate 96.8% accuracy?"<br>
          <strong>A (उत्तर):</strong> "We tested a dataset of 120 authentic kirana receipts (both handwritten Marathi Devanagari notebooks and printed thermal receipts), evaluating character error rate (CER) and field accuracy."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Sanket:</span>
        <span class="cue">"Now, let us examine the live system results. I hand over to our leader Sanket to present Result 1: Multimodal Scanner."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 12 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sanket-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 12</span>
        <span>Result 1: Smart Multimodal Scanner & POS</span>
      </div>
      <span class="badge-role role-sanket presenter-pill">Presenter: Sanket Kirdat (Team Leader)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Thank you Rushikesh. On Slide 12, we showcase <strong>Result 1: Our Smart Multimodal Scanner & POS Terminal</strong>.<br><br>
          As displayed in the live UI screenshot, when a merchant snaps a photo of a physical bill, our system applies Google Vision Transformers to segment and extract the merchant name, date, item names, weights, unit prices, and grand totals.<br><br>
          Key highlights include:<br>
          • <strong>Instant POS Grid Preview:</strong> Line items populate into an interactive table where the merchant can adjust quantities or rates on the fly.<br>
          • <strong>Automatic Stock Deduction:</strong> The moment the bill is saved, all billed commodities are automatically deducted from the store's 50 Kirana inventory items (`stock_qty = MAX(0, stock_qty - billed_qty)`).<br>
          • <strong>Dual-Mode Theming:</strong> Seamlessly switchable between Cyberpunk Dark and high-contrast Kirana Light mode."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>संकेतने स्क्रीनशॉट दाखवून सांगावे:</strong><br>
          "स्लाईडवरील स्क्रीनशॉटमध्ये पाहू शकता: पावतीचा फोटो अपलोड करताच ती स्कॅन होऊन उजव्या बाजूला सुंदर डिजिटल बिल तयार झाले आहे.<br>
          दुकानदाराला हवी असल्यास एका सेकंदात किंमत किंवा वजन बदलता येते. सर्वात महत्त्वाचे म्हणजे 'सेव्ह' बटण दाबताच साखरेचे किंवा तेलाचे प्रमाण गोदामातील साठ्यातून (Inventory) आपोआप वजा होते, त्यामुळे वेगळी नोंद करावी लागत नाही."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "What if the paper bill is torn or ink is faded?"<br>
          <strong>A (उत्तर):</strong> "We apply PIL Lanczos contrast and adaptive histogram sharpening. Furthermore, the UI provides an editable grid so the merchant can easily review and modify any uncertain character before saving."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Vaishnavi:</span>
        <span class="cue">"Next, Vaishnavi Dhavale will demonstrate Result 2: Vernacular Voice Billing Engine."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 13 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header vaishnavi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 13</span>
        <span>Result 2: Vernacular Voice Billing Engine</span>
      </div>
      <span class="badge-role role-vaishnavi presenter-pill">Presenter: Vaishnavi Dhavale (Voice & AI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 13, we present <strong>Result 2: Vernacular Voice Billing Engine</strong>.<br><br>
          During rush hours, a shopkeeper's hands are busy weighing commodities and packing bags. Typing on a keyboard causes massive counter delays.<br><br>
          With VernaLedger, the merchant simply presses the microphone and speaks naturally in Marathi, for example: <em>'सागरला २ किलो साखर ८४ रुपये आणि १ लिटर शेंगदाणा तेल १८५ रुपये'</em>.<br><br>
          Our Web Speech API (`mr-IN`) engine captures continuous speech without cutting off prematurely. Advanced regex and Gemini NLP parse customer name, items, weights, and prices, instantly generating an itemized bill. This slashes checkout delays by over 85%."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>वैष्णवीने व्हॉइस बिलिंग स्पष्ट करावे:</strong><br>
          "सकाळी आणि संध्याकाळी दुकानात ग्राहकांची गर्दी असते, तेव्हा टायपिंग करायला वेळ नसतो.<br>
          दुकानदार फक्त माईक दाबून बोलेल: 'सागरला २ किलो साखर ८४ रुपये आणि १ लिटर तेल १८५ रुपये'.<br>
          सिस्टीम आपोआप सागरचे नाव, साखरेचे वजन, किंमत ओळखून डिजिटल बिल बनवते. वाक्य पूर्ण होईपर्यंत माइक चालू राहतो. यामुळे दुकानातील गर्दीचा वेळ 85% वाचतो."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How do you handle background noise in a bustling kirana store?"<br>
          <strong>A (उत्तर):</strong> "The Web Speech API uses browser-level hardware acoustic echo cancellation and noise suppression. Additionally, our NLP parser validates extracted tokens against phonetically similar kirana staples."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Sakshi:</span>
        <span class="cue">"I now invite Sakshi Bhagat to present Result 3: Customer Khata and WhatsApp Debt Recovery."</span>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== SLIDE 14 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sakshi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 14</span>
        <span>Result 3: Customer Khata & Udhar Ledger</span>
      </div>
      <span class="badge-role role-sakshi presenter-pill">Presenter: Sakshi Bhagat (Frontend & UI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 14, we display <strong>Result 3: Customer Khata & Udhar Ledger</strong>.<br><br>
          This is our Khatabook-beating digital ledger interface. Merchants can instantly record <strong>'उधारी दिली' (Credit Given)</strong> and <strong>'जमा मिळाले' (Payment Received)</strong> with automated running balance computation.<br><br>
          Most importantly, we have solved the social awkwardness of asking for money. With a single click on the green WhatsApp icon, the merchant dispatches a polite, personalized Marathi reminder to the customer's phone containing the exact balance and an embedded UPI payment link (Google Pay / PhonePe). Customers can settle debts in 10 seconds."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>साक्षीने खातेवहीचे महत्त्व सांगावे:</strong><br>
          "हे डिजिटल खातेवही आहे जिथे 'उधारी दिली' आणि 'जमा मिळाले' यांची आपोआप वजाबाकी होऊन अंतिम बाकी दिसते.<br>
          दुकानदाराला ग्राहकाकडे उधारी मागताना संकोच वाटतो. या सिस्टीममध्ये व्हॉट्सॲप आयकॉनवर क्लिक करताच ग्राहकाला नम्र मराठी भाषेत मेसेज जातो: 'आपली बाकी ₹500 शिल्लक आहे, कृपया खालील UPI लिंकवरून त्वरित भरा'. ग्राहक घरबसल्या PhonePe किंवा Google Pay ने पैसे भरू शकतात."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Does sending WhatsApp messages require an expensive WhatsApp Business API?"<br>
          <strong>A (उत्तर):</strong> "No! We use direct deep-linking intent `https://wa.me/{phone}?text={encoded_message}`. This opens the merchant's installed WhatsApp application directly with pre-filled text and payment link at zero recurring cost."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Rushikesh:</span>
        <span class="cue">"Next, Rushikesh Mulik will present Result 4: Store Operations and our 50 Kirana Inventory Items."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 15 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header rushikesh-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 15</span>
        <span>Result 4: Store Operations & 50 Kirana Inventory Items</span>
      </div>
      <span class="badge-role role-rushikesh presenter-pill">Presenter: Rushikesh Mulik (Backend & DB)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 15, we showcase <strong>Result 4: Store Operations & 50 Kirana Inventory Items</strong>.<br><br>
          As seen in our updated live screenshot, VernaLedger comes pre-seeded with <strong>50 authentic Kirana commodities</strong> (Lokwan Wheat, Basmati Rice, Toor Dal, Sugar, Groundnut Oil, Tea, Spices, etc.) across standardized metric units (`kg`, `ltr`, `packet`, `nos`).<br><br>
          Key technical features:<br>
          • <strong>Live Search Filter:</strong> Instant real-time filtering across all 50 items by Marathi or English names.<br>
          • <strong>Automatic Stock Deduction Engine:</strong> The moment a sale occurs via scanner, voice billing, or manual checkout, stock is automatically deducted (`stock_qty = MAX(0, stock_qty - billed_qty)`).<br>
          • <strong>Low-Stock Warning Badges:</strong> Items falling below threshold trigger a bright '🚨 कमी साठा' alert.<br>
          • <strong>1-Click Default Reset:</strong> Allows shopkeepers to reset back to 50 defaults instantly via `/api/inventory/reset-defaults`."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>ऋषिकेशने 50 आयटम्सची माहिती द्यावी:</strong><br>
          "दुकानदाराला आयटम भरत बसण्याचा त्रास होऊ नये म्हणून आम्ही <strong>50 मूळ किराणा वस्तू</strong> (गहू, तांदूळ, डाळी, साखर, तेल, पोहे, रवा, मसाले) आधीच लोड करून दिल्या आहेत.<br>
          1. <strong>सर्च बार:</strong> नाव टाईप करताच सेकंदात वस्तू फिल्टर होते.<br>
          2. <strong>ऑटोमॅटिक स्टॉक वजावट:</strong> बिल बनले की साखरेचा किंवा तेलाचा साठा आपोआप गोदामातून कमी होतो.<br>
          3. <strong>कमी साठा बॅज:</strong> साठा संपत आला की लाल रंगाचा '🚨 कमी साठा' इशारा मिळतो, ज्यामुळे माल कधी आणायचा हे लगेच कळते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Can the merchant add their own custom items or change prices?"<br>
          <strong>A (उत्तर):</strong> "Yes, the UI provides an 'Add New Item' form with custom units (`kg`, `ltr`, `packet`) and alert limits, as well as one-click deletion and price editing."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Vaishnavi:</span>
        <span class="cue">"Next, Vaishnavi Dhavale will demonstrate Result 5: Verna AI Multilingual Voice Assistant."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 16 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header vaishnavi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 16</span>
        <span>Result 5: Verna AI Multilingual Voice Assistant</span>
      </div>
      <span class="badge-role role-vaishnavi presenter-pill">Presenter: Vaishnavi Dhavale (Voice & AI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Slide 16 highlights <strong>Result 5: Verna AI Multilingual Voice Assistant</strong> — an official Google Gemini app experience tailored for retail.<br><br>
          • <strong>Interactive Mic Button & Live Pulse:</strong> Featuring a sleek microphone button with real-time pulsing recording animations (`#chatVoiceBtn`).<br>
          • <strong>Word-by-Word Streaming:</strong> Answers stream onto the screen token-by-token using `sendMessageStream`, giving an instant conversational experience.<br>
          • <strong>Strict Script Persistence:</strong> If the merchant speaks in Marathi Devanagari, Verna AI strictly replies in Marathi Devanagari; if asked in Romanized Marathi, Hindi, or English, it matches the exact script.<br>
          • <strong>Zero-Hallucination SQL Store RAG:</strong> The assistant inspects live SQLite tables to answer: <em>'साखर आणि तेलाचा साठा किती शिल्लक आहे?'</em> or <em>'आजची एकूण विक्री किती?'</em> with 100% mathematical precision."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>वैष्णवीने जेमिनी असिस्टंट दाखवावा:</strong><br>
          "हा अधिकृत <strong>Google Gemini</strong> सारखा डिझाइन केलेला AI चॅटबॉट आहे.<br>
          1. <strong>माईक पल्स ॲनिमेशन:</strong> बोलताना माईक लाल रंगात पल्स होतो.<br>
          2. <strong>स्ट्रीमिंग उत्तरे:</strong> शब्द न् शब्द थेट स्क्रीनवर उमटतात.<br>
          3. <strong>स्क्रिप्ट पर्सिस्टन्स:</strong> युझर मराठीत विचारेल तर मराठीतच उत्तर मिळते, इंग्रजीत विचारले तर इंग्रजीत उत्तर मिळते.<br>
          4. <strong>खरा डेटाबेस RAG:</strong> चॅटबॉट खोट्या गप्पा मारत नाही; दुकानातील प्रत्यक्ष साठा, आजची विक्री आणि उधारी तपासून अगदी अचूक उत्तर देतो."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How do you guarantee zero hallucination in financial queries?"<br>
          <strong>A (उत्तर):</strong> "In `/api/rag-chat`, we dynamically construct a system context containing exact SQL aggregated values (Total Revenue, Pending Debt, Low-Stock items). The LLM is instructed to answer strictly based on these grounded facts without inventing figures."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Rushikesh:</span>
        <span class="cue">"Next, Rushikesh Mulik will present Result 6: Digital Ledger and Excel Export."</span>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== SLIDE 17 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header rushikesh-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 17</span>
        <span>Result 6: Digital Ledger & Excel Export</span>
      </div>
      <span class="badge-role role-rushikesh presenter-pill">Presenter: Rushikesh Mulik (Backend & DB)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 17, we showcase <strong>Result 6: Digital Ledger & Native Excel Export</strong>.<br><br>
          Every processed bill is preserved in a permanent, tamper-resistant transaction log searchable by Bill ID (`#VL-XX`), customer name, or date range.<br><br>
          • <strong>Dedicated Emerald Green Excel Button:</strong> Positioned prominently in the ledger view, one click triggers a full OpenXML `.xlsx` spreadsheet download.<br>
          • <strong>Powered by XlsxWriter:</strong> Unlike naive CSV exports, our generator sets automatic column widths (preventing date `########` clipping), applies professional header formatting, and flawlessly supports UTF-8 Marathi Devanagari text.<br>
          • <strong>Thermal POS Reprint:</strong> Allows instant 58mm / 80mm thermal receipt printing and controlled ACID record deletion."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>ऋषिकेशने लेजर व एक्सेलचे महत्त्व सांगावे:</strong><br>
          "1. <strong>डिजिटल लेजर:</strong> दुकानातील प्रत्येक बिलाची कायमस्वरूपी नोंद, बिल नंबर किंवा ग्राहकाच्या नावाने शोधता येते.<br>
          2. <strong>हिरवे एक्सेल बटण:</strong> एका क्लिकवर संपूर्ण वर्षाचा किंवा महिन्याचा हिशोब मायक्रोसॉफ्ट एक्सेल (`.xlsx`) फाईलमध्ये सेव्ह होतो.<br>
          3. <strong>मराठी फॉन्ट सपोर्ट:</strong> इतर सॉफ्टवेअरमध्ये मराठी अक्षरे एक्सेलमध्ये बिघडतात, पण आम्ही `xlsxwriter` वापरल्यामुळे मराठी नावे आणि तारखा अगदी स्पष्ट दिसतात.<br>
          4. <strong>थर्मल पावती प्रिंट:</strong> हवे तेव्हा जुनी पावती पुन्हा प्रिंट करता येते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Why did you implement Excel export when the app already has a database?"<br>
          <strong>A (उत्तर):</strong> "Kirana merchants must submit periodic income and sales records to local chartered accountants (CAs) and banks for mudra loans. CAs demand formatted `.xlsx` spreadsheets."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Sakshi:</span>
        <span class="cue">"I now invite Sakshi Bhagat to demonstrate Kirana Light Mode, Mobile PWA, and our project advantages."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 18 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sakshi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 18</span>
        <span>Result 7: High-Contrast Kirana Light Mode</span>
      </div>
      <span class="badge-role role-sakshi presenter-pill">Presenter: Sakshi Bhagat (Frontend & UI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 18, we present <strong>Result 7: High-Contrast Kirana Light Mode</strong>.<br><br>
          Local kirana stores operate in open-shutter roadside environments under harsh, direct afternoon sunlight. In such bright environments, trendy dark-mode screens suffer from severe glare, making text unreadable on budget mobile screens.<br><br>
          To solve this ergonomic challenge, we engineered a dedicated <strong>High-Contrast Kirana Light Theme</strong>. It features crisp white and ivory backgrounds, deep navy typography, and sharp emerald status badges, ensuring 100% legibility under direct sunlight. Users can toggle modes instantly with one click."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>साक्षीने किराणा लाईट मोडचे कारण सांगावे:</strong><br>
          "किराणा दुकाने रस्त्याच्या कडेला असतात आणि दुपारच्या वेळी दुकानात कडक ऊन येते. अशा उन्हामध्ये डार्क मोडमधील अक्षरे मोबाईलवर अजिबात दिसत नाहीत.<br>
          यासाठी आम्ही खास <strong>'किराणा लाईट मोड'</strong> तयार केला आहे. पांढऱ्या पार्श्वभूमीवर गडद निळी अक्षरे असल्यामुळे थेट उन्हामध्येही दुकानदाराला हिशोब आणि बिलाचे आकडे अगदी स्पष्ट वाचता येतात."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How is the theme preference saved?"<br>
          <strong>A (उत्तर):</strong> "We persist theme state in `localStorage` under `verna_theme`. When the page reloads, the theme is restored instantly without visual flicker."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 19:</span>
        <span class="cue">"On Slide 19, let us review our Mobile-First Progressive Web App interface..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 19 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sakshi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 19</span>
        <span>Result 8: Mobile-First Responsive PWA</span>
      </div>
      <span class="badge-role role-sakshi presenter-pill">Presenter: Sakshi Bhagat (Frontend & UI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 19, we display <strong>Result 8: Mobile-First Responsive PWA</strong>.<br><br>
          Most rural shopkeepers do not own expensive desktop computers; their primary computing device is an Android smartphone.<br><br>
          VernaLedger is engineered as a <strong>Progressive Web Application (PWA)</strong> with service workers (`sw.js`) and a web manifest. On mobile devices, the layout automatically transforms: the desktop sidebar disappears and converts into an intuitive, thumb-friendly 5-tab bottom navigation bar (`Scanner`, `Khata`, `Store`, `Ledger`, `Verna AI`). It is fully installable on Android home screens like a native app."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>मोबाईल ॲपचे स्वरूप स्पष्ट करा:</strong><br>
          "बहुतेक किराणा दुकानदारांकडे संगणक नसतो, त्यांच्याकडे फक्त 5,000 ते 10,000 रुपयांचा अँड्रॉइड फोन असतो.<br>
          त्यामुळे आम्ही हे ॲप <strong>मोबाईल-फर्स्ट PWA</strong> बनवले आहे. मोबाईलवर उघडताच खाली 5 सोपी बटणे (टॅब) येतात (स्कॅनर, खातेवही, किराणा साठा, लेजर, AI). हे ॲप गुगल क्रोममधून थेट मोबाईल स्क्रीनवर ॲपसारखे इन्स्टॉल करता येते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "Can the shopkeeper use the phone's native camera directly through this PWA?"<br>
          <strong>A (उत्तर):</strong> "Yes! The HTML5 file input with `capture='environment'` invokes the native smartphone rear camera directly for receipt photography."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 20:</span>
        <span class="cue">"On Slide 20, let us synthesize the primary advantages of our system..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 20 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sakshi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 20</span>
        <span>Advantages & Strengths</span>
      </div>
      <span class="badge-role role-sakshi presenter-pill">Presenter: Sakshi Bhagat (Frontend & UI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 20, we summarize the <strong>Core Strategic Advantages</strong> of VernaLedger.AI:<br><br>
          1. <strong>True Vernacular Accessibility & Gemini Voice:</strong> Eliminates digital literacy barriers. Even a merchant with minimal formal education can manage bills by speaking in Marathi.<br>
          2. <strong>60% Accelerated Working Capital Recovery:</strong> Direct WhatsApp payment links with UPI payment intents turn overdue debts into instant bank transfers.<br>
          3. <strong>Zero-Hardware Cost:</strong> Runs on existing smartphones or laptops with no costly POS terminals, barcode scanners, or thermal printers mandated.<br>
          4. <strong>Offline-First Resilience:</strong> Sub-2ms SQLite commits ensure shop billing never halts due to rural broadband failures."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>साक्षीने प्रकल्पाचे मुख्य फायदे सांगावे:</strong><br>
          "1. <strong>शून्य शिकण्याची गरज:</strong> इंग्रजी किंवा कॉम्प्युटर न शिकता मराठी आवाजातून संपूर्ण दुकानाचे काम होते.<br>
          2. <strong>उधारीची 60% जलद वसुली:</strong> व्हॉट्सॲप आणि UPI मुळे ग्राहक त्वरित पैसे पाठवतात.<br>
          3. <strong>खर्चाची बचत:</strong> वेगळे महागडे बिलिंग मशीन घेण्याची गरज नाही; स्वतःच्या मोबाईलवर चालू शकते.<br>
          4. <strong>डेटा सुरक्षितता:</strong> इंटरनेट नसतानाही स्थानिक संगणकावर सुरक्षितपणे चालते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "What is the biggest operational benefit to a small shopkeeper?"<br>
          <strong>A (उत्तर):</strong> "Saving 2 to 3 hours every day on manual bookkeeping, zero calculation mistakes, and recovering thousands of rupees in previously forgotten credit debts."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Vaishnavi:</span>
        <span class="cue">"I now hand over to Vaishnavi Dhavale to discuss system limitations and future enhancements."</span>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== SLIDE 21 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header vaishnavi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 21</span>
        <span>System Limitations (Engineering Constraints)</span>
      </div>
      <span class="badge-role role-vaishnavi presenter-pill">Presenter: Vaishnavi Dhavale (Voice & AI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Thank you Sakshi. On Slide 21, as responsible engineers, we candidly acknowledge our <strong>System Limitations & Engineering Constraints</strong>:<br><br>
          <strong>1. AI Cloud Internet Dependency:</strong> While local database commits, manual POS billing, inventory deduction, and customer khata operate 100% offline, our Gemini Flash Vision OCR and LLM RAG reasoning require an active internet connection to query cloud endpoints.<br><br>
          <strong>2. Severe Physical Document Degradation:</strong> Receipts that are severely grease-stained, oil-soaked, or where thermal dye has completely faded can occasionally yield partial extractions, requiring the merchant to verify the editable on-screen grid before committing."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>वैष्णवीने सिस्टीमच्या मर्यादा सांगाव्यात:</strong><br>
          "1. <strong>क्लाउड इंटरनेटची गरज:</strong> स्थानिक डेटाबेस, मॅन्युअल बिलिंग आणि खातेवही इंटरनेटशिवाय चालते; मात्र जेमिनी व्हिजन OCR आणि AI चॅटबॉटसाठी इंटरनेट आवश्यक आहे.<br>
          2. <strong>खूप खराब पावत्या:</strong> जर पावतीवर तेल किंवा पाणी सांडले असेल, किंवा थर्मल पावतीची शाई पूर्ण उडाली असेल, तर काही आकडे अस्पष्ट येऊ शकतात; अशा वेळी दुकानदाराला स्क्रीनवर तपासून दुरुस्त करावे लागते."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How do you plan to make OCR work 100% offline without the cloud?"<br>
          <strong>A (उत्तर):</strong> "In future iterations, we plan to embed a quantized on-device lightweight model like MobileNet-Devanagari OCR or PaddleOCR directly on the client."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Transition to Slide 22:</span>
        <span class="cue">"Building on these learnings, let us review our future development roadmap on Slide 22..."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 22 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header vaishnavi-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 22</span>
        <span>Future Enhancements (Scalability Roadmap)</span>
      </div>
      <span class="badge-role role-vaishnavi presenter-pill">Presenter: Vaishnavi Dhavale (Voice & AI)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "On Slide 22, we outline our <strong>Future Enhancements & Commercial Scalability Roadmap</strong>:<br><br>
          • <strong>Native Android APK with Edge AI:</strong> Compiling as a standalone Android application with quantized on-device models for 100% offline OCR scanning.<br>
          • <strong>Dynamic UPI QR Soundbox Integration:</strong> Printing transaction-specific dynamic UPI QR codes and integrating with Bluetooth soundboxes for real-time Marathi audio payment announcements ('गुगल पे वर ₹२५० प्राप्त झाले').<br>
          • <strong>Multi-Counter P2P Sync:</strong> Enabling peer-to-peer distributed synchronization across multiple checkout counters within the same shop.<br>
          • <strong>Automated GST Compliance:</strong> Automatically categorizing HSN codes to generate one-click GSTR-1 and GSTR-3B tax compliance spreadsheets."
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>भविष्यातील योजना:</strong><br>
          "1. <strong>अँड्रॉइड APK ॲप:</strong> मोबाईलवर ऑफलाइन चालणारे स्वतंत्र ॲप बनवणे.<br>
          2. <strong>UPI साऊंडबॉक्स (Soundbox):</strong> बिलावर डायनॅमिक QR कोड देणे आणि पैसे जमा होताच 'Paytm/PhonePe वर ₹250 मिळाले' असा मराठी आवाज देणे.<br>
          3. <strong>मल्टी-डिव्हाइस सिंक:</strong> दुकानात दोन-तीन काऊंटर असतील तर एकाच वेळी सर्वांचा हिशोब जोडणे.<br>
          4. <strong>ऑटोमॅटिक GST टॅक्स:</strong> सरकारी नियमांनुसार आपोआप GST रिटर्न शीट तयार करणे."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "How will Bluetooth soundboxes communicate with your web application?"<br>
          <strong>A (उत्तर):</strong> "Via the Web Bluetooth API or a local websocket daemon running on the counter smartphone, triggering audio alerts upon webhook payment verification."
        </div>
      </div>
      <div class="handover-banner">
        <span>➡️ Handover to Sanket:</span>
        <span class="cue">"Finally, I hand over to our Team Leader Sanket Kirdat for the concluding remarks and open defense."</span>
      </div>
    </div>
  </div>

  <!-- ==================== SLIDE 23 ==================== -->
  <div class="slide-card">
    <div class="slide-card-header sanket-header">
      <div class="slide-num-title">
        <span class="slide-pill">SLIDE 23</span>
        <span>Conclusion & Open Defense (Q&A)</span>
      </div>
      <span class="badge-role role-sanket presenter-pill">Presenter: Sanket Kirdat (Team Leader)</span>
    </div>
    <div class="slide-content-grid">
      <div class="script-box english-box">
        <div class="box-tag tag-en">🗣️ What to Speak in English (Spoken Script)</div>
        <div class="spoken-text">
          "Thank you Vaishnavi. Respected examiners, to conclude our presentation on Slide 23:<br><br>
          <strong>Executive Summary:</strong> VernaLedger.AI bridges the digital divide for India's 63 million grassroots kirana merchants. By uniting <strong>Gemini 3.1 Flash Vision OCR</strong>, <strong>continuous Marathi voice billing</strong>, a <strong>50-item Kirana auto-deduction engine</strong>, an <strong>official Google Gemini voice assistant</strong>, and a <strong>resilient SQLite ACID ledger with native Excel exports</strong>, we democratize enterprise-grade retail intelligence with zero learning curve.<br><br>
          We express our heartfelt gratitude to our guide <strong>Prof. Kaisar Atar sir</strong>, our HOD <strong>Dr. S. Y. Mulla sir</strong>, and all faculty members of Arvind Gavali College of Engineering for their invaluable mentorship.<br><br>
          Our entire team is now eager and open to answer your technical questions. Thank you very much!"
        </div>
      </div>
      <div class="script-box marathi-box">
        <div class="box-tag tag-mr">📖 मराठी अर्थ व संदर्भ (काय समजावून सांगायचे)</div>
        <div class="marathi-text">
          <strong>संकेतने शेवट कसा करावा:</strong><br>
          "शेवटी सर्वांचे आभार मानून सारांश सांगावा:<br>
          'वर्णा-लेजर AI ने ग्रामीण आणि स्थानिक दुकानदारांच्या हातामध्ये सर्वात आधुनिक कृत्रिम बुद्धिमत्ता (AI) दिली आहे. यामध्ये पावती स्कॅनर, मराठी व्हॉइस बिलिंग, 50 किराणा मालाचा साठा, जेमिनी असिस्टंट आणि व्हॉट्सॲप खातेवही यांचा सुंदर मिलाफ आहे.'<br><br>
          मार्गदर्शक अतार सर, विभागप्रमुख मुल्ला सर आणि परीक्षकांचे आभार माना आणि 'आता आम्ही आपल्या सर्व तांत्रिक प्रश्नांची उत्तरे देण्यास तयार आहोत, धन्यवाद!' असे आत्मविश्वासाने सांगा."
        </div>
      </div>
      <div class="qa-box">
        <div class="qa-title">🎯 संभाव्य प्रश्न (Examiner Q&A Tip):</div>
        <div class="qa-content">
          <strong>Q:</strong> "What is the unique contribution of each student in this project?"<br>
          <strong>A (उत्तर):</strong> "Sanket led project architecture, Gemini Multimodal OCR & system integration; Sakshi built the responsive UI, Kirana Light mode & Khata WhatsApp hooks; Vaishnavi implemented Web Speech API voice billing & the Verna AI conversational assistant; Rushikesh developed the FastAPI backend, SQLite ACID WAL database, 50-item inventory engine & Excel export."
        </div>
      </div>
      <div class="handover-banner">
        <span>🏁 Final Stage:</span>
        <span class="cue">"The presentation concludes. All 4 members stand ready for Examiner Questions."</span>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== VIVA EXAMINATION TIPS ==================== -->
  <div class="section-title">
    <span>4. परीक्षेत 100% गुण मिळवण्यासाठी विशेष टिप्स (Pro Viva Defense Tips)</span>
  </div>

  <div class="viva-tips-box">
    <h4>💡 प्रेझेंटेशन आणि व्हायव्हा (Viva) दरम्यान लक्षात ठेवायच्या अत्यंत महत्त्वाच्या गोष्टी:</h4>
    <ul>
      <li><strong>आत्मविश्वास आणि शरीराची भाषा (Body Language):</strong> बोलताना स्क्रीनकडे पाठ करू नका; परीक्षक आणि सरांकडे पाहून (Eye Contact) आत्मविश्वासाने बोला. बोलताना आवाजाचा वेग जास्त जलद ठेवू नका.</li>
      <li><strong>स्क्रीनवर बोट दाखवणे (Slide Pointing):</strong> जेव्हा तुम्ही 'Result 1', 'Result 4' किंवा आकडेवारी सांगत असाल, तेव्हा स्क्रीनवरील त्या त्या चार्ट किंवा स्क्रीनशॉटवर हात किंवा पॉइंटर दाखवा (उदा. "As you can see in this live screenshot...").</li>
      <li><strong>हँडओव्हरची शिस्त (Smooth Transitions):</strong> एकाने बोलणे संपवल्यावर लगेच शांत न बसता पुढील सदस्याचे नाव घेऊन आमंत्रित करा (उदा. "I now invite Sakshi to present the problem statement..."). यामुळे टीममधील समन्वय (Teamwork) उत्तम दिसतो आणि गुण वाढतात.</li>
      <li><strong>परीक्षकांनी मध्येच अडवले तर (Handling Interruption):</strong> जर परीक्षकांनी स्लाईड चालू असताना प्रश्न विचारला, तर घाबरू नका. शांतपणे "Yes sir/madam" म्हणा, पूर्ण प्रश्न ऐका, आणि संबंधित क्षेत्राचा जो सदस्य आहे (UI साठी साक्षी, व्हॉइससाठी वैष्णवी, बॅकएंडसाठी ऋषिकेश, AI साठी संकेत) त्याने उत्तर द्यावे.</li>
      <li><strong>मराठी विचारल्यास मराठीत उत्तर द्या:</strong> जर परीक्षकांनी मुद्दाम मराठीत प्रश्न विचारला, तर लगेच मराठीत अगदी सोप्या भाषेत सांगा; जर इंग्रजीत विचारला तर दिलेल्या इंग्रजी वाक्यांचा वापर करा.</li>
      <li><strong>लाइव्ह डेमोची तयारी (Live Demo):</strong> प्रेझेंटेशननंतर परीक्षक नेहमी सिस्टीम चालवून दाखवायला सांगतात. लॅपटॉपवर `http://127.0.0.1:8000` आधीच चालू ठेवा, 50 किराणा आयटम्स दाखवा, आणि मोबाईलवर व्हॉइस बिलिंग किंवा व्हॉट्सॲप मेसेज करून दाखवा.</li>
    </ul>
  </div>

</body>
</html>
"""

def generate_pdf():
    print("=" * 70)
    print("🚀 Generating VernaLedger.AI Presentation Script & Defense Guide PDF")
    print("=" * 70)

    html_file = os.path.abspath("temp_presentation_script.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"Temporary HTML written to: {html_file}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        file_url = "file:///" + html_file.replace("\\", "/")
        print(f"Loading: {file_url}")
        page.goto(file_url, wait_until="networkidle")
        
        print("Rendering high-quality print PDF...")
        page.pdf(
            path=OUTPUT_PDF,
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
            display_header_footer=True,
            header_template='<div style="font-size: 7.5pt; color: #64748b; width: 100%; text-align: right; padding-right: 12mm; font-family: Segoe UI, sans-serif;">VernaLedger.AI: Merchant Pro v7.5 • Final Year Project Presentation Script & Role-Wise Defense Guide</div>',
            footer_template='<div style="font-size: 7.5pt; color: #64748b; width: 100%; display: flex; justify-content: space-between; padding: 0 12mm; font-family: Segoe UI, sans-serif;"><span>Arvind Gavali College of Engineering, Satara • DBATU Lonere</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        )
        browser.close()

    # Clean up temp html
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

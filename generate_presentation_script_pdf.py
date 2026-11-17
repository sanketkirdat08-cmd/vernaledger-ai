"""
VernaLedger.AI: Merchant Pro v7.5
Presentation Script & Role-Wise Defense Guide Generator (23-Slide Comprehensive & Concise Edition)
Features:
- Complete 23 slides matching VernaLedger_Presentation.html
- Prominent Guide & HOD details: Prof. Kaisar Atar (Guide) | Dr. S. Y. Mulla (HOD)
- Detailed Technical Contribution (प्रकल्पातील नक्की योगदान) right next to each member's name
- Prominent Speaker Badges on EVERY slide card: Sanket (6), Sakshi (6), Vaishnavi (5), Rushikesh (6)
- Crisp spoken English (3-4 punchy sentences, 45-60s speech)
- Concise Marathi core concept (2 lines, direct explanation)
- Targeted Examiner Viva Question & Answer per slide
- Smooth English handover cue to next presenter
"""

import os
import sys
from playwright.sync_api import sync_playwright

OUTPUT_PDF = os.path.abspath("VernaLedger_AI_Presentation_Team_Script_and_Viva_Guide.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="utf-8">
<title>VernaLedger.AI - 23-Slide Presentation Defense Guide</title>
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
    line-height: 1.35;
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
      <span class="badge-guide">Project Guide: Prof. Kaisar Atar | HOD: Dr. S. Y. Mulla</span>
    </div>
    <div class="hero-title">VernaLedger.AI <span>Merchant Pro v7.5</span></div>
    <div class="hero-desc">Final Year Major Project Defense Guide • Complete 23-Slide Deck Script (English Spoken + Marathi Meaning)</div>
    
    <div class="guide-strip">
      <div><strong>प्रकल्प मार्गदर्शक (Guide):</strong> Prof. Kaisar Atar</div>
      <div><strong>विभागप्रमुख (HOD):</strong> Dr. S. Y. Mulla</div>
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
          • <strong>इमेज प्री-प्रोसेसिंग:</strong> 960px Lanczos कॉन्ट्रास्ट फिल्टर आणि SHA-256 हॅश द्वारे डुप्लिकेट पावती प्रतिबंध.<br>
          • <strong>प्रकल्प नेतृत्व:</strong> सिस्टीम एकत्रीकरण, उद्दिष्टे, पाईपलाईन आणि अंतिम ओपन डिफेन्स (Q&A).
        </td>
        <td><strong>Slides: 01, 02, 06, 07, 12, 23</strong><br><span style="color: #0284c7; font-weight: 700;">(६ स्लाईड्स)</span></td>
      </tr>
      <tr>
        <td><strong>Sakshi Bhagat</strong><br><span class="tag-member tag-sakshi">Frontend & UI/UX</span></td>
        <td>Roll: 4054<br><span style="font-size: 7pt; color: #64748b;">24065451263502</span></td>
        <td>
          • <strong>UI/UX आर्किटेक्चर:</strong> व्हॅनिला JavaScript आधारित जलद सिंगल पेज ॲप्लिकेशन (SPA) इंटरफेस.<br>
          • <strong>उधारी खातेवही (Khata):</strong> 'उधारी दिली' व 'जमा मिळाले' ऑटो-कॅल्क्युलेशन आणि 1-क्लिक व्हॉट्सॲप UPI पेमेंट लिंक.<br>
          • <strong>किराणा मोड व PWA:</strong> थेट उन्हात स्पष्ट दिसणारा किराणा मोड आणि मोबाईलसाठी 5-टॅब बॉटम टच बार.
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
          • <strong>50 किराणा माल साठा इंजिन:</strong> 50 वस्तूंचा साठा, रिअल-टाइम सर्च आणि बिलांनंतर स्वयंचलित स्टॉक वजावट.<br>
          • <strong>एक्सेल एक्सपोर्ट इंजिन:</strong> XlsxWriter द्वारे देवनागरी मराठी फॉन्टसह थेट `.xlsx` स्प्रेडशीट जनरेशन.
        </td>
        <td><strong>Slides: 08, 09, 10, 11, 15, 17</strong><br><span style="color: #059669; font-weight: 700;">(६ स्लाईड्स)</span></td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== ALL 23 SLIDES ==================== -->
  <div class="sec-heading">
    <span>2. सर्व २३ स्लाईड्सचे मुद्देसूद स्क्रिप्ट (Chronological Presentation Script: Slides 1 to 23)</span>
  </div>

  <!-- SLIDE 01 -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title"><span class="slide-pill">SLIDE 01</span> Cover Page: VernaLedger.AI: Merchant Pro v7.5</div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader & AI) • Slide 1/6</span>
    </div>
    <div class="card-body">
      <div class="box-en">
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Respected Project Guide <strong>Prof. Kaisar Atar sir</strong>, HOD <strong>Dr. S. Y. Mulla sir</strong>, and external examiners, a very good morning. I am <strong>Sanket Kirdat</strong>, leading our team with Sakshi Bhagat, Vaishnavi Dhavale, and Rushikesh Mulik from AGCE Satara. Today, we defend our major project: <strong>'VernaLedger.AI: Merchant Pro v7.5'</strong> — an offline-first vernacular POS suite tailored for India's 63 million kirana merchants to digitize handwritten bills and manage finances with zero English dependency."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          मार्गदर्शक <strong>अतार सर</strong>, विभागप्रमुख <strong>मुल्ला सर</strong> आणि परीक्षकांना आदरपूर्वक नमस्कार करा. स्वतःची व टीमची ओळख करून देऊन प्रकल्पाचे नाव सांगा: हा स्थानिक किराणा दुकानदारांसाठी बनवलेला मराठी AI बिलिंग प्लॅटफॉर्म आहे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What does 'Vernacular' mean? <strong>Ans:</strong> Operating in regional native languages (Marathi) so shopkeepers have zero English dependency.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us see the project overview on Slide 2."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "VernaLedger.AI unites three core capabilities: <strong>First</strong>, Multimodal Vision OCR to scan physical Marathi paper bills in under 1.5 seconds. <strong>Second</strong>, continuous Marathi Voice Billing for hands-free checkout during rush hours. <strong>Third</strong>, a local SQLite ACID Ledger with 1-click WhatsApp UPI payment links and instant Excel export."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          प्रकल्पाचे ३ मुख्य घटक सांगा: १. कागदी पावती १.५ सेकंदात स्कॅन होणे, २. गर्दीत मराठीत बोलून बिल बनणे, आणि ३. सुरक्षित स्थानिक डेटाबेससह व्हॉट्सॲपवर UPI लिंक पाठवणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why offline-first? <strong>Ans:</strong> Rural broadband fluctuates; core ledger transactions commit locally in <2ms without internet lag.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sakshi:</strong> "Now Sakshi will present the critical market problems on Slide 3."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Thank you Sanket. Over 85% of small retailers still rely on manual paper notebooks ('बही-खाते') prone to damage, page loss, and math errors. Unrecorded customer credit ties up working capital, resulting in bad debts. Existing billing apps are English-centric, full of ads, and require slow manual typing."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          ८५% दुकानदार अजूनही कागदी वह्या वापरतात, ज्यामुळे हिशोबाच्या चुका होतात आणि उधारी अडकते. सध्याची ॲप्स इंग्रजीत असल्याने अवघड आहेत.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How much capital is tied in credit? <strong>Ans:</strong> Retailers extend 15-45 days of credit, losing 15-20% working capital due to forgotten credit records.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us examine our motivation on Slide 4."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Our motivation is to eliminate digital literacy barriers. If a merchant can snap a photo or speak Marathi, they can operate VernaLedger without typing. Automated WhatsApp reminders recover debts 60% faster, giving local kiranas the power of enterprise POS at zero hardware cost."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          दुकानदाराला टायपिंग न येताही फक्त फोटो काढून किंवा बोलून बिलिंग करता यावी आणि व्हॉट्सॲपमुळे उधारी ६०% वेगाने वसूल व्हावी हा मुख्य हेतू आहे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why WhatsApp over SMS? <strong>Ans:</strong> WhatsApp has a 98% open rate in India and supports clickable UPI payment links directly in Marathi.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Vaishnavi will now present the market gap analysis on Slide 5."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Thank you Sakshi. Compared to Vyapar, Khatabook, and OKCredit: VernaLedger uniquely provides Multimodal Marathi Bill OCR, continuous Devanagari Voice Billing, a zero-hallucination Gemini AI store assistant, and 50 pre-seeded Kirana commodities with auto stock deduction at zero recurring fee."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          खाताबुक किंवा व्यापार ॲपमध्ये कागदी पावती स्कॅनर नाही, मराठी व्हॉइस बिलिंग नाही आणि AI असिस्टंट नाही; हे सर्व VernaLedger मध्ये उपलब्ध आहे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Is VernaLedger subscription-based? <strong>Ans:</strong> No, it is open, self-hosted, and zero-subscription, keeping merchant data 100% private.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sanket:</strong> "Our leader Sanket will now explain the project objectives on Slide 6."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "We achieved four concrete objectives: 1. Sub-1.5s multimodal receipt token extraction (>96% precision). 2. Continuous Marathi voice billing (`mr-IN`) with zero cutoff. 3. Automated Khata running balance with 1-click WhatsApp UPI links. 4. A 50-item Kirana auto-stock deduction engine and SQL RAG assistant."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          ४ उद्दिष्टे सांगा: १.५ सेकंदात स्कॅनिंग, सलग मराठी व्हॉइस बिलिंग, व्हॉट्सॲप उधारी वसुली, आणि ५० किराणा मालाचा साठा आपोआप वजा होणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you prevent negative stock? <strong>Ans:</strong> Via SQLite constraint `stock_qty = MAX(0, stock_qty - billed_qty)` with visual '🚨 कमी साठा' alert.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us trace the system pipeline on Slide 7."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Our pipeline operates in 4 stages: 1. Ingestion via camera bill capture, voice, or POS keyboard. 2. AI Intelligence via Gemini Flash Vision and NLP parser. 3. ACID Commit in <2ms with automatic stock deduction. 4. Output via thermal print, WhatsApp UPI bill, Excel (.xlsx), and Gemini AI chat."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          ४ टप्पे: इनपुट (कॅमेरा/आवाज) -> AI द्वारे अक्षरे व आकडे ओळखणे -> SQLite डेटाबेसमध्ये सेव्ह व ५० मालातून साठा वजावट -> आउटपुट (पावती/व्हॉट्सॲप/एक्सेल/चॅटबॉट).
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How is math verified? <strong>Ans:</strong> System verifies line item math: quantity × rate = total before committing to the database.</div>
        <div class="handover-mini"><strong>➡️ Handover to Rushikesh:</strong> "Rushikesh will now present our engineering stack and architecture on Slide 8."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Thank you Sanket. Our stack is engineered for zero latency: <strong>FastAPI & Uvicorn</strong> universal ASGI backend, vanilla JS reactive client with zero framework overhead, Web Speech API (`mr-IN`) for voice, Gemini 3.1 Flash Lite for vision OCR, SQLite in WAL mode for sub-2ms commits, and XlsxWriter for Devanagari Excel exports."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          तंत्रज्ञान सांगा: बॅकएंडला FastAPI, फ्रंटएंडला व्हॅनिला JS, आवाजासाठी Web Speech API, डेटाबेससाठी SQLite WAL मोड, आणि मराठी एक्सेलसाठी XlsxWriter.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Why SQLite over MongoDB? <strong>Ans:</strong> Relational ACID integrity is essential for running debt balance calculations; NoSQL lacks atomic joins.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 9 illustrates our modular 3-tier architecture."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "We implement a clean 3-tier architecture: <strong>Presentation Layer</strong> (Cyberpunk/Kirana UI, canvas compression), <strong>Intelligence Layer</strong> (FastAPI routing, Gemini OCR, regex parser, RAG context), and <strong>Persistence Layer</strong> (SQLite tables: receipts, khata, 50-item inventory, expenses, audit logs)."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          ३ स्तर सांगा: १. प्रेझेंटेशन (स्क्रीन व कॅमेरा), २. ॲप्लिकेशन व AI (FastAPI व जेमिनी मॉडेल), आणि ३. डेटाबेस (बिलांचे, उधारीचे, आणि ५० साठ्याचे टेबल्स).
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How are API keys secured? <strong>Ans:</strong> Managed server-side with automatic failover key pools; never exposed to client browser.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 10 details our sequential execution flow."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Step-by-step flow: 1. Merchant captures bill or speaks Marathi. 2. Image is compressed to 960px with SHA-256 duplicate detection. 3. Gemini parses items into typed JSON. 4. Interactive preview grid appears on screen. 5. On Save, SQLite commits, khata updates, and stock auto-deducts."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          कार्यप्रवाह: पावतीचा फोटो/आवाज -> ९६०px कॉम्प्रेशन व डुप्लिकेट तपासणी -> AI द्वारे JSON बिल तयार -> स्क्रीनवर पडताळणी -> डेटाबेस सेव्ह व साठा वजावट.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you block duplicate bills? <strong>Ans:</strong> SHA-256 image hashes are indexed in SQLite; re-scanning the same paper bill triggers an instant block.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Let us review performance benchmarks on Slide 11."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Benchmarks under real kirana workloads: Sub-1.5s OCR Latency, 96.8% Devanagari Extraction Accuracy across 120 test bills, 10ms in-memory store dispatch for AI chat, and sub-2ms local SQLite ACID commit latency with zero checkout delays."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          आकडेवारी सांगा: १.५ सेकंदात स्कॅनिंग, ९६.८% मराठी अक्षरांची अचूकता, १०ms मध्ये AI चॅटबॉट रिस्पॉन्स, आणि २ मिलिसेकंदात डेटाबेस सेव्ह.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is WAL mode? <strong>Ans:</strong> Write-Ahead Logging allows simultaneous concurrent reads and writes, preventing UI lockups.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sanket:</strong> "Sanket will now demonstrate Result 1: Multimodal Scanner on Slide 12."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 1 shows our live Multimodal Scanner. Photographing a physical Marathi bill segments items, weights, and prices into an editable POS grid in under 1.5 seconds. Crucially, saving the bill automatically deducts items from the store's 50 Kirana inventory items (`stock_qty = MAX(0, stock_qty - billed_qty)`)."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          स्क्रीनशॉट दाखवून सांगा: पावतीचा फोटो काढताच १.५ सेकंदात डिजिटल बिल तयार झाले. 'सेव्ह' दाबताच ५० किराणा साठ्यातून साखर किंवा तेलाचे प्रमाण आपोआप कमी होते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you handle faint thermal receipts? <strong>Ans:</strong> Client canvas applies 960px Lanczos contrast sharpening and CLAHE histogram equalization before cloud OCR.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Vaishnavi will now demonstrate Result 2: Voice Billing on Slide 13."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 2 is our Vernacular Voice Billing Engine. During rush hours, typing causes delays. The shopkeeper speaks: 'सागरला २ किलो साखर ८४ रुपये आणि १ तेल १८५ रुपये'. The Web Speech API captures speech continuously without cutoff. Our NLP parser creates the bill, updates credit, and auto-deducts stock."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          दुकानदार माईक दाबून बोलेल: 'सागरला २ किलो साखर ८४ रुपये...'. वाक्य पूर्ण होईपर्यंत माइक चालू राहतो आणि थेट बिल बनते, ज्यामुळे गर्दीत ८५% वेळ वाचतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How do you handle 'पाव किलो'? <strong>Ans:</strong> Custom regex maps vernacular fractions ('पाव' = 0.25kg, 'अर्धा' = 0.5kg) to standard numeric floats.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sakshi:</strong> "Sakshi will now present Result 3: Customer Khata on Slide 14."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 3 is Customer Khata & Udhar Ledger. Merchants record 'उधारी दिली' and 'जमा मिळाले' with live running balances. Clicking the green WhatsApp icon sends a polite Marathi reminder with an embedded dynamic UPI link, enabling customers to pay in 10 seconds via Google Pay or PhonePe."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          उधारी आणि जमा रकमेचा हिशोब. व्हॉट्सॲप आयकॉनवर क्लिक करताच ग्राहकाला नम्र मराठी मेसेज आणि थेट Google Pay/PhonePe ची UPI लिंक जाते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Are WhatsApp links costly? <strong>Ans:</strong> No, uses native URI scheme `wa.me/{phone}?text=...` launching the installed app directly at zero cost.</div>
        <div class="handover-mini"><strong>➡️ Handover to Rushikesh:</strong> "Rushikesh will now explain Result 4: 50 Kirana Inventory Items on Slide 15."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 4 showcases 50 Pre-Seeded Kirana Commodities (grains, pulses, oils, sugar, tea, spices) across metric units (`kg`, `ltr`, `packet`). Key features: real-time search filtering, automatic stock deduction on sales (`stock_qty = MAX(0, stock_qty - billed_qty)`), low-stock '🚨 कमी साठा' alert badges, and 1-click reset."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          ५० मूळ किराणा वस्तू आधीच सेव्ह आहेत. सर्च बारने वस्तू शोधता येते, बिलासोबत साठा आपोआप कमी होतो आणि माल संपत आला की लाल रंगाचा 'कमी साठा' इशारा मिळतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Can merchants add new items? <strong>Ans:</strong> Yes, via the Add Item form with custom units (`kg`, `ltr`, `packet`) and alert thresholds.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Vaishnavi will showcase Result 5: Verna AI Voice Assistant on Slide 16."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 5 is our official Gemini-style Verna AI Assistant. It features a pulsing mic button (`#chatVoiceBtn`), word-by-word streaming (`sendMessageStream`), strict script persistence (Devanagari to Devanagari), and zero-hallucination store SQL context RAG for inventory and sales questions."
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
        <div class="handover-mini"><strong>➡️ Handover to Rushikesh:</strong> "Rushikesh will demonstrate Result 6: Digital Ledger and Excel on Slide 17."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 6 is our Digital Ledger and Excel Export. All transactions are logged with dynamic search and thermal POS reprint. A prominent green button exports professional OpenXML `.xlsx` spreadsheets with auto-fitted columns and full Devanagari UTF-8 font fidelity for CAs and banks via XlsxWriter."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          सर्व बिलांचा कायमस्वरूपी रेकॉर्ड. हिरवे एक्सेल बटण दाबताच मराठी नावांसह सुटसुटीत `.xlsx` फाईल डाऊनलोड होते, जी CA किंवा बँकेला दाखवता येते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How does XlsxWriter handle Marathi? <strong>Ans:</strong> Embeds UTF-8 encoding in workbook strings, preventing character distortion common in basic CSV.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sakshi:</strong> "Sakshi will present Kirana Light Mode and Mobile PWA on Slide 18."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 7 is High-Contrast Kirana Light Mode. Open-shutter kirana stores face intense afternoon sunlight where dark mode is unreadable. Our Kirana Light mode uses crisp white backgrounds, deep navy text, and high-contrast badges for 100% sunlight legibility."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          रस्त्यावरील दुकानात दुपारच्या कडक उन्हात डार्क मोड दिसत नाही; यासाठी पांढऱ्या पार्श्वभूमीवर गडद अक्षरांचा 'किराणा लाईट मोड' बनवला आहे, जो उन्हातही स्पष्ट दिसतो.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How is theme persisted? <strong>Ans:</strong> Stored in `localStorage.getItem('verna_theme')` for instant zero-flicker restoration.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 19 showcases our Mobile PWA."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Result 8 is our Mobile-First Progressive Web App. Shopkeepers use smartphones, not PCs. On mobile, the desktop sidebar converts into an intuitive 5-tab bottom navigation bar (`Scanner`, `Khata`, `Store`, `Ledger`, `Verna AI`), installable on Android homescreens like a native app."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          दुकानदारांच्या फोनसाठी खास डिझाइन; खाली ५ सोपे टॅब मिळतात आणि गुगल क्रोमवरून थेट मोबाईल स्क्रीनवर ॲपसारखे इन्स्टॉल करता येते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> Can it access phone camera directly? <strong>Ans:</strong> Yes, HTML5 input `capture='environment'` launches the rear camera instantly.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 20 summarizes our core advantages."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Core advantages: True vernacular accessibility eliminating literacy barriers; 60% faster debt recovery via WhatsApp UPI links; zero-cost hardware running on existing phones; and offline-first SQLite resilience ensuring billing never halts."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          ४ मोठे फायदे: इंग्रजी न शिकता वापरता येणे, उधारीची ६०% जलद वसुली, वेगळे मशीन न लागणे, आणि इंटरनेट नसले तरी सुरक्षितपणे चालणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> What is the biggest daily saving? <strong>Ans:</strong> Merchants save 2-3 hours daily on manual bookkeeping and eliminate forgotten credit debts.</div>
        <div class="handover-mini"><strong>➡️ Handover to Vaishnavi:</strong> "Vaishnavi will discuss system limitations and future scope on Slide 21."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "System limitations: While local ledger commits, manual POS, and khata are 100% offline, Gemini Flash Vision OCR and RAG reasoning require an active internet connection. Additionally, severely oil-stained or faded receipts require manual review in the editable grid."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          मर्यादा: स्थानिक डेटाबेस व खातेवही ऑफलाइन चालते, पण AI स्कॅनर व चॅटबॉटसाठी इंटरनेट लागते; तसेच फाटलेली पावती असल्यास स्क्रीनवर तपासून घ्यावी लागते.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How to make OCR offline? <strong>Ans:</strong> Integrate quantized on-device lightweight models like MobileNet-OCR in future updates.</div>
        <div class="handover-mini"><strong>➡️ Handover:</strong> "Slide 22 outlines our future enhancements."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "Future roadmap: Standalone Android APK with edge AI models; dynamic UPI QR Bluetooth Soundbox for real-time Marathi audio payment announcements; multi-counter peer-to-peer sync; and automated GST compliance generating ready-to-file GSTR-1 spreadsheets."
        </div>
      </div>
      <div class="box-mr">
        <div class="box-label lbl-mr">📖 मराठी अर्थ (थोडक्यात संदर्भ)</div>
        <div class="text-mr">
          भविष्यातील योजना: ऑफलाइन अँड्रॉइड APK ॲप, 'PhonePe वर ₹250 मिळाले' असा आवाज देणारा UPI साऊंडबॉक्स, एकाच दुकानातील अनेक काऊंटर जोडणे, आणि आपोआप GST टॅक्स शीट तयार करणे.
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini"><strong>🎯 Viva Q:</strong> How will soundbox connect? <strong>Ans:</strong> Via Web Bluetooth API or local websocket daemon on counter smartphone.</div>
        <div class="handover-mini"><strong>➡️ Handover to Sanket:</strong> "Our leader Sanket will now deliver the conclusion on Slide 23."</div>
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
        <div class="box-label lbl-en">🗣️ Spoken English Script (काय बोलायचे)</div>
        <div class="text-en">
          "To conclude: VernaLedger.AI bridges the digital divide for India's 63M+ kirana merchants by uniting Gemini 3.1 Vision OCR, continuous Marathi voice billing, a 50-item inventory auto-deduction engine, official Gemini voice assistant, and SQLite ACID ledger with native Excel export. We sincerely thank our guide <strong>Prof. Kaisar Atar sir</strong>, HOD <strong>Dr. S. Y. Mulla sir</strong>, and AGCE Satara. We now welcome your questions!"
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
    <span>3. परीक्षेत पूर्ण गुण मिळवण्यासाठी ५ सुवर्ण नियम (Top 5 Golden Viva Defense Rules)</span>
  </div>

  <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 5px; padding: 6px 10px; font-size: 7.4pt; line-height: 1.35;">
    <ol style="padding-left: 14px;">
      <li><strong>नेहमी आय-कॉन्टॅक्ट ठेवा:</strong> स्लाईडकडे पाठ करून वाचू नका; परीक्षक आणि अतार सरांकडे पाहून आत्मविश्वासाने बोला.</li>
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
    print("🚀 Generating 23-Slide Presentation Script & Defense Guide PDF")
    print("=" * 70)

    html_file = os.path.abspath("temp_presentation_script_23slides.html")
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

import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# 1. Register Devanagari TrueType Fonts from Windows
font_regular = r'C:\Windows\Fonts\Nirmala.ttc'
pdfmetrics.registerFont(TTFont('Nirmala', font_regular, subfontIndex=0))
pdfmetrics.registerFont(TTFont('Nirmala-Bold', font_regular, subfontIndex=1))

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute total pages and draw elegant headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Nirmala", 8)
        self.setFillColor(colors.HexColor('#64748b'))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 810, "VernaLedger.AI (Merchant Pro v7.5) | संपूर्ण प्रकल्प निर्देशिका व आर्किटेक्चर गाईड")
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(36, 804, 559, 804)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(36, 40, 559, 40)
        self.drawString(36, 28, "AGCE सातारा | AI & DS विभाग | B.Tech Final Year 2026-2027")
        page_str = f"पान {self._pageNumber} / {page_count}"
        self.drawRightString(559, 28, page_str)
        self.restoreState()

def build_pdf(filename="VernaLedger_AI_Project_Architecture_and_File_Directory_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    c_primary = colors.HexColor('#0f172a')     # Slate 900
    c_brand = colors.HexColor('#0284c7')       # Sky 600
    c_accent = colors.HexColor('#059669')      # Emerald 600
    c_dark = colors.HexColor('#1e293b')        # Slate 800
    c_text = colors.HexColor('#334155')        # Slate 700
    c_muted = colors.HexColor('#64748b')       # Slate 500

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Nirmala-Bold',
        fontSize=20,
        leading=24,
        textColor=c_brand,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Nirmala',
        fontSize=11,
        leading=15,
        textColor=c_muted,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Nirmala-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Nirmala-Bold',
        fontSize=11,
        leading=15,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Nirmala',
        fontSize=9,
        leading=13,
        textColor=c_text
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Nirmala-Bold',
        textColor=c_primary
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Nirmala-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Nirmala',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Nirmala-Bold',
        textColor=c_primary
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Nirmala-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0369a1')
    )

    story = []

    # =========================================================================
    # 1. HEADER & HERO SECTION
    # =========================================================================
    story.append(Paragraph("VernaLedger.AI (Merchant Pro v7.5)", title_style))
    story.append(Paragraph("स्थानिक किराणा व MSMEs साठी नेक्स्ट-जनरेशन AI बिलिंग, लेजर व चॅटबॉट सिस्टीम | संपूर्ण प्रकल्प निर्देशिका", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_brand, spaceAfter=10))

    # Academic Dossier Callout Table
    dossier_data = [
        [Paragraph("🏛️ <b>महाविद्यालय:</b>", table_cell_bold), Paragraph("अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)", table_cell_style)],
        [Paragraph("🎓 <b>विद्यापीठ:</b>", table_cell_bold), Paragraph("डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)", table_cell_style)],
        [Paragraph("📚 <b>पदवी व विभाग:</b>", table_cell_bold), Paragraph("B.Tech (कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स - AI & DS) | शैक्षणिक वर्ष: २०२६ – २०२७", table_cell_style)],
        [Paragraph("👨‍🏫 <b>प्रकल्प मार्गदर्शक:</b>", table_cell_bold), Paragraph("<b>प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)</b> (AI & DS विभाग, AGCE सातारा)", table_cell_style)],
        [Paragraph("👨‍💻 <b>डेव्हलपर्स (सर्व ४):</b>", table_cell_bold), Paragraph("<b>१. संकेत किर्दत</b> (Lead Full-Stack AI) | <b>२. साक्षी भगत</b> (UI/UX) | <b>३. वैष्णवी ढवळे</b> (Data Pipeline) | <b>४. ऋषिकेश मुळीक</b> (Database & Ledger)", table_cell_style)]
    ]
    t_dossier = Table(dossier_data, colWidths=[120, 403])
    t_dossier.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_dossier)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 2. EXECUTIVE SUMMARY & 3-TIER ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("१. प्रकल्पाचे ३-टियर तांत्रिक आर्किटेक्चर (3-Tier Technical Architecture)", h1_style))
    arch_desc = (
        "<b>VernaLedger.AI</b> ही एक संपूर्ण मराठी-प्रथम (Vernacular-first) आधुनिक क्लाउड व एज आर्किटेक्चरवर आधारित सिस्टीम आहे. "
        "ही स्थानिक किराणा दुकानदार आणि लहान व्यापाऱ्यांसाठी हस्तलिखित पावती स्कॅनिंग, व्हॉइस बिलिंग, उधारी व्यवस्थापन आणि AI सल्लागार सेवा एकाच ठिकाणी उपलब्ध करून देते."
    )
    story.append(Paragraph(arch_desc, body_style))
    story.append(Spacer(1, 6))

    arch_data = [
        [Paragraph("टियर (Tier)", table_header_style), Paragraph("घटक व तंत्रज्ञान (Components & Technologies)", table_header_style), Paragraph("मुख्य कार्य (Core Functionality)", table_header_style)],
        [
            Paragraph("<b>Tier 1: Client UI</b><br/>(फ्रंटएंड)", table_cell_bold),
            Paragraph("HTML5, Vanilla JavaScript, CSS3 Glassmorphism, Web Speech API, MediaRecorder, PWA Service Worker (sw.js)", table_cell_style),
            Paragraph("वापरकर्त्याचा परस्परसंवाद, डॅशबोर्ड, रिअल-टाइम व्हॉइस रेकॉर्डिंग, कॅमेरा स्कॅनर, ऑफलाइन स्थानिक कॅशिंग.", table_cell_style)
        ],
        [
            Paragraph("<b>Tier 2: Backend AI</b><br/>(सर्व्हरलेस API)", table_cell_bold),
            Paragraph("Python 3.13 + FastAPI, Google Gemini 3.1 Flash Lite (REST Transport), Google Cloud Vision API, Regex NLP Parser", table_cell_style),
            Paragraph("पावती स्कॅनिंग, हस्तलिखित OCR, ऑडिओ ट्रान्सक्रिप्शन, RAG चॅटबॉट, बिझनेस ॲनालिटिक्स, Excel रिपोर्ट निर्मिती.", table_cell_style)
        ],
        [
            Paragraph("<b>Tier 3: Database</b><br/>(डेटा व लेजर)", table_cell_bold),
            Paragraph("SQLite 3 Engine (ACID Compliant, WAL Mode), In-Memory Caching, Native XlsxWriter Engine, WhatsApp/UPI Deeplinks", table_cell_style),
            Paragraph("ग्राहक उधारी (Customer Khata), दैनंदिन विक्री, साठा (Inventory), सुरक्षित व्यवहार इतिहास आणि १-क्लिक बॅकअप.", table_cell_style)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[90, 210, 223])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_brand),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 3. AI FOUNDATIONS: 5 SCANNER PILLARS & 4 CHATBOT PILLARS
    # =========================================================================
    story.append(Paragraph("२. मुख्य AI तंत्रज्ञान पिलर्स (Core AI Architectural Foundations)", h1_style))
    
    pillars_data = [
        [Paragraph("स्कॅनरचे ५ मुख्य AI पिलर्स (Multimodal OCR)", table_header_style), Paragraph("Verna AI चॅटबॉटचे ४ मुख्य पिलर्स (Universal Engine)", table_header_style)],
        [
            Paragraph(
                "<b>१. Vision Transformers (ViTs):</b> पावतीचे लहान व्हिज्युअल पॅचेस बनवून तिरपे, घाईत लिहिलेले व अस्पष्ट मराठी हस्तलिखित अचूक वाचते.<br/>"
                "<b>२. Native Multimodal AI:</b> फोटोचे पिक्सेल आणि भाषा एकाच न्यूरल नेटवर्कद्वारे थेट (End-to-End) समजून घेते.<br/>"
                "<b>३. Google TPU Cloud Acceleration:</b> क्लाउडवरील Tensor Processing Units वर मॉडेल चालल्यामुळे अवघ्या ०.९ ते १.२ सेकंदात निकाल मिळतो.<br/>"
                "<b>४. Context-Aware Attention:</b> अस्पष्ट अंक (उदा. १ की ७) आजूबाजूच्या शब्दांवरून आणि गणिताचा हिशोब (दर × वजन) तपासून आपोआप ओळखते.<br/>"
                "<b>५. Document AI / Cloud Vision Fallback:</b> मुख्य मॉडेलवर अडथळा आल्यास गुगलच्या Document Text Detection API द्वारे पावती अखंड वाचली जाते.",
                table_cell_style
            ),
            Paragraph(
                "<b>१. Native Multimodal Architecture:</b> आवाज आणि मजकूर एकाच न्यूरल नेटवर्कद्वारे अखंडपणे समजून घेते.<br/>"
                "<b>२. High-Accuracy Vernacular ASR:</b> दुकानातील पार्श्वभूमीचा गोंगाट गाळून सातारी, कोल्हापुरी, पुणेरी व ग्रामीण मराठी उच्चार अचूक ओळखते.<br/>"
                "<b>३. Transformer LLM Reasoning (Zero-Hallucination):</b> दुकानाच्या थेट SQLite डेटाबेसमधील हिशोब तपासून १००% अचूक तात्त्विक उत्तरे देते.<br/>"
                "<b>४. Real-Time Low Latency Engine:</b> सब-मिलिसेकंद (१०-१५ ms) इन-मेमरी मेमरी ॲक्सेस आणि Google Gemini द्वारे जागतिक ज्ञान.",
                table_cell_style
            )
        ]
    ]
    t_pillars = Table(pillars_data, colWidths=[261, 262])
    t_pillars.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc')])
    ]))
    story.append(t_pillars)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 4. MASTER FILE DIRECTORY MAP (कोणती फाईल कुठे आहे आणि काय काम करते)
    # =========================================================================
    story.append(Paragraph("३. संपूर्ण प्रकल्प फाईल डिरेक्टरी नकाशा (Project File Directory & Component Map)", h1_style))
    story.append(Paragraph("प्रकल्पातील प्रत्येक महत्त्वाच्या फाईलचे स्थान, उद्देश आणि त्यामधील महत्त्वाचे घटक खालीलप्रमाणे व्यवस्थित मांडले आहेत:", body_style))
    story.append(Spacer(1, 6))

    files_data = [
        [Paragraph("फाईल / फोल्डरचे नाव", table_header_style), Paragraph("स्थान (Path)", table_header_style), Paragraph("प्रकार व स्वरूप", table_header_style), Paragraph("त्यामध्ये काय महत्त्वाचे आहे व मुख्य कार्य", table_header_style)],
        
        # Backend API
        [
            Paragraph("<b>index.py</b>", table_cell_bold),
            Paragraph("<code>api/index.py</code>", badge_style),
            Paragraph("FastAPI सर्व्हरलेस बॅकएंड (110 KB)", table_cell_style),
            Paragraph("प्रकल्पाचे <b>मुख्य AI इंजिन</b>. यात Gemini 3.1 Flash Lite RAG चॅटबॉट, व्हॉइस ट्रान्सक्रिप्शन, डायनॅमिक लांबी नियंत्रण, OCR पावती स्कॅनिंग, SQLite WAL व्यवहार आणि Excel रिपोर्ट जनरेटर समाविष्ट आहे.", table_cell_style)
        ],
        [
            Paragraph("<b>app.py</b>", table_cell_bold),
            Paragraph("<code>app.py</code>", badge_style),
            Paragraph("स्थानिक रनर स्क्रिप्ट (Python)", table_cell_style),
            Paragraph("स्थानिक मशीनवर पोर्ट ८००० वर ॲप सुरू करण्यासाठी Uvicorn रनर. यात <code>reload=True</code> सक्षम असल्याने कोड सेव्ह करताच सर्व्हर आपोआप रीलोड होतो.", table_cell_style)
        ],
        [
            Paragraph("<b>run_local.bat</b>", table_cell_bold),
            Paragraph("<code>run_local.bat</code>", badge_style),
            Paragraph("विंडोज बॅच स्क्रिप्ट", table_cell_style),
            Paragraph("स्थानिक पातळीवर एका डबल-क्लिकमध्ये Uvicorn सर्व्हर सुरू करून डीफॉल्ट ब्राऊझरमध्ये <code>http://127.0.0.1:8000</code> उघडते.", table_cell_style)
        ],

        # Frontend Client
        [
            Paragraph("<b>index.html</b>", table_cell_bold),
            Paragraph("<code>public/index.html</code><br/>& रूट <code>index.html</code>", badge_style),
            Paragraph("सिंगल पेज ॲप्लिकेशन (SPA UI)", table_cell_style),
            Paragraph("संपूर्ण फ्रंटएंड डॅशबोर्ड, स्मार्ट स्कॅनर कॅमेरा व्ह्यू, व्हॉइस बिलिंग माइक व्हिज्युअलायझर, ग्राहक उधारी वही (Khata), साठा व्यवस्थापन आणि Verna AI स्टुडिओ चॅटबॉट इंटरफेस.", table_cell_style)
        ],
        [
            Paragraph("<b>app.js</b>", table_cell_bold),
            Paragraph("<code>public/app.js</code><br/>& रूट <code>app.js</code>", badge_style),
            Paragraph("क्लायंट-साइड जावास्क्रिप्ट (117 KB)", table_cell_style),
            Paragraph("फ्रंटएंड लॉजिक, MediaRecorder द्वारे ऑडिओ रेकॉर्डिंग, बेस६४ एन्कोडिंग, API कॉल्स, थर्मल प्रिंट जनरेशन, कॅल्क्युलेटर, व्हॉट्सॲप स्मरणपत्र ट्रिगर आणि स्टेट मॅनेजमेंट.", table_cell_style)
        ],
        [
            Paragraph("<b>style.css</b>", table_cell_bold),
            Paragraph("<code>public/style.css</code><br/>& रूट <code>style.css</code>", badge_style),
            Paragraph("CSS3 स्टाईलशीट (63 KB)", table_cell_style),
            Paragraph("मॉडर्न डार्क सायबरपंक / किराणा कम्फर्ट थीम, ग्लासमोर्फिझम कार्ड्स, हाय-कॉन्ट्रास्ट फॉन्ट्स, निऑन अ‍ॅक्सेंट बार, आणि मोबाईल रिस्पॉन्सिव्ह ग्रिड मांडणी.", table_cell_style)
        ],
        [
            Paragraph("<b>sw.js & manifest</b>", table_cell_bold),
            Paragraph("<code>public/sw.js</code><br/><code>manifest.webmanifest</code>", badge_style),
            Paragraph("PWA कॉन्फिगरेशन", table_cell_style),
            Paragraph("प्रोग्रेसिव्ह वेब ॲप (PWA) सपोर्ट. ॲप मोबाईलवर नेटिव्ह ॲपप्रमाणे इन्स्टॉल करता येते आणि नेटवर्क खंडित झाल्यास ऑफलाइन कॅशिंग प्रदान करते.", table_cell_style)
        ],

        # Database
        [
            Paragraph("<b>ledger.db</b>", table_cell_bold),
            Paragraph("<code>ledger.db</code>", badge_style),
            Paragraph("SQLite 3 डेटाबेस फाईल (135 KB)", table_cell_style),
            Paragraph("ग्राहकांची माहिती (customers), उधारी वही (customer_khata), किराणा साठा (inventory), बिलांचे व्यवहार (transactions) आणि व्यवसाय खर्च (expenses) सुरक्षित साठवते.", table_cell_style)
        ],
        [
            Paragraph("<b>backups/</b>", table_cell_bold),
            Paragraph("<code>backups/*.db</code>", badge_style),
            Paragraph("डेटाबेस बॅकअप डिरेक्टरी", table_cell_style),
            Paragraph("डेटाबेसमधील माहितीचे टाइमस्टॅम्पसह स्वयंचलित सुरक्षित बॅकअप्स (Auto-Snapshots), जेणेकरून डेटा गहाळ होण्याची भीती नसते.", table_cell_style)
        ],

        # Credentials & Config
        [
            Paragraph("<b>secrets.toml</b>", table_cell_bold),
            Paragraph("<code>.streamlit/secrets.toml</code>", badge_style),
            Paragraph("स्थानिक गुप्त चाव्या (TOML)", table_cell_style),
            Paragraph("स्थानिक वातावरणातील गुगल जेमिनी API चावी (<code>GEMINI_API_KEY</code>) सुरक्षित ठेवण्याचे ठिकाण. गिटवर ही फाईल सुरक्षितपणे इग्नोर केली जाते.", table_cell_style)
        ],
        [
            Paragraph("<b>vercel.json</b>", table_cell_bold),
            Paragraph("<code>vercel.json</code>", badge_style),
            Paragraph("क्लाउड डिप्लॉयमेंट कॉन्फिग", table_cell_style),
            Paragraph("Vercel सर्व्हरलेस फंक्शन राऊट्स (<code>/api/(.*) -> api/index.py</code>), CORS हेडर, मेमरी अलोकेशन आणि ६० सेकंद टाइमआउट नियम.", table_cell_style)
        ],
        [
            Paragraph("<b>requirements.txt</b>", table_cell_bold),
            Paragraph("<code>requirements.txt</code>", badge_style),
            Paragraph("पायथन पॅकेजेस यादी", table_cell_style),
            Paragraph("प्रकल्पासाठी आवश्यक पायथन लायब्ररीज: <code>fastapi</code>, <code>uvicorn</code>, <code>google-generativeai</code>, <code>xlsxwriter</code>, <code>reportlab</code> इत्यादी.", table_cell_style)
        ],

        # Presentation & Documentation
        [
            Paragraph("<b>Presentation.html</b>", table_cell_bold),
            Paragraph("<code>VernaLedger_Presentation.html</code>", badge_style),
            Paragraph("इंटरअॅक्टिव्ह 3D सादरीकरण (140 KB)", table_cell_style),
            Paragraph("अंतिम वर्षाच्या सेमििनार व व्हायव्हासाठी तयार केलेले आधुनिक ३डी स्लाइडशो. यात कॉलेजचे नाव, विद्यापीठ, गाईड, ४ डेव्हलपर्स आणि लाइव्ह ॲप स्क्रीनशॉट्स समाविष्ट आहेत.", table_cell_style)
        ],
        [
            Paragraph("<b>Project_Report.docx</b>", table_cell_bold),
            Paragraph("<code>VernaLedger_AI_...Report.docx</code>", badge_style),
            Paragraph("अंतिम प्रकल्प अहवाल (2.19 MB)", table_cell_style),
            Paragraph("DBATU/AGCE च्या अधिकृत फॉरमॅटनुसार तयार केलेला सविस्तर <b>Final Year Project Report</b> (Word फाईल), ज्यामध्ये सर्व चॅप्टर्स, मॅथ्स आणि आर्किटेक्चर आहे.", table_cell_style)
        ],
        [
            Paragraph("<b>Project_Synopsis.docx</b>", table_cell_bold),
            Paragraph("<code>VernaLedger_AI_...Synopsis.docx</code>", badge_style),
            Paragraph("अधिकृत प्रकल्प सारांश (216 KB)", table_cell_style),
            Paragraph("प्रकल्पाचा अधिकृत सिनॉप्सिस (Synopsis), ज्यामध्ये समस्या विधान, प्रस्तावित पद्धती, उद्दिष्टे आणि संभाव्य निकाल दिले आहेत.", table_cell_style)
        ],
        [
            Paragraph("<b>Assets & Media</b>", table_cell_bold),
            Paragraph("<code>college_logo.jpeg</code>, <code>architecture_diagram.png</code>", badge_style),
            Paragraph("प्रतिमा व आकृत्या", table_cell_style),
            Paragraph("कॉलेजचा अधिकृत लोगो (AGCE Satara), सिस्टम आर्किटेक्चर आकृती, फ्लोचार्ट आणि ॲप डॅशबोर्डचे लाइव्ह स्क्रीनशॉट्स.", table_cell_style)
        ]
    ]

    t_files = Table(files_data, colWidths=[95, 110, 105, 213])
    t_files.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_brand),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_files)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 5. CORE API ENDPOINTS REFERENCE
    # =========================================================================
    story.append(Paragraph("४. मुख्य सर्व्हरलेस API एंडपॉइंट्स संदर्भावली (Core API Endpoints Reference)", h1_style))
    
    api_data = [
        [Paragraph("पद्धती (Method)", table_header_style), Paragraph("एंडपॉइंट (Endpoint Route)", table_header_style), Paragraph("इनपुट डेटा (Input)", table_header_style), Paragraph("कार्य व आउटपुट (Function & Response)", table_header_style)],
        [
            Paragraph("<b>POST</b>", badge_style),
            Paragraph("<code>/api/rag-chat</code>", table_cell_bold),
            Paragraph("<code>{ message, audio_data, lang }</code>", table_cell_style),
            Paragraph("<b>Verna AI चॅटबॉट:</b> व्हॉइस/टेक्स्ट प्रश्न समजून Google Gemini 3.1 द्वारे दुकान हिशोब किंवा जागतिक ज्ञानाचे अचूक मराठीत उत्तर देते.", table_cell_style)
        ],
        [
            Paragraph("<b>POST</b>", badge_style),
            Paragraph("<code>/api/scan-receipt</code>", table_cell_bold),
            Paragraph("<code>{ image_data, language }</code>", table_cell_style),
            Paragraph("<b>स्मार्ट स्कॅनर:</b> ५ AI पिलर्सद्वारे हस्तलिखित मराठी पावतीतील वस्तू, वजन, दर व एकूण रकमांचा अचूक डिजिटल डेटा काढते.", table_cell_style)
        ],
        [
            Paragraph("<b>POST</b>", badge_style),
            Paragraph("<code>/api/voice-billing</code>", table_cell_bold),
            Paragraph("<code>{ audio_data, mime_type }</code>", table_cell_style),
            Paragraph("<b>व्हॉइस बिलिंग:</b> दुकानातील आवाजाचे थेट बिलात रूपांतर करते व ग्राहकाच्या खात्यावर व्यवहार नोंदवते.", table_cell_style)
        ],
        [
            Paragraph("<b>GET/POST</b>", badge_style),
            Paragraph("<code>/api/customers</code>", table_cell_bold),
            Paragraph("<code>{ customer_name, phone }</code>", table_cell_style),
            Paragraph("<b>ग्राहक उधारी वही:</b> ग्राहकांची यादी, एकूण उधारी, नवीन ग्राहक जोडणे व १-क्लिक WhatsApp स्मरणपत्र लिंक.", table_cell_style)
        ],
        [
            Paragraph("<b>GET/POST</b>", badge_style),
            Paragraph("<code>/api/inventory</code>", table_cell_bold),
            Paragraph("<code>{ item_name, stock_qty... }</code>", table_cell_style),
            Paragraph("<b>साठा व्यवस्थापन:</b> किराणा वस्तूंचा साठा, विक्री दर आणि कमी साठा (Low stock) अलर्ट व्यवस्थापन.", table_cell_style)
        ],
        [
            Paragraph("<b>GET</b>", badge_style),
            Paragraph("<code>/api/export-excel</code>", table_cell_bold),
            Paragraph("<i>None (Direct Download)</i>", table_cell_style),
            Paragraph("<b>एक्सेल रिपोर्ट:</b> <code>xlsxwriter</code> द्वारे संपूर्ण व्यवसायाची सुंदर फॉरमॅट केलेली <code>.xlsx</code> फाईल डाउनलोड होते.", table_cell_style)
        ]
    ]
    t_api = Table(api_data, colWidths=[65, 120, 138, 200])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_api)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 6. LOCAL EXECUTION & CLOUD DEPLOYMENT GUIDE
    # =========================================================================
    story.append(Paragraph("५. प्रकल्प कसा चालवायचा? (Execution & Deployment Quick Guide)", h1_style))
    
    exec_data = [
        [Paragraph("वातावरण (Environment)", table_header_style), Paragraph("कमांड / पद्धत (Command / Action)", table_header_style), Paragraph("तपशील व सूचना (Details & Notes)", table_header_style)],
        [
            Paragraph("<b>स्थानिक संगणक</b><br/>(Localhost 8000)", table_cell_bold),
            Paragraph("<code>run_local.bat</code> वर डबल क्लिक करा<br/>किंवा <code>python app.py</code>", table_cell_style),
            Paragraph("Uvicorn सर्व्हर पोर्ट ८००० वर सुरू होतो (<code>http://127.0.0.1:8000</code>). <code>reload=True</code> असल्याने फाईल सेव्ह करताच बदल तात्काळ लागू होतात.", table_cell_style)
        ],
        [
            Paragraph("<b>Vercel क्लाउड</b><br/>(Live Production)", table_cell_bold),
            Paragraph("<code>git add .</code><br/><code>git commit -m 'update'</code><br/><code>git push origin main</code>", table_cell_style),
            Paragraph("GitHub <code>main</code> ब्रँचवर पुश करताच Vercel आपोआप संपूर्ण ॲप व सर्व्हरलेस फंक्शन्स क्लाउडवर लाईव्ह डिप्लॉय करते.", table_cell_style)
        ],
        [
            Paragraph("<b>ब्राऊझर कॅश क्लिअर</b><br/>(Hard Reload)", table_cell_bold),
            Paragraph("ब्राऊझरमध्ये <b>Ctrl + F5</b> दाबा<br/>किंवा DevTools मध्ये 'Empty Cache'", table_cell_style),
            Paragraph("वेब ब्राऊझर जुन्या जावास्क्रिप्ट फाईल्स कॅशमध्ये ठेवू नयेत म्हणून व्हर्जनिंग पॅरामीटर (उदा. <code>?v=31.0</code>) वापरले आहे.", table_cell_style)
        ]
    ]
    t_exec = Table(exec_data, colWidths=[100, 180, 243])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_exec)

    # Build document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: High-quality PDF guide generated successfully at: {os.path.abspath(filename)}")
    print(f"File size: {os.path.getsize(filename):,} bytes")

if __name__ == "__main__":
    build_pdf()

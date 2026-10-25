import sys

with open("api/index.py", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Rushikesh Mulik individual answers
old_mulik_en = '''    if is_mulik and not is_all_devs_query:
        if is_english:
            answer = """👨‍💻 **Rushikesh Mulik**:
• **Role:** Co-Developer (Database & Ledger Architecture)
• **Key Contributions:** SQLite ACID Database Architecture, Customer Ledger (उधारी वही), Real-Time Transaction Engine, and Balance Sheet Management.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👨‍💻 **ऋषिकेश मुळीक (Rushikesh Mulik)**:
• **भूमिका:** सह-विकासक (Co-Developer - Database & Ledger Architecture)
• **महत्त्वाचे योगदान:** SQLite ACID डेटाबेस आर्किटेक्चर, ग्राहक खाते (उधारी वही), रिअल-टाइम लेजर व्यवस्थापन आणि बॅलन्स शीट इंजिन.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **प्रकल्प मार्गदर्शक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)"""'''

new_mulik_en = '''    if is_mulik and not is_all_devs_query:
        if is_english:
            answer = """👨‍💻 **Rushikesh Mulik**:
• **Roll No:** 4004
• **PRN No:** 23065451263005
• **Role:** Co-Developer (Database & Ledger Architecture)
• **Key Contributions:** SQLite ACID Database Architecture, Customer Ledger (उधारी वही), Real-Time Transaction Engine, and Balance Sheet Management.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👨‍💻 **ऋषिकेश मुळीक (Rushikesh Mulik)**:
• **रोल नंबर (Roll No):** 4004
• **पीआरएन नंबर (PRN No):** 23065451263005
• **भूमिका:** सह-विकासक (Co-Developer - Database & Ledger Architecture)
• **महत्त्वाचे योगदान:** SQLite ACID डेटाबेस आर्किटेक्चर, ग्राहक खाते (उधारी वही), रिअल-टाइम लेजर व्यवस्थापन आणि बॅलन्स शीट इंजिन.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **प्रकल्प मार्गदर्शक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)"""'''

# 2. Sakshi Bhagat individual answers
old_bhagat_en = '''    elif is_bhagat and not is_all_devs_query:
        if is_english:
            answer = """👩‍💻 **Sakshi Bhagat**:
• **Role:** Co-Developer (UI/UX & System Design)
• **Key Contributions:** Responsive Cyberpunk Business Studio UI/UX, Dynamic Theme Engine, Accessibility, and Voice-to-UI Interaction Design.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👩‍💻 **साक्षी भगत (Sakshi Bhagat)**:
• **भूमिका:** सह-विकासक (Co-Developer - UI/UX & System Design)
• **महत्त्वाचे योगदान:** सायबरपंक बिझनेस स्टुडिओ UI/UX डिझाईन, रिस्पॉन्सिव्ह मोबाईल/डेस्कटॉप इंटरफेस आणि व्हॉईस-टू-UI इंटरअॅक्शन डिझाईन.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **प्रकल्प मार्गदर्शक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)"""'''

new_bhagat_en = '''    elif is_bhagat and not is_all_devs_query:
        if is_english:
            answer = """👩‍💻 **Sakshi Bhagat**:
• **Roll No:** 4054
• **PRN No:** 24065451263502
• **Role:** Co-Developer (UI/UX & System Design)
• **Key Contributions:** Responsive Cyberpunk Business Studio UI/UX, Dynamic Theme Engine, Accessibility, and Voice-to-UI Interaction Design.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👩‍💻 **साक्षी भगत (Sakshi Bhagat)**:
• **रोल नंबर (Roll No):** 4054
• **पीआरएन नंबर (PRN No):** 24065451263502
• **भूमिका:** सह-विकासक (Co-Developer - UI/UX & System Design)
• **महत्त्वाचे योगदान:** सायबरपंक बिझनेस स्टुडिओ UI/UX डिझाईन, रिस्पॉन्सिव्ह मोबाईल/डेस्कटॉप इंटरफेस आणि व्हॉईस-टू-UI इंटरअॅक्शन डिझाईन.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **प्रकल्प मार्गदर्शक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)"""'''

# 3. Vaishnavi Dhavale individual answers
old_dhawale_en = '''    elif is_dhawale and not is_all_devs_query:
        if is_english:
            answer = """👩‍💻 **Vaishnavi Dhawale**:
• **Role:** Co-Developer (Multilingual Data Pipeline)
• **Key Contributions:** Multilingual Marathi/Hindi/English NLP, Regional ASR Dialect Datasets, Vernacular Voice Pipeline, and Audio Transcription Processing.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👩‍💻 **वैष्णवी ढवळे (Vaishnavi Dhawale)**:
• **भूमिका:** सह-विकासक (Co-Developer - Multilingual Data Pipeline)
• **महत्त्वाचे योगदान:** बहुभाषिक (मराठी/इंग्रजी/हिंदी) NLP डेटा पाईपलाईन, प्रादेशिक (सातारी/पुणेरी/कोल्हापुरी) ASR उच्चार डेटासेट आणि ऑडिओ प्रोसेसिंग.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **प्रकल्प मार्गदर्शक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)"""'''

new_dhawale_en = '''    elif is_dhawale and not is_all_devs_query:
        if is_english:
            answer = """👩‍💻 **Vaishnavi Dhavale**:
• **Roll No:** 4056
• **PRN No:** 24065451263504
• **Role:** Co-Developer (Multilingual Data Pipeline)
• **Key Contributions:** Multilingual Marathi/Hindi/English NLP, Regional ASR Dialect Datasets, Vernacular Voice Pipeline, and Audio Transcription Processing.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👩‍💻 **वैष्णवी ढवळे (Vaishnavi Dhavale)**:
• **रोल नंबर (Roll No):** 4056
• **पीआरएन नंबर (PRN No):** 24065451263504
• **भूमिका:** सह-विकासक (Co-Developer - Multilingual Data Pipeline)
• **महत्त्वाचे योगदान:** बहुभाषिक (मराठी/इंग्रजी/हिंदी) NLP डेटा पाईपलाईन, प्रादेशिक (सातारी/पुणेरी/कोल्हापुरी) ASR उच्चार डेटासेट आणि ऑडिओ प्रोसेसिंग.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **प्रकल्प मार्गदर्शक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)"""'''

# 4. Sanket Kirdat individual answers
old_kirdat_en = '''    elif is_kirdat_individual and not is_all_devs_query:
        if is_english:
            answer = """👨‍💻 **Sanket Kirdat**:
• **Role:** Lead Full-Stack AI Developer & Project Head
• **Key Contributions:** Complete VernaLedger.AI Architecture, Multimodal AI Engine (ViT & Document AI), Vernacular Marathi Voice Billing, and Full-Stack Platform.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👨‍💻 **संकेत किर्दत (Sanket Kirdat)**:
• **भूमिका:** प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
• **महत्त्वाचे योगदान:** संपूर्ण VernaLedger.AI सिस्टीम आर्किटेक्चर, मल्टिमोडल AI स्कॅनर, अस्खलित मराठी व्हॉईस बिलिंग आणि फुल-स्टॅक प्लॅटफॉर्म विकसक.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)"""'''

new_kirdat_en = '''    elif is_kirdat_individual and not is_all_devs_query:
        if is_english:
            answer = """👨‍💻 **Sanket Kirdat**:
• **Roll No:** 4060
• **PRN No:** 24065451263508
• **Role:** Lead Full-Stack AI Developer & Project Head
• **Key Contributions:** Complete VernaLedger.AI Architecture, Multimodal AI Engine (ViT & Document AI), Vernacular Marathi Voice Billing, and Full-Stack Platform.
• **Department:** B.Tech Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Project Guide:** Prof. Kaisar Atar Sir"""
        else:
            answer = """👨‍💻 **संकेत किर्दत (Sanket Kirdat)**:
• **रोल नंबर (Roll No):** 4060
• **पीआरएन नंबर (PRN No):** 24065451263508
• **भूमिका:** प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
• **महत्त्वाचे योगदान:** संपूर्ण VernaLedger.AI सिस्टीम आर्किटेक्चर, मल्टिमोडल AI स्कॅनर, अस्खलित मराठी व्हॉईस बिलिंग आणि फुल-स्टॅक प्लॅटफॉर्म विकसक.
• **विभाग:** B.Tech कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (AI & DS)
• **महाविद्यालय:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (AGCE Satara)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)"""'''

# 5. Team listings
old_team_lead_en = '''👨‍💻 **Lead Developer**:
• **Sanket Kirdat** – Lead Full-Stack AI Developer & Project Head
  *(Architected the core VernaLedger.AI engine, multimodal scanner, voice billing, and end-to-end platform)*

👥 **Co-Developers**:
२. **Sakshi Bhagat** – Co-Developer (UI/UX & System Design)
३. **Vaishnavi Dhawale** – Co-Developer (Multilingual Data Pipeline)
४. **Rushikesh Mulik** – Co-Developer (Database & Ledger Architecture)'''

new_team_lead_en = '''👨‍💻 **Lead Developer**:
• **Sanket Kirdat** [Roll: 4060 | PRN: 24065451263508] – Lead Full-Stack AI Developer & Project Head
  *(Architected the core VernaLedger.AI engine, multimodal scanner, voice billing, and end-to-end platform)*

👥 **Co-Developers**:
२. **Sakshi Bhagat** [Roll: 4054 | PRN: 24065451263502] – Co-Developer (UI/UX & System Design)
३. **Vaishnavi Dhavale** [Roll: 4056 | PRN: 24065451263504] – Co-Developer (Multilingual Data Pipeline)
४. **Rushikesh Mulik** [Roll: 4004 | PRN: 23065451263005] – Co-Developer (Database & Ledger Architecture)'''

old_team_lead_mr = '''👨‍💻 **प्रकल्प प्रमुख आणि लीड डेव्हलपर (Lead Developer)**:
• **संकेत किर्दत (Sanket Kirdat)** – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
  *(संपूर्ण VernaLedger.AI आर्किटेक्चर, मल्टिमोडल स्कॅनर, व्हॉईस बिलिंग आणि फुल-स्टॅक प्लॅटफॉर्म विकसक)*

👥 **सह-विकासक टीम (Co-Developers)**:
२. **साक्षी भगत (Sakshi Bhagat)** – सह-विकासक (UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** – सह-विकासक (Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** – सह-विकासक (Database & Ledger Architecture)'''

new_team_lead_mr = '''👨‍💻 **प्रकल्प प्रमुख आणि लीड डेव्हलपर (Lead Developer)**:
• **संकेत किर्दत (Sanket Kirdat)** [रोल: 4060 | PRN: 24065451263508] – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
  *(संपूर्ण VernaLedger.AI आर्किटेक्चर, मल्टिमोडल स्कॅनर, व्हॉईस बिलिंग आणि फुल-स्टॅक प्लॅटफॉर्म विकसक)*

👥 **सह-विकासक टीम (Co-Developers)**:
२. **साक्षी भगत (Sakshi Bhagat)** [रोल: 4054 | PRN: 24065451263502] – सह-विकासक (UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhavale)** [रोल: 4056 | PRN: 24065451263504] – सह-विकासक (Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** [रोल: 4004 | PRN: 23065451263005] – सह-विकासक (Database & Ledger Architecture)'''

old_team_all_en = '''👨‍💻 **Project Development Team (All 4 Developers)**:
1. **Sanket Kirdat** – Lead Full-Stack AI Developer & Project Head
2. **Sakshi Bhagat** – Co-Developer (UI/UX & System Design)
3. **Vaishnavi Dhawale** – Co-Developer (Multilingual Data Pipeline)
4. **Rushikesh Mulik** – Co-Developer (Database & Ledger Architecture)'''

new_team_all_en = '''👨‍💻 **Project Development Team (All 4 Developers)**:
1. **Sanket Kirdat** (Roll: 4060 | PRN: 24065451263508) – Lead Full-Stack AI Developer & Project Head
2. **Sakshi Bhagat** (Roll: 4054 | PRN: 24065451263502) – Co-Developer (UI/UX & System Design)
3. **Vaishnavi Dhavale** (Roll: 4056 | PRN: 24065451263504) – Co-Developer (Multilingual Data Pipeline)
4. **Rushikesh Mulik** (Roll: 4004 | PRN: 23065451263005) – Co-Developer (Database & Ledger Architecture)'''

old_team_all_mr = '''👨‍💻 **प्रकल्प डेव्हलपमेंट टीम (Project Development Team - सर्व ४ डेव्हलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** – सह-विकासक (Co-Developer - UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** – सह-विकासक (Co-Developer - Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** – सह-विकासक (Co-Developer - Database & Ledger Architecture)'''

new_team_all_mr = '''👨‍💻 **प्रकल्प डेव्हलपमेंट टीम (Project Development Team - सर्व ४ डेव्हलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** (Roll: 4060 | PRN: 24065451263508) – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** (Roll: 4054 | PRN: 24065451263502) – सह-विकासक (Co-Developer - UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhavale)** (Roll: 4056 | PRN: 24065451263504) – सह-विकासक (Co-Developer - Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** (Roll: 4004 | PRN: 23065451263005) – सह-विकासक (Co-Developer - Database & Ledger Architecture)'''

old_dossier_devs_en = '''👨‍💻 **Project Development Team (All 4 Developers)**:
1. **Sanket Kirdat** – Lead Full-Stack AI Developer & Project Head
2. **Sakshi Bhagat** – Co-Developer (UI/UX & System Design)
3. **Vaishnavi Dhawale** – Co-Developer (Multilingual Data Pipeline)
4. **Rushikesh Mulik** – Co-Developer (Database & Ledger Architecture)'''

old_dossier_devs_hi = '''👨‍💻 **प्रोजेक्ट डेवलपमेंट टीम (सभी 4 डेवलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** – प्रोजेक्ट हेड और मुख्य डेवलपर (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** – सह-डेवलपर (UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** – सह-डेवलपर (Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** – सह-डेवलपर (Database & Ledger Architecture)'''

new_dossier_devs_hi = '''👨‍💻 **प्रोजेक्ट डेवलपमेंट टीम (सभी 4 डेवलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** (Roll: 4060 | PRN: 24065451263508) – प्रोजेक्ट हेड और मुख्य डेवलपर (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** (Roll: 4054 | PRN: 24065451263502) – सह-डेवलपर (UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** (Roll: 4056 | PRN: 24065451263504) – सह-डेवलपर (Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** (Roll: 4004 | PRN: 23065451263005) – सह-डेवलपर (Database & Ledger Architecture)'''

old_dossier_devs_mr = '''👨‍💻 **प्रकल्प डेव्हलपमेंट टीम (Project Team Members - सर्व ४ डेव्हलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** – सह-विकासक (Co-Developer - UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** – सह-विकासक (Co-Developer - Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** – सह-विकासक (Co-Developer - Database & Ledger Architecture)'''

new_dossier_devs_mr = '''👨‍💻 **प्रकल्प डेव्हलपमेंट टीम (Project Team Members - सर्व ४ डेव्हलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** (Roll: 4060 | PRN: 24065451263508) – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** (Roll: 4054 | PRN: 24065451263502) – सह-विकासक (Co-Developer - UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** (Roll: 4056 | PRN: 24065451263504) – सह-विकासक (Co-Developer - Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** (Roll: 4004 | PRN: 23065451263005) – सह-विकासक (Co-Developer - Database & Ledger Architecture)'''

# 6. Gemini instruction
old_gemini_prompt = '''    - Complete Development Team (All 4 Developers):
      1. Sanket Kirdat (Lead Full-Stack AI Developer)
      2. Sakshi Bhagat (Co-Developer - UI/UX & System Design)
      3. Vaishnavi Dhawale (Co-Developer - Multilingual Data Pipeline)
      4. Rushikesh Mulik (Co-Developer - Database & Ledger Architecture)
    - CRITICAL DEVELOPER INSTRUCTION: When asked about developers, team, or who built this project, you MUST ALWAYS explicitly list ALL 4 DEVELOPERS (1. Sanket Kirdat - Lead, 2. Sakshi Bhagat, 3. Vaishnavi Dhawale, 4. Rushikesh Mulik) and Guide Prof. Kaisar Atar Sir (AGCE Satara). Never omit any member.'''

new_gemini_prompt = '''    - Complete Development Team (All 4 Developers):
      1. Sanket Kirdat (Roll: 4060 | PRN: 24065451263508) - Lead Full-Stack AI Developer
      2. Sakshi Bhagat (Roll: 4054 | PRN: 24065451263502) - Co-Developer - UI/UX & System Design
      3. Vaishnavi Dhavale (Roll: 4056 | PRN: 24065451263504) - Co-Developer - Multilingual Data Pipeline
      4. Rushikesh Mulik (Roll: 4004 | PRN: 23065451263005) - Co-Developer - Database & Ledger Architecture
    - CRITICAL DEVELOPER INSTRUCTION: When asked about developers, team, or who built this project, you MUST ALWAYS explicitly list ALL 4 DEVELOPERS with their Roll No and PRN No: (1. Sanket Kirdat - Roll: 4060, PRN: 24065451263508; 2. Sakshi Bhagat - Roll: 4054, PRN: 24065451263502; 3. Vaishnavi Dhavale - Roll: 4056, PRN: 24065451263504; 4. Rushikesh Mulik - Roll: 4004, PRN: 23065451263005) and Guide Prof. Kaisar Atar Sir (AGCE Satara). Never omit any member.'''

for old, new in [
    (old_mulik_en, new_mulik_en),
    (old_bhagat_en, new_bhagat_en),
    (old_dhawale_en, new_dhawale_en),
    (old_kirdat_en, new_kirdat_en),
    (old_team_lead_en, new_team_lead_en),
    (old_team_lead_mr, new_team_lead_mr),
    (old_team_all_en, new_team_all_en),
    (old_team_all_mr, new_team_all_mr),
    (old_dossier_devs_hi, new_dossier_devs_hi),
    (old_dossier_devs_mr, new_dossier_devs_mr),
    (old_gemini_prompt, new_gemini_prompt)
]:
    c = c.replace(old.replace('\r\n', '\n'), new.replace('\r\n', '\n'))

with open("api/index.py", "w", encoding="utf-8") as f:
    f.write(c)

print("api/index.py updated successfully!")

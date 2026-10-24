import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('api/index.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove Mahadev Kirana Store fallback in system prompts
code = code.replace(
    'Default: "महादेव किराणा स्टोअर".',
    'Default: "किराणा पावती" (or "Kirana Store").'
)

# 2. Add Trilingual support to Full Project Dossier (Branch D)
old_dossier = '''    # D. Full Project Dossier (Triggered for 'project baddal mahiti sanga', 'project chi mahiti sanga', etc.)
    elif (any(p in lower_msg for p in ['प्रकल्प', 'प्रकल्पा', 'प्रोजेक्ट', 'project', 'vernaledger', 'सॉफ्टवेअर', 'software', 'सिस्टीम', 'system']) and any(k in lower_msg for k in ['सर्व माहिती', 'पूर्ण माहिती', 'सविस्तर माहिती', 'संपूर्ण माहिती', 'माहिती सांगा', 'माहिती द्या', 'माहिती', 'mahiti', 'info', 'details', 'about', 'overview', 'उद्दिष्ट', 'हेतू', 'वैशिष्ट्य', 'baddal', 'vishayi', 'sanga', 'dya', 'काय आहे', 'kay ahe'])) or any(k in lower_msg for k in ['project details', 'about project', 'clg developer', 'college developer', 'प्रकल्प माहिती', 'प्रोजेक्ट माहिती']):
        answer = """🏛️ **महाविद्यालय व शैक्षणिक तपशील (College & Academic Info)**:
• **प्रकल्प शीर्षक:** VernaLedger.AI (Merchant Pro v7.5)
• **पदवी:** B.Tech (Bachelor of Technology)
• **विभाग:** कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (Artificial Intelligence & Data Science - AI & DS)
• **महाविद्यालयाचे नाव:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (Arvind Gavali College of Engineering, Satara - AGCE)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **शैक्षणिक वर्ष:** २०२६ – २०२७ (2026 - 2027)

🎓 **प्रकल्प मार्गदर्शक (Project Guide)**:
• **मार्गदर्शक प्राध्यापक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)
• **विभाग:** Department of Artificial Intelligence & Data Science, AGCE Satara

👨‍💻 **प्रकल्प डेव्हलपमेंट टीम (Project Team Members - सर्व ४ डेव्हलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** – सह-विकासक (Co-Developer - UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** – सह-विकासक (Co-Developer - Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** – सह-विकासक (Co-Developer - Database & Ledger Architecture)

🎯 **प्रकल्पाचा मुख्य हेतू व वैशिष्ट्ये (Project Overview)**:
स्थानिक किराणा दुकानदार, व्यापारी आणि MSMEs साठी मराठी भाषेत थेट काम करणारी नेक्स्ट-जनरेशन AI बिलिंग आणि फायनान्शियल सिस्टीम:
१. 📸 **स्मार्ट मल्टिमोडल स्कॅनर:** हस्तलिखित मराठी पावत्यांचे ५ AI पिलर्सद्वारे (ViT, Multimodal, TPUs, Attention, Document AI) क्षणार्धात अचूक डिजिटल बिलात रूपांतर.
२. 🎙️ **स्थानिक व्हॉइस बिलिंग:** मराठी भाषेत बोलून थेट पावती तयार करणे.
३. 💳 **डिजिटल ग्राहक खाते (उधारी वही):** उधारी आणि जमा रकमेचा स्वयंचलित हिशोब व १-क्लिक व्हॉट्सॲप / UPI स्मरणपत्र.
४. 🤖 **Verna AI स्टुडिओ (चॅटबॉट):** दुकानातील नफा, विक्री, उधारी आणि साठ्याची माहिती अवघ्या काही मिलिसेकंदांत देणारा व्यवसाय सल्लागार.
५. 📊 **एक्सेल एक्सपोर्ट आणि प्रिंटर सपोर्ट:** संपूर्ण हिशोबाची एक-क्लिक Excel (.xlsx) फाईल व थर्मल प्रिंट पावती."""'''

new_dossier = '''    # D. Full Project Dossier (Triggered for 'project baddal mahiti sanga', 'project chi mahiti sanga', etc.)
    elif (any(p in lower_msg for p in ['प्रकल्प', 'प्रकल्पा', 'प्रोजेक्ट', 'project', 'vernaledger', 'सॉफ्टवेअर', 'software', 'सिस्टीम', 'system']) and any(k in lower_msg for k in ['सर्व माहिती', 'पूर्ण माहिती', 'सविस्तर माहिती', 'संपूर्ण माहिती', 'माहिती सांगा', 'माहिती द्या', 'माहिती', 'mahiti', 'info', 'details', 'about', 'overview', 'उद्दिष्ट', 'हेतू', 'वैशिष्ट्य', 'baddal', 'vishayi', 'sanga', 'dya', 'काय आहे', 'kay ahe', 'chi mahiti', 'baddal mahiti'])) or any(k in lower_msg for k in ['project details', 'about project', 'clg developer', 'college developer', 'प्रकल्प माहिती', 'प्रोजेक्ट माहिती', 'project mahiti', 'project baddal']):
        if is_english:
            answer = """🏛️ **College & Academic Information**:
• **Project Title:** VernaLedger.AI (Merchant Pro v7.5)
• **Degree:** B.Tech (Bachelor of Technology)
• **Department:** Artificial Intelligence & Data Science (AI & DS)
• **College:** Arvind Gavali College of Engineering, Satara (AGCE Satara)
• **University:** Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere
• **Academic Year:** 2026 - 2027

🎓 **Project Guide**:
• **Faculty Guide:** Prof. Kaisar Atar Sir (Department of AI & DS, AGCE Satara)

👨‍💻 **Project Development Team (All 4 Developers)**:
1. **Sanket Kirdat** – Lead Full-Stack AI Developer & Project Head
2. **Sakshi Bhagat** – Co-Developer (UI/UX & System Design)
3. **Vaishnavi Dhawale** – Co-Developer (Multilingual Data Pipeline)
4. **Rushikesh Mulik** – Co-Developer (Database & Ledger Architecture)

🎯 **Key Highlights & Core Capabilities**:
A next-generation AI-powered billing & digital ledger platform built for retail merchants and MSMEs:
1. 📸 **Smart Multimodal Scanner:** Real-time conversion of handwritten Marathi & English receipts to digital POS bills via ViTs & Document AI.
2. 🎙️ **Vernacular Voice Billing:** Hands-free billing by speaking natural language commands in Marathi, Hindi, or English.
3. 💳 **Customer Khata (Digital Ledger):** Automated debt tracking and 1-click WhatsApp / UPI payment reminders.
4. 🤖 **Verna AI Business Studio:** Real-time business advisor for profit, revenue, stock analytics, and store intelligence.
5. 📊 **Excel & Thermal Print:** Instant XLSX spreadsheet downloads and POS thermal receipt printing."""
        elif is_hindi:
            answer = """🏛️ **महाविद्यालय व शैक्षणिक विवरण (College & Academic Info)**:
• **प्रोजेक्ट शीर्षक:** VernaLedger.AI (Merchant Pro v7.5)
• **डिग्री:** B.Tech (Bachelor of Technology)
• **विभाग:** आर्टिफिशियल इंटेलिजेंस और डेटा साइंस (AI & DS)
• **महाविद्यालय:** अरविंद गवली कॉलेज ऑफ इंजीनियरिंग, सातारा (AGCE Satara)
• **विश्वविद्यालय:** डॉ. बाबासाहेब आंबेडकर तकनीकी विश्वविद्यालय, लोनेरे (DBATU)
• **शैक्षणिक वर्ष:** 2026 - 2027

🎓 **प्रोजेक्ट मार्गदर्शक (Project Guide)**:
• **मार्गदर्शक प्राध्यापक:** प्रो. कैसर अत्तार सर (Prof. Kaisar Atar Sir)
• **विभाग:** Department of AI & DS, AGCE Satara

👨‍💻 **प्रोजेक्ट डेवलपमेंट टीम (सभी 4 डेवलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** – प्रोजेक्ट हेड और मुख्य डेवलपर (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** – सह-डेवलपर (UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** – सह-डेवलपर (Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** – सह-डेवलपर (Database & Ledger Architecture)

🎯 **प्रोजेक्ट के मुख्य उद्देश्य व विशेषताएं**:
भारतीय किराना दुकानदारों और व्यापारियों के लिए स्थानीय भाषा में काम करने वाला AI बिलिंग और डिजिटल लेजर सिस्टम:
१. 📸 **स्मार्ट मल्टीमॉडल स्कैनर:** हस्तलिखित बिलों का ViT और Document AI द्वारा 1 सेकंड में डिजिटल बिल में रूपांतरण।
२. 🎙️ **स्थानीय वॉइस बिलिंग:** आवाज से बोलकर सीधे रसीद तैयार करना।
३. 💳 **डिजिटल ग्राहक खाता (उधारी बही):** उधारी और जमा का हिसाब व 1-क्लिक WhatsApp / UPI भुगतान रिमाइंडर।
४. 🤖 **Verna AI स्टूडियो (चैटबॉट):** दुकान के लाभ, बिक्री, उधारी और स्टॉक की सटीक जानकारी देने वाला AI सलाहकार।
५. 📊 **एक्सेल एक्सपोर्ट और प्रिंटर सपोर्ट:** सम्पूर्ण हिसाब की 1-क्लिक Excel (.xlsx) फ़ाइल व थर्मल प्रिंट रसीद।"""
        else:
            answer = """🏛️ **महाविद्यालय व शैक्षणिक तपशील (College & Academic Info)**:
• **प्रकल्प शीर्षक:** VernaLedger.AI (Merchant Pro v7.5)
• **पदवी:** B.Tech (Bachelor of Technology)
• **विभाग:** कृत्रिम बुद्धिमत्ता आणि डेटा सायन्स (Artificial Intelligence & Data Science - AI & DS)
• **महाविद्यालयाचे नाव:** अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (Arvind Gavali College of Engineering, Satara - AGCE)
• **विद्यापीठ:** डॉ. बाबासाहेब आंबेडकर तंत्रज्ञान विद्यापीठ, लोणेरे (DBATU University, Lonere)
• **शैक्षणिक वर्ष:** २०२६ – २०२७ (2026 - 2027)

🎓 **प्रकल्प मार्गदर्शक (Project Guide)**:
• **मार्गदर्शक प्राध्यापक:** प्रा. कैसर अत्तार सर (Prof. Kaisar Atar Sir)
• **विभाग:** Department of Artificial Intelligence & Data Science, AGCE Satara

👨‍💻 **प्रकल्प डेव्हलपमेंट टीम (Project Team Members - सर्व ४ डेव्हलपर्स)**:
१. **संकेत किर्दत (Sanket Kirdat)** – प्रकल्प प्रमुख आणि मुख्य विकसक (Lead Full-Stack AI Developer)
२. **साक्षी भगत (Sakshi Bhagat)** – सह-विकासक (Co-Developer - UI/UX & System Design)
३. **वैष्णवी ढवळे (Vaishnavi Dhawale)** – सह-विकासक (Co-Developer - Multilingual Data Pipeline)
४. **ऋषिकेश मुळीक (Rushikesh Mulik)** – सह-विकासक (Co-Developer - Database & Ledger Architecture)

🎯 **प्रकल्पाचा मुख्य हेतू व वैशिष्ट्ये (Project Overview)**:
स्थानिक किराणा दुकानदार, व्यापारी आणि MSMEs साठी मराठी भाषेत थेट काम करणारी नेक्स्ट-जनरेशन AI बिलिंग आणि फायनान्शियल सिस्टीम:
१. 📸 **स्मार्ट मल्टिमोडल स्कॅनर:** हस्तलिखित मराठी पावत्यांचे ५ AI पिलर्सद्वारे (ViT, Multimodal, TPUs, Attention, Document AI) क्षणार्धात अचूक डिजिटल बिलात रूपांतर.
२. 🎙️ **स्थानिक व्हॉइस बिलिंग:** मराठी भाषेत बोलून थेट पावती तयार करणे.
३. 💳 **डिजिटल ग्राहक खाते (उधारी वही):** उधारी आणि जमा रकमेचा स्वयंचलित हिशोब व १-क्लिक व्हॉट्सॲप / UPI स्मरणपत्र.
४. 🤖 **Verna AI स्टुडिओ (चॅटबॉट):** दुकानातील नफा, विक्री, उधारी आणि साठ्याची माहिती अवघ्या काही मिलिसेकंदांत देणारा व्यवसाय सल्लागार.
५. 📊 **एक्सेल एक्सपोर्ट आणि प्रिंटर सपोर्ट:** संपूर्ण हिशोबाची एक-क्लिक Excel (.xlsx) फाईल व थर्मल प्रिंट पावती."""'''

# Normalize newlines
def normalize(s):
    return s.replace('\r\n', '\n')

code_norm = normalize(code)
old_norm = normalize(old_dossier)
new_norm = normalize(new_dossier)

if old_norm in code_norm:
    code_norm = code_norm.replace(old_norm, new_norm)
    print("Replaced dossier block in api/index.py successfully!")
else:
    print("Error: old_dossier not found in api/index.py.")

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(code_norm)

print("Saved updated api/index.py.")

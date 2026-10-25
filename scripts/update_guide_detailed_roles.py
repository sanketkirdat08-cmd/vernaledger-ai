import os

with open("generate_project_directory_guide_pdf.py", "r", encoding="utf-8") as f:
    c = f.read()

old_snippet = '''        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 4px; vertical-align:top;">👨‍💻 प्रकल्प डेव्हलपर्स:</td>
          <td style="border:none; padding:2px 4px; line-height: 1.6;">
            <b>१. संकेत किर्दत</b> (Roll: 4060 | PRN: 24065451263508) &bull; टीम लीडर व AI डेव्हलपर (Team Leader & AI Developer)<br>
            <b>२. साक्षी भगत</b> (Roll: 4054 | PRN: 24065451263502) &bull; फ्रंटएंड व UI डेव्हलपर (Frontend & UI Developer)<br>
            <b>३. वैष्णवी ढवळे</b> (Roll: 4056 | PRN: 24065451263504) &bull; व्हॉइस बिलिंग व AI डेव्हलपर (Voice Billing & AI Developer)<br>
            <b>४. ऋषिकेश मुळीक</b> (Roll: 4004 | PRN: 23065451263005) &bull; बॅकएंड व डेटाबेस डेव्हलपर (Backend & Database Developer)
          </td>
        </tr>'''

new_snippet = '''        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:4px 4px; vertical-align:top;">👨‍💻 प्रकल्प डेव्हलपर्स व कार्यविभागणी:</td>
          <td style="border:none; padding:4px 4px; line-height: 1.45;">
            <div style="margin-bottom: 5px;">
              <b>१. संकेत किर्दत</b> (Roll: 4060 | PRN: 24065451263508) &bull; <span class="pill pill-blue">टीम लीडर व मुख्य AI डेव्हलपर</span><br/>
              <span style="color:#475569; font-size:7.5pt;">↳ <b>प्रकल्पातील काम:</b> Google Gemini Flash OCR व Vision Transformer (ViT) मॉडेल इंटिग्रेशन, हस्तलिखित मराठी पावती स्कॅनिंग, क्लायंट-सर्व्हर एंड-टू-एंड आर्किटेक्चर व टीमचे तांत्रिक नेतृत्व.</span>
            </div>
            <div style="margin-bottom: 5px;">
              <b>२. साक्षी भगत</b> (Roll: 4054 | PRN: 24065451263502) &bull; <span class="pill pill-green">फ्रंटएंड व UI/UX डेव्हलपर</span><br/>
              <span style="color:#475569; font-size:7.5pt;">↳ <b>प्रकल्पातील काम:</b> HTML5/CSS3 आधारित रिस्पॉन्सिव्ह वेब व मोबाईल इंटरफेस, सायबरपंक ग्लास-मॉर्फिझम लेआउट, १-क्लिक 'किराणा डे/नाईट मोड' थीम इंजिन आणि डिजिटल पावती प्रिव्ह्यू डिझाईन.</span>
            </div>
            <div style="margin-bottom: 5px;">
              <b>३. वैष्णवी ढवळे</b> (Roll: 4056 | PRN: 24065451263504) &bull; <span class="pill pill-purple">व्हॉइस बिलिंग व AI डेव्हलपर</span><br/>
              <span style="color:#475569; font-size:7.5pt;">↳ <b>प्रकल्पातील काम:</b> अस्खलित मराठी व्हॉइस बिलिंग, Web Speech API व मीडिया रेकॉर्डरद्वारे तोंडी बोलण्यावरून पावती तयार करणे, ग्रामीण मराठी ASR पार्सर आणि Edge TTS ऑडिओ फीडबॅक.</span>
            </div>
            <div>
              <b>४. ऋषिकेश मुळीक</b> (Roll: 4004 | PRN: 23065451263005) &bull; <span class="pill pill-slate">बॅकएंड व डेटाबेस डेव्हलपर</span><br/>
              <span style="color:#475569; font-size:7.5pt;">↳ <b>प्रकल्पातील काम:</b> SQLite ACID डेटाबेस आर्किटेक्चर, ग्राहक डिजिटल उधारी वही (Khata Ledger), रिअल-टाइम व्यवहार लॉग्स आणि XlsxWriter द्वारे १-क्लिक Excel (.xlsx) रिपोर्ट डाऊनलोड कार्यप्रणाली.</span>
            </div>
          </td>
        </tr>'''

c = c.replace(old_snippet.replace('\r\n', '\n'), new_snippet.replace('\r\n', '\n'))

with open("generate_project_directory_guide_pdf.py", "w", encoding="utf-8") as f:
    f.write(c)

print("generate_project_directory_guide_pdf.py updated with detailed role explanations!")


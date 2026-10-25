with open("generate_project_directory_guide_pdf.py", "r", encoding="utf-8") as f:
    c = f.read()

old_block = '''        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 4px; vertical-align:top;">👨‍💻 प्रकल्प डेव्हलपर्स:</td>
          <td style="border:none; padding:2px 4px; line-height: 1.5;">
            <b>१. संकेत किर्दत</b> (Roll: 4060 | PRN: 24065451263508) &bull; Lead Full-Stack AI<br>
            <b>२. साक्षी भगत</b> (Roll: 4054 | PRN: 24065451263502) &bull; UI/UX System Design<br>
            <b>३. वैष्णवी ढवळे</b> (Roll: 4056 | PRN: 24065451263504) &bull; Multilingual Data Pipeline<br>
            <b>४. ऋषिकेश मुळीक</b> (Roll: 4004 | PRN: 23065451263005) &bull; Database & Ledger Architecture
          </td>
        </tr>'''

new_block = '''        <tr>
          <td style="font-weight:700; color:#0369a1; border:none; padding:2px 4px; vertical-align:top;">👨‍💻 प्रकल्प डेव्हलपर्स:</td>
          <td style="border:none; padding:2px 4px; line-height: 1.6;">
            <b>१. संकेत किर्दत</b> (Roll: 4060 | PRN: 24065451263508) &bull; टीम लीडर व AI डेव्हलपर (Team Leader & AI Developer)<br>
            <b>२. साक्षी भगत</b> (Roll: 4054 | PRN: 24065451263502) &bull; फ्रंटएंड व UI डेव्हलपर (Frontend & UI Developer)<br>
            <b>३. वैष्णवी ढवळे</b> (Roll: 4056 | PRN: 24065451263504) &bull; व्हॉइस बिलिंग व AI डेव्हलपर (Voice Billing & AI Developer)<br>
            <b>४. ऋषिकेश मुळीक</b> (Roll: 4004 | PRN: 23065451263005) &bull; बॅकएंड व डेटाबेस डेव्हलपर (Backend & Database Developer)
          </td>
        </tr>'''

c = c.replace(old_block.replace('\r\n', '\n'), new_block.replace('\r\n', '\n'))

with open("generate_project_directory_guide_pdf.py", "w", encoding="utf-8") as f:
    f.write(c)

print("generate_project_directory_guide_pdf.py updated!")


with open("create_presentation.py", "r", encoding="utf-8") as f:
    c = f.read()

old_s1 = '''    p_names1 = tf.add_paragraph()
    p_names1.text = "1. Sanket Kirdat (Roll: 4060 | PRN: 24065451263508)   •   2. Sakshi Bhagat (Roll: 4054 | PRN: 24065451263502)"
    p_names1.font.name = FONT_BODY
    p_names1.font.size = Pt(11)
    p_names1.font.bold = True
    p_names1.font.color.rgb = COLOR_WHITE
    p_names1.alignment = PP_ALIGN.CENTER

    p_names2 = tf.add_paragraph()
    p_names2.text = "3. Vaishnavi Dhavale (Roll: 4056 | PRN: 24065451263504)   •   4. Rushikesh Mulik (Roll: 4004 | PRN: 23065451263005)"'''

new_s1 = '''    p_names1 = tf.add_paragraph()
    p_names1.text = "1. Sanket Kirdat (Team Leader & AI Dev | Roll: 4060)   •   2. Sakshi Bhagat (Frontend & UI Dev | Roll: 4054)"
    p_names1.font.name = FONT_BODY
    p_names1.font.size = Pt(11)
    p_names1.font.bold = True
    p_names1.font.color.rgb = COLOR_WHITE
    p_names1.alignment = PP_ALIGN.CENTER

    p_names2 = tf.add_paragraph()
    p_names2.text = "3. Vaishnavi Dhavale (Voice Billing & AI Dev | Roll: 4056)   •   4. Rushikesh Mulik (Backend & Database | Roll: 4004)"'''

old_s23 = 'p_names.text = "Project Team: Sanket Kirdat (Roll: 4060 | PRN: 24065451263508) • Sakshi Bhagat (Roll: 4054 | PRN: 24065451263502)\\nVaishnavi Dhavale (Roll: 4056 | PRN: 24065451263504) • Rushikesh Mulik (Roll: 4004 | PRN: 23065451263005)"'
new_s23 = 'p_names.text = "Project Team: Sanket Kirdat (Team Leader & AI Developer) • Sakshi Bhagat (Frontend & UI Developer)\\nVaishnavi Dhavale (Voice Billing & AI Developer) • Rushikesh Mulik (Backend & Database Developer)"'

c = c.replace(old_s1.replace('\r\n', '\n'), new_s1.replace('\r\n', '\n'))
c = c.replace(old_s23, new_s23)

with open("create_presentation.py", "w", encoding="utf-8") as f:
    f.write(c)

print("create_presentation.py updated with simple roles!")

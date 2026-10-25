import sys

with open("create_presentation.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace slide 1 team names
old_s1 = '''    names = [
        "1. Sanket Kirdat",
        "2. Sakshi Bhagat",
        "3. Vaishnavi Dhawale",
        "4. Rushikesh Mulik"
    ]
    p_names = tf.add_paragraph()
    p_names.text = "       •  ".join(names)
    p_names.font.name = FONT_BODY
    p_names.font.size = Pt(13)
    p_names.font.bold = True
    p_names.font.color.rgb = COLOR_WHITE
    p_names.alignment = PP_ALIGN.CENTER'''

new_s1 = '''    p_names1 = tf.add_paragraph()
    p_names1.text = "1. Sanket Kirdat (Roll: 4060 | PRN: 24065451263508)   •   2. Sakshi Bhagat (Roll: 4054 | PRN: 24065451263502)"
    p_names1.font.name = FONT_BODY
    p_names1.font.size = Pt(11)
    p_names1.font.bold = True
    p_names1.font.color.rgb = COLOR_WHITE
    p_names1.alignment = PP_ALIGN.CENTER

    p_names2 = tf.add_paragraph()
    p_names2.text = "3. Vaishnavi Dhavale (Roll: 4056 | PRN: 24065451263504)   •   4. Rushikesh Mulik (Roll: 4004 | PRN: 23065451263005)"
    p_names2.font.name = FONT_BODY
    p_names2.font.size = Pt(11)
    p_names2.font.bold = True
    p_names2.font.color.rgb = COLOR_WHITE
    p_names2.alignment = PP_ALIGN.CENTER'''

old_s1_box = "t_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(3.2), Inches(9.733), Inches(1.8))"
new_s1_box = "t_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(3.1), Inches(10.933), Inches(2.2))"

# Replace slide 23 team names
old_s23 = 'p_names.text = "Project Team: Sanket Kirdat • Sakshi Bhagat • Vaishnavi Dhawale • Rushikesh Mulik"'
new_s23 = '''p_names.text = "Project Team: Sanket Kirdat (Roll: 4060 | PRN: 24065451263508) • Sakshi Bhagat (Roll: 4054 | PRN: 24065451263502)\\nVaishnavi Dhavale (Roll: 4056 | PRN: 24065451263504) • Rushikesh Mulik (Roll: 4004 | PRN: 23065451263005)"'''

old_s23_box = "qa_box = s23.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.5), Inches(4.5), Inches(8.333), Inches(1.8))"
new_s23_box = "qa_box = s23.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(4.3), Inches(10.333), Inches(2.2))"

# Normalize line breaks for replacement
content = content.replace(old_s1_box, new_s1_box)
content = content.replace(old_s1.replace('\r\n', '\n'), new_s1.replace('\r\n', '\n'))
content = content.replace(old_s23_box, new_s23_box)
content = content.replace(old_s23, new_s23)

with open("create_presentation.py", "w", encoding="utf-8") as f:
    f.write(content)

print("create_presentation.py updated successfully!")


with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find slide 12 snippet
s12_start = content.find('<!-- SLIDE 12: RESULT 1 - SMART SCANNER & LIVE POS -->')
s12_end = content.find('<!-- SLIDE 13: RESULT 2 - VERNACULAR VOICE BILLING -->')

print("Slide 12 found:", s12_start, s12_end)
# print without image base64
s12_text = content[s12_start:s12_end]
img_pos = s12_text.find('data:image/png;base64,')
if img_pos != -1:
    print("S12 before img:")
    print(s12_text[:img_pos])
    close_img = s12_text.find('</section>', img_pos)
    print("S12 after img:")
    print(s12_text[close_img:])

# Let's find slide 15 snippet
s15_start = content.find('<!-- SLIDE 15: RESULT 4 - STORE OPERATIONS & EXPENSES -->')
s15_end = content.find('<!-- SLIDE 16: RESULT 5 - NEURAL AI STUDIO (RAG) -->')

print("\nSlide 15 found:", s15_start, s15_end)
s15_text = content[s15_start:s15_end]
img_pos15 = s15_text.find('data:image/png;base64,')
if img_pos15 != -1:
    print("S15 before img:")
    print(s15_text[:img_pos15])
    close_img15 = s15_text.find('</section>', img_pos15)
    print("S15 after img:")
    print(s15_text[close_img15:])

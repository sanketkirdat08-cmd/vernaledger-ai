with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect CSS styles length and structure
start_css = text.find('<style>')
end_css = text.find('</style>')
print(f"CSS length: {end_css - start_css}")

# Let's see the fonts imported
head_end = text.find('</head>')
print("Head content:")
print(text[:start_css])

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect line range of style block
start_css = text.find('<style>')
end_css = text.find('</style>')
print(f"Style tag found at: {start_css} to {end_css}")

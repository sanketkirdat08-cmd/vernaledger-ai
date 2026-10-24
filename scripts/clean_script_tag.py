with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    <script src="app.js?v=35.0"></script>\n', '')
text = text.replace('    <script src="app.js?v=35.0"></script>\r\n', '')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Cleaned script tag successfully.')

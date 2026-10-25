with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('app.js?v=36.0', 'app.js?v=37.0')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Bumped version to v=37.0")


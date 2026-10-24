with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_str = 'document.getElementById("receipt-shop-name").innerText = formatLocalizedName(bill.vendor_name, state.lang) || (isMr ? "महादेव किराणा स्टोअर" : "Mahadev Kirana Store");'
new_str = 'document.getElementById("receipt-shop-name").innerText = formatLocalizedName(bill.vendor_name, state.lang) || (state.lang === "en" ? "Kirana Store" : (state.lang === "hi" ? "किराना स्टोर" : "किराणा स्टोअर"));'

text = text.replace(old_str, new_str)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(text)

with open('public/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated receipt-shop-name fallback in app.js and public/app.js')


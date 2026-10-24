import re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

from translations_master import TRANSLATIONS

with open('app.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

# Extract existing i18n
mr_match = re.search(r'mr:\s*\{(.*?)\n\s*\},', js_code, re.DOTALL)
en_match = re.search(r'en:\s*\{(.*?)\n\s*\},', js_code, re.DOTALL)
hi_match = re.search(r'hi:\s*\{(.*?)\n\s*\}\n\};', js_code, re.DOTALL)

def parse_dict(text):
    result = {}
    lines = text.split('\n')
    for line in lines:
        m = re.match(r'^\s*([a-zA-Z0-9_-]+):\s*"(.*)"\s*,?\s*$', line)
        if m:
            result[m.group(1)] = m.group(2).replace('\\"', '"')
    return result

mr_dict = parse_dict(mr_match.group(1)) if mr_match else {}
en_dict = parse_dict(en_match.group(1)) if en_match else {}
hi_dict = parse_dict(hi_match.group(1)) if hi_match else {}

print(f"Existing MR keys: {len(mr_dict)}, EN keys: {len(en_dict)}, HI keys: {len(hi_dict)}")

# Update with TRANSLATIONS
for k, v in TRANSLATIONS.items():
    if "mr" in v: mr_dict[k] = v["mr"]
    if "en" in v: en_dict[k] = v["en"]
    if "hi" in v: hi_dict[k] = v["hi"]

# Cross-fill any keys missing between mr, en, hi
all_keys = sorted(list(set(mr_dict.keys()) | set(en_dict.keys()) | set(hi_dict.keys())))

for k in all_keys:
    if k not in mr_dict: mr_dict[k] = en_dict.get(k, "")
    if k not in en_dict: en_dict[k] = mr_dict.get(k, "")
    if k not in hi_dict: hi_dict[k] = mr_dict.get(k, "")

print(f"Total merged keys for all 3 languages: {len(all_keys)}")

def format_js_dict(d):
    lines = []
    for k in sorted(d.keys()):
        val = d[k].replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'        {k}: "{val}",')
    # Remove trailing comma on last item
    if lines:
        lines[-1] = lines[-1].rstrip(',')
    return '\n'.join(lines)

new_i18n_code = f"""// I18N Translations (100% Complete Trilingual Marathi / English / Hindi Coverage)
const i18n = {{
    mr: {{
{format_js_dict(mr_dict)}
    }},
    en: {{
{format_js_dict(en_dict)}
    }},
    hi: {{
{format_js_dict(hi_dict)}
    }}
}};"""

# Replace old i18n in js_code
pattern = r'// I18N Translations.*?\nconst i18n = \{.*?\n\};'
js_code, n = re.subn(pattern, new_i18n_code, js_code, flags=re.DOTALL)
print(f"Replaced i18n block: {n} match.")

# Now update resetBillCard in js_code
old_reset = """function resetBillCard() {
    state.currentBill = null;
    const vendorEl = document.getElementById("bill-vendor-name");
    const dateEl = document.getElementById("bill-date");
    const tbody = document.getElementById("bill-items-tbody");
    const totalEl = document.getElementById("bill-grand-total");
    const badge = document.getElementById("bill-badge-status");

    if (vendorEl) vendorEl.value = "";
    if (dateEl) {
        dateEl.value = new Date().toISOString().split("T")[0];
    }
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-slate); padding: 24px 10px; font-size: 0.82rem;">📸 पावती स्कॅन करा किंवा 🎙️ व्हॉइस बोला — वस्तू व हिशोब येथे आपोआप दिसेल.</td></tr>`;
    }
    if (totalEl) totalEl.innerText = "₹0.00";
    if (badge) {
        badge.innerText = "READY";
        badge.className = "user-role-badge badge-admin";
    }
}"""

new_reset = """function resetBillCard() {
    state.currentBill = null;
    const vendorEl = document.getElementById("bill-vendor-name");
    const dateEl = document.getElementById("bill-date");
    const tbody = document.getElementById("bill-items-tbody");
    const totalEl = document.getElementById("bill-grand-total");
    const badge = document.getElementById("bill-badge-status");
    const dict = i18n[state.lang] || i18n.mr;

    if (vendorEl) vendorEl.value = "";
    if (dateEl) {
        dateEl.value = new Date().toISOString().split("T")[0];
    }
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-slate); padding: 24px 10px; font-size: 0.82rem;">${dict.empty_bill_placeholder || "📸 पावती स्कॅन करा किंवा 🎙️ व्हॉइस बोला — वस्तू व हिशोब येथे आपोआप दिसेल."}</td></tr>`;
    }
    if (totalEl) totalEl.innerText = "₹0.00";
    if (badge) {
        badge.innerText = dict.receipt_preview_ready || "READY";
        badge.className = "user-role-badge badge-admin";
    }
}"""

if old_reset in js_code:
    js_code = js_code.replace(old_reset, new_reset)
    print("Updated resetBillCard function.")
else:
    print("Warning: old_reset not found exactly.")

# Now update applyLanguage in js_code
old_apply_pattern = r'function applyLanguage\(\)\s*\{.*?\n\}'
new_apply = """function applyLanguage() {
    const dict = i18n[state.lang] || i18n.mr;
    const isMr = state.lang === "mr";
    const language = getLanguage();

    // 1. Language buttons & selects
    const mBtn = document.getElementById("mobile-lang-btn");
    if (mBtn) mBtn.innerText = `🌐 ${language.label}`;
    const dBtn = document.getElementById("desktop-lang-btn");
    if (dBtn) dBtn.innerText = `🌐 ${language.label}`;
    const hBtn = document.getElementById("hud-lang-btn");
    if (hBtn) hBtn.innerText = `🌐 ${language.label}`;
    const cBtn = document.getElementById("chat-lang-btn");
    if (cBtn) {
        if (state.lang === "mr") cBtn.innerText = "🌐 भाषा: मराठी (mr-IN)";
        else if (state.lang === "hi") cBtn.innerText = "🌐 भाषा: हिन्दी (hi-IN)";
        else cBtn.innerText = "🌐 Language: English (en-IN)";
    }
    document.querySelectorAll(".language-select").forEach(select => {
        select.value = state.lang;
    });

    // 2. All [data-i18n] text nodes
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key] !== undefined) {
            el.innerHTML = dict[key];
        }
    });

    // 3. All [data-i18n-ph] input placeholders
    document.querySelectorAll("[data-i18n-ph]").forEach(el => {
        const key = el.getAttribute("data-i18n-ph");
        if (dict[key] !== undefined) {
            el.placeholder = dict[key];
        }
    });

    // 4. All [data-i18n-title] tooltip titles
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        const key = el.getAttribute("data-i18n-title");
        if (dict[key] !== undefined) {
            el.title = dict[key];
        }
    });

    // 5. Update HUD Text (Active View Title & Subtitle)
    updateHudText();

    // 6. Update Theme button label in active language
    const currentTheme = localStorage.getItem("verna_theme") || "dark";
    applyTheme(currentTheme);

    // 7. Update Live Bill Preview status badge & empty table placeholder
    const billBadge = document.getElementById("bill-badge-status");
    if (billBadge) {
        billBadge.innerText = dict.receipt_preview_ready || "READY";
    }
    const tbody = document.getElementById("bill-items-tbody");
    if (tbody && (!state.currentBill || !state.currentBill.items || state.currentBill.items.length === 0)) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-slate); padding: 24px 10px; font-size: 0.82rem;">${dict.empty_bill_placeholder || "📸 पावती स्कॅन करा किंवा 🎙️ व्हॉइस बोला — वस्तू व हिशोब येथे आपोआप दिसेल."}</td></tr>`;
    }

    // 8. Update AI Chat elements
    const sendBtn = document.getElementById("btn-ai-send");
    if (sendBtn && !isAiProcessing) {
        sendBtn.innerHTML = `<span>${dict.btn_send}</span> 🚀`;
    }
    const initialAiBubble = document.querySelector("#ai-chat-history .chat-bubble.chat-ai");
    if (initialAiBubble && (!state.chatHistory || state.chatHistory.length === 0)) {
        initialAiBubble.innerHTML = dict.ai_greeting;
    }
    const voiceStatus = document.getElementById("rag-voice-status");
    if (voiceStatus) {
        voiceStatus.innerText = dict.rag_voice_status_text;
    }

    // 9. Re-render dynamic tables so item & customer names switch languages instantly!
    if (state.allInventory && state.allInventory.length > 0) {
        renderInventoryTable(state.allInventory);
    }
    if (state.allKhata && state.allKhata.customers && state.allKhata.customers.length > 0) {
        renderKhataCards(state.allKhata.customers);
        renderKhataTable(state.allKhata.transactions);
    }
    if (state.allReceipts && state.allReceipts.length > 0) {
        renderLedgerTable(state.allReceipts);
    }
    if (state.currentBill && state.currentBill.items && state.currentBill.items.length > 0) {
        renderBillItems();
    }
}"""

js_code, n_apply = re.subn(old_apply_pattern, new_apply, js_code, count=1)
print(f"Replaced applyLanguage: {n_apply} match.")

# Update applyTheme to support trilingual label
old_apply_theme_pattern = r'function applyTheme\(theme\)\s*\{.*?\n\}'
new_apply_theme = """function applyTheme(theme) {
    const isLight = (theme === "light");
    if (isLight) {
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.remove("light-theme");
    }
    const dict = i18n[state.lang] || i18n.mr;
    const hudLbl = document.getElementById("hud-theme-label");
    const hudIcon = document.getElementById("hud-theme-icon");
    const mobIcon = document.getElementById("mob-theme-icon");

    const labelText = isLight 
        ? (dict.theme_night_mode || (state.lang === "en" ? "Night Mode" : "नाईट मोड"))
        : (dict.theme_kirana_mode || (state.lang === "en" ? "Day Mode" : (state.lang === "hi" ? "किराना मोड" : "किराणा मोड")));

    if (hudLbl) hudLbl.innerText = labelText;
    if (hudIcon) hudIcon.innerText = isLight ? "🌙" : "☀️";
    if (mobIcon) mobIcon.innerText = isLight ? "🌙" : "☀️";
}"""

js_code, n_theme = re.subn(old_apply_theme_pattern, new_apply_theme, js_code, count=1)
print(f"Replaced applyTheme: {n_theme} match.")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

with open('public/app.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

print("Saved app.js and public/app.js successfully.")

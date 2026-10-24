import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update applyLanguage
old_apply = """function applyLanguage() {
    const dict = i18n[state.lang] || i18n.mr;
    const isMr = state.lang === "mr";
    const language = getLanguage();

    // 1. Language buttons
    const mBtn = document.getElementById("mobile-lang-btn");
    if (mBtn) mBtn.innerText = `🌐 ${language.label}`;
    const dBtn = document.getElementById("desktop-lang-btn");
    if (dBtn) dBtn.innerText = `🌐 ${language.label}`;
    const hBtn = document.getElementById("hud-lang-btn");
    if (hBtn) hBtn.innerText = `🌐 ${language.label}`;
    const cBtn = document.getElementById("chat-lang-btn");
    if (cBtn) if (state.lang === "mr") cBtn.innerText = "🌐 भाषा: मराठी (mr-IN)";
    else if (state.lang === "hi") cBtn.innerText = "🌐 भाषा: हिन्दी (hi-IN)";
    else cBtn.innerText = "🌐 Language: English (en-IN)";
    document.querySelectorAll(".language-select").forEach(select => {
        select.value = state.lang;
    });

    // 2. All [data-i18n] text nodes
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key]) el.innerHTML = dict[key];
    });

    // 3. All [data-i18n-ph] input placeholders
    document.querySelectorAll("[data-i18n-ph]").forEach(el => {
        const key = el.getAttribute("data-i18n-ph");
        if (dict[key]) el.placeholder = dict[key];
    });

    // 4. All [data-i18n-title] tooltip titles
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        const key = el.getAttribute("data-i18n-title");
        if (dict[key]) el.title = dict[key];
    });

    // 5. Update HUD Text
    updateHudText();

    // 6. Update Send button text
    const sendBtn = document.getElementById("btn-ai-send");
    if (sendBtn && !isAiProcessing) {
        sendBtn.innerHTML = `<span>${dict.btn_send}</span> 🚀`;
    }

    // 7. Update initial AI greeting if present
    const aiInitial = document.querySelector(".chat-ai-initial");
    if (aiInitial) {
        aiInitial.innerHTML = dict.ai_greeting;
    }

    // 8. Re-render dynamic tables so item & customer names switch languages instantly!
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
    if (state.currentBill && state.currentBill.items) {
        renderBillItems();
    }
}"""

new_apply = """function applyLanguage() {
    const dict = i18n[state.lang] || i18n.mr;
    const isMr = state.lang === "mr";
    const language = getLanguage();

    // 1. Language buttons & dropdowns sync
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
        if (dict[key] !== undefined) el.innerHTML = dict[key];
    });

    // 3. All [data-i18n-ph] input placeholders
    document.querySelectorAll("[data-i18n-ph]").forEach(el => {
        const key = el.getAttribute("data-i18n-ph");
        if (dict[key] !== undefined) el.placeholder = dict[key];
    });

    // 4. All [data-i18n-title] tooltip titles
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        const key = el.getAttribute("data-i18n-title");
        if (dict[key] !== undefined) el.title = dict[key];
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

# 2. Update applyTheme
old_theme = """function applyTheme(theme) {
    const isLight = (theme === "light");
    if (isLight) {
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.remove("light-theme");
    }
    const lbl = document.getElementById("theme-label");
    const icon = document.getElementById("theme-icon");
    const hudLbl = document.getElementById("hud-theme-label");
    const hudIcon = document.getElementById("hud-theme-icon");
    const mobIcon = document.getElementById("mob-theme-icon");

    if (lbl) lbl.innerText = isLight ? "नाईट मोड (Dark)" : "किराणा मोड (Light)";
    if (icon) icon.innerText = isLight ? "🌙" : "☀️";
    if (hudLbl) hudLbl.innerText = isLight ? "नाईट मोड" : "किराणा मोड";
    if (hudIcon) hudIcon.innerText = isLight ? "🌙" : "☀️";
    if (mobIcon) mobIcon.innerText = isLight ? "🌙" : "☀️";
}"""

new_theme = """function applyTheme(theme) {
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

# Normalizing newlines
def normalize(s):
    return s.replace('\r\n', '\n')

code_norm = normalize(code)
old_apply_norm = normalize(old_apply)
new_apply_norm = normalize(new_apply)
old_theme_norm = normalize(old_theme)
new_theme_norm = normalize(new_theme)

if old_apply_norm in code_norm:
    code_norm = code_norm.replace(old_apply_norm, new_apply_norm)
    print("Replaced applyLanguage successfully!")
else:
    print("Error: old_apply not found.")

if old_theme_norm in code_norm:
    code_norm = code_norm.replace(old_theme_norm, new_theme_norm)
    print("Replaced applyTheme successfully!")
else:
    print("Error: old_theme not found.")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code_norm)

with open('public/app.js', 'w', encoding='utf-8') as f:
    f.write(code_norm)

print("Saved updated app.js and public/app.js.")

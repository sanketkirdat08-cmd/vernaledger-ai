import os

def fix_app_js(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Fix fatal bug in renderKhataCards: replace (bill.vendor_name || 'किराणा पावती')
    old_wa_chunk = '''        const safePhone = (c.phone || "").replace(/\D/g, "");
        const waMsg = encodeURIComponent(
            `🙏 *${(bill.vendor_name || 'किराणा पावती').trim()}*\\n` +
            `नमस्कार ${c.name} जी!\\n` +
            `आपल्या खात्यावर दुकानाचे एकूण *₹${c.balance.toFixed(2)}* उधारीचे येणे बाकी आहे.\\n\\n` +
            `💳 कृपया खालील UPI लिंकवरून GooglePay / PhonePe द्वारे पेमेंट करावे:\\n` +
            `upi://pay?pa=merchant@upi&pn=KiranaStore&am=${c.balance.toFixed(2)}&cu=INR\\n\\n` +
            `लवकरात लवकर भरणा करून सहकार्य करावे. धन्यवाद!`
        );'''

    new_wa_chunk = '''        const safePhone = (c.phone || "").replace(/\D/g, "");
        const shopTitle = (state.user && state.user.shop_name) || (state.lang === 'mr' ? 'किराणा स्टोअर' : (state.lang === 'hi' ? 'किराना स्टोर' : 'Kirana Store'));
        const waMsg = encodeURIComponent(
            `🙏 *${shopTitle.trim()}*\\n` +
            `नमस्कार ${c.name} जी!\\n` +
            `आपल्या खात्यावर दुकानाचे एकूण *₹${c.balance.toFixed(2)}* उधारीचे येणे बाकी आहे.\\n\\n` +
            `💳 कृपया खालील UPI लिंकवरून GooglePay / PhonePe द्वारे पेमेंट करावे:\\n` +
            `upi://pay?pa=merchant@upi&pn=${encodeURIComponent(shopTitle)}&am=${c.balance.toFixed(2)}&cu=INR\\n\\n` +
            `लवकरात लवकर भरणा करून सहकार्य करावे. धन्यवाद!`
        );'''

    c = c.replace(old_wa_chunk.replace('\r\n', '\n'), new_wa_chunk.replace('\r\n', '\n'))

    # 2. Add i18n keys to mr
    mr_target = 'lbl_total_receipts: "एकूण पावत्या:",'
    mr_add = '''lbl_total_receipts: "एकूण पावत्या:",
        lbl_filter_cust: "फिल्टर:",
        filter_all_cust: "सर्व ग्राहक",
        filter_pending_cust: "उधारी बाकी",
        filter_cleared_cust: "हिशोब क्लिअर",
        empty_khata_cust: "कोणतेही उधारी खाते सापडले नाही. नवीन खाते जोडा.",
        empty_khata_txns: "कोणताही खाते व्यवहार उपलब्ध नाही.",
        no_filtered_cust: "या फिल्टरमध्ये कोणतेही ग्राहक सापडले नाहीत.",'''

    if mr_target in c and "filter_all_cust" not in c:
        c = c.replace(mr_target, mr_add)

    # 3. Add i18n keys to en
    en_target = 'lbl_total_receipts: "Total Receipts:",'
    en_add = '''lbl_total_receipts: "Total Receipts:",
        lbl_filter_cust: "Filter:",
        filter_all_cust: "All Customers",
        filter_pending_cust: "Credit Due",
        filter_cleared_cust: "Cleared",
        empty_khata_cust: "No customer khata found. Add a new customer account.",
        empty_khata_txns: "No transactions found in ledger.",
        no_filtered_cust: "No customers found in this filter.",'''

    if en_target in c and 'filter_all_cust: "All Customers"' not in c:
        c = c.replace(en_target, en_add)

    # 4. Add i18n keys to hi
    hi_target = 'lbl_total_receipts: "कुल रसीदें:",'
    hi_add = '''lbl_total_receipts: "कुल रसीदें:",
        lbl_filter_cust: "फ़िल्टर:",
        filter_all_cust: "सभी ग्राहक",
        filter_pending_cust: "उधारी बकाया",
        filter_cleared_cust: "हिसाब क्लीयर",
        empty_khata_cust: "कोई खाता नहीं मिला। नया खाता जोड़ें।",
        empty_khata_txns: "कोई खाता लेनदेन उपलब्ध नहीं है।",
        no_filtered_cust: "इस फ़िल्टर में कोई ग्राहक नहीं मिला।",'''

    if hi_target in c and 'filter_all_cust: "सभी ग्राहक"' not in c:
        c = c.replace(hi_target, hi_add)

    # 5. Fix updateHudText to guarantee active language title
    old_hud_fn = '''function updateHudText() {
    const dict = i18n[state.lang] || i18n.mr;
    const view = state.currentView || "scanner";
    const titleKey = `hud_${view}_title`;
    const subKey = `hud_${view}_sub`;

    const titleEl = document.getElementById("hud-title");
    const subEl = document.getElementById("hud-subtitle");
    if (titleEl && dict[titleKey]) titleEl.innerText = dict[titleKey];
    if (subEl && dict[subKey]) subEl.innerText = dict[subKey];
}'''

    new_hud_fn = '''function updateHudText() {
    const dict = i18n[state.lang] || i18n.mr;
    const view = state.currentView || "scanner";
    const titleKey = `hud_${view}_title`;
    const subKey = `hud_${view}_sub`;

    const titleMap = {
        scanner: dict.hud_scanner_title || (state.lang === "en" ? "⚡ Smart Multimodal Scanner & Voice Billing" : (state.lang === "hi" ? "⚡ स्मार्ट मल्टीमॉडल स्कैनर व वॉइस बिलिंग" : "⚡ स्मार्ट मल्टीमॉडेल स्कॅनर व व्हॉइस बिलिंग")),
        khata: dict.hud_khata_title || (state.lang === "en" ? "💳 Customer Khata & Digital Credit Ledger" : (state.lang === "hi" ? "💳 ग्राहक खाता व डिजिटल उधारी बही" : "💳 ग्राहक खाते व डिजिटल उधारी वही")),
        business: dict.hud_business_title || (state.lang === "en" ? "🏬 Store Operations & Inventory" : (state.lang === "hi" ? "🏬 स्टोर ऑपरेशन्स व स्टॉक" : "🏬 स्टोअर ऑपरेशन्स, माल साठा व खर्च")),
        ledger: dict.hud_ledger_title || (state.lang === "en" ? "📊 Resilient Digital Ledger" : (state.lang === "hi" ? "📊 सुरक्षित डिजिटल लेजर डेटाबेस" : "📊 सुरक्षित डिजिटल लेजर डेटाबेस")),
        ai: dict.hud_ai_title || (state.lang === "en" ? "🤖 Verna AI Business Studio" : (state.lang === "hi" ? "🤖 Verna AI बिजनेस स्टूडियो" : "🤖 VernaLedger AI बिझनेस स्टुडिओ"))
    };

    const titleEl = document.getElementById("hud-title");
    const subEl = document.getElementById("hud-subtitle");
    if (titleEl) titleEl.innerText = titleMap[view] || dict[titleKey] || "VernaLedger.AI";
    if (subEl && dict[subKey]) subEl.innerText = dict[subKey];
}'''

    c = c.replace(old_hud_fn.replace('\r\n', '\n'), new_hud_fn.replace('\r\n', '\n'))

    # 6. Fix applyTheme to guarantee language-appropriate theme label
    old_apply_theme = '''function applyTheme(theme) {
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
}'''

    new_apply_theme = '''function applyTheme(theme) {
    const isLight = (theme === "light");
    if (isLight) {
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.remove("light-theme");
    }
    const hudLbl = document.getElementById("hud-theme-label");
    const hudIcon = document.getElementById("hud-theme-icon");
    const mobIcon = document.getElementById("mob-theme-icon");

    let labelText = "";
    if (isLight) {
        labelText = state.lang === "en" ? "Night Mode" : (state.lang === "hi" ? "नाइट मोड" : "नाईट मोड");
    } else {
        labelText = state.lang === "en" ? "Day Mode" : (state.lang === "hi" ? "किराना मोड" : "किराणा मोड");
    }

    if (hudLbl) hudLbl.innerText = labelText;
    if (hudIcon) hudIcon.innerText = isLight ? "🌙" : "☀️";
    if (mobIcon) mobIcon.innerText = isLight ? "🌙" : "☀️";
}'''

    c = c.replace(old_apply_theme.replace('\r\n', '\n'), new_apply_theme.replace('\r\n', '\n'))

    # 7. Protect loadKhataData calls
    old_load_render = '''        renderKhataCards(finalData.customers);
        renderKhataTable(finalData.transactions);'''

    new_load_render = '''        try {
            renderKhataCards(finalData.customers);
        } catch (errCards) {
            console.error("Error in renderKhataCards:", errCards);
        }
        try {
            renderKhataTable(finalData.transactions);
        } catch (errTable) {
            console.error("Error in renderKhataTable:", errTable);
        }'''

    c = c.replace(old_load_render.replace('\r\n', '\n'), new_load_render.replace('\r\n', '\n'))

    # 8. Guard renderKhataTable with empty placeholder
    old_render_khata_table = '''function renderKhataTable(transactions) {
    const tbody = document.getElementById("khata-table-tbody");
    tbody.innerHTML = "";

    transactions.forEach(t => {'''

    new_render_khata_table = '''function renderKhataTable(transactions) {
    const tbody = document.getElementById("khata-table-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!transactions || transactions.length === 0) {
        const dict = i18n[state.lang] || i18n.mr;
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 24px;">${dict.empty_khata_txns || "कोणताही खाते व्यवहार उपलब्ध नाही."}</td></tr>`;
        return;
    }

    transactions.forEach(t => {'''

    c = c.replace(old_render_khata_table.replace('\r\n', '\n'), new_render_khata_table.replace('\r\n', '\n'))

    # 9. Guard filterKhataList
    old_filter_khata = '''function filterKhataList() {
    const query = document.getElementById("khata-search-input").value.toLowerCase();
    const filteredCust = state.allKhata.customers.filter(c =>'''

    new_filter_khata = '''function filterKhataList() {
    if (!state.allKhata || !state.allKhata.customers) return;
    const query = document.getElementById("khata-search-input").value.toLowerCase();
    const filteredCust = state.allKhata.customers.filter(c =>'''

    c = c.replace(old_filter_khata.replace('\r\n', '\n'), new_filter_khata.replace('\r\n', '\n'))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"Fixed {filepath}")

fix_app_js("app.js")
fix_app_js(os.path.join("public", "app.js"))

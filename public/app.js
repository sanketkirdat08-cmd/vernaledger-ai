/**
 * VernaLedger.AI - Merchant Pro v7.5
 * Client-Side Application Engine (Vercel Serverless Ready)
 * Handles OCR Vision, Vernacular Voice Billing, Edge TTS, Khata, Ledger, and RAG Chat.
 */

// -----------------------------------------------------------------------------
// GLOBAL STATE & STORAGE
// -----------------------------------------------------------------------------
const state = {
    user: null,
    lang: localStorage.getItem("verna_lang") || "mr",
    currentView: "scanner",
    scannerMode: "vision",
    selectedFile: null,
    isRecording: false,
    speechRecognition: null,
    cameraStream: null,
    allReceipts: [],
    allKhata: { transactions: [], customers: [] },
    allInventory: [],
    allExpenses: [],
    dashboard: null,
    currentBill: null,
    chatHistory: []
};

// -----------------------------------------------------------------------------
// LOCAL-FIRST PERSISTENT STORAGE & AUTO-SYNC ENGINE (OFFLINE & SERVERLESS PROOF)
// -----------------------------------------------------------------------------
const VernaStorage = {
    KEY_RECEIPTS: "verna_persistent_receipts",
    KEY_KHATA: "verna_persistent_khata",
    KEY_EXPENSES: "verna_persistent_expenses",

    get(key) {
        try {
            const raw = localStorage.getItem(key);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            console.warn("VernaStorage get notice:", e);
            return [];
        }
    },

    save(key, items) {
        try {
            localStorage.setItem(key, JSON.stringify(items));
        } catch (e) {
            console.warn("VernaStorage save notice:", e);
        }
    },

    addReceipt(receipt) {
        if (!receipt) return;
        const list = this.get(this.KEY_RECEIPTS);
        const exists = list.some(r => 
            (r.id && receipt.id && r.id === receipt.id) ||
            (r.vendor_name === receipt.vendor_name && r.date === receipt.date && Math.abs((Number(r.grand_total) || 0) - (Number(receipt.grand_total) || 0)) < 0.01)
        );
        if (!exists) {
            list.unshift(receipt);
            this.save(this.KEY_RECEIPTS, list);
        }
    },

    removeReceipt(id) {
        const list = this.get(this.KEY_RECEIPTS).filter(r => r.id !== id);
        this.save(this.KEY_RECEIPTS, list);
    },

    removeReceipts(ids) {
        const idSet = new Set((ids || []).map(Number));
        const list = this.get(this.KEY_RECEIPTS).filter(r => !idSet.has(Number(r.id)));
        this.save(this.KEY_RECEIPTS, list);
    },

    clearAllReceipts() {
        this.save(this.KEY_RECEIPTS, []);
    },

    mergeReceipts(serverReceipts) {
        const local = this.get(this.KEY_RECEIPTS);
        const map = new Map();
        (serverReceipts || []).forEach(r => {
            const key = r.id ? String(r.id) : `${r.vendor_name}_${r.date}_${r.grand_total}`;
            map.set(key, r);
        });
        (local || []).forEach(r => {
            const key = r.id ? String(r.id) : `${r.vendor_name}_${r.date}_${r.grand_total}`;
            if (!map.has(key)) {
                map.set(key, r);
            }
        });
        const merged = Array.from(map.values());
        this.save(this.KEY_RECEIPTS, merged);
        return merged;
    },

    addKhata(entry) {
        if (!entry) return;
        const list = this.get(this.KEY_KHATA);
        list.unshift(entry);
        this.save(this.KEY_KHATA, list);
    },

    removeKhata(id) {
        const list = this.get(this.KEY_KHATA).filter(k => k.id !== id);
        this.save(this.KEY_KHATA, list);
    },

    mergeKhata(serverTxns) {
        const local = this.get(this.KEY_KHATA);
        const map = new Map();
        (serverTxns || []).forEach(t => {
            const key = t.id ? String(t.id) : `${t.customer_name}_${t.date}_${t.amount}_${t.transaction_type}`;
            map.set(key, t);
        });
        (local || []).forEach(t => {
            const key = t.id ? String(t.id) : `${t.customer_name}_${t.date}_${t.amount}_${t.transaction_type}`;
            if (!map.has(key)) {
                map.set(key, t);
            }
        });
        const merged = Array.from(map.values());
        this.save(this.KEY_KHATA, merged);
        return merged;
    },

    addExpense(exp) {
        if (!exp) return;
        const list = this.get(this.KEY_EXPENSES);
        list.unshift(exp);
        this.save(this.KEY_EXPENSES, list);
    },

    getReceipts() {
        return this.get(this.KEY_RECEIPTS);
    },

    saveReceipts(items) {
        this.save(this.KEY_RECEIPTS, items);
    },

    getKhata() {
        return this.get(this.KEY_KHATA);
    },

    saveKhata(items) {
        this.save(this.KEY_KHATA, items);
    },

    getExpenses() {
        return this.get(this.KEY_EXPENSES);
    },

    saveExpenses(items) {
        this.save(this.KEY_EXPENSES, items);
    },

    mergeExpenses(serverExps) {
        const local = this.get(this.KEY_EXPENSES);
        const map = new Map();
        (serverExps || []).forEach(e => {
            const key = e.id ? String(e.id) : `${e.expense_title}_${e.date}_${e.amount}`;
            map.set(key, e);
        });
        (local || []).forEach(e => {
            const key = e.id ? String(e.id) : `${e.expense_title}_${e.date}_${e.amount}`;
            if (!map.has(key)) {
                map.set(key, e);
            }
        });
        const merged = Array.from(map.values());
        this.save(this.KEY_EXPENSES, merged);
        return merged;
    }
};

let isAutoSyncing = false;
async function syncLocalDataToServer() {
    if (isAutoSyncing) return;
    try {
        isAutoSyncing = true;
        const localReceipts = VernaStorage.get(VernaStorage.KEY_RECEIPTS);
        const localKhata = VernaStorage.get(VernaStorage.KEY_KHATA);
        const localExpenses = VernaStorage.get(VernaStorage.KEY_EXPENSES);
        let localSettings = state.shopSettings || null;
        if (!localSettings) {
            try {
                const cached = localStorage.getItem("verna_shop_settings");
                if (cached) localSettings = JSON.parse(cached);
            } catch (_) {}
        }

        if (localReceipts.length === 0 && localKhata.length === 0 && localExpenses.length === 0 && !localSettings) {
            return;
        }

        await apiCall("/api/sync", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                receipts: localReceipts,
                khata: localKhata,
                expenses: localExpenses,
                shop_settings: localSettings
            })
        });
    } catch (e) {
        console.warn("Auto-sync notice:", e);
    } finally {
        isAutoSyncing = false;
    }
}

const supportedLanguages = [
    { code: "mr", label: "मराठी", speech: "mr-IN", tts: "mr-IN-AarohiNeural" },
    { code: "en", label: "English", speech: "en-IN", tts: "en-IN-NeerjaNeural" },
    { code: "hi", label: "हिन्दी", speech: "hi-IN", tts: "hi-IN-SwaraNeural" }
];

function parseDevanagariNum(str) {
    if (str === null || str === undefined) return 0;
    const devanagariDigits = {'०':'0','१':'1','२':'2','३':'3','४':'4','५':'5','६':'6','७':'7','८':'8','९':'9'};
    const normalized = String(str).replace(/[०-९]/g, d => devanagariDigits[d] || d);
    const match = normalized.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : 0;
}

if (!supportedLanguages.some(language => language.code === state.lang)) {
    state.lang = "mr";
}

function getLanguage(code = state.lang) {
    return supportedLanguages.find(language => language.code === code) || supportedLanguages[0];
}

// I18N Translations (100% Complete Trilingual Marathi / English / Hindi Coverage)
const i18n = {
    mr: {
        ai_greeting: "नमस्कार! मी <strong>Verna AI</strong>. दुकानातील विक्री, उधारी किंवा साठ्याबद्दल विचारा किंवा माईक दाबून बोला.",
        ai_voice_listening: "🎙️ मी ऐकत आहे... प्रश्न विचारा किंवा उधारी बोला...",
        app_name: "VernaLedger.AI",
        btn_add_entry: "+ जमा/उधारी",
        btn_add_expense: "+ नोंद करा",
        btn_add_item: "+ वस्तू जोडा",
        btn_add_khata_tx: "+ नवीन व्यवहार",
        btn_add_stock: "+ नवीन माल जोडा",
        btn_add_to_khata: "💳 खात्यावर उधारी नोंदवा",
        btn_ai_scan: "⚡ AI स्कॅन करा",
        btn_camera: "📷 लाईव्ह कॅमेराने फोटो काढा",
        btn_camera_capture: "📷 लाईव्ह कॅमेराने फोटो काढा",
        btn_cancel: "रद्द करा",
        btn_delete_selected: "निवडलेल्या डिलीट करा",
        btn_clear_all_ledger: "⚠️ सर्व रिकामे करा",
        lbl_selected_receipts: "निवडलेल्या:",
        lbl_total_receipts: "एकूण पावत्या:",
        lbl_filter_cust: "फिल्टर:",
        filter_all_cust: "सर्व ग्राहक",
        filter_pending_cust: "उधारी बाकी",
        filter_cleared_cust: "हिशोब क्लिअर",
        empty_khata_cust: "कोणतेही उधारी खाते सापडले नाही. नवीन खाते जोडा.",
        empty_khata_txns: "कोणताही खाते व्यवहार उपलब्ध नाही.",
        no_filtered_cust: "या फिल्टरमध्ये कोणतेही ग्राहक सापडले नाहीत.",
        confirm_bulk_delete: "तुम्हाला निवडलेल्या {n} पावत्या लेजरमधून कायमच्या डिलीट करायच्या आहेत का?",
        confirm_clear_all: "⚠️ सावधान! तुम्हाला लेजरमधील सर्व पावत्या कायमच्या डिलीट करायच्या आहेत का? ही कृती पूर्ववत करता येणार नाही!",
        msg_bulk_delete_success: "✅ निवडलेल्या {n} पावत्या यशस्वीरीत्या डिलीट केल्या!",
        msg_clear_all_success: "✅ सर्व पावत्या लेजरमधून यशस्वीरीत्या डिलीट केल्या!",
        lbl_selected_khata: "निवडलेले व्यवहार:",
        btn_delete_selected_khata: "🗑️ निवडलेले डिलीट करा",
        btn_clear_all_khata: "⚠️ सर्व रिकामे करा",
        link_forgot_password: "🔑 पासवर्ड विसरलात?",
        link_register_account: "✨ नवीन खाते तयार करा",
        title_forgot_password: "पासवर्ड रीसेट करा (Reset Password)",
        lbl_forgot_user: "वापरकर्ता नाव (Username) किंवा फोन नंबर",
        lbl_new_password: "नवीन पासवर्ड (New Password)",
        btn_submit_reset_password: "✅ पासवर्ड बदला (Set New Password)",
        title_register_merchant: "नवीन खाते तयार करा (New Merchant Register)",
        lbl_reg_username: "वापरकर्ता नाव (Username)",
        lbl_reg_password: "पासवर्ड",
        lbl_reg_shop_name: "दुकान / व्यवसायाचे नाव",
        lbl_reg_phone: "मोबाईल नंबर (WhatsApp)",
        btn_submit_register: "🚀 खाते तयार करा व सुरू करा",
        lbl_active_shop: "माझे दुकान:",
        title_shop_profile_settings: "दुकान प्रोफाईल व बिलिंग माहिती (Shop Settings)",
        sub_shop_profile_settings: "ही माहिती सर्व डिजिटल पावत्या, थर्मल प्रिंट, QR कोड आणि WhatsApp बिलांवर आपोआप दिसेल.",
        btn_save_shop_info: "💾 माहिती सेव्ह करा",
        lbl_setting_shop_name: "दुकान / व्यवसायाचे नाव",
        lbl_setting_owner_name: "मालकाचे नाव",
        lbl_setting_phone: "मोबाईल / WhatsApp नंबर",
        lbl_setting_upi: "UPI ID (QR पेमेंटसाठी)",
        lbl_setting_address: "दुकान पत्ता / ठिकाण",
        title_modal_shop_settings: "दुकान माहिती बदला (Shop Profile)",
        confirm_bulk_delete_khata: "तुम्हाला निवडलेले {n} खाते व्यवहार कायमचे डिलीट करायचे आहेत का?",
        confirm_clear_all_khata: "⚠️ सावधान! तुम्हाला सर्व खाते व्यवहार कायमचे डिलीट करायचे आहेत का? ही कृती पूर्ववत करता येणार नाही!",
        msg_bulk_delete_khata_success: "✅ निवडलेले {n} व्यवहार यशस्वीरीत्या डिलीट केले!",
        msg_clear_all_khata_success: "✅ सर्व खाते व्यवहार रिकामे केले गेले!",
        no_receipts_selected: "कृपया आधी किमान एक पावती निवडा!",
        empty_ledger: "कोणतीही पावती उपलब्ध नाही.",
        btn_clear_chat: "🗑️ Clear",
        btn_close: "बंद करा",
        btn_export_csv: "📑 CSV",
        btn_export_excel: "📊 Excel (.xlsx)",
        btn_history: "इतिहास",
        btn_login: "🚀 सिस्टममध्ये प्रवेश करा (Login)",
        btn_logout: "बाहेर पडा",
        btn_new_customer: "+ नवीन खाते",
        btn_new_expense: "+ नवीन खर्च",
        btn_new_stock: "+ नवीन माल",
        btn_ocr: "⚡ AI स्कॅन करा",
        btn_print_now: "🖨️ आताच प्रिंट करा",
        btn_print_receipt: "🖨️ पावती प्रिंट",
        btn_repeat_audio: "🔊 पुन्हा ऐका",
        btn_save_bill: "💾 बिल सेव्ह करा",
        btn_save_ledger: "💾 लेजरमध्ये सेव्ह करा",
        btn_save_stock: "💾 साठा नोंदवा",
        btn_save_tx: "💾 व्यवहार सेव्ह करा",
        btn_send: "पाठवा",
        btn_send_wa: "🚀 WhatsApp वर पाठवा",
        btn_send_wa_digest: "💬 WhatsApp वर दैनिक रिपोर्ट शेअर करा",
        btn_snap_photo: "📸 फोटो क्लिक करा",
        btn_submit: "सेव्ह करा",
        btn_voice_submit: "⚡ व्हॉइस वरून पावती तयार करा",
        btn_whatsapp: "WhatsApp तगादा",
        btn_whatsapp_bill: "📲 WhatsApp बिल",
        card_ai_title: "VernaLedger AI बिझनेस स्टुडिओ",
        card_current_bill: "📋 सध्याचे बिल (Live POS)",
        card_expenses: "दैनिक दुकान खर्च",
        card_inventory: "दुकानातील माल साठा",
        card_khata_title: "ग्राहक उधारी यादी",
        card_ledger_title: "सर्व जुन्या पावत्यांचा इतिहास",
        card_live_preview: "डिजिटल पावती प्रिव्ह्यू",
        card_scan_input: "पावती स्कॅन / व्हॉइस इनपुट",
        chip_developers: "🎓 प्रोजेक्ट डेव्हलपर्स?",
        chip_low_stock: "🚨 कमी साठा",
        chip_pending_credit: "👥 बाकी उधारी",
        chip_sales: "💰 आजची एकूण विक्री किती?",
        chip_today_sales: "📊 आजची विक्री",
        chip_udhar: "👥 बाकी उधारी किती?",
        desc_wa_digest: "आजचा संपूर्ण विक्री, उधारी वसुली आणि निव्वळ नफ्याचा अहवाल १-क्लिक मध्ये स्वतःच्या किंवा मालकाच्या WhatsApp वर पाठवा.",
        desc_wa_share: "ग्राहकाचा १० अंकी WhatsApp नंबर टाका. बिलाचा संपूर्ण तपशील आणि UPI पेमेंट लिंक थेट त्यांच्या WhatsApp वर उघडेल:",
        dropzone_sub: "PNG, JPG, JPEG (हस्तलिखित किंवा छापील बिल)",
        dropzone_title: "पावतीचा फोटो निवडा किंवा येथे ड्रॅग करा",
        empty_bill_placeholder: "📸 पावती स्कॅन करा किंवा 🎙️ व्हॉइस बोला — वस्तू व हिशोब येथे आपोआप दिसेल.",
        filter_all: "सर्व",
        filter_pending: "बाकी उधारी",
        filter_settled: "हिशोब पूर्ण",
        hud_ai_sub: "तुमच्या दुकानाचा नफा, उधारी व साठ्याचा वैयक्तिक AI सल्लागार",
        hud_ai_title: "🤖 VernaLedger AI बिझनेस स्टुडिओ",
        hud_business_sub: "इन्व्हेंटरी ट्रॅकिंग, कमी स्टॉक अलर्ट्स आणि दैनिक खर्च व्यवस्थापन",
        hud_business_title: "🏬 स्टोअर ऑपरेशन्स, माल साठा व खर्च",
        hud_khata_sub: "WhatsApp द्वारे १-क्लिक देय स्मरणपत्रे व पारदर्शक जमा-खर्च हिशोब",
        hud_khata_title: "💳 ग्राहक खाते व डिजिटल उधारी वही",
        hud_ledger_sub: "सर्व जुन्या पावत्यांचा इतिहास, शोध आणि थर्मल पावती प्रिंट",
        hud_ledger_title: "📊 सुरक्षित डिजिटल लेजर डेटाबेस",
        hud_scanner_sub: "हस्तलिखित व छापील पावत्यांचे १ सेकंदात डिजिटल बिलामध्ये रूपांतर",
        hud_scanner_title: "⚡ स्मार्ट मल्टीमॉडेल स्कॅनर व व्हॉइस बिलिंग",
        hud_title_ai: "🤖 Verna AI बिझनेस स्टुडिओ",
        hud_title_business: "🏬 स्टोअर ऑपरेशन्स व स्टॉक",
        hud_title_khata: "💳 ग्राहक खाते (उधारी वही)",
        hud_title_ledger: "📜 लेजर व पावत्या इतिहास",
        hud_title_scanner: "⚡ स्मार्ट स्कॅनर व व्हॉइस बिलिंग",
        kpi_avg: "सरासरी बिल",
        kpi_avg_bill: "सरासरी पावती मूल्य",
        kpi_bills: "एकूण पावत्या",
        kpi_collected_amt: "जमा झालेली रक्कम",
        kpi_customers: "एकूण ग्राहक",
        kpi_pending_udhar: "एकूण बाकी उधारी",
        kpi_profit: "निव्वळ नफा",
        kpi_registered_cust: "नोंदणीकृत ग्राहक",
        kpi_sales: "एकूण विक्री",
        kpi_total_receipts: "एकूण पावत्या",
        kpi_total_sales: "एकूण नोंदवलेली विक्री",
        kpi_total_tx: "एकूण व्यवहार",
        kpi_txns: "एकूण व्यवहार",
        kpi_udhar: "बाकी उधारी",
        lang_label: "🌐 मराठी",
        lbl_amount: "रक्कम (₹)",
        lbl_category: "श्रेणी",
        lbl_cust_name: "ग्राहकाचे नाव (Customer Name)",
        lbl_date: "तारीख",
        lbl_due_date: "परतफेडीची देय तारीख (Due Date)",
        lbl_grand_total: "एकूण रक्कम:",
        lbl_inv_alert_limit: "कमी साठा मर्यादा (Alert Limit)",
        lbl_inv_item_name: "वस्तूचे नाव (Item Name)",
        lbl_inv_price: "विक्री किंमत (₹)",
        lbl_inv_stock_qty: "उपलब्ध साठा (Stock Qty)",
        lbl_inv_unit: "एकक (Unit)",
        lbl_mobile: "मोबाईल नंबर (WhatsApp)",
        lbl_notes: "नोंद / तपशील (Notes)",
        lbl_password: "पासवर्ड (Password)",
        lbl_tx_type: "व्यवहार प्रकार",
        lbl_username: "वापरकर्ता नाव (Username)",
        lbl_vendor: "दुकान / विक्रेत्याचे नाव",
        lbl_voice_output: "🔊 व्हॉइस उत्तर ऐका",
        lbl_wa_phone: "ग्राहकाचा WhatsApp मोबाईल नंबर:",
        login_demo_admin: "⚡ ॲडमिन डेमो",
        login_demo_hint: "झटपट डेमो क्रेडेंशियल्स (Quick Access):",
        login_demo_staff: "👤 स्टाफ डेमो",
        login_subtitle: "भारतीय व्यापाऱ्यांसाठी व्हर्नाक्युलर AI डिजिटल लेजर व बिलिंग प्रणाली",
        login_title: "मर्चंट लॉगिन",
        low_stock_banner: "काही वस्तूंचा साठा संपत आला आहे.",
        low_stock_msg: "काही वस्तूंचा साठा संपत आला आहे.",
        low_stock_notice: "कमी स्टॉक अलर्ट (Low Stock Notice)",
        mob_nav_ai: "AI स्टुडिओ",
        mob_nav_business: "ऑपरेशन्स",
        mob_nav_khata: "खाते",
        mob_nav_ledger: "लेजर",
        mob_nav_scanner: "स्कॅनर",
        modal_camera_title: "📷 पावतीचा फोटो काढा",
        modal_entry_title: "💳 नवीन व्यवहार नोंदवा (जमा/उधारी)",
        modal_expense_title: "💸 नवीन खर्च नोंदवा (Store Expense)",
        modal_khata_title: "💳 नवीन खाते व्यवहार नोंदवा",
        modal_stock_title: "📦 नवीन वस्तू / माल जोडा",
        modal_wa_title: "📲 WhatsApp वर पावती पाठवा",
        nav_ai: "AI बिझनेस स्टुडिओ",
        nav_business: "स्टोअर ऑपरेशन्स",
        nav_khata: "ग्राहक खाते",
        nav_ledger: "लेजर व पावत्या",
        nav_scanner: "स्मार्ट स्कॅनर",
        ocr_scanning: "⚡ AI द्वारे पावती स्कॅनिंग सुरू आहे...",
        opt_credit_given: "उधारी दिली (Credit Given)",
        opt_expense_other: "इतर (Other)",
        opt_expense_salary: "पगार (Salary)",
        opt_expense_shop: "दुकान खर्च (Shop)",
        opt_expense_transport: "वाहतूक / हमाली (Transport)",
        opt_expense_utilities: "लाईट / पाणी (Utilities)",
        opt_payment_received: "पैसे जमा केले (Payment)",
        ph_ai_input: "येथे प्रश्न विचारा किंवा बोला... (उदा. 'आजची विक्री किती?')",
        ph_amount: "उदा. 500",
        ph_cust_name: "उदा. सागर पाटील",
        ph_expense_amount: "रक्कम (₹)",
        ph_expense_title: "खर्चाचे नाव (उदा. लाईट बिल, वाहतूक)",
        ph_inv_alert_limit: "उदा. 10",
        ph_inv_item_name: "उदा. साखर (Sugar M-30)",
        ph_inv_price: "उदा. 45",
        ph_inv_stock_qty: "उदा. 50",
        ph_khata_search: "🔍 ग्राहकाचे नाव किंवा मोबाईल नंबर शोधा...",
        ph_ledger_search: "🔍 पावती क्रमांक, विक्रेता किंवा तारीख शोधा...",
        ph_mobile: "उदा. 9876543210",
        ph_notes: "उदा. किराणा सामान उधारी",
        ph_search_khata: "ग्राहक नाव किंवा मोबाईल नंबरने शोधा...",
        ph_search_ledger: "पावती क्रमांक किंवा दुकानाच्या नावाने शोधा...",
        ph_vendor: "दुकान / विक्रेत्याचे नाव",
        ph_voice_input: "येथे उच्चारलेला मजकूर दिसेल किंवा स्वतः टाईप करा...",
        ph_wa_phone: "उदा. 9822001122",
        rag_voice_status_text: "🎙️ मी ऐकत आहे... प्रश्न विचारा किंवा उधारी बोला...",
        receipt_bill_no_label: "Bill No:",
        receipt_footer_thanks: "🙏 पुन्हा भेट द्या! धन्यवाद! 🙏",
        receipt_greeting: "🙏 पुन्हा भेट द्या! धन्यवाद! 🙏",
        receipt_preview_new: "नवीन",
        receipt_preview_ready: "तयार",
        receipt_preview_title: "🖨️ डिजिटल पावती प्रिव्ह्यू",
        receipt_total_label: "एकूण देय रक्कम:",
        receipt_upi_text: "स्कॅन करून UPI द्वारे पैसे भरा",
        scanner_card_title: "पावती स्कॅन / व्हॉइस इनपुट",
        tab_expenses: "📉 दैनंदिन खर्च (Expenses)",
        tab_inventory: "📦 साठा व्यवस्थापन (Inventory)",
        tab_vision: "📷 AI व्हिजन स्कॅनर",
        tab_vision_scanner: "📷 AI व्हिजन स्कॅनर",
        tab_voice: "🎙️ व्हॉइस बिलिंग",
        tab_voice_billing: "🎙️ व्हॉइस बिलिंग",
        tagline: "किराणा दुकानांसाठी सुरक्षित स्मार्ट लेजर",
        th_action: "कृती",
        th_amount: "रक्कम (₹)",
        th_bill_no: "बिल क्र.",
        th_customer: "ग्राहक नाव",
        th_due: "बाकी उधारी",
        th_due_date: "देय तारीख",
        th_exp_amount: "रक्कम (₹)",
        th_exp_category: "प्रवर्ग",
        th_exp_date: "तारीख",
        th_exp_title: "खर्च",
        th_inv_item: "वस्तू नाव",
        th_inv_price: "किंमत (₹)",
        th_inv_status: "स्थिती",
        th_inv_stock: "साठा",
        th_item: "वस्तू / माल",
        th_note: "टीप",
        th_phone: "मोबाईल",
        th_price: "किंमत (₹)",
        th_qty: "नग / वजन",
        th_rate: "दर (₹)",
        th_reason: "खर्चाचे कारण",
        th_rec_action: "कृती",
        th_rec_date: "तारीख",
        th_rec_id: "पावती क्र.",
        th_rec_items: "वस्तू संख्या",
        th_rec_total: "एकूण रक्कम (₹)",
        th_rec_vendor: "दुकान / विक्रेता",
        th_status: "स्थिती",
        th_stock: "साठा",
        th_store_customer: "दुकान / ग्राहक",
        th_total: "एकूण (₹)",
        th_type: "प्रकार",
        theme_kirana_mode: "किराणा मोड",
        theme_night_mode: "नाईट मोड",
        title_expenses: "📉 दैनंदिन बिझनेस खर्च (Expenses)",
        title_khata_audit: "📜 संपूर्ण खाते व्यवहार इतिहास (Transaction Audit)",
        title_ledger_table: "📜 सर्व सेव्ह केलेल्या पावत्या (Ledger Audit Table)",
        title_rag_mic: "माईक द्वारे बोला",
        title_wa_digest: "📲 दैनिक बिझनेस रिपोर्ट (WhatsApp Digest)",
        voice_hint: "मायक्रोफोन बटण दाबून ग्राहकाचे नाव व सामान बोला (उदा. 'सागर ला २ किलो साखर ५० रुपये आणि १ तेल १५० रुपये')",
        voice_listening: "मी ऐकत आहे... सामान बोला...",
        voice_mic_title: "माईक द्वारे बोला",
        voice_placeholder: "येथे उच्चारलेला मजकूर दिसेल किंवा स्वतः टाईप करा...",
        voice_ready: "बोलण्यासाठी माईक वर क्लिक करा"
    },
    en: {
        ai_greeting: "Hello! I am <strong>Verna AI</strong>. Ask about store sales, customer credit, or inventory, or tap the mic to speak.",
        ai_voice_listening: "🎙️ Listening... Ask a question or speak credit...",
        app_name: "VernaLedger.AI",
        btn_add_entry: "+ Credit/Payment",
        btn_add_expense: "+ Add Expense",
        btn_add_item: "+ Add Item",
        btn_add_khata_tx: "+ New Transaction",
        btn_add_stock: "+ Add Stock Item",
        btn_add_to_khata: "💳 Add to Khata (Credit)",
        btn_ai_scan: "⚡ Run AI Scan",
        btn_camera: "📷 Capture with Live Camera",
        btn_camera_capture: "📷 Capture via Live Camera",
        btn_cancel: "Cancel",
        btn_delete_selected: "Delete Selected",
        btn_clear_all_ledger: "⚠️ Clear All",
        lbl_selected_receipts: "Selected:",
        lbl_total_receipts: "Total Receipts:",
        lbl_filter_cust: "Filter:",
        filter_all_cust: "All Customers",
        filter_pending_cust: "Credit Due",
        filter_cleared_cust: "Cleared",
        empty_khata_cust: "No customer khata found. Add a new customer account.",
        empty_khata_txns: "No transactions found in ledger.",
        no_filtered_cust: "No customers found in this filter.",
        confirm_bulk_delete: "Are you sure you want to permanently delete {n} selected receipts from the ledger?",
        confirm_clear_all: "⚠️ Warning! Are you sure you want to delete ALL receipts from the ledger? This action cannot be undone!",
        msg_bulk_delete_success: "✅ Successfully deleted {n} selected receipts!",
        msg_clear_all_success: "✅ Successfully cleared all receipts from ledger!",
        lbl_selected_khata: "Selected Transactions:",
        btn_delete_selected_khata: "🗑️ Delete Selected",
        btn_clear_all_khata: "⚠️ Clear All",
        link_forgot_password: "🔑 Forgot Password?",
        link_register_account: "✨ Create New Account",
        title_forgot_password: "Reset Password",
        lbl_forgot_user: "Username or Mobile Number",
        lbl_new_password: "New Password",
        btn_submit_reset_password: "✅ Set New Password",
        title_register_merchant: "Register New Merchant Account",
        lbl_reg_username: "Username",
        lbl_reg_password: "Password",
        lbl_reg_shop_name: "Shop / Store Name",
        lbl_reg_phone: "Mobile Number (WhatsApp)",
        btn_submit_register: "🚀 Register & Get Started",
        lbl_active_shop: "My Shop:",
        title_shop_profile_settings: "Shop Profile & Billing Settings",
        sub_shop_profile_settings: "This information automatically appears on digital bills, thermal receipts, UPI QR codes, and WhatsApp messages.",
        btn_save_shop_info: "💾 Save Store Info",
        lbl_setting_shop_name: "Shop / Business Name",
        lbl_setting_owner_name: "Owner Name",
        lbl_setting_phone: "Mobile / WhatsApp Number",
        lbl_setting_upi: "UPI ID (For QR Payments)",
        lbl_setting_address: "Store Address / Location",
        title_modal_shop_settings: "Edit Store Profile",
        confirm_bulk_delete_khata: "Are you sure you want to permanently delete {n} selected transactions?",
        confirm_clear_all_khata: "⚠️ Warning! Are you sure you want to delete ALL customer transactions? This action cannot be undone!",
        msg_bulk_delete_khata_success: "✅ Successfully deleted {n} transactions!",
        msg_clear_all_khata_success: "✅ All transactions cleared successfully!",
        no_receipts_selected: "Please select at least one receipt first!",
        empty_ledger: "No receipts available in ledger.",
        btn_clear_chat: "🗑️ Clear",
        btn_close: "Close",
        btn_export_csv: "📑 CSV",
        btn_export_excel: "📊 Excel (.xlsx)",
        btn_history: "History",
        btn_login: "🚀 Login to System",
        btn_logout: "Logout",
        btn_new_customer: "+ New Customer",
        btn_new_expense: "+ Add Expense",
        btn_new_stock: "+ Add Stock",
        btn_ocr: "⚡ AI Scan Receipt",
        btn_print_now: "🖨️ Print Now",
        btn_print_receipt: "🖨️ Print Receipt",
        btn_repeat_audio: "🔊 Replay Audio",
        btn_save_bill: "💾 Save Bill",
        btn_save_ledger: "💾 Save to Ledger",
        btn_save_stock: "💾 Save Stock",
        btn_save_tx: "💾 Save Transaction",
        btn_send: "Send",
        btn_send_wa: "🚀 Send on WhatsApp",
        btn_send_wa_digest: "💬 Share Daily Report on WhatsApp",
        btn_snap_photo: "📸 Snap Photo",
        btn_submit: "Save",
        btn_voice_submit: "⚡ Create Bill from Voice",
        btn_whatsapp: "WhatsApp Reminder",
        btn_whatsapp_bill: "📲 WhatsApp Bill",
        card_ai_title: "VernaLedger AI Business Studio",
        card_current_bill: "📋 Current Live Bill (POS)",
        card_expenses: "Daily Store Expenses",
        card_inventory: "Store Inventory & Stock",
        card_khata_title: "Customer Ledger Accounts",
        card_ledger_title: "All Saved Receipts History",
        card_live_preview: "Digital Receipt Preview",
        card_scan_input: "Receipt Scanner / Voice Input",
        chip_developers: "🎓 Project Developers?",
        chip_low_stock: "🚨 Low Stock",
        chip_pending_credit: "👥 Pending Credit",
        chip_sales: "💰 Today's total sales?",
        chip_today_sales: "📊 Today's Sales",
        chip_udhar: "👥 Total pending credit?",
        desc_wa_digest: "Send today's total sales, credit recovery, and net profit report to your or owner's WhatsApp in 1-click.",
        desc_wa_share: "Enter customer's 10-digit WhatsApp number. Full bill details and UPI payment link will open directly on their WhatsApp:",
        dropzone_sub: "PNG, JPG, JPEG (Handwritten or Printed Bill)",
        dropzone_title: "Choose receipt photo or drag here",
        empty_bill_placeholder: "📸 Scan receipt or 🎙️ speak voice — items & total will appear here automatically.",
        filter_all: "All",
        filter_pending: "Pending Due",
        filter_settled: "Settled",
        hud_ai_sub: "Real-time store intelligence powered by SQLite & Gemini 2.5 RAG",
        hud_ai_title: "🤖 VernaLedger AI Business Studio",
        hud_business_sub: "Inventory tracking, low-stock alerts, and daily expense management",
        hud_business_title: "🏬 Store Operations, Inventory & Expenses",
        hud_khata_sub: "1-Click WhatsApp payment reminders and transparent accounts",
        hud_khata_title: "💳 Customer Khata & Digital Credit Ledger",
        hud_ledger_sub: "Full history of saved receipts, search, and POS thermal print",
        hud_ledger_title: "📊 Secure Digital Ledger Database",
        hud_scanner_sub: "Convert handwritten receipts into digital ledger using Gemini 2.5 Flash",
        hud_scanner_title: "⚡ Smart Multimodal Scanner & Voice Billing",
        hud_title_ai: "🤖 Verna AI Business Studio",
        hud_title_business: "🏬 Store Operations & Stock",
        hud_title_khata: "💳 Customer Khata (Credit Ledger)",
        hud_title_ledger: "📜 Ledger & Scanned Receipts",
        hud_title_scanner: "⚡ Smart Scanner & Voice Billing",
        kpi_avg: "Average Ticket",
        kpi_avg_bill: "Average Bill Value",
        kpi_bills: "Total Receipts",
        kpi_collected_amt: "Total Collected Amount",
        kpi_customers: "Total Customers",
        kpi_pending_udhar: "Total Pending Credit",
        kpi_profit: "Net Profit",
        kpi_registered_cust: "Registered Customers",
        kpi_sales: "Total Sales",
        kpi_total_receipts: "Total Receipts",
        kpi_total_sales: "Total Recorded Sales",
        kpi_total_tx: "Total Transactions",
        kpi_txns: "Total Txns",
        kpi_udhar: "Pending Udhar",
        lang_label: "🌐 English",
        lbl_amount: "Amount (₹)",
        lbl_category: "Category",
        lbl_cust_name: "Customer Name",
        lbl_date: "Date",
        lbl_due_date: "Due Date",
        lbl_grand_total: "Grand Total:",
        lbl_inv_alert_limit: "Low Stock Alert Limit",
        lbl_inv_item_name: "Item Name",
        lbl_inv_price: "Selling Price (₹)",
        lbl_inv_stock_qty: "Available Stock Qty",
        lbl_inv_unit: "Unit",
        lbl_mobile: "Mobile Number (WhatsApp)",
        lbl_notes: "Notes / Details",
        lbl_password: "Password",
        lbl_tx_type: "Transaction Type",
        lbl_username: "Username",
        lbl_vendor: "Store / Merchant Name",
        lbl_voice_output: "🔊 Voice Audio Output",
        lbl_wa_phone: "Customer's WhatsApp Mobile Number:",
        login_demo_admin: "⚡ Admin Demo",
        login_demo_hint: "Instant Demo Credentials (Quick Access):",
        login_demo_staff: "👤 Staff Demo",
        login_subtitle: "Vernacular AI Digital Ledger & Billing System for Indian Merchants",
        login_title: "Merchant Login",
        low_stock_banner: "Some items are running low on stock.",
        low_stock_msg: "Some items are running out of stock.",
        low_stock_notice: "Low Stock Alert Notice",
        mob_nav_ai: "AI Studio",
        mob_nav_business: "Operations",
        mob_nav_khata: "Khata",
        mob_nav_ledger: "Ledger",
        mob_nav_scanner: "Scanner",
        modal_camera_title: "📷 Capture Receipt Photo",
        modal_entry_title: "💳 Record Transaction (Credit/Payment)",
        modal_expense_title: "💸 Record Store Expense",
        modal_khata_title: "💳 Record New Customer Transaction",
        modal_stock_title: "📦 Add New Stock Item",
        modal_wa_title: "📲 Send Receipt on WhatsApp",
        nav_ai: "AI Business Studio",
        nav_business: "Store Operations",
        nav_khata: "Customer Khata",
        nav_ledger: "Ledger Database",
        nav_scanner: "Smart Scanner",
        ocr_scanning: "⚡ AI is scanning receipt...",
        opt_credit_given: "Credit Given",
        opt_expense_other: "Other",
        opt_expense_salary: "Staff Salary",
        opt_expense_shop: "Shop Expense",
        opt_expense_transport: "Transport / Labor",
        opt_expense_utilities: "Utilities (Power/Water)",
        opt_payment_received: "Payment Received",
        ph_ai_input: "Ask a question or speak... (e.g. 'What is today's sales?')",
        ph_amount: "e.g. 500",
        ph_cust_name: "e.g. Sagar Patil",
        ph_expense_amount: "Amount (₹)",
        ph_expense_title: "Expense title (e.g. Electricity, Transport)",
        ph_inv_alert_limit: "e.g. 10",
        ph_inv_item_name: "e.g. Sugar M-30",
        ph_inv_price: "e.g. 45",
        ph_inv_stock_qty: "e.g. 50",
        ph_khata_search: "🔍 Search customer name or mobile number...",
        ph_ledger_search: "🔍 Search receipt #, merchant or date...",
        ph_mobile: "e.g. 9876543210",
        ph_notes: "e.g. Grocery items credit",
        ph_search_khata: "Search customer by name or phone...",
        ph_search_ledger: "Search by receipt number or store...",
        ph_vendor: "Store / Merchant Name",
        ph_voice_input: "Spoken text will appear here or type manually...",
        ph_wa_phone: "e.g. 9822001122",
        rag_voice_status_text: "🎙️ Listening... Ask a question or speak credit entry...",
        receipt_bill_no_label: "Bill No:",
        receipt_footer_thanks: "🙏 Visit Again! Thank You! 🙏",
        receipt_greeting: "🙏 Thank you! Visit Again! 🙏",
        receipt_preview_new: "NEW",
        receipt_preview_ready: "READY",
        receipt_preview_title: "🖨️ Digital POS Receipt Preview",
        receipt_total_label: "Grand Total:",
        receipt_upi_text: "Scan to pay via UPI",
        scanner_card_title: "Receipt Scan / Voice Input",
        tab_expenses: "📉 Daily Expenses",
        tab_inventory: "📦 Stock & Inventory",
        tab_vision: "📷 AI Vision Scanner",
        tab_vision_scanner: "📷 AI Vision Scanner",
        tab_voice: "🎙️ Voice Billing",
        tab_voice_billing: "🎙️ Voice Billing",
        tagline: "Secure Smart Retail Ledger for Kirana Stores",
        th_action: "Action",
        th_amount: "Amount (₹)",
        th_bill_no: "Bill #",
        th_customer: "Customer Name",
        th_due: "Pending Due",
        th_due_date: "Due Date",
        th_exp_amount: "Amount (₹)",
        th_exp_category: "Category",
        th_exp_date: "Date",
        th_exp_title: "Expense",
        th_inv_item: "Item Name",
        th_inv_price: "Selling Price (₹)",
        th_inv_status: "Status",
        th_inv_stock: "Stock Qty",
        th_item: "Item Name",
        th_note: "Notes",
        th_phone: "Mobile",
        th_price: "Price (₹)",
        th_qty: "Qty / Wt",
        th_rate: "Rate (₹)",
        th_reason: "Expense Reason",
        th_rec_action: "Actions",
        th_rec_date: "Date",
        th_rec_id: "Receipt #",
        th_rec_items: "Items Count",
        th_rec_total: "Grand Total (₹)",
        th_rec_vendor: "Store / Merchant",
        th_status: "Status",
        th_stock: "Stock",
        th_store_customer: "Store / Customer",
        th_total: "Total (₹)",
        th_type: "Type",
        theme_kirana_mode: "Day Mode",
        theme_night_mode: "Night Mode",
        title_expenses: "📉 Daily Business Expenses",
        title_khata_audit: "📜 Full Customer Ledger Audit History",
        title_ledger_table: "📜 All Saved Receipts (Ledger Audit Table)",
        title_rag_mic: "Speak using microphone",
        title_wa_digest: "📲 Daily Business Report (WhatsApp Digest)",
        voice_hint: "Tap mic and speak customer name and items (e.g. 'Sagar 2 kg sugar 50 rupees and 1 oil 150 rupees')",
        voice_listening: "Listening... Speak items...",
        voice_mic_title: "Speak using microphone",
        voice_placeholder: "Spoken text will appear here or type manually...",
        voice_ready: "Click mic to speak"
    },
    hi: {
        ai_greeting: "नमस्ते! मैं <strong>Verna AI</strong> हूँ। दुकान की बिक्री, उधारी या स्टॉक के बारे में पूछें या माइक दबाकर बोलें।",
        ai_voice_listening: "🎙️ मैं सुन रहा हूँ... प्रश्न पूछें या उधारी बोलें...",
        app_name: "VernaLedger.AI",
        btn_add_entry: "+ जमा/उधारी",
        btn_add_expense: "+ दर्ज करें",
        btn_add_item: "+ सामान जोड़ें",
        btn_add_khata_tx: "+ नया लेनदेन",
        btn_add_stock: "+ नया सामान जोड़ें",
        btn_add_to_khata: "💳 खाते पर उधारी दर्ज करें",
        btn_ai_scan: "⚡ AI स्कैन करें",
        btn_camera: "📷 लाइव कैमरे से फोटो लें",
        btn_camera_capture: "📷 लाइव कैमरे से फोटो लें",
        btn_cancel: "रद्द करें",
        btn_delete_selected: "चुनी गई डिलीट करें",
        btn_clear_all_ledger: "⚠️ सब डिलीट करें",
        lbl_selected_receipts: "चुनी गई:",
        lbl_total_receipts: "कुल रसीदें:",
        lbl_filter_cust: "फ़िल्टर:",
        filter_all_cust: "सभी ग्राहक",
        filter_pending_cust: "उधारी बकाया",
        filter_cleared_cust: "हिसाब क्लीयर",
        empty_khata_cust: "कोई खाता नहीं मिला। नया खाता जोड़ें।",
        empty_khata_txns: "कोई खाता लेनदेन उपलब्ध नहीं है।",
        no_filtered_cust: "इस फ़िल्टर में कोई ग्राहक नहीं मिला।",
        confirm_bulk_delete: "क्या आप चुनी गई {n} रसीदें लेजर से स्थायी रूप से हटाना चाहते हैं?",
        confirm_clear_all: "⚠️ चेतावनी! क्या आप लेजर से सभी रसीदें स्थायी रूप से हटाना चाहते हैं? यह क्रिया पूर्ववत नहीं की जा सकती!",
        msg_bulk_delete_success: "✅ चुनी गई {n} रसीदें सफलतापूर्वक डिलीट कर दी गईं!",
        msg_clear_all_success: "✅ सभी रसीदें लेजर से सफलतापूर्वक हटा दी गईं!",
        lbl_selected_khata: "चुने गए लेनदेन:",
        btn_delete_selected_khata: "🗑️ चुने गए डिलीट करें",
        btn_clear_all_khata: "⚠️ सब डिलीट करें",
        link_forgot_password: "🔑 पासवर्ड भूल गए?",
        link_register_account: "✨ नया खाता बनाएं",
        title_forgot_password: "पासवर्ड रीसेट करें (Reset Password)",
        lbl_forgot_user: "उपयोगकर्ता नाम (Username) या फ़ोन नंबर",
        lbl_new_password: "नया पासवर्ड (New Password)",
        btn_submit_reset_password: "✅ पासवर्ड बदलें (Set New Password)",
        title_register_merchant: "नया व्यापारी खाता बनाएं (New Merchant Register)",
        lbl_reg_username: "उपयोगकर्ता नाम (Username)",
        lbl_reg_password: "पासवर्ड",
        lbl_reg_shop_name: "दुकान / व्यापार का नाम",
        lbl_reg_phone: "मोबाइल नंबर (WhatsApp)",
        btn_submit_register: "🚀 खाता बनाएं और शुरू करें",
        lbl_active_shop: "मेरी दुकान:",
        title_shop_profile_settings: "दुकान प्रोफ़ाइल व बिलिंग जानकारी (Shop Settings)",
        sub_shop_profile_settings: "यह जानकारी सभी डिजिटल बिलों, थर्मल रसीदों, QR कोड और WhatsApp संदेशों पर दिखाई देगी।",
        btn_save_shop_info: "💾 जानकारी सुरक्षित करें",
        lbl_setting_shop_name: "दुकान / व्यापार का नाम",
        lbl_setting_owner_name: "मालिक का नाम",
        lbl_setting_phone: "मोबाइल / WhatsApp नंबर",
        lbl_setting_upi: "UPI ID (QR भुगतान के लिए)",
        lbl_setting_address: "दुकान का पता",
        title_modal_shop_settings: "दुकान प्रोफ़ाइल बदलें",
        confirm_bulk_delete_khata: "क्या आप चुने गए {n} लेनदेन स्थायी रूप से हटाना चाहते हैं?",
        confirm_clear_all_khata: "⚠️ चेतावनी! क्या आप सभी लेनदेन स्थायी रूप से हटाना चाहते हैं? यह क्रिया पूर्ववत नहीं की जा सकती!",
        msg_bulk_delete_khata_success: "✅ सफलतापूर्वक {n} लेनदेन डिलीट किए गए!",
        msg_clear_all_khata_success: "✅ सभी लेनदेन सफलतापूर्वक साफ़ कर दिए गए!",
        no_receipts_selected: "कृपया पहले कम से कम एक रसीद चुनें!",
        empty_ledger: "लेजर में कोई रसीद उपलब्ध नहीं है।",
        btn_clear_chat: "🗑️ साफ़ करें",
        btn_close: "बंद करें",
        btn_export_csv: "📑 CSV",
        btn_export_excel: "📊 Excel (.xlsx)",
        btn_history: "इतिहास",
        btn_login: "🚀 सिस्टम में प्रवेश करें (Login)",
        btn_logout: "लॉगआउट",
        btn_new_customer: "+ नया खाता",
        btn_new_expense: "+ नया खर्च",
        btn_new_stock: "+ नया सामान",
        btn_ocr: "⚡ AI स्कैन करें",
        btn_print_now: "🖨️ अभी प्रिंट करें",
        btn_print_receipt: "🖨️ रसीद प्रिंट",
        btn_repeat_audio: "🔊 दोबारा सुनें",
        btn_save_bill: "💾 बिल सेव करें",
        btn_save_ledger: "💾 लेजर में सेव करें",
        btn_save_stock: "💾 स्टॉक दर्ज करें",
        btn_save_tx: "💾 लेनदेन सेव करें",
        btn_send: "भेजें",
        btn_send_wa: "🚀 WhatsApp पर भेजें",
        btn_send_wa_digest: "💬 WhatsApp पर दैनिक रिपोर्ट भेजें",
        btn_snap_photo: "📸 फोटो खींचें",
        btn_submit: "सेव करें",
        btn_voice_submit: "⚡ वॉइस से रसीद बनाएं",
        btn_whatsapp: "WhatsApp तकादा",
        btn_whatsapp_bill: "📲 WhatsApp बिल",
        card_ai_title: "VernaLedger AI बिजनेस स्टूडियो",
        card_current_bill: "📋 वर्तमान बिल (Live POS)",
        card_expenses: "दैनिक दुकान खर्च",
        card_inventory: "दुकान का स्टॉक (Inventory)",
        card_khata_title: "ग्राहक उधारी सूची",
        card_ledger_title: "सभी पुरानी रसीदों का इतिहास",
        card_live_preview: "डिजिटल रसीद पूर्वावलोकन",
        card_scan_input: "रसीद स्कैन / वॉइस इनपुट",
        chip_developers: "🎓 प्रोजेक्ट डेवलपर्स कौन हैं?",
        chip_low_stock: "🚨 कम स्टॉक",
        chip_pending_credit: "👥 बकाया उधारी",
        chip_sales: "💰 आज की कुल बिक्री कितनी है?",
        chip_today_sales: "📊 आज की बिक्री",
        chip_udhar: "👥 कुल बकाया उधारी कितनी है?",
        desc_wa_digest: "आज की कुल बिक्री, उधारी वसूली और शुद्ध लाभ की रिपोर्ट 1-क्लिक में अपने या मालिक के WhatsApp पर भेजें।",
        desc_wa_share: "ग्राहक का 10 अंकों का WhatsApp नंबर दर्ज करें। बिल का पूरा विवरण और UPI पेमेंट लिंक उनके WhatsApp पर खुलेगा:",
        dropzone_sub: "PNG, JPG, JPEG (हस्तलिखित या मुद्रित बिल)",
        dropzone_title: "रसीद का फोटो चुनें या यहाँ ड्रैग करें",
        empty_bill_placeholder: "📸 रसीद स्कैन करें या 🎙️ वॉइस बोलें — सामान व हिसाब यहाँ अपने आप दिखेगा।",
        filter_all: "सभी",
        filter_pending: "बकाया उधारी",
        filter_settled: "हिसाब चुकता",
        hud_ai_sub: "आपकी दुकान की बिक्री, उधारी और स्टॉक का व्यक्तिगत AI सलाहकार",
        hud_ai_title: "🤖 VernaLedger AI बिजनेस स्टूडियो",
        hud_business_sub: "इन्वेंट्री ट्रैकिंग, कम स्टॉक अलर्ट्स और दैनिक खर्च प्रबंधन",
        hud_business_title: "🏬 स्टोर ऑपरेशन्स, माल स्टॉक व खर्च",
        hud_khata_sub: "WhatsApp द्वारा 1-क्लिक भुगतान अनुस्मारक व पारदर्शी जमा-उधारी हिसाब",
        hud_khata_title: "💳 ग्राहक खाता व डिजिटल उधारी बही",
        hud_ledger_sub: "सभी पुरानी रसीदों का इतिहास, खोज और थर्मल बिल प्रिंट",
        hud_ledger_title: "📊 सुरक्षित डिजिटल लेजर डेटाबेस",
        hud_scanner_sub: "हस्तलिखित और मुद्रित बिलों का 1 सेकंड में डिजिटल बिल में रूपांतरण",
        hud_scanner_title: "⚡ स्मार्ट मल्टीमॉडल स्कैनर व वॉइस बिलिंग",
        hud_title_ai: "🤖 Verna AI बिजनेस स्टूडियो",
        hud_title_business: "🏬 स्टोर ऑपरेशन्स व स्टॉक",
        hud_title_khata: "💳 ग्राहक खाता (उधारी बही)",
        hud_title_ledger: "📜 लेजर व रसीद इतिहास",
        hud_title_scanner: "⚡ स्मार्ट स्कैनर व वॉइस बिलिंग",
        kpi_avg: "औसत बिल",
        kpi_avg_bill: "औसत रसीद मूल्य",
        kpi_bills: "कुल रसीदें",
        kpi_collected_amt: "कुल जमा राशि",
        kpi_customers: "कुल ग्राहक",
        kpi_pending_udhar: "कुल बकाया उधारी",
        kpi_profit: "शुद्ध लाभ",
        kpi_registered_cust: "पंजीकृत ग्राहक",
        kpi_sales: "कुल बिक्री",
        kpi_total_receipts: "कुल रसीदें",
        kpi_total_sales: "कुल दर्ज बिक्री",
        kpi_total_tx: "कुल लेनदेन",
        kpi_txns: "कुल लेनदेन",
        kpi_udhar: "बकाया उधारी",
        lang_label: "🌐 हिन्दी",
        lbl_amount: "राशि (₹)",
        lbl_category: "श्रेणी",
        lbl_cust_name: "ग्राहक का नाम",
        lbl_date: "तारीख",
        lbl_due_date: "चुकता करने की देय तारीख",
        lbl_grand_total: "कुल राशि:",
        lbl_inv_alert_limit: "कम स्टॉक चेतावनी सीमा",
        lbl_inv_item_name: "सामान का नाम",
        lbl_inv_price: "बिक्री मूल्य (₹)",
        lbl_inv_stock_qty: "उपलब्ध स्टॉक (मात्रा)",
        lbl_inv_unit: "इकाई (Unit)",
        lbl_mobile: "मोबाइल नंबर (WhatsApp)",
        lbl_notes: "विवरण / नोट",
        lbl_password: "पासवर्ड (Password)",
        lbl_tx_type: "लेनदेन प्रकार",
        lbl_username: "उपयोगकर्ता नाम (Username)",
        lbl_vendor: "दुकान / विक्रेता का नाम",
        lbl_voice_output: "🔊 वॉइस उत्तर सुनें",
        lbl_wa_phone: "ग्राहक का WhatsApp मोबाइल नंबर:",
        login_demo_admin: "⚡ एडमिन डेमो",
        login_demo_hint: "त्वरित डेमो क्रेडेंशियल्स (Quick Access):",
        login_demo_staff: "👤 स्टाफ डेमो",
        login_subtitle: "भारतीय व्यापारियों के लिए वर्नाक्युलर AI डिजिटल लेजर व बिलिंग प्रणाली",
        login_title: "मर्चेंट लॉगिन",
        low_stock_banner: "कुछ सामानों का स्टॉक खत्म होने वाला है।",
        low_stock_msg: "कुछ वस्तुओं का स्टॉक समाप्त होने वाला है.",
        low_stock_notice: "कम स्टॉक अलर्ट (Low Stock Notice)",
        mob_nav_ai: "AI स्टूडियो",
        mob_nav_business: "ऑपरेशन्स",
        mob_nav_khata: "खाता",
        mob_nav_ledger: "लेजर",
        mob_nav_scanner: "स्कैनर",
        modal_camera_title: "📷 रसीद का फोटो लें",
        modal_entry_title: "💳 नया लेनदेन दर्ज करें (जमा/उधारी)",
        modal_expense_title: "💸 नया खर्च दर्ज करें (Store Expense)",
        modal_khata_title: "💳 नया खाता लेनदेन दर्ज करें",
        modal_stock_title: "📦 नया सामान दर्ज करें",
        modal_wa_title: "📲 WhatsApp पर रसीद भेजें",
        nav_ai: "AI बिजनेस स्टूडियो",
        nav_business: "स्टोर ऑपरेशन्स",
        nav_khata: "ग्राहक खाता",
        nav_ledger: "लेजर व रसीदें",
        nav_scanner: "स्मार्ट स्कैनर",
        ocr_scanning: "⚡ AI द्वारा रसीद स्कैनिंग जारी है...",
        opt_credit_given: "उधारी दी (Credit Given)",
        opt_expense_other: "अन्य",
        opt_expense_salary: "वेतन (Salary)",
        opt_expense_shop: "दुकान खर्च",
        opt_expense_transport: "परिवहन / मजदूरी",
        opt_expense_utilities: "बिजली / पानी",
        opt_payment_received: "पैसे जमा किए (Payment)",
        ph_ai_input: "यहाँ प्रश्न पूछें या बोलें... (उदा. 'आज की बिक्री कितनी है?')",
        ph_amount: "उदा. 500",
        ph_cust_name: "उदा. सागर पाटिल",
        ph_expense_amount: "राशि (₹)",
        ph_expense_title: "खर्च का नाम (उदा. बिजली बिल, ढुलाई)",
        ph_inv_alert_limit: "उदा. 10",
        ph_inv_item_name: "उदा. चीनी (Sugar M-30)",
        ph_inv_price: "उदा. 45",
        ph_inv_stock_qty: "उदा. 50",
        ph_khata_search: "🔍 ग्राहक का नाम या मोबाइल नंबर खोजें...",
        ph_ledger_search: "🔍 रसीद संख्या, विक्रेता या तारीख खोजें...",
        ph_mobile: "उदा. 9876543210",
        ph_notes: "उदा. किराना सामान उधारी",
        ph_search_khata: "ग्राहक का नाम या मोबाइल नंबर से खोजें...",
        ph_search_ledger: "रसीद संख्या या दुकान के नाम से खोजें...",
        ph_vendor: "दुकान / विक्रेता का नाम",
        ph_voice_input: "यहाँ बोला गया पाठ दिखेगा या स्वयं टाइप करें...",
        ph_wa_phone: "उदा. 9822001122",
        rag_voice_status_text: "🎙️ मैं सुन रहा हूँ... प्रश्न पूछें या उधारी बोलें...",
        receipt_bill_no_label: "Bill No:",
        receipt_footer_thanks: "🙏 फिर पधारें! धन्यवाद! 🙏",
        receipt_greeting: "🙏 फिर पधारें! धन्यवाद! 🙏",
        receipt_preview_new: "नया",
        receipt_preview_ready: "तैयार",
        receipt_preview_title: "🖨️ डिजिटल रसीद पूर्वावलोकन",
        receipt_total_label: "कुल देय राशि:",
        receipt_upi_text: "स्कैन करके UPI से भुगतान करें",
        scanner_card_title: "रसीद स्कैन / वॉइस इनपुट",
        tab_expenses: "📉 दैनिक खर्च (Expenses)",
        tab_inventory: "📦 स्टॉक प्रबंधन (Inventory)",
        tab_vision: "📷 AI विजन स्कैनर",
        tab_vision_scanner: "📷 AI विजन स्कैनर",
        tab_voice: "🎙️ वॉइस बिलिंग",
        tab_voice_billing: "🎙️ वॉइस बिलिंग",
        tagline: "किराना दुकानों के लिए सुरक्षित स्मार्ट डिजिटल लेजर",
        th_action: "कार्रवाई",
        th_amount: "राशि (₹)",
        th_bill_no: "बिल क्र.",
        th_customer: "ग्राहक नाम",
        th_due: "बकाया उधारी",
        th_due_date: "देय तारीख",
        th_exp_amount: "राशि (₹)",
        th_exp_category: "श्रेणी",
        th_exp_date: "तारीख",
        th_exp_title: "खर्च",
        th_inv_item: "सामान का नाम",
        th_inv_price: "बिक्री मूल्य (₹)",
        th_inv_status: "स्थिति",
        th_inv_stock: "स्टॉक",
        th_item: "सामान / वस्तु",
        th_note: "टिप्पणी",
        th_phone: "मोबाइल",
        th_price: "कीमत (₹)",
        th_qty: "मात्रा / वजन",
        th_rate: "दर (₹)",
        th_reason: "खर्च का कारण",
        th_rec_action: "कार्रवाई",
        th_rec_date: "तारीख",
        th_rec_id: "रसीद क्र.",
        th_rec_items: "सामान संख्या",
        th_rec_total: "कुल राशि (₹)",
        th_rec_vendor: "दुकान / विक्रेता",
        th_status: "स्थिति",
        th_stock: "स्टॉक",
        th_store_customer: "दुकान / ग्राहक",
        th_total: "कुल (₹)",
        th_type: "प्रकार",
        theme_kirana_mode: "किराना मोड",
        theme_night_mode: "नाईट मोड",
        title_expenses: "📉 दैनिक व्यापार खर्च",
        title_khata_audit: "📜 संपूर्ण खाता लेनदेन इतिहास",
        title_ledger_table: "📜 सभी सहेजी गई रसीदें (Ledger Audit Table)",
        title_rag_mic: "माइक द्वारा बोलें",
        title_wa_digest: "📲 दैनिक व्यापार रिपोर्ट (WhatsApp Digest)",
        voice_hint: "माइक दबाकर ग्राहक का नाम और सामान बोलें (उदा. 'सागर को 2 किलो चीनी 50 रुपये और 1 तेल 150 रुपये')",
        voice_listening: "मैं सुन रहा हूँ... सामान का नाम बोलें...",
        voice_mic_title: "माइक द्वारा बोलें",
        voice_placeholder: "यहाँ बोला गया पाठ दिखेगा या स्वयं टाइप करें...",
        voice_ready: "बोलने के लिए माइक पर क्लिक करें"
    }
};

// Universal Kirana & Grocery Multilingual Item Dictionary
const KIRANA_ITEMS_DICT = {
    "साखर": { mr: "साखर", en: "Sugar", hi: "चीनी" },
    "sugar": { mr: "साखर", en: "Sugar", hi: "चीनी" },
    "चीनी": { mr: "साखर", en: "Sugar", hi: "चीनी" },
    "शेंगदाणा तेल": { mr: "शेंगदाणा तेल", en: "Peanut Oil", hi: "मूंगफली तेल" },
    "peanut oil": { mr: "शेंगदाणा तेल", en: "Peanut Oil", hi: "मूंगफली तेल" },
    "मूंगफली तेल": { mr: "शेंगदाणा तेल", en: "Peanut Oil", hi: "मूंगफली तेल" },
    "तेल": { mr: "तेल", en: "Cooking Oil", hi: "तेल" },
    "oil": { mr: "तेल", en: "Cooking Oil", hi: "तेल" },
    "गहू": { mr: "गहू", en: "Wheat", hi: "गेहूं" },
    "wheat": { mr: "गहू", en: "Wheat", hi: "गेहूं" },
    "गेहूं": { mr: "गहू", en: "Wheat", hi: "गेहूं" },
    "तांदूळ": { mr: "तांदूळ", en: "Rice", hi: "चावल" },
    "तांदुळ": { mr: "तांदूळ", en: "Rice", hi: "चावल" },
    "rice": { mr: "तांदूळ", en: "Rice", hi: "चावल" },
    "चावल": { mr: "तांदूळ", en: "Rice", hi: "चावल" },
    "तूर डाळ": { mr: "तूर डाळ", en: "Toor Dal", hi: "अरहर दाल" },
    "toor dal": { mr: "तूर डाळ", en: "Toor Dal", hi: "अरहर दाल" },
    "डाळ": { mr: "डाळ", en: "Dal / Pulses", hi: "दाल" },
    "dal": { mr: "डाळ", en: "Dal / Pulses", hi: "दाल" },
    "चहा": { mr: "चहा पावडर", en: "Tea Powder", hi: "चाय पत्ती" },
    "चहा पावडर": { mr: "चहा पावडर", en: "Tea Powder", hi: "चाय पत्ती" },
    "tea": { mr: "चहा पावडर", en: "Tea Powder", hi: "चाय पत्ती" },
    "साबण": { mr: "साबण", en: "Soap", hi: "साबुन" },
    "soap": { mr: "साबण", en: "Soap", hi: "साबुन" },
    "दूध": { mr: "दूध", en: "Milk", hi: "दूध" },
    "milk": { mr: "दूध", en: "Milk", hi: "दूध" },
    "तूप": { mr: "तूप", en: "Ghee", hi: "घी" },
    "ghee": { mr: "तूप", en: "Ghee", hi: "घी" },
    "मीठ": { mr: "मीठ", en: "Salt", hi: "नमक" },
    "salt": { mr: "मीठ", en: "Salt", hi: "नमक" },
    "हळद": { mr: "हळद", en: "Turmeric", hi: "हल्दी" },
    "turmeric": { mr: "हळद", en: "Turmeric", hi: "हल्दी" },
    "मिरची": { mr: "मिरची", en: "Chili", hi: "मिर्च" },
    "chili": { mr: "मिरची", en: "Chili", hi: "मिर्च" },
    "कांदा": { mr: "कांदा", en: "Onion", hi: "प्याज" },
    "onion": { mr: "कांदा", en: "Onion", hi: "प्याज" },
    "बटाटा": { mr: "बटाटा", en: "Potato", hi: "आलू" },
    "potato": { mr: "बटाटा", en: "Potato", hi: "आलू" },
    "बिस्कीट": { mr: "बिस्कीट", en: "Biscuits", hi: "बिस्कुट" },
    "biscuit": { mr: "बिस्कीट", en: "Biscuits", hi: "बिस्कुट" },
    "sk store": { mr: "SK Store", en: "SK Store", hi: "SK Store" },
    "sk स्टोअर": { mr: "SK Store", en: "SK Store", hi: "SK Store" },
    "महादेव किराणा स्टोअर": { mr: "महादेव किराणा स्टोअर", en: "Mahadev Kirana Store", hi: "महादेव किराना स्टोर" },
    "mahadev kirana store": { mr: "महादेव किराणा स्टोअर", en: "Mahadev Kirana Store", hi: "महादेव किराना स्टोर" },
    "महादेव किराना स्टोर": { mr: "महादेव किराणा स्टोअर", en: "Mahadev Kirana Store", hi: "महादेव किराना स्टोर" },
    "किराणा स्टोअर": { mr: "किराणा स्टोअर", en: "Kirana Store", hi: "किराना स्टोर" },
    "kirana store": { mr: "किराणा स्टोअर", en: "Kirana Store", hi: "किराना स्टोर" },
    "किराना स्टोर": { mr: "किराणा स्टोअर", en: "Kirana Store", hi: "किराना स्टोर" }
};

// Helper: Show item and customer names strictly ONCE in the active language
function formatLocalizedName(name, lang = state.lang) {
    if (!name) return "";
    name = String(name).trim();

    // 1. Check direct match in grocery dictionary
    const lower = name.toLowerCase();
    if (KIRANA_ITEMS_DICT[lower]) {
        return KIRANA_ITEMS_DICT[lower][lang] || KIRANA_ITEMS_DICT[lower].mr || name;
    }
    if (KIRANA_ITEMS_DICT[name]) {
        return KIRANA_ITEMS_DICT[name][lang] || KIRANA_ITEMS_DICT[name].mr || name;
    }

    // 2. Check format: "Marathi (English)" e.g. "साखर (Sugar M-30)" or "सागर पाटील (Sagar Patil)"
    const parenMatch = name.match(/^([^(]+)\s*\(([^)]+)\)$/);
    if (parenMatch) {
        const mrPart = parenMatch[1].trim();
        const enPart = parenMatch[2].trim();
        if (lang === "en") return enPart;
        if (lang === "hi") {
            const lk = mrPart.toLowerCase();
            return (KIRANA_ITEMS_DICT[lk] && KIRANA_ITEMS_DICT[lk].hi) ? KIRANA_ITEMS_DICT[lk].hi : mrPart;
        }
        return mrPart;
    }

    // 3. Check format: "Marathi / English"
    const slashMatch = name.match(/^([^/]+)\s*\/\s*(.+)$/);
    if (slashMatch) {
        const mrPart = slashMatch[1].trim();
        const enPart = slashMatch[2].trim();
        if (lang === "en") return enPart;
        if (lang === "hi") {
            const lk = mrPart.toLowerCase();
            return (KIRANA_ITEMS_DICT[lk] && KIRANA_ITEMS_DICT[lk].hi) ? KIRANA_ITEMS_DICT[lk].hi : mrPart;
        }
        return mrPart;
    }

    return name;
}

// INITIALIZATION
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    // Unregister any old service workers to keep browser always 100% live and fresh
    if ("serviceWorker" in navigator) {
        navigator.serviceWorker.getRegistrations().then((regs) => {
            for (const r of regs) r.unregister();
        }).catch(() => {});
    }
    // Set today's date in bill input
    const today = new Date().toISOString().split("T")[0];
    const billDateInput = document.getElementById("bill-date");
    if (billDateInput) billDateInput.value = today;

    // Check stored user session with resilient parsing
    const savedUser = localStorage.getItem("verna_user");
    let hasSession = false;
    if (savedUser) {
        try {
            const parsed = JSON.parse(savedUser);
            if (parsed && typeof parsed === "object") {
                state.user = parsed;
                if (!state.user.username) state.user.username = "admin";
                if (!state.user.role) state.user.role = "Admin";
                hasSession = true;
            } else if (typeof parsed === "string") {
                state.user = { username: parsed, role: "Admin" };
                hasSession = true;
            }
        } catch (e) {
            console.warn("Invalid session format:", e);
            localStorage.removeItem("verna_user");
        }
    }

    if (hasSession) {
        try {
            showApp();
        } catch (err) {
            console.error("showApp startup error:", err);
            // Ensure UI stays on main app container, do NOT wipe user session!
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("app-container").style.display = "flex";
        }
    } else {
        showLogin();
    }

    // Initialize Web Speech API if supported
    initSpeechRecognition();
    initRagSpeech();
    applyLanguage();

    // Load and apply persistent shop settings on startup
    applyShopSettingsToUI();
    loadShopSettings();
});

// -----------------------------------------------------------------------------
// AUTHENTICATION
// -----------------------------------------------------------------------------
// Universal API Fetcher with automatic prefix fallback (/api/* <-> /*)
// -----------------------------------------------------------------------------
// CYBERPUNK TOAST NOTIFICATION ENGINE (REPLACES BLOCKING MODAL ALERTS)
// -----------------------------------------------------------------------------
function showToast(message, type = "info", duration = 3500) {
    try {
        let container = document.getElementById("verna-toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "verna-toast-container";
            container.style.cssText = "position:fixed;top:20px;right:20px;z-index:999999;display:flex;flex-direction:column;gap:10px;max-width:min(92vw,420px);pointer-events:none;";
            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.style.cssText = "pointer-events:auto;background:rgba(15,23,42,0.96);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-radius:12px;padding:12px 16px;font-size:0.84rem;font-weight:600;line-height:1.45;display:flex;align-items:center;gap:10px;box-shadow:0 12px 30px rgba(0,0,0,0.6);transition:all 0.3s cubic-bezier(0.16,1,0.3,1);opacity:0;transform:translateY(-15px);cursor:pointer;";

        let borderCol = "#00f2fe";
        let textCol = "#e0f2fe";
        let icon = "ℹ️";

        if (type === "success") {
            borderCol = "#10b981";
            textCol = "#a7f3d0";
            icon = "✅";
            toast.style.boxShadow = "0 0 20px rgba(16,185,129,0.25)";
        } else if (type === "warning") {
            borderCol = "#f59e0b";
            textCol = "#fde68a";
            icon = "⚠️";
            toast.style.boxShadow = "0 0 20px rgba(245,158,11,0.25)";
        } else if (type === "error") {
            borderCol = "#ef4444";
            textCol = "#fca5a5";
            icon = "❌";
            toast.style.boxShadow = "0 0 20px rgba(239,68,68,0.25)";
        }

        toast.style.border = `1px solid ${borderCol}`;
        toast.style.color = textCol;
        toast.innerHTML = `<span style="font-size:1.1rem;flex-shrink:0;">${icon}</span><span style="flex:1;">${message}</span>`;
        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.style.opacity = "1";
            toast.style.transform = "translateY(0)";
        });

        const timer = setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-15px)";
            setTimeout(() => toast.remove(), 300);
        }, duration);

        toast.onclick = () => {
            clearTimeout(timer);
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-15px)";
            setTimeout(() => toast.remove(), 300);
        };
    } catch (e) {
        console.log("Toast fallback:", message);
    }
}

async function apiCall(endpoint, options = {}) {
    try {
        const res = await fetch(endpoint, options);
        if (res.status === 404 && endpoint.startsWith('/api/')) {
            const fallbackPath = endpoint.replace('/api', '');
            return await fetch(fallbackPath, options);
        }
        return res;
    } catch (e) {
        if (endpoint.startsWith('/api/')) {
            const fallbackPath = endpoint.replace('/api', '');
            return await fetch(fallbackPath, options);
        }
        throw e;
    }
}


function fillDemoCreds(u, p) {
    document.getElementById("login-username").value = u;
    document.getElementById("login-password").value = p;
}

async function handleLogin(e) {
    if (e) e.preventDefault();
    const uInput = document.getElementById("login-username").value.trim();
    const pInput = document.getElementById("login-password").value.trim();
    const alertBox = document.getElementById("login-alert");
    const submitBtn = document.getElementById("btn-login-submit");

    alertBox.style.display = "none";
    submitBtn.innerText = "तपासणी सुरू आहे...";
    submitBtn.disabled = true;

    try {
        const res = await apiCall("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: uInput, password: pInput })
        });
        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || "लॉगिन अयशस्वी. वापरकर्ता नाव किंवा पासवर्ड तपासा.");
        }

        state.user = data;
        try {
            const cached = localStorage.getItem("verna_shop_settings");
            if (cached) {
                const parsed = JSON.parse(cached);
                if (parsed && parsed.shop_name) {
                    state.user.shop_name = parsed.shop_name;
                    state.shopSettings = Object.assign({}, state.shopSettings, parsed);
                }
            }
        } catch (_) {}
        localStorage.setItem("verna_user", JSON.stringify(state.user));
        applyShopSettingsToUI();
        loadShopSettings();
        showApp();
    } catch (err) {
        alertBox.innerText = err.message;
        alertBox.style.display = "block";
    } finally {
        submitBtn.innerText = "🚀 सिस्टममध्ये प्रवेश करा (Login)";
        submitBtn.disabled = false;
    }
}

function handleLogout() {
    state.user = null;
    localStorage.removeItem("verna_user");
    showLogin();
}

function showLogin() {
    document.getElementById("login-screen").style.display = "flex";
    document.getElementById("app-container").style.display = "none";
}

function showApp() {
    const loginScreen = document.getElementById("login-screen");
    const appContainer = document.getElementById("app-container");
    if (loginScreen) loginScreen.style.display = "none";
    if (appContainer) appContainer.style.display = "flex";

    // Set user profile indicators safely
    if (!state.user || typeof state.user !== "object") {
        state.user = { username: "admin", role: "Admin" };
    }
    const username = state.user.username || "admin";
    const role = state.user.role || "Admin";

    const nameEl = document.getElementById("sidebar-user-name");
    if (nameEl) nameEl.innerText = username;

    const roleEl = document.getElementById("sidebar-user-role");
    if (roleEl) roleEl.innerText = `Role: ${role}`;

    const badge = document.getElementById("sidebar-role-badge");
    if (badge) {
        badge.innerText = String(role).toUpperCase();
        badge.className = "user-role-badge badge-admin";
    }

    // Load initial data safely
    try { applyShopSettingsToUI(); } catch (e) {}
    try { loadShopSettings(); } catch (e) {}
    try { loadDashboardMetrics(); } catch (e) { console.warn("Metrics load notice:", e); }
    try { initTheme(); } catch (e) { console.warn("Theme init notice:", e); }
    try { resetBillCard(); } catch (e) { console.warn("Reset bill card notice:", e); }
    try { loadReceiptsLedger(); } catch (e) { console.warn("Ledger load notice:", e); }
    try { loadKhataData(); } catch (e) { console.warn("Khata load notice:", e); }
    try { loadInventoryData(); } catch (e) { console.warn("Inventory load notice:", e); }
    try { loadExpensesData(); } catch (e) { console.warn("Expenses load notice:", e); }
    try { recalcBillTotal(); } catch (e) { console.warn("Recalc bill notice:", e); }

    // Restore saved view on refresh or URL hash
    const hash = window.location.hash.replace("#", "").trim();
    const saved = localStorage.getItem("verna_active_view") || "scanner";
    let targetView = hash || saved;
    const validViews = ["scanner", "khata", "business", "ledger", "ai"];
    if (!validViews.includes(targetView)) {
        targetView = "scanner";
    }
    switchView(targetView);
}

// -----------------------------------------------------------------------------
// VIEW NAVIGATION
// -----------------------------------------------------------------------------
function updateHudText() {
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
}

function switchView(viewName) {
    const validViews = ["scanner", "khata", "business", "ledger", "ai"];
    if (!validViews.includes(viewName)) viewName = "scanner";

    state.currentView = viewName;
    localStorage.setItem("verna_active_view", viewName);
    try {
        if (window.location.hash !== `#${viewName}`) {
            history.replaceState(null, "", `#${viewName}`);
        }
    } catch (e) {}

    // Toggle Desktop Sidebar Links
    document.querySelectorAll(".desktop-sidebar .nav-link").forEach(link => {
        link.classList.toggle("active", link.dataset.view === viewName);
    });

    // Toggle Mobile Bottom Tabs
    document.querySelectorAll(".mobile-bottom-nav .tab-item").forEach(tab => {
        tab.classList.toggle("active", tab.dataset.view === viewName);
    });

    // Toggle View Sections
    document.querySelectorAll(".view-section").forEach(sec => {
        sec.classList.toggle("active", sec.id === `view-${viewName}`);
    });

    if (viewName === "business") {
        applyShopSettingsToUI();
    }

    // Update HUD titles based on active language
    updateHudText();
}

// -----------------------------------------------------------------------------
// DASHBOARD & METRICS
// -----------------------------------------------------------------------------
async function loadDashboardMetrics() {
    try {
        const res = await apiCall("/api/dashboard");
        if (!res.ok) return;
        const data = await res.json();
        state.dashboard = data;

        // Ensure total bills and sales reflect all persistent receipts if serverless container was recycled
        if (state.allReceipts && state.allReceipts.length > 0) {
            const persistentTotal = state.allReceipts.reduce((acc, r) => acc + (Number(r.grand_total) || 0), 0);
            if (persistentTotal > (data.total_sales || 0)) {
                data.total_sales = persistentTotal;
                data.total_bills = state.allReceipts.length;
                data.avg_ticket = data.total_sales / data.total_bills;
            }
        }

        // Populate top KPI cards safely
        const elSales = document.getElementById("kpi-total-sales");
        if (elSales) elSales.innerText = `₹${data.total_sales.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

        const elBills = document.getElementById("kpi-total-bills");
        if (elBills) elBills.innerText = data.total_bills;

        const elAvg = document.getElementById("kpi-avg-ticket");
        if (elAvg) elAvg.innerText = `₹${data.avg_ticket.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

        const elPending = document.getElementById("kpi-pending-udhar");
        if (elPending) elPending.innerText = `₹${data.pending_udhar.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

        const netProfitEl = document.getElementById("kpi-net-profit");
        if (netProfitEl) {
            const np = (data.net_profit !== undefined) ? data.net_profit : (data.total_sales - data.total_expenses);
            netProfitEl.innerText = `₹${np.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        }

        // Populate Khata KPI
        const khataPending = document.getElementById("khata-kpi-pending");
        if (khataPending) khataPending.innerText = `₹${data.pending_udhar.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        const khataRecovered = document.getElementById("khata-kpi-recovered");
        if (khataRecovered) khataRecovered.innerText = `₹${data.cash_recovered.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

        // Total Expenses
        const expDisp = document.getElementById("total-expenses-display");
        if (expDisp) expDisp.innerText = `₹${data.total_expenses.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    } catch (e) {
        console.error("Dashboard metrics error:", e);
    }
}

// -----------------------------------------------------------------------------
// SCANNER MODE & FILE CAPTURE
// -----------------------------------------------------------------------------
function switchScannerMode(mode) {
    state.scannerMode = mode;
    const btnVision = document.getElementById("tab-btn-vision");
    const btnVoice = document.getElementById("tab-btn-voice");
    const containerVision = document.getElementById("scanner-vision-container");
    const containerVoice = document.getElementById("scanner-voice-container");

    if (mode === "vision") {
        btnVision.style.background = "rgba(0, 242, 254, 0.2)";
        btnVision.style.color = "var(--neon-cyan)";
        btnVision.style.borderColor = "var(--neon-cyan)";

        btnVoice.style.background = "rgba(255,255,255,0.05)";
        btnVoice.style.color = "var(--text-slate)";
        btnVoice.style.borderColor = "transparent";

        containerVision.style.display = "block";
        containerVoice.style.display = "none";
    } else {
        btnVoice.style.background = "rgba(0, 242, 254, 0.2)";
        btnVoice.style.color = "var(--neon-cyan)";
        btnVoice.style.borderColor = "var(--neon-cyan)";

        btnVision.style.background = "rgba(255,255,255,0.05)";
        btnVision.style.color = "var(--text-slate)";
        btnVision.style.borderColor = "transparent";

        containerVision.style.display = "none";
        containerVoice.style.display = "block";
    }
}

function handleReceiptFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    setReceiptImage(file);
}

function setReceiptImage(file) {
    state.selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById("image-preview").src = e.target.result;
        document.getElementById("image-preview-wrapper").style.display = "block";
        document.getElementById("image-preview-name").innerText = file.name;
        document.getElementById("btn-run-ocr").disabled = false;
    };
    reader.readAsDataURL(file);
}

// Live Camera
async function openCameraModal() {
    const modal = document.getElementById("modal-camera");
    const video = document.getElementById("camera-video-stream");
    modal.classList.add("active");

    try {
        state.cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" }
        });
        video.srcObject = state.cameraStream;
    } catch (err) {
        alert("कॅमेरा सुरू करता आला नाही: " + err.message);
        closeCameraModal();
    }
}

function closeCameraModal() {
    if (state.cameraStream) {
        state.cameraStream.getTracks().forEach(t => t.stop());
        state.cameraStream = null;
    }
    document.getElementById("modal-camera").classList.remove("active");
}

function captureCameraPhoto() {
    const video = document.getElementById("camera-video-stream");
    const canvas = document.getElementById("camera-canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        const file = new File([blob], `camera_receipt_${Date.now()}.jpg`, { type: "image/jpeg" });
        setReceiptImage(file);
        closeCameraModal();
    }, "image/jpeg", 0.9);
}

// -----------------------------------------------------------------------------
// MULTIMODAL OCR (GEMINI FLASH & ULTRA-FAST COMPRESSION)
// -----------------------------------------------------------------------------
async function compressImageForOCR(file, maxDimension = 1280, quality = 0.82) {
    return new Promise((resolve) => {
        if (!file || (file.size && file.size < 350 * 1024)) {
            resolve(file);
            return;
        }
        const img = new Image();
        const reader = new FileReader();
        reader.onload = (e) => {
            img.onload = () => {
                let width = img.width;
                let height = img.height;
                if (width > maxDimension || height > maxDimension) {
                    if (width > height) {
                        height = Math.round((height * maxDimension) / width);
                        width = maxDimension;
                    } else {
                        width = Math.round((width * maxDimension) / height);
                        height = maxDimension;
                    }
                }
                const canvas = document.createElement("canvas");
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0, width, height);
                canvas.toBlob((blob) => {
                    if (!blob) {
                        resolve(file);
                        return;
                    }
                    const compressed = new File([blob], "receipt_scan.jpg", {
                        type: "image/jpeg",
                        lastModified: Date.now()
                    });
                    resolve(compressed);
                }, "image/jpeg", quality);
            };
            img.onerror = () => resolve(file);
            img.src = e.target.result;
        };
        reader.onerror = () => resolve(file);
        reader.readAsDataURL(file);
    });
}

let isOcrScanning = false;

async function submitReceiptOCR() {
    if (!state.selectedFile) return;
    if (isOcrScanning) {
        console.warn("OCR is already in progress, ignoring duplicate trigger.");
        return;
    }

    const loader = document.getElementById("scanner-loader");
    const btn = document.getElementById("btn-run-ocr");
    const fileInput = document.getElementById("receipt-file-input");

    isOcrScanning = true;
    if (loader) loader.style.display = "block";
    if (btn) btn.disabled = true;
    if (fileInput) fileInput.disabled = true;

    try {
        const fileToUpload = await compressImageForOCR(state.selectedFile);
        const formData = new FormData();
        formData.append("file", fileToUpload);

        const res = await apiCall("/api/ocr", {
            method: "POST",
            body: formData
        });

        let json;
        const text = await res.text();
        try {
            json = JSON.parse(text);
        } catch (parseErr) {
            if (!res.ok) {
                throw new Error(`सर्व्हर तात्पुरता व्यस्त आहे (${res.status}). कृपया पुन्हा प्रयत्न करा.`);
            }
            throw new Error(`अवैध सर्व्हर रिस्पॉन्स.`);
        }

        if (!res.ok || !json || !json.success || !json.data) {
            const warnMsg = (json && json.warning) || (json && json.detail) || "⚠️ पावती स्कॅन करताना अडचण आली. कृपया चांगल्या प्रकाशात सरळ फोटो काढून पुन्हा स्कॅन करा.";
            showToast(warnMsg, "warning", 5000);
            return;
        }

        state.currentBillId = json.data.id || null;
        state.currentBill = json.data;
        populateBillCard(json.data);

        if (json.duplicate) {
            showToast("⚠️ दुबार पावती: " + (json.warning || "ही पावती आधीच लेजरमध्ये नोंदवलेली आहे."), "warning", 4500);
        } else {
            VernaStorage.addReceipt(json.data);
            showToast("✅ पावती यशस्वीरित्या स्कॅन झाली व लेजरमध्ये नोंदवली गेली!", "success", 3500);
        }

        loadDashboardMetrics();
        loadReceiptsLedger();
    } catch (err) {
        console.error("OCR Error:", err);
        const errMsg = String(err.message || err || "");
        if (errMsg.includes("429") || errMsg.includes("quota") || errMsg.includes("Rate Limit") || errMsg.includes("exceeded") || errMsg.includes("502")) {
            showToast("⚠️ AI सर्व्हरवर तात्पुरती गर्दी आहे (Google Rate Limit). कृपया काही सेकंद थांबा आणि पुन्हा स्कॅन करा.", "warning", 5000);
        } else {
            showToast("❌ OCR स्कॅनिंग अयशस्वी: " + (errMsg.length > 80 ? errMsg.substring(0, 80) + "..." : errMsg), "error", 4500);
        }
    } finally {
        isOcrScanning = false;
        if (loader) loader.style.display = "none";
        if (btn) btn.disabled = false;
        if (fileInput) fileInput.disabled = false;
    }
}

// -----------------------------------------------------------------------------
// VERNACULAR MARATHI VOICE BILLING
// -----------------------------------------------------------------------------
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("Web Speech API not supported in this browser.");
        return;
    }

    state.speechRecognition = new SpeechRecognition();
    state.speechRecognition.continuous = true;
    state.speechRecognition.interimResults = true;
    state.speechRecognition.lang = getLanguage().speech;

    state.speechRecognition.onstart = () => {
        state.isRecording = true;
        document.getElementById("btn-voice-mic").classList.add("recording");
        document.getElementById("voice-recording-status").innerText = "🎙️ मी ऐकत आहे... सामान बोला...";
        document.getElementById("voice-recording-status").style.color = "var(--neon-green)";
    };

    state.speechRecognition.onresult = (event) => {
        const output = document.getElementById("voice-transcript-text");
        let finalText = "";
        let interimText = "";
        for (let i = event.resultIndex; i < event.results.length; i += 1) {
            const text = event.results[i][0].transcript;
            if (event.results[i].isFinal) finalText += text;
            else interimText += text;
        }
        const currentText = output.value.replace(/\s*\[.*\]$/, "").trim();
        const combined = `${currentText}${finalText.trim() ? ` ${finalText.trim()}` : ""}${interimText.trim() ? ` [${interimText.trim()}]` : ""}`.trim();
        output.value = autoCorrectMarathiSpeech(combined);
    };

    state.speechRecognition.onerror = (event) => {
        console.error("Speech Recognition Error:", event.error);
        stopVoiceRecording();
    };

    state.speechRecognition.onend = () => {
        stopVoiceRecording();
    };
}

function toggleVoiceRecording() {
    if (!state.speechRecognition) {
        initSpeechRecognition();
    }
    if (!state.speechRecognition) {
        alert("आपल्या ब्राऊझरमध्ये व्हॉइस रेकग्निशन समर्थित नाही. कृपया खाली बॉक्समध्ये स्वतः टाईप करा.");
        return;
    }

    if (state.isRecording) {
        state.speechRecognition.stop();
        stopVoiceRecording();
    } else {
        state.speechRecognition.lang = getLanguage().speech;
        try {
            state.speechRecognition.start();
        } catch (err) {
            console.warn("Speech recognition could not start:", err);
            stopVoiceRecording();
        }
    }
}

function stopVoiceRecording() {
    state.isRecording = false;
    document.getElementById("btn-voice-mic").classList.remove("recording");
    document.getElementById("voice-recording-status").innerText = "बोलण्यासाठी माईक वर क्लिक करा";
    document.getElementById("voice-recording-status").style.color = "var(--text-dim)";
}

async function submitVoiceBilling() {
    const text = document.getElementById("voice-transcript-text").value.trim();
    if (!text) {
        alert("कृपया आधी माईक द्वारे बोला किंवा मजकूर टाईप करा.");
        return;
    }

    const loader = document.getElementById("scanner-loader");
    loader.style.display = "block";
    document.getElementById("scanner-loader-text").innerText = "व्हॉइस पावती तयार होत आहे...";

    try {
        const res = await apiCall("/api/voice-billing", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript: text, username: state.user ? state.user.username : "admin" })
        });
        const json = await res.json();

        if (!res.ok) {
            throw new Error(json.detail || "व्हॉइस पावती तयार करता आली नाही.");
        }

        populateBillCard(json.data);
        loadDashboardMetrics();
        loadReceiptsLedger();
        alert("✅ व्हॉइस पावती तयार झाली व लेजरमध्ये नोंदवली गेली!");
    } catch (err) {
        alert("व्हॉइस एरर: " + err.message);
    } finally {
        loader.style.display = "none";
    }
}

// -----------------------------------------------------------------------------
// LIVE EDITABLE BILL CENTER
// -----------------------------------------------------------------------------
function resetBillCard() {
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
}

function populateBillCard(data) {
    state.currentBill = data;
    document.getElementById("bill-vendor-name").value = data.vendor_name || "";
    if (data.date && data.date.includes("-")) {
        document.getElementById("bill-date").value = data.date;
    }

    const tbody = document.getElementById("bill-items-tbody");
    tbody.innerHTML = "";

    if (data.items && data.items.length > 0) {
        data.items.forEach(item => {
            const displayName = formatLocalizedName(item.item_name || "", state.lang);
            appendBillRow(displayName, item.quantity || "1", item.rate || 0, item.total_price || 0);
        });
    }

    recalcBillTotal();
}

function appendBillRow(name = "", qty = "1", rate = 0, total = 0) {
    const tbody = document.getElementById("bill-items-tbody");
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td><input type="text" class="input-cyber item-name" value="${escapeHtml(name)}"></td>
        <td><input type="text" class="input-cyber item-qty" value="${escapeHtml(String(qty))}" oninput="recalcBillTotal()"></td>
        <td><input type="number" class="input-cyber item-rate" value="${rate}" step="0.5" oninput="recalcBillTotal()"></td>
        <td class="item-total" style="font-weight: 700; color: var(--neon-cyan);">${Number(total).toFixed(2)}</td>
        <td><button onclick="removeBillRow(this)" style="background: none; border: none; color: var(--neon-red); cursor: pointer; font-size: 1.1rem;">✕</button></td>
    `;
    tbody.appendChild(tr);
}

function addBillRow() {
    const tbody = document.getElementById("bill-items-tbody");
    if (tbody && tbody.querySelector("td[colspan]")) {
        tbody.innerHTML = "";
    }
    appendBillRow("", "1", 0, 0);
}

function removeBillRow(btn) {
    const row = btn.closest("tr");
    const tbody = document.getElementById("bill-items-tbody");
    if (tbody.children.length > 1) {
        row.remove();
        recalcBillTotal();
    } else {
        alert("पावतीमध्ये किमान एक वस्तू असणे आवश्यक आहे.");
    }
}

function recalcBillTotal() {
    const rows = document.querySelectorAll("#bill-items-tbody tr");
    let grandTotal = 0;

    rows.forEach(row => {
        const qtyEl = row.querySelector(".item-qty");
        const rateEl = row.querySelector(".item-rate");
        if (!qtyEl || !rateEl) return; // Skip placeholder or informational rows safely

        const qtyStr = qtyEl.value;
        const rateVal = rateEl.value;
        const qtyNum = parseDevanagariNum(qtyStr) || 1;
        const rate = parseDevanagariNum(rateVal) || 0;
        const total = qtyNum * rate;

        const totalCell = row.querySelector(".item-total");
        if (totalCell) totalCell.innerText = total.toFixed(2);
        grandTotal += total;
    });

    const totalEl = document.getElementById("bill-grand-total");
    if (totalEl) totalEl.innerText = `₹${grandTotal.toFixed(2)}`;
    return grandTotal;
}

function getCurrentBillData() {
    const vendorEl = document.getElementById("bill-vendor-name");
    const vendor = vendorEl ? (vendorEl.value.trim() || "किराणा स्टोअर") : "किराणा स्टोअर";
    const dateEl = document.getElementById("bill-date");
    const dateVal = dateEl ? (dateEl.value || new Date().toISOString().split("T")[0]) : new Date().toISOString().split("T")[0];
    const rows = document.querySelectorAll("#bill-items-tbody tr");
    const items = [];
    let grandTotal = 0;

    rows.forEach(row => {
        const nameEl = row.querySelector(".item-name");
        const qtyEl = row.querySelector(".item-qty");
        const rateEl = row.querySelector(".item-rate");
        const totalCell = row.querySelector(".item-total");
        if (!nameEl || !qtyEl || !rateEl) return; // Skip placeholder row safely

        const name = nameEl.value.trim();
        const qty = qtyEl.value.trim();
        const rate = parseFloat(rateEl.value) || 0;
        const total = totalCell ? (parseFloat(totalCell.innerText) || 0) : (rate * 1);
        if (name) {
            items.push({ item_name: name, quantity: qty, rate: rate, total_price: total });
            grandTotal += total;
        }
    });

    return {
        vendor_name: vendor,
        date: dateVal,
        category: "General",
        items: items,
        grand_total: grandTotal
    };
}

async function saveCurrentBillToLedger() {
    const bill = getCurrentBillData();
    if (bill.items.length === 0) {
        const dict = i18n[state.lang] || i18n.mr;
        alert(dict.alert_no_items || "कृपया पावतीमध्ये किमान एक वस्तू टाका.");
        return;
    }

    try {
        const payload = {
            id: state.currentBillId || (state.currentBill && state.currentBill.id ? state.currentBill.id : null),
            vendor_name: bill.vendor_name || "किराणा स्टोअर",
            date: bill.date || new Date().toISOString().split("T")[0],
            category: (state.currentBill && state.currentBill.category) ? state.currentBill.category : "General",
            items: bill.items,
            grand_total: bill.grand_total,
            username: state.user ? state.user.username : "admin"
        };

        const res = await apiCall("/api/receipts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("पावती सेव्ह करता आली नाही.");

        const jsonRes = await res.json().catch(() => ({}));
        const savedData = (jsonRes && jsonRes.data) ? jsonRes.data : { ...payload, id: jsonRes.id || Date.now() };

        VernaStorage.addReceipt(savedData);
        state.currentBillId = null;
        state.currentBill = null;

        loadDashboardMetrics();
        loadReceiptsLedger();
        
        const dict = i18n[state.lang] || i18n.mr;
        alert(dict.msg_receipt_saved || "✅ पावती यशस्वीरित्या डिजिटल लेजरमध्ये सेव्ह झाली!");
        resetBillCard();
    } catch (e) {
        console.error("Save bill error:", e);
        // Offline-first fallback
        VernaStorage.addReceipt({ ...bill, id: Date.now() });
        state.currentBillId = null;
        state.currentBill = null;
        loadDashboardMetrics();
        loadReceiptsLedger();
        alert("✅ पावती ऑफलाइन लेजरमध्ये सेव्ह झाली!");
        resetBillCard();
    }
}

// Edge TTS Audio Announcement
async function playCurrentBillTTS() {
    const bill = getCurrentBillData();
    const grandTotal = bill.grand_total;
    const vendor = bill.vendor_name;

    const marathiSpeech = `नमस्कार, ${vendor} मधून एकूण ${bill.items.length} वस्तूंची खरेदी झाली आहे. एकूण देय रक्कम रुपये ${Math.round(grandTotal)} आहे. धन्यवाद!`;

    try {
        const res = await apiCall("/api/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: marathiSpeech, voice: "mr-IN-AarohiNeural" })
        });
        const data = await res.json();

        if (data.audio_data) {
            const audio = new Audio(data.audio_data);
            audio.play();
        } else {
            // Fallback to browser SpeechSynthesis
            const utterance = new SpeechSynthesisUtterance(marathiSpeech);
            utterance.lang = "mr-IN";
            window.speechSynthesis.speak(utterance);
        }
    } catch (e) {
        console.warn("TTS API fallback to local SpeechSynthesis:", e);
        const utterance = new SpeechSynthesisUtterance(marathiSpeech);
        utterance.lang = "mr-IN";
        window.speechSynthesis.speak(utterance);
    }
}

// Thermal Print Modal
function openThermalPrintModal() {
    const bill = getCurrentBillData();
    const isMr = state.lang === "mr";
    document.getElementById("receipt-shop-name").innerText = formatLocalizedName(bill.vendor_name, state.lang) || (state.lang === "en" ? "Kirana Store" : (state.lang === "hi" ? "किराना स्टोर" : "किराणा स्टोअर"));
    document.getElementById("receipt-bill-no").innerText = `#VL-${Math.floor(100 + Math.random() * 900)}`;
    document.getElementById("receipt-print-date").innerText = bill.date;
    document.getElementById("receipt-print-total").innerText = `₹${bill.grand_total.toFixed(2)}`;

    // Build items HTML with localized item names
    const container = document.getElementById("receipt-print-items");
    container.innerHTML = "";
    bill.items.forEach(i => {
        const displayName = formatLocalizedName(i.item_name, state.lang);
        const div = document.createElement("div");
        div.className = "row-flex";
        div.style.marginBottom = "3px";
        div.innerHTML = `
            <span style="flex: 2; text-align: left;">${escapeHtml(displayName)}</span>
            <span style="flex: 1; text-align: center;">${escapeHtml(i.quantity)}</span>
            <span style="flex: 1; text-align: right;">₹${i.total_price.toFixed(2)}</span>
        `;
        container.appendChild(div);
    });

    // Update UPI QR Code URL
    const upiUrl = `upi://pay?pa=merchant@upi&pn=${encodeURIComponent(bill.vendor_name)}&am=${bill.grand_total.toFixed(2)}&cu=INR`;
    document.getElementById("receipt-qr-img").src = `https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${encodeURIComponent(upiUrl)}`;

    document.getElementById("modal-thermal").classList.add("active");
}

function triggerBrowserPrint() {
    window.print();
}

// -----------------------------------------------------------------------------
// CUSTOMER KHATA (UDHAR LEDGER)
// -----------------------------------------------------------------------------
async function loadKhataData() {
    try {
        let serverData = null;
        try {
            const res = await apiCall("/api/khata");
            if (res.ok) {
                serverData = await res.json();
            }
        } catch (netErr) {
            console.warn("Khata server fetch notice:", netErr);
        }

        const serverTxns = (serverData && serverData.transactions) ? serverData.transactions : [];
        const mergedTxns = VernaStorage.mergeKhata(serverTxns);

        const custMap = {};
        mergedTxns.forEach(t => {
            const cName = t.customer_name || "ग्राहक";
            if (!custMap[cName]) {
                custMap[cName] = { name: cName, phone: t.phone || "", balance: 0.0, last_txn: t.date };
            }
            const amt = Number(t.amount) || 0;
            if (t.transaction_type === "Credit Given" || (t.transaction_type && t.transaction_type.includes("Credit"))) {
                custMap[cName].balance += amt;
            } else {
                custMap[cName].balance -= amt;
            }
        });

        const finalData = {
            transactions: mergedTxns,
            customers: Object.values(custMap)
        };
        state.allKhata = finalData;

        const custCountEl = document.getElementById("khata-kpi-customers");
        if (custCountEl) custCountEl.innerText = finalData.customers.length;
        const txnsCountEl = document.getElementById("khata-kpi-txns");
        if (txnsCountEl) txnsCountEl.innerText = finalData.transactions.length;

        try {
            renderKhataCards(finalData.customers);
        } catch (errCards) {
            console.error("Error in renderKhataCards:", errCards);
        }
        try {
            renderKhataTable(finalData.transactions);
        } catch (errTable) {
            console.error("Error in renderKhataTable:", errTable);
        }

        if (mergedTxns.length > serverTxns.length) {
            syncLocalDataToServer();
        }
    } catch (e) {
        console.error("Khata load error:", e);
    }
}

function renderKhataCards(customers) {
    const grid = document.getElementById("khata-customers-grid");
    if (!grid) return;
    grid.innerHTML = "";

    if (!customers || customers.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 30px;">कोणतेही उधारी खाते सापडले नाही. नवीन खाते जोडा.</div>`;
        return;
    }

    // Update Filter Pill Badges
    const allCount = customers.length;
    const pendingCount = customers.filter(c => c.balance > 0).length;
    const clearedCount = customers.filter(c => c.balance <= 0).length;
    const elAll = document.getElementById("count-all-cust");
    const elPend = document.getElementById("count-pending-cust");
    const elClr = document.getElementById("count-cleared-cust");
    if (elAll) elAll.innerText = allCount;
    if (elPend) elPend.innerText = pendingCount;
    if (elClr) elClr.innerText = clearedCount;

    // Apply Filter
    let list = customers;
    if (state.khataFilter === "pending") {
        list = customers.filter(c => c.balance > 0);
    } else if (state.khataFilter === "cleared") {
        list = customers.filter(c => c.balance <= 0);
    }

    if (list.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 30px;">या फिल्टरमध्ये कोणतेही ग्राहक सापडले नाहीत.</div>`;
        return;
    }

    list.forEach(c => {
        const isDebt = c.balance > 0;
        const card = document.createElement("div");
        card.className = `glass-card ${isDebt ? 'accent-red' : 'accent-green'}`;

        const safePhone = (c.phone || "").replace(/\D/g, "");
        const shopTitle = (state.user && state.user.shop_name) || (state.lang === 'mr' ? 'किराणा स्टोअर' : (state.lang === 'hi' ? 'किराना स्टोर' : 'Kirana Store'));
        const waMsg = encodeURIComponent(
            `🙏 *${shopTitle.trim()}*\n` +
            `नमस्कार ${c.name} जी!\n` +
            `आपल्या खात्यावर दुकानाचे एकूण *₹${c.balance.toFixed(2)}* उधारीचे येणे बाकी आहे.\n\n` +
            `💳 कृपया खालील UPI लिंकवरून GooglePay / PhonePe द्वारे पेमेंट करावे:\n` +
            `upi://pay?pa=merchant@upi&pn=${encodeURIComponent(shopTitle)}&am=${c.balance.toFixed(2)}&cu=INR\n\n` +
            `लवकरात लवकर भरणा करून सहकार्य करावे. धन्यवाद!`
        );
        const waLink = `https://wa.me/91${safePhone}?text=${waMsg}`;

        const displayName = formatLocalizedName(c.name, state.lang);
        const isMr = state.lang === "mr";
        const isHi = state.lang === "hi";
        const badgeText = isDebt 
            ? (isMr ? '🔴 उधारी बाकी' : (isHi ? '🔴 उधारी बकाया' : 'Credit Due'))
            : (isMr ? '🟢 हिशोब क्लिअर' : (isHi ? '🟢 हिसाब क्लीयर' : 'Cleared'));
        const balLabel = isMr ? 'सध्याची बाकी रक्कम (Balance):' : (isHi ? 'वर्तमान बकाया राशि (Balance):' : 'Current Balance Due:');
        const balStatus = isDebt 
            ? (isMr ? 'येणे बाकी' : (isHi ? 'बकाया' : 'Pending')) 
            : (isMr ? 'क्लिअर' : (isHi ? 'क्लीयर' : 'Nil'));
        const phoneLabel = c.phone || (isMr ? "नंबर नाही" : (isHi ? "नंबर नहीं" : "No Phone"));
        const btnCreditText = isMr ? '🔴 ₹ उधारी दिली' : (isHi ? '🔴 ₹ उधारी दी' : '🔴 ₹ Give Credit');
        const btnPaymentText = isMr ? '🟢 ₹ जमा मिळाले' : (isHi ? '🟢 ₹ जमा प्राप्त' : '🟢 ₹ Got Payment');

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: var(--text-white);">${escapeHtml(displayName)}</div>
                    <div style="font-size: 0.78rem; color: var(--text-slate);">📞 ${escapeHtml(phoneLabel)}</div>
                </div>
                <span class="user-role-badge ${isDebt ? 'badge-staff' : 'badge-admin'}">
                    ${badgeText}
                </span>
            </div>

            <div style="margin: 10px 0; padding: 8px 10px; background: rgba(255,255,255,0.03); border-radius: 8px;">
                <div style="font-size: 0.75rem; color: var(--text-slate);">${balLabel}</div>
                <div style="font-size: 1.45rem; font-weight: 800; color: ${isDebt ? 'var(--neon-red)' : 'var(--neon-green)'};">
                    ₹${Math.abs(c.balance).toFixed(2)} ${balStatus}
                </div>
            </div>

            <!-- Khatabook Style Quick Action Buttons -->
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 10px;">
                <button class="btn-give-credit" onclick="quickKhataAction('${escapeHtml(c.name)}', '${escapeHtml(c.phone)}', 'Credit Given')">
                    ${btnCreditText}
                </button>
                <button class="btn-get-payment" onclick="quickKhataAction('${escapeHtml(c.name)}', '${escapeHtml(c.phone)}', 'Payment Received')">
                    ${btnPaymentText}
                </button>
                ${isDebt && safePhone ? `
                    <a href="${waLink}" target="_blank" class="btn-whatsapp-share" style="grid-column: 1/-1; padding: 6px 10px; font-size: 0.78rem;">
                        📲 WhatsApp तगादा पाठवा
                    </a>
                ` : ''}
            </div>
        `;
        grid.appendChild(card);
    });
}

state.selectedKhataIds = state.selectedKhataIds || new Set();

function renderKhataTable(transactions) {
    const tbody = document.getElementById("khata-table-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!transactions || transactions.length === 0) {
        const dict = i18n[state.lang] || i18n.mr;
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-dim); padding: 24px;">${dict.empty_khata_txns || "कोणताही खाते व्यवहार उपलब्ध नाही."}</td></tr>`;
        updateKhataBulkActionBar(0, 0);
        return;
    }

    const allTxnIds = new Set(transactions.map(t => Number(t.id)));
    // Prune selections that no longer exist
    for (const sid of Array.from(state.selectedKhataIds)) {
        if (!allTxnIds.has(sid)) state.selectedKhataIds.delete(sid);
    }

    transactions.forEach(t => {
        const isCredit = t.transaction_type === "Credit Given";
        const displayName = formatLocalizedName(t.customer_name, state.lang);
        const tr = document.createElement("tr");
        const tid = Number(t.id);
        const isSelected = state.selectedKhataIds.has(tid);
        if (isSelected) tr.classList.add("row-selected");

        tr.innerHTML = `
            <td style="text-align: center; width: 36px;">
                <input type="checkbox" class="khata-row-cb" data-id="${tid}" ${isSelected ? 'checked' : ''} onchange="toggleKhataRowSelect(${tid}, this.checked)">
            </td>
            <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">#${tid}</td>
            <td style="font-weight: 700; color: var(--text-white);">${escapeHtml(displayName)}</td>
            <td style="color: var(--text-slate);">${escapeHtml(t.phone)}</td>
            <td>
                <span class="user-role-badge ${isCredit ? 'badge-staff' : 'badge-admin'}">
                    ${isCredit ? (state.lang === "mr" ? 'उधारी दिली' : (state.lang === "hi" ? 'उधारी दी' : 'Credit Given')) : (state.lang === "mr" ? 'जमा केले' : (state.lang === "hi" ? 'जमा प्राप्त' : 'Payment Received'))}
                </span>
            </td>
            <td style="font-weight: 800; color: ${isCredit ? 'var(--neon-red)' : 'var(--neon-green)'};">
                ₹${Number(t.amount).toFixed(2)}
            </td>
            <td>${t.date}</td>
            <td style="color: var(--neon-amber);">${t.due_date || '-'}</td>
            <td>
                <button onclick="deleteKhataEntry(${tid})" style="background: none; border: none; color: var(--neon-red); cursor: pointer; font-size: 1rem;" title="डीलीट करा">
                    🗑️
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    updateKhataBulkActionBar(state.selectedKhataIds.size, transactions.length);
}

function toggleSelectAllKhata(isChecked) {
    if (!state.allKhata || !state.allKhata.transactions) return;
    const searchVal = (document.getElementById("khata-search-input") ? document.getElementById("khata-search-input").value : "").toLowerCase();
    const visibleTxns = state.allKhata.transactions.filter(t => 
        !searchVal || t.customer_name.toLowerCase().includes(searchVal) || (t.phone && t.phone.includes(searchVal))
    );

    if (isChecked) {
        visibleTxns.forEach(t => state.selectedKhataIds.add(Number(t.id)));
    } else {
        visibleTxns.forEach(t => state.selectedKhataIds.delete(Number(t.id)));
    }
    renderKhataTable(visibleTxns);
}

function toggleKhataRowSelect(id, isChecked) {
    id = Number(id);
    if (isChecked) {
        state.selectedKhataIds.add(id);
    } else {
        state.selectedKhataIds.delete(id);
    }
    const searchVal = (document.getElementById("khata-search-input") ? document.getElementById("khata-search-input").value : "").toLowerCase();
    const visibleTxns = state.allKhata.transactions.filter(t => 
        !searchVal || t.customer_name.toLowerCase().includes(searchVal) || (t.phone && t.phone.includes(searchVal))
    );
    renderKhataTable(visibleTxns);
}

function updateKhataBulkActionBar(selectedCount, totalCount) {
    const bar = document.getElementById("khata-bulk-actions-bar");
    const countEl = document.getElementById("khata-selected-count");
    const totalEl = document.getElementById("khata-total-count");
    const allCb = document.getElementById("khata-select-all-cb");

    if (countEl) countEl.innerText = selectedCount;
    if (totalEl) totalEl.innerText = totalCount;
    if (allCb) allCb.checked = (totalCount > 0 && selectedCount === totalCount);

    if (bar) {
        if (selectedCount > 0) {
            bar.style.display = "flex";
        } else {
            bar.style.display = "none";
        }
    }
}

async function bulkDeleteSelectedKhata() {
    if (!state.selectedKhataIds || state.selectedKhataIds.size === 0) return;
    const count = state.selectedKhataIds.size;
    const dict = i18n[state.lang] || i18n.mr;
    const confirmMsg = (dict.confirm_bulk_delete_khata || "तुम्हाला निवडलेले {n} खाते व्यवहार कायमचे डिलीट करायचे आहेत का?").replace("{n}", count);
    if (!confirm(confirmMsg)) return;

    const idsToDelete = Array.from(state.selectedKhataIds);
    try {
        await apiCall("/api/khata/bulk-delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ entry_ids: idsToDelete })
        });
    } catch (e) {
        console.warn("Server bulk delete notice:", e);
    }

    // Sync localStorage
    if (typeof VernaStorage !== "undefined") {
        const stored = VernaStorage.getKhata();
        const updated = stored.filter(t => !idsToDelete.includes(Number(t.id)));
        VernaStorage.saveKhata(updated);
    }

    state.selectedKhataIds.clear();
    await loadKhataData();
    alert((dict.msg_bulk_delete_khata_success || "✅ निवडलेले {n} व्यवहार यशस्वीरीत्या डिलीट केले!").replace("{n}", count));
}

async function clearEntireKhata() {
    const dict = i18n[state.lang] || i18n.mr;
    const confirmMsg = dict.confirm_clear_all_khata || "⚠️ सावधान! तुम्हाला सर्व खाते व्यवहार कायमचे डिलीट करायचे आहेत का? ही कृती पूर्ववत करता येणार नाही!";
    if (!confirm(confirmMsg)) return;

    try {
        await apiCall("/api/khata/all", { method: "DELETE" });
    } catch (e) {
        console.warn("Server clear all notice:", e);
    }

    if (typeof VernaStorage !== "undefined") {
        VernaStorage.saveKhata([]);
    }

    state.selectedKhataIds.clear();
    await loadKhataData();
    alert(dict.msg_clear_all_khata_success || "✅ सर्व खाते व्यवहार रिकामे केले गेले!");
}

function filterKhataList() {
    if (!state.allKhata || !state.allKhata.customers) return;
    const query = document.getElementById("khata-search-input").value.toLowerCase();
    const filteredCust = state.allKhata.customers.filter(c => 
        c.name.toLowerCase().includes(query) || (c.phone && c.phone.includes(query))
    );
    renderKhataCards(filteredCust);

    const filteredTxns = state.allKhata.transactions.filter(t =>
        t.customer_name.toLowerCase().includes(query) || (t.phone && t.phone.includes(query))
    );
    renderKhataTable(filteredTxns);
}

function openAddKhataModal() {
    document.getElementById("modal-add-khata").classList.add("active");
}

function prefillKhataPayment(name, phone) {
    document.getElementById("khata-input-name").value = name;
    document.getElementById("khata-input-phone").value = phone;
    document.getElementById("khata-input-type").value = "Payment Received";
    openAddKhataModal();
}

async function submitAddKhata(e) {
    e.preventDefault();
    const payload = {
        customer_name: document.getElementById("khata-input-name").value.trim(),
        phone: document.getElementById("khata-input-phone").value.trim(),
        transaction_type: document.getElementById("khata-input-type").value,
        amount: parseFloat(document.getElementById("khata-input-amount").value),
        due_date: document.getElementById("khata-input-due").value,
        notes: document.getElementById("khata-input-notes").value.trim(),
        username: state.user ? state.user.username : "admin"
    };

    try {
        const res = await apiCall("/api/khata", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("खाते नोंदवता आले नाही.");

        const jsonKhata = await res.json().catch(() => ({}));
        payload.id = jsonKhata.id || Date.now();
        payload.date = new Date().toISOString().split("T")[0];
        VernaStorage.addKhata(payload);

        closeModal("modal-add-khata");
        document.getElementById("form-add-khata").reset();
        loadKhataData();
        loadDashboardMetrics();
        alert("✅ व्यवहार यशस्वीरित्या सेव्ह झाला!");
    } catch (err) {
        alert("एरर: " + err.message);
    }
}

async function deleteKhataEntry(id) {
    if (!confirm("हा व्यवहार कायमचा डिलीट करायचा आहे का?")) return;
    try {
        VernaStorage.removeKhata(id);
        await apiCall(`/api/khata/${id}`, { method: "DELETE" }).catch(() => {});
        loadKhataData();
        loadDashboardMetrics();
    } catch (e) {
        alert("एरर: " + e.message);
    }
}

// -----------------------------------------------------------------------------
// STORE OPERATIONS & INVENTORY
// -----------------------------------------------------------------------------
async function loadInventoryData() {
    try {
        const res = await apiCall("/api/inventory");
        if (!res.ok) return;
        const data = await res.json();
        state.allInventory = data;
        renderInventoryTable(data);
    } catch (e) {
        console.error("Inventory error:", e);
    }
}

function renderInventoryTable(data) {
    if (!data) data = state.allInventory || [];
    const tbody = document.getElementById("inventory-table-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    const isMr = state.lang === "mr";
    let lowStockItems = [];

    data.forEach(item => {
        const isLow = item.stock_qty <= item.alert_limit;
        const displayName = formatLocalizedName(item.item_name, state.lang);
        if (isLow) lowStockItems.push(`${displayName} (${item.stock_qty} ${item.unit})`);

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-weight: 700; color: var(--text-white);">${escapeHtml(displayName)}</td>
            <td style="font-weight: 800; color: ${isLow ? 'var(--neon-red)' : 'var(--neon-cyan)'};">
                ${item.stock_qty} ${escapeHtml(item.unit)}
            </td>
            <td>₹${Number(item.selling_price).toFixed(2)}</td>
            <td>
                <span class="user-role-badge ${isLow ? 'badge-staff' : 'badge-admin'}">
                    ${isLow ? (state.lang === "mr" ? 'कमी साठा' : (state.lang === "hi" ? 'कम स्टॉक' : 'Low Stock')) : (state.lang === "mr" ? 'उपलब्ध' : (state.lang === "hi" ? 'उपलब्ध' : 'In Stock'))}
                </span>
            </td>
            <td>
                <button onclick="deleteInventoryItem(${item.id})" style="background: none; border: none; color: var(--neon-red); cursor: pointer;" title="हटवा">
                    ✕
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    const banner = document.getElementById("low-stock-banner");
    const bannerText = document.getElementById("low-stock-items-text");
    if (banner && bannerText) {
        if (lowStockItems.length > 0) {
            banner.style.display = "flex";
            bannerText.innerText = (isMr ? "कमी साठा: " : "Low Stock: ") + lowStockItems.join(", ");
        } else {
            banner.style.display = "none";
        }
    }
}

function openAddInventoryModal() {
    document.getElementById("modal-add-inventory").classList.add("active");
}

async function submitAddInventory(e) {
    e.preventDefault();
    const payload = {
        item_name: document.getElementById("inv-input-name").value.trim(),
        stock_qty: parseFloat(document.getElementById("inv-input-qty").value),
        unit: document.getElementById("inv-input-unit").value,
        selling_price: parseFloat(document.getElementById("inv-input-price").value),
        alert_limit: parseFloat(document.getElementById("inv-input-limit").value)
    };

    try {
        const res = await apiCall("/api/inventory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("माल सेव्ह करता आला नाही.");

        closeModal("modal-add-inventory");
        document.getElementById("form-add-inventory").reset();
        loadInventoryData();
        alert("✅ माल यशस्वीरित्या जोडला गेला!");
    } catch (err) {
        alert("एरर: " + err.message);
    }
}

async function deleteInventoryItem(id) {
    if (!confirm("हा माल स्टॉक मधून डिलीट करायचा का?")) return;
    try {
        await apiCall(`/api/inventory/${id}`, { method: "DELETE" });
        loadInventoryData();
    } catch (e) {
        alert("एरर: " + e.message);
    }
}

// Expenses
async function loadExpensesData() {
    try {
        let serverData = [];
        try {
            const res = await apiCall("/api/expenses");
            if (res.ok) {
                serverData = await res.json();
            }
        } catch (netErr) {
            console.warn("Expenses server fetch notice:", netErr);
        }
        const merged = VernaStorage.mergeExpenses(serverData);
        state.allExpenses = merged;

        const tbody = document.getElementById("expenses-table-tbody");
        if (tbody) {
            tbody.innerHTML = "";
            merged.forEach(exp => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="font-weight: 700; color: var(--text-white);">${escapeHtml(exp.expense_title)}</td>
                <td style="color: var(--text-slate);">${escapeHtml(exp.category)}</td>
                <td style="font-weight: 800; color: var(--neon-red);">₹${Number(exp.amount).toFixed(2)}</td>
                <td style="font-size: 0.78rem;">${exp.date}</td>
            `;
            tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error("Expenses load error:", e);
    }
}

async function handleAddExpense(e) {
    e.preventDefault();
    const payload = {
        expense_title: document.getElementById("expense-title").value.trim(),
        amount: parseFloat(document.getElementById("expense-amount").value),
        category: document.getElementById("expense-category").value,
        notes: ""
    };

    try {
        const res = await apiCall("/api/expenses", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("खर्च नोंदवता आला नाही.");

        payload.date = new Date().toISOString().split("T")[0];
        VernaStorage.addExpense(payload);

        document.getElementById("expense-form").reset();
        loadExpensesData();
        loadDashboardMetrics();
        alert("✅ खर्च नोंदवला गेला!");
    } catch (err) {
        alert("एरर: " + err.message);
    }
}

function shareDailyDigestWhatsApp() {
    if (!state.dashboard || !state.dashboard.daily_digest_mr) {
        alert("दैनिक अहवाल तयार होत आहे. कृपया पुन्हा प्रयत्न करा.");
        return;
    }
    const msg = encodeURIComponent(state.dashboard.daily_digest_mr);
    window.open(`https://wa.me/?text=${msg}`, "_blank");
}

// -----------------------------------------------------------------------------
// LEDGER DATABASE & RECEIPTS HISTORY
// -----------------------------------------------------------------------------
async function loadReceiptsLedger() {
    try {
        let serverData = [];
        try {
            const res = await apiCall("/api/receipts");
            if (res.ok) {
                serverData = await res.json();
            }
        } catch (netErr) {
            console.warn("Server receipts fetch notice:", netErr);
        }
        const merged = VernaStorage.mergeReceipts(serverData);
        state.allReceipts = merged;
        renderLedgerTable(merged);

        if (merged.length > serverData.length) {
            syncLocalDataToServer();
        }
    } catch (e) {
        console.error("Receipts load error:", e);
    }
}

function renderLedgerTable(receipts) {
    const tbody = document.getElementById("ledger-table-tbody");
    tbody.innerHTML = "";

    const totalCountEl = document.getElementById("ledger-total-count");
    if (totalCountEl) totalCountEl.innerText = (receipts ? receipts.length : 0);

    const selectAllCheckbox = document.getElementById("ledger-select-all");
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    }
    updateSelectedReceiptsUI();

    if (!receipts || receipts.length === 0) {
        const dict = i18n[state.lang] || i18n.mr;
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 24px;">${dict.empty_ledger || "कोणतीही पावती उपलब्ध नाही."}</td></tr>`;
        return;
    }

    receipts.forEach(r => {
        const isMr = state.lang === 'mr';
        const displayName = formatLocalizedName(r.vendor_name || (isMr ? 'किराणा स्टोअर' : 'Kirana Store'), state.lang);
        const tr = document.createElement("tr");
        tr.id = `ledger-row-${r.id}`;
        tr.innerHTML = `
            <td style="text-align: center;">
                <input type="checkbox" class="cyber-checkbox ledger-row-checkbox" value="${r.id}" onchange="onReceiptCheckboxChange(this, ${r.id})">
            </td>
            <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--neon-cyan);">#VL-${r.id}</td>
            <td style="font-weight: 700; color: var(--text-white);">${escapeHtml(displayName)}</td>
            <td>${r.date}</td>
            <td><span class="user-role-badge badge-admin">${escapeHtml(r.category || 'General')}</span></td>
            <td style="font-weight: 800; color: var(--neon-green); font-size: 0.95rem;">₹${Number(r.grand_total).toFixed(2)}</td>
            <td>
                <div style="display: flex; gap: 6px;">
                    <button class="btn-pill btn-lang" onclick="viewSavedReceiptThermal(${r.id})" title="पावती पहा">
                        🖨️
                    </button>
                    <button onclick="deleteReceipt(${r.id})" style="background: none; border: none; color: var(--neon-red); cursor: pointer; font-size: 1.1rem;" title="डीलीट">
                        🗑️
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// =============================================================================
// LEDGER MULTI-SELECT & BULK ACTIONS CONTROLLER
// =============================================================================
function getSelectedReceiptIds() {
    const checkedBoxes = document.querySelectorAll(".ledger-row-checkbox:checked");
    return Array.from(checkedBoxes).map(cb => Number(cb.value));
}

function onReceiptCheckboxChange(checkbox, id) {
    const row = document.getElementById(`ledger-row-${id}`);
    if (row) {
        if (checkbox.checked) {
            row.classList.add("row-selected");
        } else {
            row.classList.remove("row-selected");
        }
    }
    updateSelectedReceiptsUI();
}

function toggleSelectAllReceipts(master) {
    const isChecked = master.checked;
    const checkboxes = document.querySelectorAll(".ledger-row-checkbox");
    checkboxes.forEach(cb => {
        cb.checked = isChecked;
        const row = document.getElementById(`ledger-row-${cb.value}`);
        if (row) {
            if (isChecked) {
                row.classList.add("row-selected");
            } else {
                row.classList.remove("row-selected");
            }
        }
    });
    updateSelectedReceiptsUI();
}

function updateSelectedReceiptsUI() {
    const selected = getSelectedReceiptIds();
    const count = selected.length;
    const total = document.querySelectorAll(".ledger-row-checkbox").length;

    const btnBulk = document.getElementById("btn-ledger-bulk-delete");
    const countSpan = document.getElementById("ledger-selected-count");
    const numSpan = document.getElementById("ledger-selected-num");
    const statsPill = document.getElementById("ledger-selected-stats-pill");
    const master = document.getElementById("ledger-select-all");

    if (countSpan) countSpan.innerText = count;
    if (numSpan) numSpan.innerText = count;

    if (btnBulk) {
        btnBulk.style.display = count > 0 ? "inline-flex" : "none";
    }
    if (statsPill) {
        statsPill.style.display = count > 0 ? "inline-block" : "none";
    }
    if (master) {
        master.checked = total > 0 && count === total;
        master.indeterminate = count > 0 && count < total;
    }
}

async function bulkDeleteSelectedReceipts() {
    const selectedIds = getSelectedReceiptIds();
    const count = selectedIds.length;
    const dict = i18n[state.lang] || i18n.mr;

    if (count === 0) {
        alert(dict.no_receipts_selected || "कृपया आधी किमान एक पावती निवडा!");
        return;
    }

    const template = dict.confirm_bulk_delete || "तुम्हाला निवडलेल्या {n} पावत्या लेजरमधून कायमच्या डिलीट करायच्या आहेत का?";
    const msg = template.replace("{n}", count);
    if (!confirm(msg)) return;

    try {
        // 1. Remove from local client persistence
        VernaStorage.removeReceipts(selectedIds);

        // 2. Call server bulk-delete endpoint
        await apiCall("/api/receipts/bulk-delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ receipt_ids: selectedIds })
        }).catch(async (e) => {
            console.warn("Bulk delete server notice, falling back to sequential:", e);
            for (const id of selectedIds) {
                await apiCall(`/api/receipts/${id}`, { method: "DELETE" }).catch(() => {});
            }
        });

        // 3. Reload ledger and metrics
        await loadReceiptsLedger();
        loadDashboardMetrics();

        const successTpl = dict.msg_bulk_delete_success || "✅ निवडलेल्या {n} पावत्या यशस्वीरीत्या डिलीट केल्या!";
        alert(successTpl.replace("{n}", count));
    } catch (err) {
        alert("एरर: " + err.message);
    }
}

async function clearEntireLedger() {
    const total = (state.allReceipts || []).length;
    const dict = i18n[state.lang] || i18n.mr;

    if (total === 0) {
        alert(dict.empty_ledger || "लेजरमध्ये कोणतीही पावती उपलब्ध नाही.");
        return;
    }

    const msg = dict.confirm_clear_all || "⚠️ सावधान! तुम्हाला लेजरमधील सर्व पावत्या कायमच्या डिलीट करायच्या आहेत का? ही कृती पूर्ववत करता येणार नाही!";
    if (!confirm(msg)) return;

    if (!confirm(`नक्की? लेजरमधील संपूर्ण ${total} पावत्या कायमच्या नष्ट होतील!`)) return;

    try {
        VernaStorage.clearAllReceipts();
        await apiCall("/api/receipts/all", { method: "DELETE" }).catch(async () => {
            const allIds = (state.allReceipts || []).map(r => r.id);
            await apiCall("/api/receipts/bulk-delete", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ receipt_ids: allIds })
            }).catch(() => {});
        });

        await loadReceiptsLedger();
        loadDashboardMetrics();

        alert(dict.msg_clear_all_success || "✅ सर्व पावत्या लेजरमधून यशस्वीरीत्या डिलीट केल्या!");
    } catch (err) {
        alert("एरर: " + err.message);
    }
}

function filterLedgerList() {
    const q = document.getElementById("ledger-search-input").value.toLowerCase();
    const filtered = state.allReceipts.filter(r => 
        (r.vendor_name && r.vendor_name.toLowerCase().includes(q)) ||
        (r.category && r.category.toLowerCase().includes(q)) ||
        (r.date && r.date.includes(q)) ||
        String(r.id).includes(q)
    );
    renderLedgerTable(filtered);
}

function viewSavedReceiptThermal(id) {
    const r = state.allReceipts.find(x => x.id === id);
    if (!r) return;

    const raw = r.raw_json || {};
    populateBillCard({
        vendor_name: r.vendor_name,
        date: r.date,
        category: r.category,
        items: raw.items || [{ item_name: "किराणा खरेदी", quantity: "1", rate: r.grand_total, total_price: r.grand_total }],
        grand_total: r.grand_total
    });
    openThermalPrintModal();
}

async function deleteReceipt(id) {
    if (!confirm(`पावती #${id} लेजरमधून कायमची डिलीट करायची का?`)) return;
    try {
        VernaStorage.removeReceipt(id);
        await apiCall(`/api/receipts/${id}`, { method: "DELETE" }).catch(() => {});
        loadReceiptsLedger();
        loadDashboardMetrics();
    } catch (e) {
        alert("एरर: " + e.message);
    }
}

// =============================================================================
// NATIVE MICROSOFT EXCEL (.XLSX) EXPORT CONTROLLER
// Downloads server-generated OpenXML .xlsx with styled Marathi headers & numbers
// Works 100% reliably on Android, iOS, Windows, Mac (Zero 404 / Blob download)
// =============================================================================
async function downloadExcelReport() {
    const btn = document.getElementById("btn-ledger-excel-export");
    let originalHtml = "";
    if (btn) {
        originalHtml = btn.innerHTML;
        btn.innerHTML = `⏳ <span>डाऊनलोड होत आहे...</span>`;
        btn.disabled = true;
    }

    try {
        const d = new Date();
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const fileName = `VernaLedger_Receipts_${year}-${month}-${day}.xlsx`;

        // Robust multi-endpoint fallback cascade
        const candidateUrls = [
            `/export/excel?t=${Date.now()}`,
            `/receipts/export-excel?t=${Date.now()}`,
            `/api/export/excel?t=${Date.now()}`,
            `/api/receipts/export-excel?t=${Date.now()}`
        ];

        let res = null;
        for (const u of candidateUrls) {
            try {
                const tr = await fetch(u);
                if (tr.ok && tr.status === 200) {
                    res = tr;
                    break;
                }
            } catch (err) {
                console.warn(`URL ${u} fetch attempt:`, err);
            }
        }

        if (res && res.ok) {
            const blob = await res.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = blobUrl;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();

            setTimeout(() => {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(blobUrl);
            }, 3000);

            showToast("✅ Excel (.xlsx) फाईल यशस्वीरित्या डाउनलोड झाली!", "success", 4000);
            return;
        }

        // Offline / Client-Side Fallback: generate and download from localStorage receipts
        console.warn("Server excel endpoint unavailable, generating client-side export...");
        generateClientSideExcelDownload(fileName);
    } catch (err) {
        console.error("Excel download error:", err);
        showToast("⚠️ सर्व्हर व्यस्त आहे, स्थानिक डेटा डाउनलोड केला जात आहे...", "warning", 3500);
        const d = new Date();
        const fileName = `VernaLedger_Receipts_${d.toISOString().slice(0, 10)}.xlsx`;
        generateClientSideExcelDownload(fileName);
    } finally {
        if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
        }
    }
}

function generateClientSideExcelDownload(fileName) {
    try {
        const receipts = (typeof VernaStorage !== 'undefined') ? VernaStorage.get(VernaStorage.KEY_RECEIPTS) : [];
        let csv = "\ufeff"; // UTF-8 BOM so Excel opens Marathi / Devanagari accurately without mojibake
        csv += "बिल क्र. (Bill ID),दुकान / ग्राहक नाव (Store / Customer),तारीख (Date),प्रवर्ग (Category),वस्तू तपशील (Items Details),एकूण रक्कम (Grand Total ₹)\r\n";

        let grandTotal = 0;
        receipts.forEach(r => {
            const id = `#VL-${r.id || ''}`;
            const name = (r.vendor_name || 'किराणा स्टोअर').replace(/"/g, '""');
            const dt = r.date || '';
            const cat = (r.category || 'General').replace(/"/g, '""');
            const tot = Number(r.grand_total || 0);
            grandTotal += tot;

            let itemsStr = '';
            if (r.items && Array.isArray(r.items)) {
                itemsStr = r.items.map(it => `${it.item_name || ''} (${it.quantity || '1'}): ₹${it.total_price || 0}`).join(' | ');
            }
            itemsStr = itemsStr.replace(/"/g, '""');
            csv += `"${id}","${name}","${dt}","${cat}","${itemsStr}",${tot.toFixed(2)}\r\n`;
        });

        csv += `"","","","एकूण बेरीज (Total Grand Revenue):","",${grandTotal.toFixed(2)}\r\n`;

        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = blobUrl;
        a.download = fileName.replace(/\.xlsx$/i, '.csv');
        document.body.appendChild(a);
        a.click();

        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(blobUrl);
        }, 3000);

        showToast("✅ स्थानिक डेटा CSV/Excel फॉरमॅटमध्ये डाउनलोड झाला!", "success", 4000);
    } catch (e) {
        console.error("Client export error:", e);
        showToast("❌ डाउनलोड अयशस्वी: " + e.message, "error", 4500);
    }
}

function exportLedgerExcel() {
    downloadExcelReport();
}

function exportLedgerCSV() {
    downloadExcelReport();
}

// -----------------------------------------------------------------------------
// NEURAL AI STUDIO (RAG ENGINE & VOICE COMMAND EXECUTION)
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// AUDIO PLAYBACK MANAGER (PREVENTS DOUBLE / OVERLAPPING VOICE)
// -----------------------------------------------------------------------------
let currentPlayingAudio = null;
let isAiProcessing = false;
let currentAudioPlayToken = 0;

let currentAiAudio = null;
let currentAiAudioBtn = null;
let aiAudioRequestId = 0;

function stopCurrentAudio() {
    currentAudioPlayToken++; // Invalidate any in-flight TTS calls
    aiAudioRequestId++; // Invalidate in-flight AI TTS calls

    if (currentPlayingAudio) {
        try {
            currentPlayingAudio.pause();
            currentPlayingAudio.currentTime = 0;
            currentPlayingAudio.src = "";
        } catch (e) {}
        currentPlayingAudio = null;
    }

    if (currentAiAudio) {
        try {
            currentAiAudio.pause();
            currentAiAudio.currentTime = 0;
            currentAiAudio.src = "";
        } catch (e) {}
        currentAiAudio = null;
    }

    if (currentAiAudioBtn) {
        try {
            currentAiAudioBtn.classList.remove("playing", "loading");
            currentAiAudioBtn.innerHTML = `🔊 <span>ऐका</span>`;
        } catch (e) {}
        currentAiAudioBtn = null;
    }

    if (window.speechSynthesis) {
        try {
            window.speechSynthesis.cancel();
        } catch (e) {}
    }
}

function prepareClientSpeech(audio_text) {
    if (!audio_text) return "";
    let clean = audio_text.replace(/[*#_`]/g, "");
    clean = clean.replace(/\bVernaLedger\s*AI\b/gi, "व्हर्ना लेजर ए आय");
    clean = clean.replace(/\bVernaLedger\b/gi, "व्हर्ना लेजर");
    clean = clean.replace(/\bAI\b/gi, "ए आय");
    clean = clean.replace(/\bGST\b/gi, "जी एस टी");
    clean = clean.replace(/\bUPI\b/gi, "यु पी आय");
    clean = clean.replace(/\bAGCE\b/gi, "ए जी सी ई");
    clean = clean.replace(/\bAGCOE\b/gi, "ए जी सी ओ ई");
    clean = clean.replace(/\bDBATU\b/gi, "डी बाटू");
    clean = clean.replace(/[₹]|(?:\b(?:Rs|रु)\.?\s*)/gi, "रुपये ");
    clean = clean.replace(/\bSanket\s+Kirdat\b/gi, "संकेत किर-दत");
    clean = clean.replace(/\bSanket\b/gi, "संकेत");
    clean = clean.replace(/\bSakshi\s+Bhagat\b/gi, "साक्षी भगत");
    clean = clean.replace(/\bVaishnavi\s+(?:Dhavale|Dhawale)\b/gi, "वैष्णवी ढव्-ळे");
    clean = clean.replace(/\bRushikesh\s+Mulik\b/gi, "ऋषिकेश मुळीक");
    clean = clean.replace(/\b(?:Prof\.?\s*|Mr\.?\s*)?Kaisar\s+(?:Atar|Attar)(?:\s+Sir)?\b/gi, "श्री कै-सर अतार");
    clean = clean.replace(/\b(?:Dr\.?\s*)?S\.?\s*Y\.?\s*Mulla\b/gi, "डॉक्टर एस. वाय. मुल्ला");
    clean = clean.replace(/\bHead\s+of\s+Department\b/gi, "विभागप्रमुख");
    clean = clean.replace(/\bHOD\b/gi, "विभागप्रमुख");
    clean = clean.replace(/\bArvind\s+Gavali(?:\s+College(?:\s+of\s+Engineering)?)?\b/gi, "अरविंद गव्-ळी कॉलेज");
    clean = clean.replace(/\bLead\s+Developer\b/gi, "प्रमुख विकासक");
    clean = clean.replace(/\bProject\s+Guide\b/gi, "प्रकल्प मार्गदर्शक");
    clean = clean.replace(/\bDevelopers\b/gi, "इतर विकासक");
    clean = clean.replace(/\bCollege\b/gi, "महाविद्यालय");

    const hints = {
        "वैष्णवी ढवळे": "वैष्णवी ढव्-ळे",
        "ढवाळे": "ढव्-ळे",
        "ढवळे": "ढव्-ळे",
        "अरविंद गवळी": "अरविंद गव्-ळी",
        "गवाली": "गव्-ळी",
        "गवळी": "गव्-ळी",
        "कैसर अतार": "कै-सर अतार",
        "कॅसर अतार": "कै-सर अतार",
        "कैसर अत्तार": "कै-सर अतार",
        "कॅसर अत्तार": "कै-सर अतार",
        "कैसर": "कै-सर",
        "कॅसर": "कै-सर",
        "अतार सर": "अतार सर",
        "किर्दत": "किर-दत",
        "किरदत": "किर-दत",
        "साक्षी भगत": "साक्षी भगत",
        "ऋषिकेश मुळीक": "ऋषिकेश मुळीक",
        "मुळीक": "मुळीक",
        "मुलिक": "मुळीक",
    };
    for (const [k, v] of Object.entries(hints)) {
        clean = clean.replaceAll(k, v);
    }
    clean = clean.replace(/\bGavali\b/gi, "गव्-ळी");
    return clean;
}

function autoCorrectMarathiSpeech(text) {
    if (!text) return "";
    let corrected = text;
    const corrections = [
        // Romanized Marathi & Speech Recognition Common Phonetic Fixes
        [/\b(?:mande|mandhe|madey|madye)\b/gi, "madhe"],
        [/\benglish mande\b/gi, "english madhe"],
        [/\bmarathi mande\b/gi, "marathi madhe"],
        [/\bchi\b/gi, "ची"],
        [/\bmahiti\b/gi, "माहिती"],
        [/\bmaithi\b/gi, "माहिती"],
        [/\bmaheeti\b/gi, "माहिती"],
        [/\bmaheti\b/gi, "माहिती"],
        [/\bsanga\b/gi, "सांगा"],
        [/\bsango\b/gi, "सांगा"],
        [/\bkiti\b/gi, "किती"],
        [/\bketee\b/gi, "किती"],
        [/\budhari\b/gi, "उधारी"],
        [/\budari\b/gi, "उधारी"],
        [/\bvikri\b/gi, "विक्री"],
        [/\bwikri\b/gi, "विक्री"],
        [/\bhishob\b/gi, "हिशोब"],
        [/\bhisob\b/gi, "हिशोब"],
        [/\bkharch\b/gi, "खर्च"],
        [/\bsatha\b/gi, "साठा"],
        [/\bkaise?r\s+atar\b/gi, "कैसर अतार"],
        [/\batar\s+sir\b/gi, "अतार सर"],
        [/\b(?:mr\.?\s*)?kaisar\s+atar\b/gi, "श्री कैसर अतार"],
        [/\b(hod|head of department|vibhang pramukh|mulla sir)\b/gi, "विभागप्रमुख डॉ. एस. वाय. मुल्ला"],
        [/\battar\b/gi, "अतार"],
        [/\bअत्तार\b/g, "अतार"],
        [/\bधवले\b/g, "ढवळे"],
        [/\bदवले\b/g, "ढवळे"],
        [/\bधवळे\b/g, "ढवळे"],
        [/\bढवले\b/g, "ढवळे"],
        [/\bdhavale\b/gi, "ढवळे"],
        [/\bdhawale\b/gi, "ढवळे"],
        [/\bमुलिक\b/g, "मुळीक"],
        [/\bमुलिक सर\b/g, "मुळीक सर"],
        [/\bmulik\b/gi, "मुळीक"],
        [/\bगावली\b/g, "गवळी"],
        [/\bगवली\b/g, "गवळी"],
        [/\bगावळी\b/g, "गवळी"],
        [/\bgavali\b/gi, "गवळी"],
        [/\bgawali\b/gi, "गवळी"],
        [/\bउढारी\b/g, "उधारी"],
        [/\bउधारीत\b/g, "उधारी"],
        [/\bविक्रि\b/g, "विक्री"],
        [/\bसाठ\b/g, "साठा"],
        [/\bस्टॉक\b/g, "साठा"],
        [/\bकैसर अत्तार\b/g, "कैसर अतार"],
        [/\bकेसर अतार\b/g, "कैसर अतार"],
        [/\bकेसर अत्तार\b/g, "कैसर अतार"],
        [/\bकौसर अतार\b/g, "कैसर अतार"],
        [/\bसंकेत किरदत\b/g, "संकेत किर्दत"],
        [/\bकिरदत\b/g, "किर्दत"],
        [/\bऋषिकेश मुलिक\b/g, "ऋषिकेश मुळीक"],
        [/\bवैष्णवी धवले\b/g, "वैष्णवी ढवळे"],
        [/\bसाक्षी\b/g, "साक्षी"]
    ];
    for (const [pattern, repl] of corrections) {
        corrected = corrected.replace(pattern, repl);
    }
    return corrected;
}

function speakWithBrowserVoice(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const phoneticText = prepareClientSpeech(text);
    const utterance = new SpeechSynthesisUtterance(phoneticText);
    utterance.lang = getLanguage().speech || "mr-IN";
    window.speechSynthesis.speak(utterance);
}

function getActiveSpeechLang() {
    if (state && state.lang === "hi") return "hi-IN";
    if (state && state.lang === "en") return "en-IN";
    return "mr-IN";
}

function initRagSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;
    try {
        if (!ragSpeechRecognition) {
            ragSpeechRecognition = new SpeechRecognition();
        }
        ragSpeechRecognition.continuous = false;
        ragSpeechRecognition.interimResults = true;
        ragSpeechRecognition.maxAlternatives = 1;
        ragSpeechRecognition.lang = getActiveSpeechLang();

        ragSpeechRecognition.onstart = () => {
            isRagListening = true;
            const micBtn = document.getElementById("btn-rag-mic");
            const statusEl = document.getElementById("rag-voice-status");
            if (micBtn) {
                micBtn.classList.add("listening");
                micBtn.innerHTML = "🔴";
                micBtn.title = "ऐकणे थांबवण्यासाठी क्लिक करा";
            }
            if (statusEl) {
                statusEl.style.display = "block";
                const lang = state ? state.lang : "mr";
                if (lang === "en") {
                    statusEl.innerHTML = `<span class="pulse-red">🔴</span> <strong>Listening... Speak now</strong> (e.g. 'Who created this project?', 'What is today's sale?')`;
                } else if (lang === "hi") {
                    statusEl.innerHTML = `<span class="pulse-red">🔴</span> <strong>सुन रहा हूँ... बोलिए</strong> (जैसे 'प्रोजेक्ट किसने बनाया?', 'आज की बिक्री कितनी है?')`;
                } else {
                    statusEl.innerHTML = `<span class="pulse-red">🔴</span> <strong>ऐकत आहे... स्पष्ट बोला</strong> (उदा. 'प्रकल्प कोणी बनवला?', 'आजची विक्री किती?')`;
                }
            }
        };

        ragSpeechRecognition.onresult = (event) => {
            let interimTranscript = "";
            let finalTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            const inputEl = document.getElementById("ai-user-input");
            const spokenText = (finalTranscript || interimTranscript).trim();
            if (inputEl && spokenText) {
                inputEl.value = (state && state.lang === "mr") ? autoCorrectMarathiSpeech(spokenText) : spokenText;
            }

            if (finalTranscript.trim()) {
                clearTimeout(ragAutoSubmitTimer);
                ragAutoSubmitTimer = setTimeout(() => {
                    stopRagVoice();
                    submitAiChat();
                }, 800);
            }
        };

        ragSpeechRecognition.onerror = (event) => {
            console.warn("RAG Speech Recognition notice:", event.error);
            stopRagVoice();
            if (event.error === "not-allowed" || event.error === "service-not-allowed") {
                if (typeof showToast === "function") {
                    showToast("कृपया ब्राऊझर मायक्रोफोन परवानगी (Microphone Permission) Allow करा.", "warning");
                }
            }
        };

        ragSpeechRecognition.onend = () => {
            const wasListening = isRagListening;
            stopRagVoice();
            const inputEl = document.getElementById("ai-user-input");
            if (wasListening && inputEl && inputEl.value.trim() && !isAiProcessing) {
                clearTimeout(ragAutoSubmitTimer);
                ragAutoSubmitTimer = setTimeout(() => {
                    submitAiChat();
                }, 300);
            }
        };

        return ragSpeechRecognition;
    } catch (e) {
        console.warn("RAG speech init notice:", e);
        return null;
    }
}

let ragSpeechRecognition = null;
let isRagListening = false;
let ragAutoSubmitTimer = null;
let ragMediaRecorder = null;
let ragAudioChunks = [];
let isRagRecording = false;
let ragRecordTimer = null;
let ragRecordSeconds = 0;

// High-speed Native Voice Interaction for Verna AI Studio
async function toggleRagVoice() {
    if (isAiProcessing) return;

    if (isRagListening) {
        stopRagVoice();
        const inputEl = document.getElementById("ai-user-input");
        if (inputEl && inputEl.value.trim()) {
            submitAiChat();
        }
        return;
    }

    if (isRagRecording) {
        stopRagNativeRecording();
        return;
    }

    // 1. Primary: Browser Native Web Speech API with Zero Latency & Live Display
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        try {
            initRagSpeech();
            if (ragSpeechRecognition) {
                ragSpeechRecognition.lang = getActiveSpeechLang();
                ragSpeechRecognition.start();
                return;
            }
        } catch (err) {
            console.warn("Speech recognition restart notice:", err);
            stopRagVoice();
            try {
                if (ragSpeechRecognition) {
                    ragSpeechRecognition.lang = getActiveSpeechLang();
                    ragSpeechRecognition.start();
                    return;
                }
            } catch (e) {}
        }
    }

    // 2. Secondary Fallback: MediaRecorder Audio capture (for Firefox / restricted WebSpeech)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        startRagMediaRecorderFallback();
        return;
    }

    alert("आपल्या ब्राऊझरमध्ये मायक्रोफोन उपलब्ध नाही. कृपया बॉक्समध्ये स्वतः टाईप करा.");
}

async function startRagMediaRecorderFallback() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
        });

        let mimeType = 'audio/webm;codecs=opus';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' :
                       MediaRecorder.isTypeSupported('audio/mp4') ? 'audio/mp4' :
                       MediaRecorder.isTypeSupported('audio/wav') ? 'audio/wav' : '';
        }

        ragMediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
        ragAudioChunks = [];
        isRagRecording = true;
        ragRecordSeconds = 0;

        const micBtn = document.getElementById("btn-rag-mic");
        const statusEl = document.getElementById("rag-voice-status");
        if (micBtn) {
            micBtn.classList.add("listening");
            micBtn.innerHTML = "⏹️";
            micBtn.title = "रेकॉर्डिंग थांबवण्यासाठी टॅप करा";
        }
        if (statusEl) {
            statusEl.style.display = "block";
            statusEl.innerHTML = `<span class="pulse-red">🔴</span> <strong>थेट आवाज रेकॉर्ड होत आहे...</strong> (स्पष्ट बोला, पूर्ण झाल्यावर ⏹️ दाबा)`;
        }

        ragRecordTimer = setInterval(() => {
            ragRecordSeconds++;
            if (statusEl && isRagRecording) {
                statusEl.innerHTML = `<span class="pulse-red">🔴</span> <strong>थेट आवाज रेकॉर्ड होत आहे (${ragRecordSeconds}s)...</strong> (थांबवण्यासाठी ⏹️ दाबा)`;
            }
            if (ragRecordSeconds >= 12) {
                stopRagNativeRecording();
            }
        }, 1000);

        ragMediaRecorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) ragAudioChunks.push(e.data);
        };

        ragMediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
            clearInterval(ragRecordTimer);
            if (micBtn) {
                micBtn.classList.remove("listening");
                micBtn.innerHTML = "🎙️";
                micBtn.title = "माईक द्वारे थेट बोला";
            }
            if (statusEl) statusEl.style.display = "none";
            if (ragAudioChunks.length === 0) return;

            const finalMime = ragMediaRecorder.mimeType || 'audio/webm';
            const audioBlob = new Blob(ragAudioChunks, { type: finalMime });
            if (audioBlob.size < 500) return;

            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = async () => {
                await submitNativeVoiceAi(reader.result, finalMime);
            };
        };

        ragMediaRecorder.start(250);
    } catch (err) {
        console.warn("Microphone access error:", err);
        stopRagVoice();
        alert("कृपया ब्राऊझर मायक्रोफोन परवानगी (Microphone Permission) Allow करा.");
    }
}

function stopRagNativeRecording() {
    if (ragMediaRecorder && ragMediaRecorder.state !== "inactive") {
        try { ragMediaRecorder.stop(); } catch (e) {}
    }
    isRagRecording = false;
    clearInterval(ragRecordTimer);
}

function stopRagVoice() {
    isRagListening = false;
    clearTimeout(ragAutoSubmitTimer);
    if (ragSpeechRecognition) {
        try { ragSpeechRecognition.stop(); } catch (e) {}
    }
    const micBtn = document.getElementById("btn-rag-mic");
    const statusEl = document.getElementById("rag-voice-status");
    if (micBtn) {
        micBtn.classList.remove("listening");
        micBtn.innerHTML = "🎙️";
        micBtn.title = "माईक द्वारे बोला";
    }
    if (statusEl) {
        statusEl.style.display = "none";
    }
}

function clearAiChat() {
    const historyContainer = document.getElementById("ai-chat-history");
    historyContainer.innerHTML = `
        <div class="chat-bubble chat-ai">
            संभाषण रीसेट झाले आहे. आपल्या किराणा दुकानाची विक्री, उधारी किंवा साठ्याबद्दल आपण मराठीत काहीही विचारू शकता किंवा माईक दाबून थेट उधारी/खर्च नोंदवू शकता.
        </div>
    `;
    state.chatHistory = [];
}

function askAiPrompt(text) {
    document.getElementById("ai-user-input").value = text;
    submitAiChat();
}

// Submit Native Spoken Voice Directly to Gemini Native Multimodal Model
async function submitNativeVoiceAi(base64Audio, mimeType) {
    if (isAiProcessing) return;
    isAiProcessing = true;
    stopCurrentAudio();

    const historyContainer = document.getElementById("ai-chat-history");
    const sendBtn = document.getElementById("btn-ai-send");
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = `<span>...</span> ⏳`;
    }

    // Add User Bubble with Audio Icon
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble chat-user";
    userBubble.innerHTML = `
        <div style="font-weight:700; font-size:0.75rem; color:var(--neon-cyan); margin-bottom:2px;">👤 आपण (व्हॉइस इनपुट)</div>
        <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:1.1rem;">🎙️</span>
            <span>व्हॉइस रेकॉर्डिंग पाठवत आहे...</span>
        </div>
    `;
    historyContainer.appendChild(userBubble);
    historyContainer.scrollTo({ top: historyContainer.scrollHeight, behavior: 'smooth' });

    // Add AI Typing Indicator
    const aiBubble = document.createElement("div");
    aiBubble.className = "chat-bubble chat-ai";
    aiBubble.innerHTML = `<span style="animation: pulseDot 1s infinite;">🧠 जेमिनी मल्टिमोडल AI आवाज ऐकत आहे...</span>`;
    historyContainer.appendChild(aiBubble);
    historyContainer.scrollTo({ top: historyContainer.scrollHeight, behavior: 'smooth' });

    try {
        const res = await apiCall("/api/rag-chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: "",
                audio_data: base64Audio,
                mime_type: mimeType,
                lang: state.lang,
                chat_history: state.chatHistory.slice(-10)
            })
        });

        const data = await res.json();

        // Update user bubble with Gemini's exact native transcription
        const spokenWords = data.user_transcript || "व्हॉइस ऑडिओ मेसेज";
        userBubble.innerHTML = `
            <div style="font-weight:700; font-size:0.75rem; color:var(--neon-cyan); margin-bottom:2px;">👤 आपण (व्हॉइस इनपुट)</div>
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="font-size:1.1rem;">🎙️</span>
                <span>"${escapeHtml(spokenWords)}"</span>
            </div>
        `;
        state.chatHistory.push({ role: "user", parts: [{ text: spokenWords }] });
        state.chatHistory.push({ role: "model", parts: [{ text: data.answer || "" }] });

        renderAiResponseBubble(aiBubble, data);
    } catch (err) {
        aiBubble.innerHTML = `एरर: जेमिनी मल्टिमोडल व्हॉइस प्रोसेस होऊ शकला नाही. कृपया पुन्हा प्रयत्न करा.`;
    } finally {
        isAiProcessing = false;
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.innerHTML = `<span>पाठवा</span> 🚀`;
        }
        historyContainer.scrollTo({ top: historyContainer.scrollHeight, behavior: 'smooth' });
    }
}

// Submit Text Chat Message
async function submitAiChat() {
    if (isAiProcessing) return;

    const input = document.getElementById("ai-user-input");
    const msg = input.value.trim();
    if (!msg) return;

    stopCurrentAudio();
    isAiProcessing = true;
    input.value = "";
    const sendBtn = document.getElementById("btn-ai-send");
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = `<span>...</span> ⏳`;
    }
    const historyContainer = document.getElementById("ai-chat-history");

    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble chat-user";
    userBubble.innerHTML = `<div style="font-weight:700; font-size:0.75rem; color:var(--neon-cyan); margin-bottom:2px;">👤 आपण (You)</div>` + escapeHtml(msg);
    historyContainer.appendChild(userBubble);
    historyContainer.scrollTo({ top: historyContainer.scrollHeight, behavior: 'smooth' });

    const aiBubble = document.createElement("div");
    aiBubble.className = "chat-bubble chat-ai";
    aiBubble.innerHTML = `<span style="animation: pulseDot 1s infinite;">🧠 विचार करत आहे...</span>`;
    historyContainer.appendChild(aiBubble);
    historyContainer.scrollTo({ top: historyContainer.scrollHeight, behavior: 'smooth' });

    try {
        const res = await apiCall("/api/rag-chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: msg,
                lang: state.lang,
                chat_history: state.chatHistory.slice(-10)
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "AI सर्व्हरशी संपर्क होऊ शकला नाही.");

        state.chatHistory.push({ role: "user", parts: [{ text: msg }] });
        state.chatHistory.push({ role: "model", parts: [{ text: data.answer || "" }] });

        renderAiResponseBubble(aiBubble, data);
    } catch (e) {
        console.error("AI CHAT ERROR CAUGHT:", e);
        aiBubble.innerHTML = `एरर: ${e.message || "सर्व्हरशी संपर्क होऊ शकला नाही."}`;
    } finally {
        isAiProcessing = false;
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.innerHTML = `<span>पाठवा</span> 🚀`;
        }
        historyContainer.scrollTo({ top: historyContainer.scrollHeight, behavior: 'smooth' });
    }
}

// Next-Level Markdown & Table Parser for Verna AI Chatbot
function formatAiMarkdown(text) {
    if (!text) return "";

    // 1. Extract and preserve code blocks
    const codeBlocks = [];
    let processed = text.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const id = `__CODE_BLOCK_${codeBlocks.length}__`;
        codeBlocks.push(`<pre class="ai-code-block"><code>${escapeHtml(code.trim())}</code></pre>`);
        return id;
    });

    // 2. Parse Markdown Tables (| Col 1 | Col 2 | ...)
    const tableRegex = /((?:^[ \t]*\|[^\n]+\|[ \t]*(?:\n|$))+)/gm;
    processed = processed.replace(tableRegex, (tableBlock) => {
        const lines = tableBlock.trim().split('\n').map(l => l.trim()).filter(l => l.startsWith('|') && l.endsWith('|'));
        if (lines.length < 2) return tableBlock;

        const parseRow = (line) => line.slice(1, -1).split('|').map(c => c.trim());
        const headerCells = parseRow(lines[0]);
        const separatorLine = lines[1];

        // Ensure row 2 is a valid table separator (e.g. | :--- | :---: | ---: |)
        const sepCells = parseRow(separatorLine);
        const isValidSep = sepCells.length > 0 && sepCells.every(c => /^:?-+:?$/.test(c));
        if (!isValidSep) return tableBlock;

        const aligns = sepCells.map(s => {
            if (s.startsWith(':') && s.endsWith(':')) return 'center';
            if (s.endsWith(':')) return 'right';
            return 'left';
        });

        let html = '<div class="ai-table-wrapper"><table class="ai-chat-table"><thead><tr>';
        headerCells.forEach((h, idx) => {
            const align = aligns[idx] || 'left';
            html += `<th style="text-align: ${align};">${formatInlineAi(h)}</th>`;
        });
        html += '</tr></thead><tbody>';

        for (let i = 2; i < lines.length; i++) {
            const rowCells = parseRow(lines[i]);
            html += '<tr>';
            rowCells.forEach((c, idx) => {
                const align = aligns[idx] || 'left';
                html += `<td style="text-align: ${align};">${formatInlineAi(c)}</td>`;
            });
            html += '</tr>';
        }

        html += '</tbody></table></div>';
        return html;
    });

    // 3. Process lines (Headers, Lists, Blockquotes, Paragraphs)
    const lines = processed.split('\n');
    let inUl = false;
    let inOl = false;
    const output = [];

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];

        // If line is already part of the table HTML, output directly
        if (line.includes('<div class="ai-table-wrapper">') || line.includes('</table></div>')) {
            if (inUl) { output.push('</ul>'); inUl = false; }
            if (inOl) { output.push('</ol>'); inOl = false; }
            output.push(line);
            continue;
        }

        // Markdown Headers
        if (line.startsWith('### ')) {
            if (inUl) { output.push('</ul>'); inUl = false; }
            if (inOl) { output.push('</ol>'); inOl = false; }
            output.push(`<h3>${formatInlineAi(line.slice(4))}</h3>`);
            continue;
        }
        if (line.startsWith('## ')) {
            if (inUl) { output.push('</ul>'); inUl = false; }
            if (inOl) { output.push('</ol>'); inOl = false; }
            output.push(`<h2>${formatInlineAi(line.slice(3))}</h2>`);
            continue;
        }
        if (line.startsWith('# ')) {
            if (inUl) { output.push('</ul>'); inUl = false; }
            if (inOl) { output.push('</ol>'); inOl = false; }
            output.push(`<h1>${formatInlineAi(line.slice(2))}</h1>`);
            continue;
        }

        // Unordered lists (*, -, •)
        const ulMatch = line.match(/^[ \t]*[-*•][ \t]+(.*)/);
        if (ulMatch) {
            if (inOl) { output.push('</ol>'); inOl = false; }
            if (!inUl) { output.push('<ul>'); inUl = true; }
            output.push(`<li>${formatInlineAi(ulMatch[1])}</li>`);
            continue;
        }

        // Numbered lists (1. or १. or 1) )
        const olMatch = line.match(/^[ \t]*([0-9]+|[०-९]+)[\.\)][ \t]+(.*)/);
        if (olMatch) {
            if (inUl) { output.push('</ul>'); inUl = false; }
            if (!inOl) { output.push('<ol>'); inOl = true; }
            output.push(`<li>${formatInlineAi(olMatch[2])}</li>`);
            continue;
        }

        // Close lists if this is not a list item
        if (inUl) { output.push('</ul>'); inUl = false; }
        if (inOl) { output.push('</ol>'); inOl = false; }

        // Blockquotes (> )
        if (line.startsWith('> ')) {
            output.push(`<blockquote class="ai-blockquote">${formatInlineAi(line.slice(2))}</blockquote>`);
            continue;
        }

        // Blank lines
        if (!line.trim()) {
            output.push('<div class="ai-line-gap"></div>');
            continue;
        }

        // Normal paragraph text
        output.push(`<div>${formatInlineAi(line)}</div>`);
    }

    if (inUl) output.push('</ul>');
    if (inOl) output.push('</ol>');

    let finalHtml = output.join('');

    // Restore preserved code blocks
    codeBlocks.forEach((block, idx) => {
        finalHtml = finalHtml.replace(`__CODE_BLOCK_${idx}__`, block);
    });

    return finalHtml;
}

function formatInlineAi(text) {
    if (!text) return "";
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/~~(.*?)~~/g, '<del>$1</del>');
}

// Safe URI component encoder that never throws URIError on malformed surrogate pairs
function safeEncodeURIComponent(str) {
    if (!str) return "";
    try {
        const clean = (typeof str === "string" && typeof str.toWellFormed === "function") 
            ? str.toWellFormed() 
            : String(str);
        return encodeURIComponent(clean);
    } catch (e) {
        try {
            const sanitized = String(str).replace(/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/g, '');
            return encodeURIComponent(sanitized);
        } catch (e2) {
            return encodeURIComponent(String(str).replace(/[^\x00-\x7F]/g, ''));
        }
    }
}

// Natural table-to-speech script converter with dynamic table type awareness
function convertMarkdownToSpeechScript(md) {
    if (!md) return "";
    const lines = md.split('\n');
    const speechLines = [];
    let inTable = false;
    let headers = [];
    let tableType = "general";

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        if (line.startsWith('|') && line.endsWith('|')) {
            const cells = line.slice(1, -1).split('|').map(c => c.trim());
            if (cells.every(c => /^:?-+:?$/.test(c))) {
                inTable = true;
                continue;
            }
            if (!inTable) {
                headers = cells.map(c => c.replace(/[*#_`\(\)]/g, '').trim());
                const hStr = headers.join(' ').toLowerCase();
                if (/विद्यार्थ्या|नाव|रोल|भूमिका|role|team|prn/.test(hStr)) {
                    tableType = "team";
                } else if (/vernaledger|वैशिष्ट्ये|फिचर्स|feature|vs/.test(hStr)) {
                    tableType = "comparison";
                } else if (/साठा|वस्तू|स्टॉक|stock|item/.test(hStr)) {
                    tableType = "stock";
                } else if (/घटक|metric|नफा|रक्कम|financial/.test(hStr)) {
                    tableType = "financial";
                } else {
                    tableType = "general";
                }
                inTable = true;
            } else {
                // Strip emojis safely using Unicode property escapes
                const cleanCells = cells.map(c => c.replace(/[\p{Extended_Pictographic}\u200D\uFE0F\uFE0E*#_`•]/gu, '').trim());
                if (tableType === "team" && cleanCells.length >= 5) {
                    speechLines.push(`${cleanCells[1]}, रोल नंबर ${cleanCells[2]}, भूमिका: ${cleanCells[4]}.`);
                } else if (tableType === "comparison" && cleanCells.length >= 3) {
                    speechLines.push(`${cleanCells[0]}: VernaLedger मध्ये ${cleanCells[1]}, तर इतर ॲप्स मध्ये ${cleanCells[2]}.`);
                } else if (tableType === "stock" && cleanCells.length >= 4) {
                    speechLines.push(`${cleanCells[1]}: शिल्लक साठा ${cleanCells[2]}, दर ${cleanCells[3]}.`);
                } else if (tableType === "financial" && cleanCells.length >= 3) {
                    speechLines.push(`${cleanCells[0]}: ${cleanCells[1]}, ${cleanCells[2]}.`);
                } else if (cleanCells.length === 2) {
                    speechLines.push(`${cleanCells[0]}: ${cleanCells[1]}.`);
                } else {
                    speechLines.push(cleanCells.filter(Boolean).join(', ') + '.');
                }
            }
            continue;
        }

        inTable = false;
        let clean = line
            .replace(/^#+\s*/, '')
            .replace(/^[-*•]\s*/, '')
            .replace(/^[0-9]+[\.\)]\s*/, '')
            .replace(/[\p{Extended_Pictographic}\u200D\uFE0F\uFE0E*#_`•]/gu, '')
            .replace(/[\(\[\{]/g, ', ')
            .replace(/[\)\]\}]/g, ', ')
            .trim();

        if (clean) speechLines.push(clean);
    }

    return speechLines.join(' ').replace(/\s+/g, ' ').trim();
}

// Next-Level Verna AI Rich Response Bubble
function renderAiResponseBubble(aiBubble, data) {
    const rawAnswer = data.answer || "माफ करा, उत्तर मिळू शकले नाही.";
    const formattedHtml = formatAiMarkdown(rawAnswer);

    aiBubble.innerHTML = `
        <div class="ai-bubble-content">${formattedHtml}</div>
        ${data.action_status ? `<div style="margin-top: 8px; font-size: 0.78rem; color: var(--neon-green); font-weight: 700; background: rgba(0,255,102,0.08); padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(0,255,102,0.25);">⚡ ${data.action_status}</div>` : ''}
        <div class="ai-bubble-footer">
            <span style="font-size: 0.72rem; color: var(--text-dim); display: flex; align-items: center; gap: 4px;">
                <span>✨</span> <span>Verna AI Enterprise Pro</span>
            </span>
            <div style="display: flex; gap: 6px;">
                <button class="ai-action-btn-sm" onclick="copyAiBubbleText(this)" data-raw="${safeEncodeURIComponent(rawAnswer)}" title="उत्तर कॉपी करा">
                    📋 <span>कॉपी</span>
                </button>
            </div>
        </div>
    `;
}

async function speakAiBubbleText(btn) {
    stopCurrentAudio();
}

function speakWithBrowserVoiceClean(text, onEnd) {
    if (!window.speechSynthesis) {
        if (onEnd) onEnd();
        return;
    }
    window.speechSynthesis.cancel();

    const cleanText = text
        .replace(/[*#_`❌✅⚠️🎯📸🎙️⚡🤖💳🖨️🔒•]/g, '')
        .replace(/[₹]/g, ' रुपये ')
        .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);

    // Detect language: English, Hindi, or Marathi
    const devanagariCount = (cleanText.match(/[\u0900-\u097f]/g) || []).length;
    const latinCount = (cleanText.match(/[A-Za-z]/g) || []).length;

    let targetLang = "mr-IN";
    if (latinCount > devanagariCount * 1.2) {
        targetLang = "en-IN";
    } else if (/नमस्ते|हैं|किया|दुकानदार|रुपये|चाहिए|होगा|हूँ/.test(cleanText)) {
        targetLang = "hi-IN";
    }

    utterance.lang = targetLang;
    utterance.rate = 1.0;

    const voices = window.speechSynthesis.getVoices() || [];
    const matchedVoice = voices.find(v => v.lang === targetLang) ||
                         voices.find(v => v.lang.startsWith(targetLang.slice(0, 2))) ||
                         voices.find(v => v.lang.includes("IN") || v.lang.includes("hi") || v.lang.includes("mr"));
    if (matchedVoice) {
        utterance.voice = matchedVoice;
    }

    utterance.onend = () => { if (onEnd) onEnd(); };
    utterance.onerror = () => { if (onEnd) onEnd(); };

    window.speechSynthesis.speak(utterance);
}

function copyAiBubbleText(btn) {
    const rawEncoded = btn.getAttribute("data-raw");
    if (!rawEncoded) return;
    const text = decodeURIComponent(rawEncoded);
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            const span = btn.querySelector("span");
            if (span) {
                const original = span.innerText;
                span.innerText = "कॉपी झाले! ✅";
                setTimeout(() => { span.innerText = original; }, 2000);
            }
        }).catch(() => {
            alert("मजकूर कॉपी करण्यात अडचण आली.");
        });
    } else {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
        const span = btn.querySelector("span");
        if (span) {
            const original = span.innerText;
            span.innerText = "कॉपी झाले! ✅";
            setTimeout(() => { span.innerText = original; }, 2000);
        }
    }
}

async function speakText(encoded) {
    stopCurrentAudio();
    const token = currentAudioPlayToken;
    const raw = decodeURIComponent(encoded);
    const voice = getLanguage().tts;

    try {
        const res = await apiCall("/api/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text: raw,
                voice: voice
            })
        });
        if (token !== currentAudioPlayToken) return; // Stale request cancelled by newer click!
        const data = await res.json();
        if (token !== currentAudioPlayToken) return; // Stale request cancelled!

        if (data.audio_data) {
            stopCurrentAudio();
            const playToken = ++currentAudioPlayToken;
            currentPlayingAudio = new Audio(data.audio_data);
            currentPlayingAudio.onended = () => {
                if (currentAudioPlayToken === playToken) currentPlayingAudio = null;
            };
            await currentPlayingAudio.play();
        } else {
            speakWithBrowserVoice(raw);
        }
    } catch (e) {
        if (token === currentAudioPlayToken) {
            speakWithBrowserVoice(raw);
        }
    }
}

// -----------------------------------------------------------------------------
// MODALS & HELPERS
// -----------------------------------------------------------------------------
function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("active");
}

function setLanguage(languageCode) {
    if (!supportedLanguages.some(language => language.code === languageCode)) return;
    state.lang = languageCode;
    localStorage.setItem("verna_lang", state.lang);
    if (state.speechRecognition) state.speechRecognition.lang = getLanguage().speech;
    if (ragSpeechRecognition) ragSpeechRecognition.lang = getLanguage().speech;
    applyLanguage();
}

function toggleLanguage() {
    const currentIndex = supportedLanguages.findIndex(language => language.code === state.lang);
    setLanguage(supportedLanguages[(currentIndex + 1) % supportedLanguages.length].code);
}

function applyLanguage() {
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
    
    // In-place live translation of Digital Receipt Preview inputs
    const vendorInput = document.getElementById("bill-vendor-name");
    if (vendorInput && vendorInput.value) {
        vendorInput.value = formatLocalizedName(vendorInput.value, state.lang);
    }
    document.querySelectorAll("#bill-items-tbody tr").forEach(row => {
        const nameInput = row.querySelector(".item-name");
        if (nameInput && nameInput.value) {
            nameInput.value = formatLocalizedName(nameInput.value, state.lang);
        }
    });
}

function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// Handle browser back/forward and hash changes
window.addEventListener("hashchange", () => {
    const hash = window.location.hash.replace("#", "").trim();
    if (hash && state.user) {
        switchView(hash);
    }
});

function renderBillItems() {
    if (!state.currentBill) return;
    populateBillCard(state.currentBill);
}


// -----------------------------------------------------------------------------
// KHATABOOK-BEATING ENHANCEMENTS: THEME, QUICK ACTIONS & WHATSAPP SHARING
// -----------------------------------------------------------------------------

function initTheme() {
    const saved = localStorage.getItem("verna_theme") || "dark";
    applyTheme(saved);
}

function toggleTheme() {
    const isLight = document.body.classList.contains("light-theme");
    const next = isLight ? "dark" : "light";
    applyTheme(next);
    localStorage.setItem("verna_theme", next);
}

function applyTheme(theme) {
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
}

state.khataFilter = "all";

function setKhataFilter(filterType) {
    state.khataFilter = filterType;
    document.querySelectorAll(".khata-filter-pill").forEach(p => p.classList.remove("active"));
    const activeBtn = document.getElementById(`filter-pill-${filterType}`);
    if (activeBtn) activeBtn.classList.add("active");
    if (state.allKhata && state.allKhata.customers) {
        renderKhataCards(state.allKhata.customers);
    }
}

function quickKhataAction(name, phone, type) {
    document.getElementById("khata-input-name").value = name;
    document.getElementById("khata-input-phone").value = phone;
    document.getElementById("khata-input-type").value = type;
    document.getElementById("khata-input-amount").value = "";
    openAddKhataModal();
    setTimeout(() => {
        const amtInput = document.getElementById("khata-input-amount");
        if (amtInput) amtInput.focus();
    }, 150);
}

function openWhatsAppBillModal() {
    const modal = document.getElementById("modal-whatsapp-share");
    if (modal) modal.classList.add("active");
}

function confirmSendWhatsAppBill() {
    const phoneInput = document.getElementById("wa-share-phone");
    const phone = (phoneInput.value || "").replace(/\D/g, "");
    if (!phone || phone.length < 10) {
        alert("कृपया वैध १० अंकी मोबाईल नंबर टाका!");
        return;
    }
    const vendor = document.getElementById("bill-vendor-name")?.value || "किराणा स्टोअर";
    const total = document.getElementById("bill-grand-total")?.innerText || "₹0";
    const rows = document.querySelectorAll("#bill-items-tbody tr");
    let itemsList = "";
    rows.forEach(r => {
        const name = r.querySelector(".item-name")?.value || "";
        const qty = r.querySelector(".item-qty")?.value || "";
        const tot = r.querySelector(".item-total")?.innerText || "";
        if (name) {
            itemsList += `• ${name} (${qty}) - ₹${tot}\n`;
        }
    });

    const msg = encodeURIComponent(
        `🧾 *डिजिटल पावती - ${vendor}*\n` +
        `━━━━━━━━━━━━━━━━━━━━\n` +
        `${itemsList}` +
        `━━━━━━━━━━━━━━━━━━━━\n` +
        `💰 *एकूण रक्कम: ${total}*\n\n` +
        `🙏 खरेदी केल्याबद्दल धन्यवाद!\n` +
        `_VernaLedger.AI द्वारे पाठवले_`
    );

    closeModal("modal-whatsapp-share");
    window.open(`https://wa.me/91${phone}?text=${msg}`, "_blank");
}


// -----------------------------------------------------------------------------
// MINIMALIST TOUCH-DRAGGABLE VOICE PLAYER ENGINE (1 BUTTON + DRAGGABLE SLIDER)
// -----------------------------------------------------------------------------
const isVoiceSliderDragging = {};

function formatAudioTime(seconds) {
    if (isNaN(seconds) || seconds < 0 || !isFinite(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function togglePlayAudio(msgId) {
    const audio = document.getElementById(`audio-${msgId}`);
    const btn = document.getElementById(`btn-play-${msgId}`);
    if (!audio) return;

    if (audio.paused) {
        // Pause any other playing audio on the page
        document.querySelectorAll("audio").forEach(a => {
            if (a !== audio && !a.paused) {
                a.pause();
                const otherId = a.id.replace("audio-", "");
                const otherBtn = document.getElementById(`btn-play-${otherId}`);
                if (otherBtn) {
                    otherBtn.innerHTML = "▶";
                    otherBtn.classList.remove("playing");
                }
            }
        });
        audio.play().catch(e => console.warn("Audio play prevented:", e));
        if (btn) {
            btn.innerHTML = "⏸";
            btn.classList.add("playing");
        }
    } else {
        audio.pause();
        if (btn) {
            btn.innerHTML = "▶";
            btn.classList.remove("playing");
        }
    }
}

function onVoiceSliderInput(msgId) {
    isVoiceSliderDragging[msgId] = true;
    const audio = document.getElementById(`audio-${msgId}`);
    const slider = document.getElementById(`seek-${msgId}`);
    const time = document.getElementById(`time-${msgId}`);
    if (audio && audio.duration && slider) {
        const seekTo = (parseFloat(slider.value) / 100) * audio.duration;
        if (time) time.innerText = `${formatAudioTime(seekTo)} / ${formatAudioTime(audio.duration)}`;
    }
}

function onVoiceSliderChange(msgId) {
    const audio = document.getElementById(`audio-${msgId}`);
    const slider = document.getElementById(`seek-${msgId}`);
    if (audio && audio.duration && slider) {
        audio.currentTime = (parseFloat(slider.value) / 100) * audio.duration;
    }
    setTimeout(() => {
        isVoiceSliderDragging[msgId] = false;
    }, 120);
}

function attachVoicePlayerListeners(msgId) {
    const audio = document.getElementById(`audio-${msgId}`);
    const btn = document.getElementById(`btn-play-${msgId}`);
    const slider = document.getElementById(`seek-${msgId}`);
    const time = document.getElementById(`time-${msgId}`);
    if (!audio) return;

    const updateDisplayTime = (cur, dur) => {
        if (!time) return;
        time.innerText = `${formatAudioTime(cur)} / ${formatAudioTime(dur)}`;
    };

    audio.addEventListener("loadedmetadata", () => {
        updateDisplayTime(0, audio.duration);
    });

    audio.addEventListener("timeupdate", () => {
        if (audio.duration && !isVoiceSliderDragging[msgId]) {
            const pct = (audio.currentTime / audio.duration) * 100;
            if (slider) slider.value = pct;
            updateDisplayTime(audio.currentTime, audio.duration);
        }
    });

    audio.addEventListener("ended", () => {
        if (btn) {
            btn.innerHTML = "▶";
            btn.classList.remove("playing");
        }
        if (slider) slider.value = 0;
        updateDisplayTime(0, audio.duration);
        isVoiceSliderDragging[msgId] = false;
    });

    if (slider) {
        slider.addEventListener("pointerdown", () => { isVoiceSliderDragging[msgId] = true; });
        slider.addEventListener("pointerup", () => {
            setTimeout(() => { isVoiceSliderDragging[msgId] = false; }, 120);
        });
        slider.addEventListener("touchstart", () => { isVoiceSliderDragging[msgId] = true; }, { passive: true });
        slider.addEventListener("touchend", () => {
            setTimeout(() => { isVoiceSliderDragging[msgId] = false; }, 120);
        }, { passive: true });
    }
}

// Backward-compatibility aliases
function attachMpcAudioListeners(msgId) { attachVoicePlayerListeners(msgId); }
function seekAudio(msgId, delta) {
    const audio = document.getElementById(`audio-${msgId}`);
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(audio.duration || 0, audio.currentTime + delta));
}
function stopAudioMsg(msgId) {
    const audio = document.getElementById(`audio-${msgId}`);
    const btn = document.getElementById(`btn-play-${msgId}`);
    const slider = document.getElementById(`seek-${msgId}`);
    const time = document.getElementById(`time-${msgId}`);
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
    if (btn) {
        btn.innerHTML = "▶";
        btn.classList.remove("playing");
    }
    if (slider) slider.value = 0;
    if (time) time.innerText = `0:00 / ${formatAudioTime(audio.duration)}`;
}
function seekAudioBar(event, msgId) { /* legacy */ }


// -----------------------------------------------------------------------------
// AUTH ENHANCEMENTS: FORGOT PASSWORD & REGISTER NEW MERCHANT
// -----------------------------------------------------------------------------
function openForgotPasswordModal() {
    const modal = document.getElementById("modal-forgot-password");
    if (modal) modal.classList.add("active");
}

async function handleForgotPassword(e) {
    e.preventDefault();
    const userVal = document.getElementById("forgot-username").value.trim();
    const newPass = document.getElementById("forgot-new-password").value.trim();
    if (!userVal || !newPass) {
        alert("कृपया वापरकर्ता नाव आणि नवीन पासवर्ड टाका.");
        return;
    }

    try {
        const payload = {
            username: userVal.includes("@") || isNaN(userVal) ? userVal : "",
            phone: !isNaN(userVal) ? userVal : "",
            new_password: newPass
        };
        const res = await apiCall("/api/auth/forgot-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(data.detail || data.message || "पासवर्ड रीसेट करता आला नाही.");
        }
        alert("✅ पासवर्ड यशस्वीरीत्या बदलला आहे! आता लॉगिन करा.");
        closeModal("modal-forgot-password");
        const loginUserInput = document.getElementById("login-username");
        const loginPassInput = document.getElementById("login-password");
        if (loginUserInput) loginUserInput.value = data.username || userVal;
        if (loginPassInput) loginPassInput.value = newPass;
    } catch (err) {
        alert("त्रुटी: " + err.message);
    }
}

function openRegisterModal() {
    const modal = document.getElementById("modal-register");
    if (modal) modal.classList.add("active");
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById("reg-username").value.trim();
    const password = document.getElementById("reg-password").value.trim();
    const shop_name = document.getElementById("reg-shop-name").value.trim();
    const phone = document.getElementById("reg-phone").value.trim();

    if (!username || !password || !shop_name) {
        alert("कृपया सर्व आवश्यक माहिती भरा.");
        return;
    }

    try {
        const payload = { username, password, shop_name, phone, role: "Admin" };
        const res = await apiCall("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(data.detail || "नोंदणी अयशस्वी झाली.");
        }

        // Save session
        state.user = {
            username: data.username,
            role: data.role,
            phone: data.phone,
            shop_name: data.shop_name
        };
        localStorage.setItem("verna_user", JSON.stringify(state.user));

        closeModal("modal-register");
        alert(`✅ स्वागत आहे, ${shop_name}! आपले खाते यशस्वीरित्या तयार झाले आहे.`);
        showApp();
        loadShopSettings();
    } catch (err) {
        alert("नोंदणी त्रुटी: " + err.message);
    }
}

// -----------------------------------------------------------------------------
// SHOP PROFILE & BILLING SETTINGS MANAGEMENT
// -----------------------------------------------------------------------------
state.shopSettings = (function() {
    try {
        const cached = localStorage.getItem("verna_shop_settings");
        if (cached) {
            const parsed = JSON.parse(cached);
            if (parsed && parsed.shop_name) return parsed;
        }
    } catch (_) {}
    return {
        shop_name: "SK Store",
        owner_name: "संकेत किर्दत",
        phone: "9876543210",
        upi_id: "merchant@upi",
        address: "सातारा, महाराष्ट्र"
    };
})();

async function loadShopSettings() {
    // 1. Immediately apply cached local settings to eliminate UI latency or flickering
    let local = null;
    try {
        const cached = localStorage.getItem("verna_shop_settings");
        if (cached) local = JSON.parse(cached);
    } catch (_) {}
    if (local && local.shop_name) {
        state.shopSettings = Object.assign({}, state.shopSettings, local);
        applyShopSettingsToUI();
    }

    // 2. Query server for settings
    try {
        const res = await apiCall("/api/shop/settings");
        if (res.ok) {
            const data = await res.json();
            if (data && data.shop_name) {
                // If user has a local custom name, do NOT let a server default overwrite it!
                if (local && local.shop_name && local.shop_name !== data.shop_name && (data.shop_name === "महादेव किराणा स्टोअर" || data.shop_name === "SK Store")) {
                    // Sync user's custom name back to server
                    apiCall("/api/shop/settings", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(local)
                    }).catch(() => {});
                } else {
                    state.shopSettings = Object.assign({}, state.shopSettings, data);
                    localStorage.setItem("verna_shop_settings", JSON.stringify(state.shopSettings));
                }
            }
        }
    } catch (e) {
        console.warn("Using cached shop settings:", e);
    }
    applyShopSettingsToUI();
}

function applyShopSettingsToUI() {
    let s = state.shopSettings;
    if (!s || !s.shop_name) {
        try {
            const cached = localStorage.getItem("verna_shop_settings");
            if (cached) s = JSON.parse(cached);
        } catch (_) {}
    }
    if (!s) s = { shop_name: "SK Store", owner_name: "संकेत किर्दत", phone: "9876543210", upi_id: "merchant@upi", address: "सातारा, महाराष्ट्र" };
    state.shopSettings = s;

    // Sidebar Shop Name
    const sNameEl = document.getElementById("sidebar-shop-name");
    if (sNameEl) sNameEl.innerText = s.shop_name || "SK Store";

    // Operation view inputs
    const elShopName = document.getElementById("setting-shop-name");
    const elOwnerName = document.getElementById("setting-owner-name");
    const elPhone = document.getElementById("setting-phone");
    const elUpi = document.getElementById("setting-upi");
    const elAddr = document.getElementById("setting-address");

    if (elShopName) elShopName.value = s.shop_name || "";
    if (elOwnerName) elOwnerName.value = s.owner_name || "";
    if (elPhone) elPhone.value = s.phone || "";
    if (elUpi) elUpi.value = s.upi_id || "";
    if (elAddr) elAddr.value = s.address || "";

    // Default vendor name in Digital Receipt Preview if empty or default placeholder
    const billVendor = document.getElementById("bill-vendor-name");
    if (billVendor && (!billVendor.value || billVendor.value === "किराणा स्टोअर" || billVendor.value === "Kirana Store" || billVendor.value === "महादेव किराणा स्टोअर")) {
        billVendor.value = s.shop_name || "SK Store";
    }
}

function openShopSettingsModal() {
    const s = state.shopSettings || {};
    const mShop = document.getElementById("modal-shop-name");
    const mOwner = document.getElementById("modal-owner-name");
    const mPhone = document.getElementById("modal-phone");
    const mUpi = document.getElementById("modal-upi");
    const mAddr = document.getElementById("modal-address");

    if (mShop) mShop.value = s.shop_name || "";
    if (mOwner) mOwner.value = s.owner_name || "";
    if (mPhone) mPhone.value = s.phone || "";
    if (mUpi) mUpi.value = s.upi_id || "";
    if (mAddr) mAddr.value = s.address || "";

    const modal = document.getElementById("modal-shop-settings");
    if (modal) modal.classList.add("active");
}

async function saveShopSettingsFromOperations() {
    const enteredName = (document.getElementById("setting-shop-name") ? document.getElementById("setting-shop-name").value : "").trim();
    const payload = {
        shop_name: enteredName || (state.shopSettings && state.shopSettings.shop_name) || "SK Store",
        owner_name: (document.getElementById("setting-owner-name") ? document.getElementById("setting-owner-name").value : "").trim() || (state.shopSettings && state.shopSettings.owner_name) || "संकेत किर्दत",
        phone: (document.getElementById("setting-phone") ? document.getElementById("setting-phone").value : "").trim() || (state.shopSettings && state.shopSettings.phone) || "9876543210",
        upi_id: (document.getElementById("setting-upi") ? document.getElementById("setting-upi").value : "").trim() || (state.shopSettings && state.shopSettings.upi_id) || "merchant@upi",
        address: (document.getElementById("setting-address") ? document.getElementById("setting-address").value : "").trim() || (state.shopSettings && state.shopSettings.address) || "सातारा, महाराष्ट्र"
    };

    await persistShopSettings(payload);
}

async function handleSaveShopSettingsModal(e) {
    if (e) e.preventDefault();
    const enteredName = (document.getElementById("modal-shop-name") ? document.getElementById("modal-shop-name").value : "").trim();
    const payload = {
        shop_name: enteredName || (state.shopSettings && state.shopSettings.shop_name) || "SK Store",
        owner_name: (document.getElementById("modal-owner-name") ? document.getElementById("modal-owner-name").value : "").trim() || (state.shopSettings && state.shopSettings.owner_name) || "संकेत किर्दत",
        phone: (document.getElementById("modal-phone") ? document.getElementById("modal-phone").value : "").trim() || (state.shopSettings && state.shopSettings.phone) || "9876543210",
        upi_id: (document.getElementById("modal-upi") ? document.getElementById("modal-upi").value : "").trim() || (state.shopSettings && state.shopSettings.upi_id) || "merchant@upi",
        address: (document.getElementById("modal-address") ? document.getElementById("modal-address").value : "").trim() || (state.shopSettings && state.shopSettings.address) || "सातारा, महाराष्ट्र"
    };

    await persistShopSettings(payload);
    closeModal("modal-shop-settings");
}

async function persistShopSettings(payload) {
    if (!payload.shop_name) payload.shop_name = "SK Store";
    state.shopSettings = payload;
    localStorage.setItem("verna_shop_settings", JSON.stringify(payload));
    
    // Synchronize user session state as well
    if (state.user) {
        state.user.shop_name = payload.shop_name;
        localStorage.setItem("verna_user", JSON.stringify(state.user));
    }
    
    applyShopSettingsToUI();

    try {
        const res = await apiCall("/api/shop/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            const json = await res.json();
            if (json.data) {
                state.shopSettings = json.data;
                localStorage.setItem("verna_shop_settings", JSON.stringify(json.data));
            }
        }
    } catch (e) {
        console.warn("Persisting shop settings locally:", e);
    }

    applyShopSettingsToUI();
    alert(`✅ दुकान माहिती कायमस्वरूपी सेव्ह झाली!\nदुकान: ${state.shopSettings.shop_name}\nमालक: ${state.shopSettings.owner_name}`);
}

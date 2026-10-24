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

        if (localReceipts.length === 0 && localKhata.length === 0 && localExpenses.length === 0) {
            return;
        }

        await apiCall("/api/sync", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                receipts: localReceipts,
                khata: localKhata,
                expenses: localExpenses
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

// I18N Translations (100% Complete Bilingual Coverage)
const i18n = {
    mr: {
        app_name: "VernaLedger.AI",
        tagline: "किराणा दुकानांसाठी सुरक्षित स्मार्ट लेजर",
        login_title: "मर्चंट लॉगिन",
        login_demo_admin: "⚡ ॲडमिन डेमो",
        login_demo_staff: "👤 स्टाफ डेमो",
        lbl_username: "वापरकर्ता नाव",
        lbl_password: "पासवर्ड",
        btn_login: "🔐 ॲप्लिकेशन उघडा",
        nav_scanner: "स्मार्ट स्कॅनर",
        nav_khata: "ग्राहक खाते",
        nav_business: "स्टोअर ऑपरेशन्स",
        nav_ledger: "लेजर व पावत्या",
        nav_ai: "AI बिझनेस स्टुडिओ",
        btn_logout: "🚪 बाहेर पडा",
        lang_label: "🌐 मराठी",
        mob_nav_scanner: "स्कॅनर",
        mob_nav_khata: "खाते",
        mob_nav_business: "ऑपरेशन्स",
        mob_nav_ledger: "लेजर",
        mob_nav_ai: "AI स्टुडिओ",

        hud_scanner_title: "⚡ स्मार्ट मल्टीमॉडेल स्कॅनर व व्हॉइस बिलिंग",
        hud_scanner_sub: "हस्तलिखित व छापील पावत्यांचे १ सेकंदात डिजिटल बिलामध्ये रूपांतर",
        hud_khata_title: "💳 ग्राहक खाते व डिजिटल उधारी वही",
        hud_khata_sub: "WhatsApp द्वारे १-क्लिक देय स्मरणपत्रे व पारदर्शक जमा-खर्च हिशोब",
        hud_business_title: "🏬 स्टोअर ऑपरेशन्स, माल साठा व खर्च",
        hud_business_sub: "इन्व्हेंटरी ट्रॅकिंग, कमी स्टॉक अलर्ट्स आणि दैनिक खर्च व्यवस्थापन",
        hud_ledger_title: "📊 सुरक्षित डिजिटल लेजर डेटाबेस",
        hud_ledger_sub: "सर्व जुन्या पावत्यांचा इतिहास, शोध आणि थर्मल पावती प्रिंट",
        hud_ai_title: "🤖 VernaLedger AI बिझनेस स्टुडिओ",
        hud_ai_sub: "तुमच्या दुकानाचा नफा, उधारी व साठ्याचा वैयक्तिक AI सल्लागार",

        kpi_sales: "एकूण विक्री",
        kpi_bills: "एकूण पावत्या",
        kpi_avg: "सरासरी बिल",
        kpi_profit: "निव्वळ नफा",
        kpi_udhar: "बाकी उधारी",

        card_scan_input: "पावती स्कॅन / व्हॉइस इनपुट",
        tab_vision: "📷 AI व्हिजन स्कॅनर",
        tab_voice: "🎙️ व्हॉइस बिलिंग",
        dropzone_title: "पावतीचा फोटो निवडा किंवा येथे ड्रॅग करा",
        dropzone_sub: "PNG, JPG, JPEG (हस्तलिखित किंवा छापील बिल)",
        btn_camera: "📷 लाईव्ह कॅमेराने फोटो काढा",
        btn_ocr: "⚡ AI स्कॅन करा",
        voice_hint: "मायक्रोफोन बटण दाबून ग्राहकाचे नाव व सामान मराठीत बोला (उदा. 'सागर ला २ किलो साखर ५० रुपये आणि १ तेल १५० रुपये')",
        voice_ready: "बोलण्यासाठी माईक वर क्लिक करा",
        voice_listening: "मी ऐकत आहे... सामान बोला...",
        voice_placeholder: "येथे उच्चारलेला मजकूर दिसेल किंवा स्वतः टाईप करा...",
        btn_voice_submit: "⚡ व्हॉइस वरून पावती तयार करा",

        card_current_bill: "📋 सध्याचे बिल (Live POS)",
        lbl_vendor: "किराणा स्टोअर नाव",
        lbl_date: "तारीख",
        lbl_category: "श्रेणी",
        th_item: "वस्तू नाव",
        th_qty: "नग/प्रमाण",
        th_rate: "दर (₹)",
        th_total: "एकूण (₹)",
        th_action: "कृती",
        btn_add_item: "+ वस्तू जोडा",
        lbl_grand_total: "एकूण देय रक्कम:",
        btn_save_ledger: "💾 लेजरमध्ये सेव्ह करा",
        btn_print_receipt: "🖨️ प्रिंट पावती",
        btn_add_to_khata: "💳 खात्यावर उधारी नोंदवा",

        kpi_customers: "एकूण ग्राहक",
        kpi_txns: "एकूण व्यवहार",
        card_khata_title: "ग्राहक उधारी यादी",
        btn_new_customer: "+ नवीन खाते",
        ph_search_khata: "ग्राहक नाव किंवा मोबाईल नंबरने शोधा...",
        th_customer: "ग्राहक नाव",
        th_phone: "मोबाईल",
        th_type: "प्रकार",
        th_amount: "रक्कम (₹)",
        th_note: "टीप",
        th_due: "बाकी उधारी",
        btn_whatsapp: "WhatsApp तगादा",
        btn_add_entry: "+ जमा/उधारी",
        btn_history: "इतिहास",

        low_stock_notice: "कमी स्टॉक अलर्ट (Low Stock Notice)",
        low_stock_msg: "काही वस्तूंचा साठा संपत आला आहे.",
        card_inventory: "दुकानातील माल साठा",
        btn_new_stock: "+ नवीन माल",
        th_stock: "साठा",
        th_price: "किंमत (₹)",
        th_status: "स्थिती",
        card_expenses: "दैनिक दुकान खर्च",
        btn_new_expense: "+ नवीन खर्च",
        th_reason: "खर्चाचे कारण",

        card_ledger_title: "सर्व जुन्या पावत्यांचा इतिहास",
        ph_search_ledger: "पावती क्रमांक किंवा दुकानाच्या नावाने शोधा...",
        btn_export_csv: "📥 CSV डाउनलोड",
        btn_export_excel: "Excel (.xlsx) संपूर्ण डेटा डाऊनलोड",
        th_bill_no: "बिल क्र.",
        th_store_customer: "दुकान / ग्राहक",

        card_ai_title: "VernaLedger AI बिझनेस स्टुडिओ",
        chip_sales: "💰 आजची एकूण विक्री किती?",
        chip_udhar: "👥 बाकी उधारी किती?",
        chip_low_stock: "🚨 कमी साठा?",
        chip_developers: "🎓 प्रोजेक्ट डेव्हलपर्स?",
        ai_greeting: "नमस्कार! मी <strong>VernaLedger AI</strong> आहे. आपल्या किराणा दुकानाची विक्री, उधारी किंवा साठ्याबद्दल आपण मराठीत विचारू शकता किंवा माईक दाबून थेट उधारी/खर्च नोंदवू शकता.",
        ai_voice_listening: "🎙️ मी ऐकत आहे... प्रश्न विचारा किंवा उधारी बोला...",
        ph_ai_input: "येथे प्रश्न विचारा किंवा बोला... (उदा. 'आजची विक्री किती?')",
        btn_send: "पाठवा",
        lbl_voice_output: "🔊 व्हॉइस उत्तर ऐका",
        btn_repeat_audio: "🔊 पुन्हा ऐका",


        receipt_preview_title: "🖨️ डिजिटल पावती प्रिव्ह्यू",
        receipt_bill_no_label: "Bill No:",
        receipt_total_label: "एकूण देय रक्कम:",
        receipt_upi_text: "स्कॅन करून UPI द्वारे पैसे भरा",
        receipt_greeting: "🙏 पुन्हा भेट द्या! धन्यवाद! 🙏",
        btn_print_now: "🖨️ आताच प्रिंट करा",
        btn_close: "बंद करा",

        modal_khata_title: "👥 नवीन ग्राहक खाते उघडा",
        modal_entry_title: "💳 नवीन व्यवहार नोंदवा (जमा/उधारी)",
        modal_stock_title: "📦 नवीन माल नोंदवा (Inventory)",
        modal_expense_title: "💸 नवीन खर्च नोंदवा (Store Expense)",
        btn_submit: "सेव्ह करा",
        btn_cancel: "रद्द करा",
        btn_save_bill: "💾 बिल सेव्ह करा",
        btn_whatsapp_bill: "📲 WhatsApp बिल",
        ocr_scanning: "⚡ AI द्वारे पावती स्कॅनिंग सुरू आहे..."
    },
    en: {
        app_name: "VernaLedger.AI",
        tagline: "Secure Smart Retail Ledger for Kirana Stores",
        login_title: "Merchant Login",
        login_demo_admin: "⚡ Admin Demo",
        login_demo_staff: "👤 Staff Demo",
        lbl_username: "Username",
        lbl_password: "Password",
        btn_login: "🔐 Open Application",
        nav_scanner: "Smart Scanner",
        nav_khata: "Customer Khata",
        nav_business: "Store Operations",
        nav_ledger: "Ledger Database",
        nav_ai: "AI Business Studio",
        btn_logout: "🚪 Logout",
        lang_label: "🌐 English",
        mob_nav_scanner: "Scanner",
        mob_nav_khata: "Khata",
        mob_nav_business: "Operations",
        mob_nav_ledger: "Ledger",
        mob_nav_ai: "AI Studio",

        hud_scanner_title: "⚡ Smart Multimodal Scanner & Voice Billing",
        hud_scanner_sub: "Convert handwritten receipts into digital ledger using Gemini 2.5 Flash",
        hud_khata_title: "💳 Customer Khata & Digital Credit Ledger",
        hud_khata_sub: "1-Click WhatsApp payment reminders and transparent accounts",
        hud_business_title: "🏬 Store Operations, Inventory & Expenses",
        hud_business_sub: "Inventory tracking, low-stock alerts, and daily expense management",
        hud_ledger_title: "📊 Secure Digital Ledger Database",
        hud_ledger_sub: "Full history of saved receipts, search, and POS thermal print",
        hud_ai_title: "🤖 VernaLedger AI Business Studio",
        hud_ai_sub: "Real-time store intelligence powered by SQLite & Gemini 2.5 RAG",

        kpi_sales: "Total Sales",
        kpi_bills: "Total Receipts",
        kpi_avg: "Average Ticket",
        kpi_profit: "Net Profit",
        kpi_udhar: "Pending Udhar",

        card_scan_input: "Receipt Scanner / Voice Input",
        tab_vision: "📷 AI Vision Scanner",
        tab_voice: "🎙️ Voice Billing",
        dropzone_title: "Select Receipt Photo or Drag Here",
        dropzone_sub: "PNG, JPG, JPEG (Handwritten or Printed Bill)",
        btn_camera: "📷 Capture with Live Camera",
        btn_ocr: "⚡ AI Scan Receipt",
        voice_hint: "Click microphone and speak customer name and items (e.g. '2 kg sugar 50 rupees and 1 oil 150 rupees to Sagar')",
        voice_ready: "Click mic to speak",
        voice_listening: "Listening... Speak items...",
        voice_placeholder: "Spoken text will appear here or type manually...",
        btn_voice_submit: "⚡ Generate Bill from Voice",

        card_current_bill: "📋 Current Live Bill (POS)",
        lbl_vendor: "Kirana Store Name",
        lbl_date: "Date",
        lbl_category: "Category",
        th_item: "Item Name",
        th_qty: "Qty",
        th_rate: "Rate (₹)",
        th_total: "Total (₹)",
        th_action: "Action",
        btn_add_item: "+ Add Item",
        lbl_grand_total: "Grand Total:",
        btn_save_ledger: "💾 Save to Ledger",
        btn_print_receipt: "🖨️ Print Receipt",
        btn_add_to_khata: "💳 Add to Khata (Credit)",

        kpi_customers: "Total Customers",
        kpi_txns: "Total Txns",
        card_khata_title: "Customer Ledger Accounts",
        btn_new_customer: "+ New Customer",
        ph_search_khata: "Search customer by name or phone...",
        th_customer: "Customer Name",
        th_phone: "Mobile",
        th_type: "Type",
        th_amount: "Amount (₹)",
        th_note: "Notes",
        th_due: "Pending Due",
        btn_whatsapp: "WhatsApp Reminder",
        btn_add_entry: "+ Credit/Payment",
        btn_history: "History",

        low_stock_notice: "Low Stock Alert Notice",
        low_stock_msg: "Some items are running out of stock.",
        card_inventory: "Store Inventory & Stock",
        btn_new_stock: "+ Add Stock",
        th_stock: "Stock",
        th_price: "Price (₹)",
        th_status: "Status",
        card_expenses: "Daily Store Expenses",
        btn_new_expense: "+ Add Expense",
        th_reason: "Expense Reason",

        card_ledger_title: "All Saved Receipts History",
        ph_search_ledger: "Search by receipt number or store...",
        btn_export_csv: "📥 Export CSV",
        btn_export_excel: "Download Excel (.xlsx) Ledger",
        th_bill_no: "Bill #",
        th_store_customer: "Store / Customer",

        card_ai_title: "VernaLedger AI Business Studio",
        chip_sales: "💰 Today's total sales?",
        chip_udhar: "👥 Total pending credit?",
        chip_low_stock: "🚨 Low stock items?",
        chip_developers: "🎓 Project Developers?",
        ai_greeting: "Hello! I am <strong>VernaLedger AI</strong>. You can ask in English or Marathi about your store sales, customer credit, stock, or expenses, or speak voice commands to record entries.",
        ai_voice_listening: "🎙️ Listening... Ask a question or speak credit...",
        ph_ai_input: "Ask a question or speak... (e.g. 'What is today's sales?')",
        btn_send: "Send",
        lbl_voice_output: "🔊 Voice Audio Output",
        btn_repeat_audio: "🔊 Replay Audio",


        receipt_preview_title: "🖨️ Digital POS Receipt Preview",
        receipt_bill_no_label: "Bill No:",
        receipt_total_label: "Grand Total:",
        receipt_upi_text: "Scan to pay via UPI",
        receipt_greeting: "🙏 Thank you! Visit Again! 🙏",
        btn_print_now: "🖨️ Print Now",
        btn_close: "Close",

        modal_khata_title: "👥 Add New Customer Khata",
        modal_entry_title: "💳 Record Transaction (Credit/Payment)",
        modal_stock_title: "📦 Add Inventory Item",
        modal_expense_title: "💸 Record Store Expense",
        btn_submit: "Save",
        btn_cancel: "Cancel"
    },
    hi: {
        app_name: "VernaLedger.AI",
        tagline: "किराना दुकानों के लिए सुरक्षित स्मार्ट डिजिटल लेजर",
        login_title: "मर्चेंट लॉगिन",
        login_demo_admin: "⚡ एडमिन डेमो",
        login_demo_staff: "👤 स्टाफ डेमो",
        lbl_username: "उपयोगकर्ता नाम",
        lbl_password: "पासवर्ड",
        btn_login: "🔐 एप्लिकेशन खोलें (Login)",
        nav_scanner: "स्मार्ट स्कैनर",
        nav_khata: "ग्राहक खाता",
        nav_business: "स्टोर ऑपरेशन्स",
        nav_ledger: "लेजर व रसीदें",
        nav_ai: "AI बिजनेस स्टूडियो",
        btn_logout: "🚪 बाहर निकलें",
        lang_label: "🌐 हिन्दी",
        mob_nav_scanner: "स्कैनर",
        mob_nav_khata: "खाता",
        mob_nav_business: "ऑपरेशन्स",
        mob_nav_ledger: "लेजर",
        mob_nav_ai: "AI स्टूडियो",

        hud_scanner_title: "⚡ स्मार्ट मल्टीमॉडल स्कैनर व वॉइस बिलिंग",
        hud_scanner_sub: "हस्तलिखित और मुद्रित बिलों का 1 सेकंड में डिजिटल बिल में रूपांतरण",
        hud_khata_title: "💳 ग्राहक खाता व डिजिटल उधारी बही",
        hud_khata_sub: "WhatsApp द्वारा 1-क्लिक भुगतान अनुस्मारक व पारदर्शी जमा-उधारी हिसाब",
        hud_business_title: "🏬 स्टोर ऑपरेशन्स, माल स्टॉक व खर्च",
        hud_business_sub: "इन्वेंट्री ट्रैकिंग, कम स्टॉक अलर्ट्स और दैनिक खर्च प्रबंधन",
        hud_ledger_title: "📊 सुरक्षित डिजिटल लेजर डेटाबेस",
        hud_ledger_sub: "सभी पुरानी रसीदों का इतिहास, खोज और थर्मल बिल प्रिंट",
        hud_ai_title: "🤖 VernaLedger AI बिजनेस स्टूडियो",
        hud_ai_sub: "आपकी दुकान की बिक्री, उधारी और स्टॉक का व्यक्तिगत AI सलाहकार",

        kpi_sales: "कुल बिक्री",
        kpi_bills: "कुल रसीदें",
        kpi_avg: "औसत बिल",
        kpi_profit: "शुद्ध लाभ",
        kpi_udhar: "बकाया उधारी",

        card_scan_input: "रसीद स्कैन / वॉइस इनपुट",
        tab_vision: "📷 AI विजन स्कैनर",
        tab_voice: "🎙️ वॉइस बिलिंग",
        dropzone_title: "रसीद का फोटो चुनें या यहाँ ड्रैग करें",
        dropzone_sub: "PNG, JPG, JPEG (हस्तलिखित या मुद्रित बिल)",
        btn_camera: "📷 लाइव कैमरे से फोटो लें",
        btn_ocr: "⚡ AI स्कैन करें",
        voice_hint: "माइक दबाकर ग्राहक का नाम और सामान बोलें (उदा. 'रोहन को 2 किलो चीनी 50 रुपये और 1 तेल 150 रुपये')",
        voice_ready: "बोलने के लिए माइक पर क्लिक करें",
        voice_listening: "मैं सुन रहा हूँ... सामान का नाम बोलें...",
        voice_placeholder: "यहाँ बोला गया पाठ दिखेगा या स्वयं टाइप करें...",
        btn_voice_submit: "⚡ वॉइस से रसीद बनाएं",

        card_current_bill: "📋 वर्तमान बिल (Live POS)",
        lbl_vendor: "किराना स्टोर नाम",
        lbl_date: "तारीख",
        lbl_category: "श्रेणी",
        th_item: "सामान का नाम",
        th_qty: "मात्रा/वजन",
        th_rate: "दर (₹)",
        th_total: "कुल (₹)",
        th_action: "कार्रवाई",
        btn_add_item: "+ सामान जोड़ें",
        lbl_grand_total: "कुल देय राशि:",
        btn_save_ledger: "💾 लेजर में सेव करें",
        btn_print_receipt: "🖨️ रसीद प्रिंट करें",
        btn_add_to_khata: "💳 खाते पर उधारी दर्ज करें",

        kpi_customers: "कुल ग्राहक",
        kpi_txns: "कुल लेनदेन",
        card_khata_title: "ग्राहक उधारी सूची",
        btn_new_customer: "+ नया खाता",
        ph_search_khata: "ग्राहक का नाम या मोबाइल नंबर से खोजें...",
        th_customer: "ग्राहक का नाम",
        th_phone: "मोबाइल",
        th_type: "प्रकार",
        th_amount: "राशि (₹)",
        th_note: "टिप्पणी",
        th_due: "बकाया उधारी",
        btn_whatsapp: "WhatsApp तकादा",
        btn_add_entry: "+ जमा/उधारी",
        btn_history: "इतिहास",

        low_stock_notice: "कम स्टॉक अलर्ट (Low Stock Notice)",
        low_stock_msg: "कुछ वस्तुओं का स्टॉक समाप्त होने वाला है.",
        card_inventory: "दुकान का स्टॉक (Inventory)",
        btn_new_stock: "+ नया सामान",
        th_stock: "स्टॉक",
        th_price: "कीमत (₹)",
        th_status: "स्थिति",
        card_expenses: "दैनिक दुकान खर्च",
        btn_new_expense: "+ नया खर्च",
        th_reason: "खर्च का कारण",

        card_ledger_title: "सभी पुरानी रसीदों का इतिहास",
        ph_search_ledger: "रसीद संख्या या दुकान के नाम से खोजें...",
        btn_export_csv: "📥 CSV डाउनलोड",
        btn_export_excel: "Excel (.xlsx) संपूर्ण डेटा डाउनलोड",
        th_bill_no: "बिल क्र.",
        th_store_customer: "दुकान / ग्राहक",

        card_ai_title: "VernaLedger AI बिजनेस स्टूडियो",
        chip_sales: "💰 आज की कुल बिक्री कितनी है?",
        chip_udhar: "👥 कुल बकाया उधारी कितनी है?",
        chip_low_stock: "🚨 कम स्टॉक कौन सा है?",
        chip_developers: "🎓 प्रोजेक्ट डेवलपर्स कौन हैं?",
        ai_greeting: "नमस्ते! मैं <strong>VernaLedger AI</strong> हूँ। अपनी किराना दुकान की बिक्री, उधारी या स्टॉक के बारे में हिन्दी में पूछ सकते हैं या माइक दबाकर सीधे उधारी/खर्च दर्ज कर सकते हैं।",
        ai_voice_listening: "🎙️ मैं सुन रहा हूँ... प्रश्न पूछें या उधारी बोलें...",
        ph_ai_input: "यहाँ प्रश्न पूछें या बोलें... (उदा. 'आज की बिक्री कितनी है?')",
        btn_send: "भेजें",
        lbl_voice_output: "🔊 वॉइस उत्तर सुनें",
        btn_repeat_audio: "🔊 दोबारा सुनें",

        receipt_preview_title: "🖨️ डिजिटल रसीद पूर्वावलोकन",
        receipt_bill_no_label: "Bill No:",
        receipt_total_label: "कुल देय राशि:",
        receipt_upi_text: "स्कैन करके UPI से भुगतान करें",
        receipt_greeting: "🙏 फिर पधारें! धन्यवाद! 🙏",
        btn_print_now: "🖨️ अभी प्रिंट करें",
        btn_close: "बंद करें",

        modal_khata_title: "👥 नया ग्राहक खाता खोलें",
        modal_entry_title: "💳 नया लेनदेन दर्ज करें (जमा/उधारी)",
        modal_stock_title: "📦 नया सामान दर्ज करें (Inventory)",
        modal_expense_title: "💸 नया खर्च दर्ज करें (Store Expense)",
        btn_submit: "सेव करें",
        btn_cancel: "रद्द करें",
        btn_save_bill: "💾 बिल सेव करें",
        btn_whatsapp_bill: "📲 WhatsApp बिल",
        ocr_scanning: "⚡ AI द्वारा रसीद स्कैनिंग जारी है..."
    }
};

// Helper: Show item and customer names strictly ONCE in the active language
function formatLocalizedName(name, lang = state.lang) {
    if (!name) return "";
    name = String(name).trim();
    // Check format: "Marathi (English)" e.g. "साखर (Sugar M-30)" or "सागर पाटील (Sagar Patil)"
    const parenMatch = name.match(/^([^(]+)\s*\(([^)]+)\)$/);
    if (parenMatch) {
        const mrPart = parenMatch[1].trim();
        const enPart = parenMatch[2].trim();
        return lang === "en" ? enPart : mrPart;
    }
    // Check format: "Marathi / English"
    const slashMatch = name.match(/^([^/]+)\s*\/\s*(.+)$/);
    if (slashMatch) {
        const mrPart = slashMatch[1].trim();
        const enPart = slashMatch[2].trim();
        return lang === "en" ? enPart : mrPart;
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

    // Check stored user session
    const savedUser = localStorage.getItem("verna_user");
    if (savedUser) {
        try {
            state.user = JSON.parse(savedUser);
            showApp();
        } catch (e) {
            localStorage.removeItem("verna_user");
            showLogin();
        }
    } else {
        showLogin();
    }

    // Initialize Web Speech API if supported
    initSpeechRecognition();
    initRagSpeech();
    applyLanguage();
});

// -----------------------------------------------------------------------------
// AUTHENTICATION
// -----------------------------------------------------------------------------
// Universal API Fetcher with automatic prefix fallback (/api/* <-> /*)
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
        localStorage.setItem("verna_user", JSON.stringify(data));
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
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("app-container").style.display = "flex";

    // Set user profile indicators
    document.getElementById("sidebar-user-name").innerText = state.user.username;
    document.getElementById("sidebar-user-role").innerText = `Role: ${state.user.role}`;
    const badge = document.getElementById("sidebar-role-badge");
    badge.innerText = state.user.role.toUpperCase();

    badge.className = "user-role-badge badge-admin";

    // Load initial data
    loadDashboardMetrics();

    // Initialize High-Contrast Theme (किराणा मोड)
    initTheme();
    resetBillCard();

    loadReceiptsLedger();
    loadKhataData();
    loadInventoryData();
    loadExpensesData();
    recalcBillTotal();

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

    const titleEl = document.getElementById("hud-title");
    const subEl = document.getElementById("hud-subtitle");
    if (titleEl && dict[titleKey]) titleEl.innerText = dict[titleKey];
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

        if (!res.ok || !json.data) {
            throw new Error(json.detail || json.error || "OCR स्कॅनिंग अयशस्वी झाले.");
        }

        populateBillCard(json.data);

        if (json.duplicate) {
            alert("⚠️ दुबार पावती: " + (json.warning || "ही पावती आधीच लेजरमध्ये नोंदवलेली आहे. दुबार नोंद टाळली गेली आहे."));
        } else {
            VernaStorage.addReceipt(json.data);
            alert("✅ पावती यशस्वीरित्या स्कॅन झाली व लेजरमध्ये नोंदवली गेली!");
        }

        loadDashboardMetrics();
        loadReceiptsLedger();
    } catch (err) {
        console.error("OCR Error:", err);
        alert("OCR एरर: " + err.message);
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
        const qtyStr = row.querySelector(".item-qty").value;
        const rateVal = row.querySelector(".item-rate").value;
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
    const vendor = document.getElementById("bill-vendor-name").value.trim() || "किराणा स्टोअर";
    const dateVal = document.getElementById("bill-date").value || new Date().toISOString().split("T")[0];
    const rows = document.querySelectorAll("#bill-items-tbody tr");
    const items = [];
    let grandTotal = 0;

    rows.forEach(row => {
        const name = row.querySelector(".item-name").value.trim();
        const qty = row.querySelector(".item-qty").value.trim();
        const rate = parseFloat(row.querySelector(".item-rate").value) || 0;
        const total = parseFloat(row.querySelector(".item-total").innerText) || 0;
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
        alert("कृपया पावतीमध्ये किमान एक वस्तू टाका.");
        return;
    }

    try {
        // Send as a manual voice-like bill or ledger insert
        const res = await apiCall("/api/voice-billing", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                transcript: `${bill.vendor_name} येथे ${bill.items.map(i => `${i.quantity} ${i.item_name} ${i.rate} रुपये`).join(', ')}`,
                username: state.user ? state.user.username : "admin"
            })
        });

        if (!res.ok) throw new Error("पावती सेव्ह करता आली नाही.");

        const jsonBill = await res.json().catch(() => ({}));
        if (jsonBill && jsonBill.data) {
            VernaStorage.addReceipt(jsonBill.data);
        } else {
            VernaStorage.addReceipt(bill);
        }

        loadDashboardMetrics();
        loadReceiptsLedger();
        alert("✅ पावती यशस्वीरित्या डिजिटल लेजरमध्ये सेव्ह झाली!");
        resetBillCard();
    } catch (e) {
        alert("एरर: " + e.message);
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
    document.getElementById("receipt-shop-name").innerText = formatLocalizedName(bill.vendor_name, state.lang) || (isMr ? "महादेव किराणा स्टोअर" : "Mahadev Kirana Store");
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

        renderKhataCards(finalData.customers);
        renderKhataTable(finalData.transactions);

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
        const waMsg = encodeURIComponent(
            `🙏 *${(bill.vendor_name || 'किराणा पावती').trim()}*\n` +
            `नमस्कार ${c.name} जी!\n` +
            `आपल्या खात्यावर दुकानाचे एकूण *₹${c.balance.toFixed(2)}* उधारीचे येणे बाकी आहे.\n\n` +
            `💳 कृपया खालील UPI लिंकवरून GooglePay / PhonePe द्वारे पेमेंट करावे:\n` +
            `upi://pay?pa=merchant@upi&pn=KiranaStore&am=${c.balance.toFixed(2)}&cu=INR\n\n` +
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

function renderKhataTable(transactions) {
    const tbody = document.getElementById("khata-table-tbody");
    tbody.innerHTML = "";

    transactions.forEach(t => {
        const isCredit = t.transaction_type === "Credit Given";
        const isMr = state.lang === "mr";
        const displayName = formatLocalizedName(t.customer_name, state.lang);
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">#${t.id}</td>
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
                <button onclick="deleteKhataEntry(${t.id})" style="background: none; border: none; color: var(--neon-red); cursor: pointer; font-size: 1rem;" title="डीलीट करा">
                    🗑️
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filterKhataList() {
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

    if (!receipts || receipts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 24px;">कोणतीही पावती उपलब्ध नाही.</td></tr>`;
        return;
    }

    receipts.forEach(r => {
        const isMr = state.lang === 'mr';
        const displayName = formatLocalizedName(r.vendor_name || (isMr ? 'किराणा स्टोअर' : 'Kirana Store'), state.lang);
        const tr = document.createElement("tr");
        tr.innerHTML = `
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
// =============================================================================
function downloadExcelReport() {
    try {
        const d = new Date();
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const fileName = `VernaLedger_Receipts_${year}-${month}-${day}.xlsx`;
        const downloadUrl = `/api/export/excel?t=${Date.now()}`;
        
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.setAttribute("download", fileName);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } catch (err) {
        console.error("Excel download error:", err);
        window.location.href = `/api/export/excel?t=${Date.now()}`;
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

function stopCurrentAudio() {
    currentAudioPlayToken++; // Invalidate any in-flight TTS calls
    if (currentPlayingAudio) {
        try {
            currentPlayingAudio.pause();
            currentPlayingAudio.currentTime = 0;
            currentPlayingAudio.src = "";
        } catch (e) {}
        currentPlayingAudio = null;
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
    clean = clean.replace(/\b(?:Prof\.?\s*)?Kaisar\s+(?:Atar|Attar)(?:\s+Sir)?\b/gi, "प्राध्यापक कै-सर अतार सर");
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

let ragSpeechRecognition = null;
let isRagListening = false;
let ragAutoSubmitTimer = null;
let ragMediaRecorder = null;
let ragAudioChunks = [];
let isRagRecording = false;
let ragRecordTimer = null;
let ragRecordSeconds = 0;

// -----------------------------------------------------------------------------
// NATIVE MULTIMODAL VOICE INTERACTION (GOOGLE GEMINI NATIVE AUDIO STREAM)
// -----------------------------------------------------------------------------
async function toggleRagVoice() {
    if (isAiProcessing) return;

    if (isRagRecording) {
        stopRagNativeRecording();
        return;
    }

    // Check if getUserMedia is supported in this browser
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        fallbackWebSpeech();
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });

        // Determine supported audio container
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

        // Live seconds counter
        ragRecordTimer = setInterval(() => {
            ragRecordSeconds++;
            if (statusEl && isRagRecording) {
                statusEl.innerHTML = `<span class="pulse-red">🔴</span> <strong>थेट आवाज रेकॉर्ड होत आहे (${ragRecordSeconds}s)...</strong> (थांबवण्यासाठी ⏹️ दाबा)`;
            }
            if (ragRecordSeconds >= 14) {
                stopRagNativeRecording();
            }
        }, 1000);

        ragMediaRecorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) {
                ragAudioChunks.push(e.data);
            }
        };

        ragMediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
            clearInterval(ragRecordTimer);

            if (micBtn) {
                micBtn.classList.remove("listening");
                micBtn.innerHTML = "🎙️";
                micBtn.title = "माईक द्वारे थेट बोला";
            }
            if (statusEl) {
                statusEl.style.display = "none";
            }

            if (ragAudioChunks.length === 0) return;

            const finalMime = ragMediaRecorder.mimeType || 'audio/webm';
            const audioBlob = new Blob(ragAudioChunks, { type: finalMime });

            if (audioBlob.size < 500) {
                console.warn("Audio too small, silence detected.");
                return;
            }

            // Convert to Base64 data URL
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = async () => {
                const base64Data = reader.result;
                await submitNativeVoiceAi(base64Data, finalMime);
            };
        };

        ragMediaRecorder.start(250);
    } catch (err) {
        console.warn("Microphone access error, falling back to Web Speech:", err);
        fallbackWebSpeech();
    }
}

function stopRagNativeRecording() {
    if (ragMediaRecorder && ragMediaRecorder.state !== "inactive") {
        try { ragMediaRecorder.stop(); } catch (e) {}
    }
    isRagRecording = false;
    clearInterval(ragRecordTimer);
}

// Fallback for browsers that block MediaRecorder or microphone
function fallbackWebSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("आपल्या ब्राऊझरमध्ये मायक्रोफोन उपलब्ध नाही. कृपया स्वतः खाली टाईप करा.");
        return;
    }

    if (!ragSpeechRecognition) {
        ragSpeechRecognition = new SpeechRecognition();
        ragSpeechRecognition.continuous = false;
        ragSpeechRecognition.interimResults = true;
        ragSpeechRecognition.lang = (state.lang === "en") ? "en-IN" : "mr-IN";

        ragSpeechRecognition.onstart = () => {
            isRagListening = true;
            const btn = document.getElementById("btn-rag-mic");
            if (btn) btn.classList.add("listening");
            const status = document.getElementById("rag-voice-status");
            if (status) {
                status.innerText = "🎙️ ऐकत आहे... बोला...";
                status.style.display = "block";
            }
        };

        ragSpeechRecognition.onresult = (event) => {
            let finalT = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) finalT += event.results[i][0].transcript;
            }
            if (finalT) {
                const corrected = autoCorrectMarathiSpeech(finalT.trim());
                document.getElementById("ai-user-input").value = corrected;
                stopRagVoice();
                submitAiChat();
            }
        };

        ragSpeechRecognition.onerror = () => stopRagVoice();
        ragSpeechRecognition.onend = () => stopRagVoice();
    }

    try {
        ragSpeechRecognition.start();
    } catch (e) {
        stopRagVoice();
    }
}

function stopRagVoice() {
    isRagListening = false;
    const btn = document.getElementById("btn-rag-mic");
    if (btn) btn.classList.remove("listening");
    const status = document.getElementById("rag-voice-status");
    if (status) status.style.display = "none";
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
        aiBubble.innerHTML = `एरर: सर्व्हरशी संपर्क होऊ शकला नाही.`;
    } finally {
        isAiProcessing = false;
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.innerHTML = `<span>पाठवा</span> 🚀`;
        }
        historyContainer.scrollTo({ top: historyContainer.scrollHeight, behavior: 'smooth' });
    }
}

// Ultra-fast Gemini-style pure text response bubble
function renderAiResponseBubble(aiBubble, data) {
    const formatted = (data.answer || "माफ करा, उत्तर मिळू शकले नाही.")
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

    aiBubble.innerHTML = `
        <div>${formatted}</div>
        ${data.action_status ? `<div style="margin-top: 6px; font-size: 0.74rem; color: var(--neon-green); font-weight: 700;">● ${data.action_status}</div>` : ''}
    `;
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

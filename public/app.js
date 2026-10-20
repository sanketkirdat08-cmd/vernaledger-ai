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

// I18N Translations
const i18n = {
    mr: {
        nav_scanner: "स्मार्ट स्कॅनर",
        nav_khata: "ग्राहक खाते",
        nav_business: "स्टोअर ऑपरेशन्स",
        nav_ledger: "लेजर व पावत्या",
        nav_ai: "AI बिझनेस स्टुडिओ",
        nav_staff: "कर्मचारी व ऑडिट",
        kpi_sales: "आजची एकूण विक्री",
        kpi_bills: "एकूण पावत्या",
        kpi_avg: "सरासरी पावती मूल्य",
        kpi_udhar: "बाकी एकूण उधारी",
        ocr_scanning: "Gemini 2.5 Flash द्वारे विश्लेषण सुरू आहे...",
        voice_listening: "मी ऐकत आहे... सामान बोला...",
        voice_ready: "बोलण्यासाठी माईक वर क्लिक करा"
    },
    en: {
        nav_scanner: "Smart Scanner",
        nav_khata: "Customer Khata",
        nav_business: "Store Operations",
        nav_ledger: "Ledger Database",
        nav_ai: "AI Business Studio",
        nav_staff: "Staff & Audit",
        kpi_sales: "Today's Gross Sales",
        kpi_bills: "Total Receipts",
        kpi_avg: "Average Ticket",
        kpi_udhar: "Pending Udhar",
        ocr_scanning: "Analyzing receipt with Gemini 2.5 Flash...",
        voice_listening: "Listening... Speak items...",
        voice_ready: "Click mic to speak"
    }
};

// -----------------------------------------------------------------------------
// INITIALIZATION
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
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
    if (state.user.role === "Admin") {
        badge.className = "user-role-badge badge-admin";
        document.getElementById("nav-item-staff").style.display = "flex";
    } else {
        badge.className = "user-role-badge badge-staff";
        document.getElementById("nav-item-staff").style.display = "none";
    }

    // Load initial data
    loadDashboardMetrics();
    loadReceiptsLedger();
    loadKhataData();
    loadInventoryData();
    loadExpensesData();
    if (state.user.role === "Admin") {
        loadStaffData();
    }

    recalcBillTotal();
}

// -----------------------------------------------------------------------------
// VIEW NAVIGATION
// -----------------------------------------------------------------------------
function switchView(viewName) {
    if (viewName === "staff" && state.user && state.user.role !== "Admin") {
        alert("केवळ ॲडमिनला कर्मचारी व्यवस्थापनाचा अधिकार आहे.");
        return;
    }

    state.currentView = viewName;

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

    // Update HUD titles
    const hudTitles = {
        scanner: {
            title: "⚡ स्मार्ट मल्टीमॉडेल स्कॅनर व व्हॉइस बिलिंग",
            sub: "Gemini 2.5 Flash द्वारे हस्तलिखित पावत्यांचे डिजिटल लेजरमध्ये रूपांतर"
        },
        khata: {
            title: "💳 ग्राहक खाते व डिजिटल उधारी वही",
            sub: "WhatsApp द्वारे १-क्लिक देय स्मरणपत्रे व पारदर्शक जमा-खर्च हिशोब"
        },
        business: {
            title: "🏬 स्टोअर ऑपरेशन्स, माल साठा व खर्च",
            sub: "इन्व्हेंटरी ट्रॅकिंग, कमी स्टॉक अलर्ट्स आणि दैनिक खर्च व्यवस्थापन"
        },
        ledger: {
            title: "📊 सुरक्षित डिजिटल लेजर डेटाबेस",
            sub: "सर्व जुन्या पावत्यांचा इतिहास, शोध आणि थर्मल पावती प्रिंट"
        },
        ai: {
            title: "🤖 VernaLedger AI बिझनेस स्टुडिओ",
            sub: "लाइव्ह SQLite डेटाबेस व Gemini 2.5 RAG द्वारे स्टोअर अंतर्दृष्टी"
        },
        staff: {
            title: "👥 कर्मचारी व्यवस्थापन व सुरक्षा ऑडिट",
            sub: "भूमिका-आधारित प्रवेश (RBAC) व सिस्टम हालचालींचा संपूर्ण इतिहास"
        }
    };

    if (hudTitles[viewName]) {
        document.getElementById("hud-title").innerText = hudTitles[viewName].title;
        document.getElementById("hud-subtitle").innerText = hudTitles[viewName].sub;
    }
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

        // Populate top KPI cards
        document.getElementById("kpi-total-sales").innerText = `₹${data.total_sales.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        document.getElementById("kpi-total-bills").innerText = data.total_bills;
        document.getElementById("kpi-avg-ticket").innerText = `₹${data.avg_ticket.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        document.getElementById("kpi-pending-udhar").innerText = `₹${data.pending_udhar.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

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
// MULTIMODAL OCR (GEMINI FLASH)
// -----------------------------------------------------------------------------
async function submitReceiptOCR() {
    if (!state.selectedFile) return;

    const loader = document.getElementById("scanner-loader");
    const btn = document.getElementById("btn-run-ocr");
    loader.style.display = "block";
    btn.disabled = true;

    const formData = new FormData();
    formData.append("file", state.selectedFile);

    try {
        const res = await apiCall("/api/ocr", {
            method: "POST",
            body: formData
        });
        const json = await res.json();

        if (!res.ok) {
            throw new Error(json.detail || "OCR स्कॅनिंग अयशस्वी झाले.");
        }

        populateBillCard(json.data);
        loadDashboardMetrics();
        loadReceiptsLedger();
        alert("✅ पावती यशस्वीरित्या स्कॅन झाली व लेजरमध्ये नोंदवली गेली!");
    } catch (err) {
        alert("OCR एरर: " + err.message);
    } finally {
        loader.style.display = "none";
        btn.disabled = false;
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
    state.speechRecognition.continuous = false;
    state.speechRecognition.interimResults = false;
    state.speechRecognition.lang = state.lang === "mr" ? "mr-IN" : "en-IN";

    state.speechRecognition.onstart = () => {
        state.isRecording = true;
        document.getElementById("btn-voice-mic").classList.add("recording");
        document.getElementById("voice-recording-status").innerText = "🎙️ मी ऐकत आहे... सामान बोला...";
        document.getElementById("voice-recording-status").style.color = "var(--neon-green)";
    };

    state.speechRecognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const currentText = document.getElementById("voice-transcript-text").value;
        document.getElementById("voice-transcript-text").value = (currentText ? currentText + " " : "") + transcript;
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
        state.speechRecognition.lang = state.lang === "mr" ? "mr-IN" : "en-IN";
        state.speechRecognition.start();
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
function populateBillCard(data) {
    state.currentBill = data;
    document.getElementById("bill-vendor-name").value = data.vendor_name || "महादेव किराणा स्टोअर";
    if (data.date && data.date.includes("-")) {
        document.getElementById("bill-date").value = data.date;
    }

    const tbody = document.getElementById("bill-items-tbody");
    tbody.innerHTML = "";

    if (data.items && data.items.length > 0) {
        data.items.forEach(item => {
            appendBillRow(item.item_name || "", item.quantity || "1", item.rate || 0, item.total_price || 0);
        });
    } else {
        appendBillRow("साखर", "1 kg", 44, 44);
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
        const rate = parseFloat(row.querySelector(".item-rate").value) || 0;
        
        // Extract numeric quantity
        const numMatch = qtyStr.match(/[\d.]+/);
        const qtyNum = numMatch ? parseFloat(numMatch[0]) : 1;
        const total = qtyNum * rate;

        row.querySelector(".item-total").innerText = total.toFixed(2);
        grandTotal += total;
    });

    document.getElementById("bill-grand-total").innerText = `₹${grandTotal.toFixed(2)}`;
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

        loadDashboardMetrics();
        loadReceiptsLedger();
        alert("✅ पावती यशस्वीरित्या डिजिटल लेजरमध्ये सेव्ह झाली!");
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
    document.getElementById("receipt-shop-name").innerText = bill.vendor_name;
    document.getElementById("receipt-bill-no").innerText = `#VL-${Math.floor(100 + Math.random() * 900)}`;
    document.getElementById("receipt-print-date").innerText = bill.date;
    document.getElementById("receipt-print-total").innerText = `₹${bill.grand_total.toFixed(2)}`;

    // Build items HTML
    const container = document.getElementById("receipt-print-items");
    container.innerHTML = "";
    bill.items.forEach(i => {
        const div = document.createElement("div");
        div.className = "row-flex";
        div.style.marginBottom = "3px";
        div.innerHTML = `
            <span style="flex: 2; text-align: left;">${escapeHtml(i.item_name)}</span>
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
        const res = await apiCall("/api/khata");
        if (!res.ok) return;
        const data = await res.json();
        state.allKhata = data;

        // Update KPIs
        document.getElementById("khata-kpi-customers").innerText = data.customers.length;
        document.getElementById("khata-kpi-txns").innerText = data.transactions.length;

        renderKhataCards(data.customers);
        renderKhataTable(data.transactions);
    } catch (e) {
        console.error("Khata load error:", e);
    }
}

function renderKhataCards(customers) {
    const grid = document.getElementById("khata-customers-grid");
    grid.innerHTML = "";

    if (!customers || customers.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 30px;">कोणतेही उधारी खाते सापडले नाही. नवीन खाते जोडा.</div>`;
        return;
    }

    customers.forEach(c => {
        const isDebt = c.balance > 0;
        const card = document.createElement("div");
        card.className = `glass-card ${isDebt ? 'accent-red' : 'accent-green'}`;

        const safePhone = c.phone.replace(/\D/g, "");
        const waMsg = encodeURIComponent(
            `नमस्कार ${c.name} जी! आपल्याकडे किराणा दुकानाचे एकूण ₹${c.balance.toFixed(2)} उधारीचे येणे बाकी आहे. कृपया लवकरात लवकर भरणा करावा. धन्यवाद!`
        );
        const waLink = `https://wa.me/91${safePhone}?text=${waMsg}`;

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #fff;">${escapeHtml(c.name)}</div>
                    <div style="font-size: 0.78rem; color: var(--text-slate);">📞 ${escapeHtml(c.phone || "नंबर नाही")}</div>
                </div>
                <span class="user-role-badge ${isDebt ? 'badge-staff' : 'badge-admin'}">
                    ${isDebt ? 'उधारी बाकी' : 'हिशोब क्लिअर'}
                </span>
            </div>

            <div style="margin: 12px 0;">
                <div style="font-size: 0.75rem; color: var(--text-slate);">सध्याची बाकी रक्कम (Balance):</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: ${isDebt ? 'var(--neon-red)' : 'var(--neon-green)'};">
                    ₹${Math.abs(c.balance).toFixed(2)}
                </div>
            </div>

            <div style="display: flex; gap: 8px; margin-top: 12px;">
                ${isDebt && safePhone ? `
                    <a href="${waLink}" target="_blank" class="btn-cyber whatsapp" style="flex: 1; font-size: 0.78rem; padding: 6px 10px; text-decoration: none;">
                        💬 WhatsApp तगादा
                    </a>
                ` : ''}
                <button class="btn-pill btn-lang" onclick="prefillKhataPayment('${escapeHtml(c.name)}', '${escapeHtml(c.phone)}')">
                    + व्यवहार
                </button>
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
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">#${t.id}</td>
            <td style="font-weight: 700; color: #fff;">${escapeHtml(t.customer_name)}</td>
            <td style="color: var(--text-slate);">${escapeHtml(t.phone)}</td>
            <td>
                <span class="user-role-badge ${isCredit ? 'badge-staff' : 'badge-admin'}">
                    ${isCredit ? 'उधारी दिली' : 'जमा केले'}
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
        await apiCall(`/api/khata/${id}`, { method: "DELETE" });
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

        const tbody = document.getElementById("inventory-table-tbody");
        tbody.innerHTML = "";

        let lowStockItems = [];

        data.forEach(item => {
            const isLow = item.stock_qty <= item.alert_limit;
            if (isLow) lowStockItems.push(`${item.item_name} (${item.stock_qty} ${item.unit})`);

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="font-weight: 700; color: #fff;">${escapeHtml(item.item_name)}</td>
                <td style="font-weight: 800; color: ${isLow ? 'var(--neon-red)' : 'var(--neon-cyan)'};">
                    ${item.stock_qty} ${escapeHtml(item.unit)}
                </td>
                <td>₹${Number(item.selling_price).toFixed(2)}</td>
                <td>
                    <span class="user-role-badge ${isLow ? 'badge-staff' : 'badge-admin'}">
                        ${isLow ? 'कमी साठा' : 'उपलब्ध'}
                    </span>
                </td>
                <td>
                    <button onclick="deleteInventoryItem(${item.id})" style="background: none; border: none; color: var(--neon-red); cursor: pointer;">✕</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Banner visibility
        const banner = document.getElementById("low-stock-banner");
        if (lowStockItems.length > 0) {
            banner.style.display = "flex";
            document.getElementById("low-stock-items-text").innerText = `साठा कमी: ${lowStockItems.join(', ')}`;
        } else {
            banner.style.display = "none";
        }
    } catch (e) {
        console.error("Inventory error:", e);
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
        const res = await apiCall("/api/expenses");
        if (!res.ok) return;
        const data = await res.json();
        state.allExpenses = data;

        const tbody = document.getElementById("expenses-table-tbody");
        tbody.innerHTML = "";

        data.forEach(exp => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="font-weight: 700; color: #fff;">${escapeHtml(exp.expense_title)}</td>
                <td style="color: var(--text-slate);">${escapeHtml(exp.category)}</td>
                <td style="font-weight: 800; color: var(--neon-red);">₹${Number(exp.amount).toFixed(2)}</td>
                <td style="font-size: 0.78rem;">${exp.date}</td>
            `;
            tbody.appendChild(tr);
        });
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
        const res = await apiCall("/api/receipts");
        if (!res.ok) return;
        const data = await res.json();
        state.allReceipts = data;
        renderLedgerTable(data);
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
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--neon-cyan);">#VL-${r.id}</td>
            <td style="font-weight: 700; color: #fff;">${escapeHtml(r.vendor_name || 'किराणा स्टोअर')}</td>
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
        await apiCall(`/api/receipts/${id}`, { method: "DELETE" });
        loadReceiptsLedger();
        loadDashboardMetrics();
    } catch (e) {
        alert("एरर: " + e.message);
    }
}

function exportLedgerCSV() {
    if (!state.allReceipts || state.allReceipts.length === 0) {
        alert("एक्सपोर्ट करण्यासाठी पावत्या उपलब्ध नाहीत.");
        return;
    }

    let csvContent = "data:text/csv;charset=utf-8,ID,Vendor,Date,Category,GrandTotal\n";
    state.allReceipts.forEach(r => {
        const v = (r.vendor_name || "").replace(/"/g, '""');
        csvContent += `${r.id},"${v}",${r.date},"${r.category || 'General'}",${r.grand_total}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `VernaLedger_Receipts_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// -----------------------------------------------------------------------------
// NEURAL AI STUDIO (RAG ENGINE QUERY)
// -----------------------------------------------------------------------------
function askAiPrompt(text) {
    document.getElementById("ai-user-input").value = text;
    submitAiChat();
}

async function submitAiChat() {
    const input = document.getElementById("ai-user-input");
    const msg = input.value.trim();
    if (!msg) return;

    input.value = "";
    const historyContainer = document.getElementById("ai-chat-history");

    // Add User Bubble
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble chat-user";
    userBubble.innerText = msg;
    historyContainer.appendChild(userBubble);
    historyContainer.scrollTop = historyContainer.scrollHeight;

    // Add AI Typing Bubble
    const aiBubble = document.createElement("div");
    aiBubble.className = "chat-bubble chat-ai";
    aiBubble.innerHTML = `<span style="animation: pulseDot 1s infinite;">विचार करत आहे... 🤖</span>`;
    historyContainer.appendChild(aiBubble);
    historyContainer.scrollTop = historyContainer.scrollHeight;

    try {
        const res = await apiCall("/api/rag-chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg, lang: state.lang })
        });
        const data = await res.json();

        const formatted = (data.answer || "माफ करा, उत्तर मिळू शकले नाही.")
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        aiBubble.innerHTML = `
            <div>${formatted}</div>
            <div style="margin-top: 8px;">
                <button class="btn-pill" style="font-size: 0.7rem; background: rgba(176,38,255,0.15); color: var(--neon-purple); border-color: rgba(176,38,255,0.4);" onclick="speakText('${encodeURIComponent(data.answer)}')">
                    🔊 ऐका
                </button>
            </div>
        `;
    } catch (e) {
        aiBubble.innerHTML = `एरर: सर्व्हरशी संपर्क होऊ शकला नाही.`;
    } finally {
        historyContainer.scrollTop = historyContainer.scrollHeight;
    }
}

async function speakText(encoded) {
    const raw = decodeURIComponent(encoded);
    try {
        const res = await apiCall("/api/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: raw, voice: "mr-IN-AarohiNeural" })
        });
        const data = await res.json();
        if (data.audio_data) {
            new Audio(data.audio_data).play();
        }
    } catch (e) {
        const ut = new SpeechSynthesisUtterance(raw);
        ut.lang = "mr-IN";
        window.speechSynthesis.speak(ut);
    }
}

// -----------------------------------------------------------------------------
// STAFF & AUDIT LOGS
// -----------------------------------------------------------------------------
async function loadStaffData() {
    try {
        const res = await apiCall("/api/users");
        if (!res.ok) return;
        const users = await res.json();

        const tbody = document.getElementById("staff-table-tbody");
        tbody.innerHTML = "";

        users.forEach(u => {
            const isAdmin = u.role === "Admin";
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="font-weight: 700; color: #fff;">${escapeHtml(u.username)}</td>
                <td>
                    <span class="user-role-badge ${isAdmin ? 'badge-admin' : 'badge-staff'}">
                        ${u.role}
                    </span>
                </td>
                <td style="color: var(--text-slate);">${escapeHtml(u.phone || '-')}</td>
                <td>
                    ${!isAdmin ? `
                        <button onclick="deleteStaffUser('${escapeHtml(u.username)}')" style="background: none; border: none; color: var(--neon-red); cursor: pointer;">
                            ✕ डिलीट
                        </button>
                    ` : '<span style="font-size: 0.72rem; color: var(--text-dim);">संरक्षित</span>'}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Staff load error:", e);
    }
}

function openAddStaffModal() {
    document.getElementById("modal-add-staff").classList.add("active");
}

async function submitAddStaff(e) {
    e.preventDefault();
    const payload = {
        username: document.getElementById("staff-input-user").value.trim(),
        password: document.getElementById("staff-input-pass").value.trim(),
        role: document.getElementById("staff-input-role").value,
        phone: document.getElementById("staff-input-phone").value.trim()
    };

    try {
        const res = await apiCall("/api/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || "कर्मचारी तयार करता आला नाही.");

        closeModal("modal-add-staff");
        document.getElementById("form-add-staff").reset();
        loadStaffData();
        alert("✅ कर्मचारी खाते यशस्वीरित्या तयार झाले!");
    } catch (err) {
        alert("एरर: " + err.message);
    }
}

async function deleteStaffUser(username) {
    if (!confirm(`वापरकर्ता '${username}' डिलीट करायचा का?`)) return;
    try {
        const res = await apiCall(`/api/users/${username}`, { method: "DELETE" });
        if (!res.ok) {
            const j = await res.json();
            throw new Error(j.detail || "डिलीट करता आले नाही");
        }
        loadStaffData();
    } catch (e) {
        alert("एरर: " + e.message);
    }
}

// -----------------------------------------------------------------------------
// MODALS & HELPERS
// -----------------------------------------------------------------------------
function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("active");
}

function toggleLanguage() {
    state.lang = state.lang === "mr" ? "en" : "mr";
    localStorage.setItem("verna_lang", state.lang);
    applyLanguage();
}

function applyLanguage() {
    const isMr = state.lang === "mr";
    const label = isMr ? "🌐 मराठी" : "🌐 English";
    
    const mBtn = document.getElementById("mobile-lang-btn");
    if (mBtn) mBtn.innerText = label;
    const dBtn = document.getElementById("desktop-lang-btn");
    if (dBtn) dBtn.innerText = isMr ? "🌐 मराठी / EN" : "🌐 English / MR";
    const hBtn = document.getElementById("hud-lang-btn");
    if (hBtn) hBtn.innerText = label;

    // Apply i18n data tags
    const dict = i18n[state.lang] || i18n.mr;
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key]) el.innerText = dict[key];
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

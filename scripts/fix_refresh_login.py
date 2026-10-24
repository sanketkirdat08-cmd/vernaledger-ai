import re, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix recalcBillTotal
old_recalc = """function recalcBillTotal() {
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
}"""

new_recalc = """function recalcBillTotal() {
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
}"""

# 2. Fix getCurrentBillData
old_current_bill = """function getCurrentBillData() {
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
}"""

new_current_bill = """function getCurrentBillData() {
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
}"""

# 3. Fix DOMContentLoaded & showApp
old_dom_block = """    // Check stored user session
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
    }"""

new_dom_block = """    // Check stored user session with resilient parsing
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
    }"""

old_show_app = """function showApp() {
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
}"""

new_show_app = """function showApp() {
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
}"""

def normalize(s):
    return s.replace('\r\n', '\n')

code_norm = normalize(code)
old_recalc_norm = normalize(old_recalc)
new_recalc_norm = normalize(new_recalc)

old_current_bill_norm = normalize(old_current_bill)
new_current_bill_norm = normalize(new_current_bill)

old_dom_block_norm = normalize(old_dom_block)
new_dom_block_norm = normalize(new_dom_block)

old_show_app_norm = normalize(old_show_app)
new_show_app_norm = normalize(new_show_app)

if old_recalc_norm in code_norm:
    code_norm = code_norm.replace(old_recalc_norm, new_recalc_norm)
    print("Fixed recalcBillTotal successfully!")
else:
    print("Warning: old_recalc not found.")

if old_current_bill_norm in code_norm:
    code_norm = code_norm.replace(old_current_bill_norm, new_current_bill_norm)
    print("Fixed getCurrentBillData successfully!")
else:
    print("Warning: old_current_bill not found.")

if old_dom_block_norm in code_norm:
    code_norm = code_norm.replace(old_dom_block_norm, new_dom_block_norm)
    print("Fixed DOMContentLoaded session check successfully!")
else:
    print("Warning: old_dom_block not found.")

if old_show_app_norm in code_norm:
    code_norm = code_norm.replace(old_show_app_norm, new_show_app_norm)
    print("Fixed showApp successfully!")
else:
    print("Warning: old_show_app not found.")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(code_norm)

with open('public/app.js', 'w', encoding='utf-8') as f:
    f.write(code_norm)

print("Saved app.js and public/app.js")

import os

def update_app_js(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Update VernaStorage methods
    old_storage_remove = '''    removeReceipt(id) {
        const list = this.get(this.KEY_RECEIPTS).filter(r => r.id !== id);
        this.save(this.KEY_RECEIPTS, list);
    },'''

    new_storage_remove = '''    removeReceipt(id) {
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
    },'''

    if old_storage_remove in c:
        c = c.replace(old_storage_remove, new_storage_remove)
    elif "removeReceipts(ids)" not in c:
        print(f"Warning: old_storage_remove not found in {filepath}")

    # 2. Add i18n keys to mr
    mr_target = 'btn_cancel: "रद्द करा",'
    mr_add = '''btn_cancel: "रद्द करा",
        btn_delete_selected: "निवडलेल्या डिलीट करा",
        btn_clear_all_ledger: "⚠️ सर्व रिकामे करा",
        lbl_selected_receipts: "निवडलेल्या:",
        lbl_total_receipts: "एकूण पावत्या:",
        confirm_bulk_delete: "तुम्हाला निवडलेल्या {n} पावत्या लेजरमधून कायमच्या डिलीट करायच्या आहेत का?",
        confirm_clear_all: "⚠️ सावधान! तुम्हाला लेजरमधील सर्व पावत्या कायमच्या डिलीट करायच्या आहेत का? ही कृती पूर्ववत करता येणार नाही!",
        msg_bulk_delete_success: "✅ निवडलेल्या {n} पावत्या यशस्वीरीत्या डिलीट केल्या!",
        msg_clear_all_success: "✅ सर्व पावत्या लेजरमधून यशस्वीरीत्या डिलीट केल्या!",
        no_receipts_selected: "कृपया आधी किमान एक पावती निवडा!",
        empty_ledger: "कोणतीही पावती उपलब्ध नाही.",'''

    if mr_target in c and "btn_delete_selected" not in c:
        c = c.replace(mr_target, mr_add)

    # 3. Add i18n keys to en
    en_target = 'btn_cancel: "Cancel",'
    en_add = '''btn_cancel: "Cancel",
        btn_delete_selected: "Delete Selected",
        btn_clear_all_ledger: "⚠️ Clear All",
        lbl_selected_receipts: "Selected:",
        lbl_total_receipts: "Total Receipts:",
        confirm_bulk_delete: "Are you sure you want to permanently delete {n} selected receipts from the ledger?",
        confirm_clear_all: "⚠️ Warning! Are you sure you want to delete ALL receipts from the ledger? This action cannot be undone!",
        msg_bulk_delete_success: "✅ Successfully deleted {n} selected receipts!",
        msg_clear_all_success: "✅ Successfully cleared all receipts from ledger!",
        no_receipts_selected: "Please select at least one receipt first!",
        empty_ledger: "No receipts available in ledger.",'''

    if en_target in c and 'btn_delete_selected: "Delete Selected"' not in c:
        c = c.replace(en_target, en_add)

    # 4. Add i18n keys to hi
    hi_target = 'btn_cancel: "रद्द करें",'
    hi_add = '''btn_cancel: "रद्द करें",
        btn_delete_selected: "चुनी गई डिलीट करें",
        btn_clear_all_ledger: "⚠️ सब डिलीट करें",
        lbl_selected_receipts: "चुनी गई:",
        lbl_total_receipts: "कुल रसीदें:",
        confirm_bulk_delete: "क्या आप चुनी गई {n} रसीदें लेजर से स्थायी रूप से हटाना चाहते हैं?",
        confirm_clear_all: "⚠️ चेतावनी! क्या आप लेजर से सभी रसीदें स्थायी रूप से हटाना चाहते हैं? यह क्रिया पूर्ववत नहीं की जा सकती!",
        msg_bulk_delete_success: "✅ चुनी गई {n} रसीदें सफलतापूर्वक डिलीट कर दी गईं!",
        msg_clear_all_success: "✅ सभी रसीदें लेजर से सफलतापूर्वक हटा दी गईं!",
        no_receipts_selected: "कृपया पहले कम से कम एक रसीद चुनें!",
        empty_ledger: "लेजर में कोई रसीद उपलब्ध नहीं है।",'''

    if hi_target in c and 'btn_delete_selected: "चुनी गई डिलीट करें"' not in c:
        c = c.replace(hi_target, hi_add)

    # 5. Update renderLedgerTable and add bulk delete controller functions
    old_render = '''function renderLedgerTable(receipts) {
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
}'''

    new_render = '''function renderLedgerTable(receipts) {
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
}'''

    c = c.replace(old_render.replace('\r\n', '\n'), new_render.replace('\r\n', '\n'))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"Updated {filepath} with Ledger multi-select and bulk deletion!")

update_app_js("app.js")
update_app_js(os.path.join("public", "app.js"))

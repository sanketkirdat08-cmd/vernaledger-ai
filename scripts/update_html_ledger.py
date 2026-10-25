import os

old_ledger_html = '''            <section id="view-ledger" class="view-section">
                <div class="glass-card" style="margin-bottom: 20px;">
                    <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: space-between; align-items: center;">
                        <input type="text" id="ledger-search-input" class="input-cyber" data-i18n-ph="ph_ledger_search" placeholder="🔍 पावती क्रमांक, विक्रेता किंवा कॅटेगरी शोधा..." style="max-width: 400px;" oninput="filterLedgerList()">
                        <div>
                            <button class="btn-cyber" id="btn-ledger-excel-export" onclick="downloadExcelReport()" style="background: linear-gradient(135deg, #15803d, #16a34a) !important; color: #ffffff !important; border: 2px solid #22c55e !important; font-weight: 800; padding: 9px 20px; font-size: 0.95rem; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 16px rgba(34, 197, 94, 0.5);">
                                📗 <span data-i18n="btn_export_excel">Excel (.xlsx) संपूर्ण डेटा डाऊनलोड</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="glass-card">
                    <h3 style="font-size: 1.1rem; font-weight: 800; color: var(--text-white); margin-bottom: 14px;" data-i18n="title_ledger_table">
                        📜 सर्व सेव्ह केलेल्या पावत्या (Ledger Audit Table)
                    </h3>
                    <div class="table-responsive">
                        <table class="cyber-table">
                            <thead>
                                <tr>
                                    <th data-i18n="th_rec_id">पावती क्र.</th>
                                    <th data-i18n="th_rec_vendor">विक्रेता / ग्राहक</th>
                                    <th data-i18n="th_rec_date">तारीख</th>
                                    <th data-i18n="th_exp_category">प्रवर्ग</th>
                                    <th data-i18n="th_rec_total">एकूण रक्कम (₹)</th>
                                    <th data-i18n="th_rec_action">कृती</th>
                                </tr>
                            </thead>
                            <tbody id="ledger-table-tbody">
                                <!-- Dynamic rows -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>'''

new_ledger_html = '''            <section id="view-ledger" class="view-section">
                <div class="glass-card" style="margin-bottom: 20px;">
                    <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: space-between; align-items: center;">
                        <input type="text" id="ledger-search-input" class="input-cyber" data-i18n-ph="ph_ledger_search" placeholder="🔍 पावती क्रमांक, विक्रेता किंवा कॅटेगरी शोधा..." style="max-width: 380px; flex: 1 1 280px;" oninput="filterLedgerList()">
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                            <!-- Bulk Delete Button (Visible when 1 or more receipts checked) -->
                            <button class="btn-cyber danger" id="btn-ledger-bulk-delete" onclick="bulkDeleteSelectedReceipts()" style="display: none; padding: 9px 16px; font-weight: 700; font-size: 0.88rem; align-items: center; gap: 6px; border-radius: 8px; box-shadow: 0 0 15px rgba(255, 0, 85, 0.4); animation: pulseDanger 1.8s infinite;">
                                🗑️ <span id="lbl-bulk-delete" data-i18n="btn_delete_selected">निवडलेल्या डिलीट करा</span> (<span id="ledger-selected-count">0</span>)
                            </button>

                            <!-- Clear Entire Ledger Button -->
                            <button class="btn-pill" id="btn-ledger-clear-all" onclick="clearEntireLedger()" style="background: rgba(255, 0, 85, 0.1); color: var(--neon-red); border: 1px solid rgba(255, 0, 85, 0.35); padding: 8px 14px; font-size: 0.82rem; font-weight: 700; cursor: pointer;" title="सर्व पावत्या डिलीट करा" data-i18n="btn_clear_all_ledger">
                                ⚠️ सर्व रिकामे करा
                            </button>

                            <!-- Native Excel Export Button -->
                            <button class="btn-cyber" id="btn-ledger-excel-export" onclick="downloadExcelReport()" style="background: linear-gradient(135deg, #15803d, #16a34a) !important; color: #ffffff !important; border: 2px solid #22c55e !important; font-weight: 800; padding: 9px 20px; font-size: 0.95rem; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 16px rgba(34, 197, 94, 0.5);">
                                📗 <span data-i18n="btn_export_excel">Excel (.xlsx) संपूर्ण डेटा डाऊनलोड</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
                        <h3 style="font-size: 1.1rem; font-weight: 800; color: var(--text-white); margin: 0;" data-i18n="title_ledger_table">
                            📜 सर्व सेव्ह केलेल्या पावत्या (Ledger Audit Table)
                        </h3>
                        <div id="ledger-selection-stats" style="font-size: 0.82rem; color: var(--text-slate); display: flex; align-items: center; gap: 12px;">
                            <span><span data-i18n="lbl_total_receipts">एकूण पावत्या:</span> <strong id="ledger-total-count" style="color: var(--neon-cyan);">0</strong></span>
                            <span id="ledger-selected-stats-pill" style="display: none; background: rgba(0, 242, 254, 0.12); padding: 3px 9px; border-radius: 6px; border: 1px solid rgba(0, 242, 254, 0.3); color: var(--neon-cyan); font-weight: 700;">
                                <span data-i18n="lbl_selected_receipts">निवडलेल्या:</span> <span id="ledger-selected-num">0</span>
                            </span>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="cyber-table">
                            <thead>
                                <tr>
                                    <th style="width: 44px; text-align: center;">
                                        <input type="checkbox" id="ledger-select-all" class="cyber-checkbox" onchange="toggleSelectAllReceipts(this)" title="सर्व निवडा">
                                    </th>
                                    <th data-i18n="th_rec_id">पावती क्र.</th>
                                    <th data-i18n="th_rec_vendor">विक्रेता / ग्राहक</th>
                                    <th data-i18n="th_rec_date">तारीख</th>
                                    <th data-i18n="th_exp_category">प्रवर्ग</th>
                                    <th data-i18n="th_rec_total">एकूण रक्कम (₹)</th>
                                    <th data-i18n="th_rec_action">कृती</th>
                                </tr>
                            </thead>
                            <tbody id="ledger-table-tbody">
                                <!-- Dynamic rows -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>'''

for path in ["index.html", os.path.join("public", "index.html")]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        c = c.replace(old_ledger_html.replace('\r\n', '\n'), new_ledger_html.replace('\r\n', '\n'))
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Updated {path}")

print("HTML ledger views updated!")


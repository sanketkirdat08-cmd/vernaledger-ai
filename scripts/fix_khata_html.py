import os

# 1. Update index.html and public/index.html
def update_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        c = f.read()

    # Replace KPI 4 icon
    old_kpi4 = '''                    <div class="glass-card accent-amber">
                        <div class="kpi-title">
                            <span data-i18n="kpi_total_tx">एकूण व्यवहार</span>
                            <span>📝</span>
                        </div>
                        <div class="kpi-val" style="color: var(--neon-amber);" id="khata-kpi-txns">0</div>
                    </div>'''
    
    new_kpi4 = '''                    <div class="glass-card accent-amber">
                        <div class="kpi-title">
                            <span data-i18n="kpi_total_tx">एकूण व्यवहार</span>
                            <span>📊</span>
                        </div>
                        <div class="kpi-val" style="color: var(--neon-amber);" id="khata-kpi-txns">0</div>
                    </div>'''

    if old_kpi4 in c:
        c = c.replace(old_kpi4, new_kpi4)

    # Add filter pills inside Customer Khata Controls glass card
    old_controls = '''                <!-- Customer Khata Controls -->
                <div class="glass-card" style="margin-bottom: 20px;">
                    <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: space-between; align-items: center;">
                        <input type="text" id="khata-search-input" class="input-cyber" data-i18n-ph="ph_khata_search" placeholder="🔍 ग्राहकाचे नाव किंवा मोबाईल नंबर शोधा..." style="max-width: 380px;" oninput="filterKhataList()">
                        <button class="btn-cyber success" onclick="openAddKhataModal()">
                            <span data-i18n="btn_add_khata_tx">+ नवीन व्यवहार</span>
                        </button>
                    </div>
                </div>'''

    new_controls = '''                <!-- Customer Khata Controls & Filter Tabs -->
                <div class="glass-card" style="margin-bottom: 20px;">
                    <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <input type="text" id="khata-search-input" class="input-cyber" data-i18n-ph="ph_khata_search" placeholder="🔍 ग्राहकाचे नाव किंवा मोबाईल नंबर शोधा..." style="max-width: 380px; flex: 1 1 260px;" oninput="filterKhataList()">
                        <button class="btn-cyber success" onclick="openAddKhataModal()">
                            <span data-i18n="btn_add_khata_tx">+ नवीन व्यवहार</span>
                        </button>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px;">
                        <span style="font-size: 0.74rem; color: var(--text-slate); font-weight: 700;" data-i18n="lbl_filter_cust">फिल्टर:</span>
                        <button class="khata-filter-pill active" id="filter-pill-all" onclick="setKhataFilter('all')">
                            🔘 <span data-i18n="filter_all_cust">सर्व ग्राहक</span> (<span id="count-all-cust">0</span>)
                        </button>
                        <button class="khata-filter-pill" id="filter-pill-pending" onclick="setKhataFilter('pending')">
                            🔴 <span data-i18n="filter_pending_cust">उधारी बाकी</span> (<span id="count-pending-cust">0</span>)
                        </button>
                        <button class="khata-filter-pill" id="filter-pill-cleared" onclick="setKhataFilter('cleared')">
                            🟢 <span data-i18n="filter_cleared_cust">हिशोब क्लिअर</span> (<span id="count-cleared-cust">0</span>)
                        </button>
                    </div>
                </div>'''

    c = c.replace(old_controls.replace('\r\n', '\n'), new_controls.replace('\r\n', '\n'))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"Updated {filepath}")

update_html("index.html")
update_html(os.path.join("public", "index.html"))


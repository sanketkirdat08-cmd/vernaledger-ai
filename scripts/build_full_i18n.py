import os, sys, re, json

sys.stdout.reconfigure(encoding='utf-8')

from translations_master import TRANSLATIONS

print(f"Loaded {len(TRANSLATIONS)} translation keys from master.")

# Build dictionary JS object
mr_dict = {}
en_dict = {}
hi_dict = {}

for k, v in TRANSLATIONS.items():
    mr_dict[k] = v.get("mr", "")
    en_dict[k] = v.get("en", "")
    hi_dict[k] = v.get("hi", "")

# Load existing index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Apply targeted replacements to ensure all elements have data-i18n / data-i18n-ph / data-i18n-title
replacements = [
    # Subtitle
    (
        '<p style="font-size: 0.88rem; color: #cbd5e1; margin: 12px 0 20px 0;">\n                भारतीय व्यापाऱ्यांसाठी व्हर्नाक्युलर AI डिजिटल लेजर व बिलिंग प्रणाली\n            </p>',
        '<p style="font-size: 0.88rem; color: #cbd5e1; margin: 12px 0 20px 0;" data-i18n="login_subtitle">\n                भारतीय व्यापाऱ्यांसाठी व्हर्नाक्युलर AI डिजिटल लेजर व बिलिंग प्रणाली\n            </p>'
    ),
    # Labels
    (
        '<label style="font-size: 0.76rem; font-weight: 700; color: var(--text-slate); text-transform: uppercase;">वापरकर्ता नाव (Username)</label>',
        '<label style="font-size: 0.76rem; font-weight: 700; color: var(--text-slate); text-transform: uppercase;" data-i18n="lbl_username">वापरकर्ता नाव (Username)</label>'
    ),
    (
        '<label style="font-size: 0.76rem; font-weight: 700; color: var(--text-slate); text-transform: uppercase;">पासवर्ड (Password)</label>',
        '<label style="font-size: 0.76rem; font-weight: 700; color: var(--text-slate); text-transform: uppercase;" data-i18n="lbl_password">पासवर्ड (Password)</label>'
    ),
    (
        '🚀 सिस्टममध्ये प्रवेश करा (Login)\n                </button>',
        '<span data-i18n="btn_login">🚀 सिस्टममध्ये प्रवेश करा (Login)</span>\n                </button>'
    ),
    (
        '<p style="font-size: 0.74rem; color: var(--text-dim); margin-bottom: 8px;">झटपट डेमो क्रेडेंशियल्स (Quick Access):</p>',
        '<p style="font-size: 0.74rem; color: var(--text-dim); margin-bottom: 8px;" data-i18n="login_demo_hint">झटपट डेमो क्रेडेंशियल्स (Quick Access):</p>'
    ),
    # HUD title & theme label
    (
        '<h2 id="hud-title">⚡ स्मार्ट स्कॅनर व व्हॉइस बिलिंग</h2>',
        '<h2 id="hud-title" data-i18n="hud_title_scanner">⚡ स्मार्ट स्कॅनर व व्हॉइस बिलिंग</h2>'
    ),
    (
        '<span id="hud-theme-label">किराणा मोड</span>',
        '<span id="hud-theme-label" data-i18n="theme_kirana_mode">किराणा मोड</span>'
    ),
    # Digital Receipt Preview Card Header
    (
        '<h3 style="font-size: 1.1rem; font-weight: 800; color: var(--text-white); display: flex; align-items: center; gap: 8px;">\n                                <span>🧾</span> डिजिटल पावती प्रिव्ह्यू\n                            </h3>',
        '<h3 style="font-size: 1.1rem; font-weight: 800; color: var(--text-white); display: flex; align-items: center; gap: 8px;">\n                                <span>🧾</span> <span data-i18n="card_live_preview">डिजिटल पावती प्रिव्ह्यू</span>\n                            </h3>'
    ),
    (
        '<span class="user-role-badge badge-admin" id="bill-badge-status">READY</span>',
        '<span class="user-role-badge badge-admin" id="bill-badge-status" data-i18n="receipt_preview_ready">READY</span>'
    ),
    # Vendor input placeholder
    (
        '<input type="text" id="bill-vendor-name" class="input-cyber" placeholder="दुकान / विक्रेत्याचे नाव" value="">',
        '<input type="text" id="bill-vendor-name" class="input-cyber" placeholder="दुकान / विक्रेत्याचे नाव" data-i18n-ph="ph_vendor" value="">'
    ),
    # Empty bill placeholder
    (
        '<td colspan="5" style="text-align: center; color: var(--text-slate); padding: 24px 10px; font-size: 0.82rem;">\n                                            📸 पावती स्कॅन करा किंवा 🎙️ व्हॉइस बोला — वस्तू व हिशोब येथे आपोआप दिसेल.\n                                        </td>',
        '<td colspan="5" style="text-align: center; color: var(--text-slate); padding: 24px 10px; font-size: 0.82rem;" data-i18n="empty_bill_placeholder">\n                                            📸 पावती स्कॅन करा किंवा 🎙️ व्हॉइस बोला — वस्तू व हिशोब येथे आपोआप दिसेल.\n                                        </td>'
    ),
    # Khata KPIs
    (
        '<span>एकूण बाकी उधारी</span>',
        '<span data-i18n="kpi_pending_udhar">एकूण बाकी उधारी</span>'
    ),
    (
        '<span>जमा झालेली रक्कम</span>',
        '<span data-i18n="kpi_collected_amt">जमा झालेली रक्कम</span>'
    ),
    (
        '<span>नोंदणीकृत ग्राहक</span>',
        '<span data-i18n="kpi_registered_cust">नोंदणीकृत ग्राहक</span>'
    ),
    (
        '<span>एकूण व्यवहार</span>',
        '<span data-i18n="kpi_total_tx">एकूण व्यवहार</span>'
    ),
    (
        '<input type="text" id="khata-search-input" class="input-cyber" placeholder="🔍 ग्राहकाचे नाव किंवा मोबाईल नंबर शोधा..." style="max-width: 380px;" oninput="filterKhataList()">',
        '<input type="text" id="khata-search-input" class="input-cyber" data-i18n-ph="ph_khata_search" placeholder="🔍 ग्राहकाचे नाव किंवा मोबाईल नंबर शोधा..." style="max-width: 380px;" oninput="filterKhataList()">'
    ),
    (
        '<button class="btn-cyber success" onclick="openAddKhataModal()">\n                            <span data-i18n="btn_new_customer">+ नवीन खाते</span> / व्यवहार जोडा\n                        </button>',
        '<button class="btn-cyber success" onclick="openAddKhataModal()">\n                            <span data-i18n="btn_add_khata_tx">+ नवीन व्यवहार</span>\n                        </button>'
    ),
    (
        '<h3 style="font-size: 1.05rem; font-weight: 800; color: var(--text-white); margin-bottom: 14px;">\n                        📜 संपूर्ण खाते व्यवहार इतिहास (Transaction Audit)\n                    </h3>',
        '<h3 style="font-size: 1.05rem; font-weight: 800; color: var(--text-white); margin-bottom: 14px;" data-i18n="title_khata_audit">\n                        📜 संपूर्ण खाते व्यवहार इतिहास (Transaction Audit)\n                    </h3>'
    ),
    # Khata Table Headers
    (
        '<th>ग्राहक नाव</th>\n                                    <th>मोबाईल</th>\n                                    <th>प्रकार</th>\n                                    <th>रक्कम (₹)</th>\n                                    <th>तारीख</th>\n                                    <th>देय तारीख</th>\n                                    <th>कृती</th>',
        '<th data-i18n="th_customer">ग्राहक नाव</th>\n                                    <th data-i18n="th_phone">मोबाईल</th>\n                                    <th data-i18n="th_type">प्रकार</th>\n                                    <th data-i18n="th_amount">रक्कम (₹)</th>\n                                    <th data-i18n="lbl_date">तारीख</th>\n                                    <th data-i18n="th_due_date">देय तारीख</th>\n                                    <th data-i18n="th_action">कृती</th>'
    ),
    # Inventory Table Headers
    (
        '<th>वस्तू नाव</th>\n                                        <th>साठा</th>\n                                        <th>किंमत (₹)</th>\n                                        <th>स्थिती</th>',
        '<th data-i18n="th_inv_item">वस्तू नाव</th>\n                                        <th data-i18n="th_inv_stock">साठा</th>\n                                        <th data-i18n="th_inv_price">किंमत (₹)</th>\n                                        <th data-i18n="th_inv_status">स्थिती</th>'
    ),
    (
        '<span style="font-size: 0.74rem; color: #fca5a5; margin-left: 4px;" id="low-stock-items-text">काही वस्तूंचा साठा संपत आला आहे.</span>',
        '<span style="font-size: 0.74rem; color: #fca5a5; margin-left: 4px;" id="low-stock-items-text" data-i18n="low_stock_banner">काही वस्तूंचा साठा संपत आला आहे.</span>'
    ),
    # Expenses Title & Form
    (
        '<span>📉</span> दैनंदिन बिझनेस खर्च (Expenses)',
        '<span>📉</span> <span data-i18n="title_expenses">दैनंदिन बिझनेस खर्च (Expenses)</span>'
    ),
    (
        '<input type="text" id="expense-title" class="input-cyber" placeholder="खर्चाचे नाव (उदा. लाईट बिल, वाहतूक)" required>\n                                    <input type="number" id="expense-amount" class="input-cyber" placeholder="रक्कम (₹)" required>',
        '<input type="text" id="expense-title" class="input-cyber" data-i18n-ph="ph_expense_title" placeholder="खर्चाचे नाव (उदा. लाईट बिल, वाहतूक)" required>\n                                    <input type="number" id="expense-amount" class="input-cyber" data-i18n-ph="ph_expense_amount" placeholder="रक्कम (₹)" required>'
    ),
    (
        '<option value="दुकान खर्च">दुकान खर्च (Shop)</option>\n                                        <option value="वाहतूक / हमाली">वाहतूक / हमाली (Transport)</option>\n                                        <option value="लाईट / पाणी">लाईट / पाणी (Utilities)</option>\n                                        <option value="पगार">पगार (Salary)</option>\n                                        <option value="इतर">इतर (Other)</option>',
        '<option value="दुकान खर्च" data-i18n="opt_expense_shop">दुकान खर्च (Shop)</option>\n                                        <option value="वाहतूक / हमाली" data-i18n="opt_expense_transport">वाहतूक / हमाली (Transport)</option>\n                                        <option value="लाईट / पाणी" data-i18n="opt_expense_utilities">लाईट / पाणी (Utilities)</option>\n                                        <option value="पगार" data-i18n="opt_expense_salary">पगार (Salary)</option>\n                                        <option value="इतर" data-i18n="opt_expense_other">इतर (Other)</option>'
    ),
    (
        '+ नोंद करा\n                                    </button>',
        '<span data-i18n="btn_add_expense">+ नोंद करा</span>\n                                    </button>'
    ),
    (
        '<th>खर्च</th>\n                                            <th>प्रवर्ग</th>\n                                            <th>रक्कम (₹)</th>\n                                            <th>तारीख</th>',
        '<th data-i18n="th_exp_title">खर्च</th>\n                                            <th data-i18n="th_exp_category">प्रवर्ग</th>\n                                            <th data-i18n="th_exp_amount">रक्कम (₹)</th>\n                                            <th data-i18n="th_exp_date">तारीख</th>'
    ),
    # WhatsApp Digest
    (
        '<span>📲</span> दैनिक बिझनेस रिपोर्ट (WhatsApp Digest)',
        '<span>📲</span> <span data-i18n="title_wa_digest">दैनिक बिझनेस रिपोर्ट (WhatsApp Digest)</span>'
    ),
    (
        '<p style="font-size: 0.82rem; color: var(--text-slate); margin-bottom: 14px;">\n                                आजचा संपूर्ण विक्री, उधारी वसुली आणि निव्वळ नफ्याचा अहवाल १-क्लिक मध्ये स्वतःच्या किंवा मालकाच्या WhatsApp वर पाठवा.\n                            </p>',
        '<p style="font-size: 0.82rem; color: var(--text-slate); margin-bottom: 14px;" data-i18n="desc_wa_digest">\n                                आजचा संपूर्ण विक्री, उधारी वसुली आणि निव्वळ नफ्याचा अहवाल १-क्लिक मध्ये स्वतःच्या किंवा मालकाच्या WhatsApp वर पाठवा.\n                            </p>'
    ),
    (
        '💬 WhatsApp वर दैनिक रिपोर्ट शेअर करा\n                            </button>',
        '<span data-i18n="btn_send_wa_digest">💬 WhatsApp वर दैनिक रिपोर्ट शेअर करा</span>\n                            </button>'
    ),
    # Ledger search & table
    (
        '<input type="text" id="ledger-search-input" class="input-cyber" placeholder="🔍 पावती क्रमांक, विक्रेता किंवा कॅटेगरी शोधा..." style="max-width: 400px;" oninput="filterLedgerList()">',
        '<input type="text" id="ledger-search-input" class="input-cyber" data-i18n-ph="ph_ledger_search" placeholder="🔍 पावती क्रमांक, विक्रेता किंवा कॅटेगरी शोधा..." style="max-width: 400px;" oninput="filterLedgerList()">'
    ),
    (
        '<h3 style="font-size: 1.1rem; font-weight: 800; color: var(--text-white); margin-bottom: 14px;">\n                        📚 सुरक्षित डिजिटल लेजर डेटाबेस (SQLite ACID Verified)\n                    </h3>',
        '<h3 style="font-size: 1.1rem; font-weight: 800; color: var(--text-white); margin-bottom: 14px;" data-i18n="title_ledger_table">\n                        📜 सर्व सेव्ह केलेल्या पावत्या (Ledger Audit Table)\n                    </h3>'
    ),
    (
        '<th>पावती क्र.</th>\n                                    <th>विक्रेता / ग्राहक</th>\n                                    <th>तारीख</th>\n                                    <th>प्रवर्ग</th>\n                                    <th>एकूण रक्कम (₹)</th>\n                                    <th>कृती</th>',
        '<th data-i18n="th_rec_id">पावती क्र.</th>\n                                    <th data-i18n="th_rec_vendor">विक्रेता / ग्राहक</th>\n                                    <th data-i18n="th_rec_date">तारीख</th>\n                                    <th data-i18n="th_exp_category">प्रवर्ग</th>\n                                    <th data-i18n="th_rec_total">एकूण रक्कम (₹)</th>\n                                    <th data-i18n="th_rec_action">कृती</th>'
    ),
    # AI Studio
    (
        '<button class="btn-pill btn-logout" onclick="clearAiChat()" title="संभाषण स्वच्छ करा" style="padding: 5px 12px;">\n                                🗑️ Clear\n                            </button>',
        '<button class="btn-pill btn-logout" onclick="clearAiChat()" data-i18n="btn_clear_chat" title="संभाषण स्वच्छ करा" style="padding: 5px 12px;">\n                                🗑️ Clear\n                            </button>'
    ),
    (
        '<span class="chip" onclick="askAiPrompt(\'आजची विक्री किती आहे?\')">📊 आजची विक्री</span>\n                        <span class="chip" onclick="askAiPrompt(\'एकूण बाकी उधारी किती आहे?\')">👥 बाकी उधारी</span>\n                        <span class="chip" onclick="askAiPrompt(\'कमी साठा असलेल्या वस्तू कोणत्या आहेत?\')">🚨 कमी साठा</span>',
        '<span class="chip" onclick="askAiPrompt(\'आजची विक्री किती आहे?\')" data-i18n="chip_today_sales">📊 आजची विक्री</span>\n                        <span class="chip" onclick="askAiPrompt(\'एकूण बाकी उधारी किती आहे?\')" data-i18n="chip_pending_credit">👥 बाकी उधारी</span>\n                        <span class="chip" onclick="askAiPrompt(\'कमी साठा असलेल्या वस्तू कोणत्या आहेत?\')" data-i18n="chip_low_stock">🚨 कमी साठा</span>'
    ),
    (
        '<div class="chat-bubble chat-ai">\n                                नमस्कार! मी <strong>Verna AI</strong>. दुकानातील विक्री, उधारी किंवा साठ्याबद्दल विचारा किंवा माईक दाबून बोला.\n                            </div>',
        '<div class="chat-bubble chat-ai" data-i18n="ai_greeting">\n                                नमस्कार! मी <strong>Verna AI</strong>. दुकानातील विक्री, उधारी किंवा साठ्याबद्दल विचारा किंवा माईक दाबून बोला.\n                            </div>'
    ),
    (
        '<div id="rag-voice-status" style="display: none; padding: 6px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; color: #ef4444; background: rgba(239, 68, 68, 0.12); border: 1px solid #ef4444; text-align: center; margin-bottom: 6px;">\n                            🎙️ मी ऐकत आहे... प्रश्न विचारा किंवा उधारी बोला...\n                        </div>',
        '<div id="rag-voice-status" style="display: none; padding: 6px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; color: #ef4444; background: rgba(239, 68, 68, 0.12); border: 1px solid #ef4444; text-align: center; margin-bottom: 6px;" data-i18n="rag_voice_status_text">\n                            🎙️ मी ऐकत आहे... प्रश्न विचारा किंवा उधारी बोला...\n                        </div>'
    ),
    (
        '<button id="btn-rag-mic" class="rag-mic-btn" onclick="toggleRagVoice()" title="माईक द्वारे मराठीत बोला">',
        '<button id="btn-rag-mic" class="rag-mic-btn" onclick="toggleRagVoice()" data-i18n-title="title_rag_mic" title="माईक द्वारे बोला">'
    ),
    (
        '<span>पाठवा</span> 🚀\n                            </button>',
        '<span data-i18n="btn_send">पाठवा</span> 🚀\n                            </button>'
    ),
    # Modals
    (
        '<div class="center" style="font-size: 0.72rem; font-weight: 700; margin-top: 4px;" data-i18n="receipt_greeting">\n                        🙏 पुन्हा भेट द्या! धन्यवाद! 🙏\n                    </div>',
        '<div class="center" style="font-size: 0.72rem; font-weight: 700; margin-top: 4px;" data-i18n="receipt_footer_thanks">\n                        🙏 पुन्हा भेट द्या! धन्यवाद! 🙏\n                    </div>'
    ),
    (
        '<div style="font-weight: 800; font-size: 1rem; color: var(--text-white);">💳 नवीन खाते व्यवहार नोंदवा</div>',
        '<div style="font-weight: 800; font-size: 1rem; color: var(--text-white);" data-i18n="modal_khata_title">💳 नवीन खाते व्यवहार नोंदवा</div>'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">ग्राहकाचे नाव (Customer Name)</label>\n                        <input type="text" id="khata-input-name" class="input-cyber" required placeholder="उदा. सागर पाटील">',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_cust_name">ग्राहकाचे नाव (Customer Name)</label>\n                        <input type="text" id="khata-input-name" class="input-cyber" required data-i18n-ph="ph_cust_name" placeholder="उदा. सागर पाटील">'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">मोबाईल नंबर (WhatsApp)</label>\n                        <input type="tel" id="khata-input-phone" class="input-cyber" required placeholder="उदा. 9876543210" pattern="[0-9]{10}">',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_mobile">मोबाईल नंबर (WhatsApp)</label>\n                        <input type="tel" id="khata-input-phone" class="input-cyber" required data-i18n-ph="ph_mobile" placeholder="उदा. 9876543210" pattern="[0-9]{10}">'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">व्यवहार प्रकार</label>\n                            <select id="khata-input-type" class="input-cyber">\n                                <option value="Credit Given">उधारी दिली (Credit Given)</option>\n                                <option value="Payment Received">पैसे जमा केले (Payment)</option>\n                            </select>',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_tx_type">व्यवहार प्रकार</label>\n                            <select id="khata-input-type" class="input-cyber">\n                                <option value="Credit Given" data-i18n="opt_credit_given">उधारी दिली (Credit Given)</option>\n                                <option value="Payment Received" data-i18n="opt_payment_received">पैसे जमा केले (Payment)</option>\n                            </select>'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">रक्कम (₹)</label>\n                            <input type="number" id="khata-input-amount" class="input-cyber" required placeholder="उदा. 500" step="0.5">',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_amount">रक्कम (₹)</label>\n                            <input type="number" id="khata-input-amount" class="input-cyber" required data-i18n-ph="ph_amount" placeholder="उदा. 500" step="0.5">'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">परतफेडीची देय तारीख (Due Date)</label>',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_due_date">परतफेडीची देय तारीख (Due Date)</label>'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">नोंद / तपशील (Notes)</label>\n                        <input type="text" id="khata-input-notes" class="input-cyber" placeholder="उदा. किराणा सामान उधारी">',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_notes">नोंद / तपशील (Notes)</label>\n                        <input type="text" id="khata-input-notes" class="input-cyber" data-i18n-ph="ph_notes" placeholder="उदा. किराणा सामान उधारी">'
    ),
    (
        '💾 व्यवहार सेव्ह करा\n                    </button>',
        '<span data-i18n="btn_save_tx">💾 व्यवहार सेव्ह करा</span>\n                    </button>'
    ),
    # Add Inventory Modal
    (
        '<div style="font-weight: 800; font-size: 1rem; color: var(--text-white);">📦 नवीन वस्तू / माल जोडा</div>',
        '<div style="font-weight: 800; font-size: 1rem; color: var(--text-white);" data-i18n="modal_stock_title">📦 नवीन वस्तू / माल जोडा</div>'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">वस्तूचे नाव (Item Name)</label>\n                        <input type="text" id="inv-input-name" class="input-cyber" required placeholder="उदा. साखर (Sugar M-30)">',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_inv_item_name">वस्तूचे नाव (Item Name)</label>\n                        <input type="text" id="inv-input-name" class="input-cyber" required data-i18n-ph="ph_inv_item_name" placeholder="उदा. साखर (Sugar M-30)">'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">उपलब्ध साठा (Stock Qty)</label>\n                            <input type="number" id="inv-input-qty" class="input-cyber" required placeholder="उदा. 50" step="0.5">',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_inv_stock_qty">उपलब्ध साठा (Stock Qty)</label>\n                            <input type="number" id="inv-input-qty" class="input-cyber" required data-i18n-ph="ph_inv_stock_qty" placeholder="उदा. 50" step="0.5">'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">एकक (Unit)</label>',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_inv_unit">एकक (Unit)</label>'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">विक्री किंमत (₹)</label>\n                            <input type="number" id="inv-input-price" class="input-cyber" required placeholder="उदा. 45" step="0.5">',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_inv_price">विक्री किंमत (₹)</label>\n                            <input type="number" id="inv-input-price" class="input-cyber" required data-i18n-ph="ph_inv_price" placeholder="उदा. 45" step="0.5">'
    ),
    (
        '<label style="font-size: 0.75rem; color: var(--text-slate);">कमी साठा मर्यादा (Alert Limit)</label>',
        '<label style="font-size: 0.75rem; color: var(--text-slate);" data-i18n="lbl_inv_alert_limit">कमी साठा मर्यादा (Alert Limit)</label>'
    ),
    (
        '💾 साठा नोंदवा\n                    </button>',
        '<span data-i18n="btn_save_stock">💾 साठा नोंदवा</span>\n                    </button>'
    ),
    # Camera modal
    (
        '<div style="font-weight: 800; font-size: 1rem; color: var(--text-white);">📷 पावतीचा फोटो काढा</div>',
        '<div style="font-weight: 800; font-size: 1rem; color: var(--text-white);" data-i18n="modal_camera_title">📷 पावतीचा फोटो काढा</div>'
    ),
    (
        '📸 फोटो क्लिक करा\n                    </button>',
        '<span data-i18n="btn_snap_photo">📸 फोटो क्लिक करा</span>\n                    </button>'
    ),
    # WhatsApp Share Modal
    (
        '<span>📲</span> WhatsApp वर पावती पाठवा',
        '<span>📲</span> <span data-i18n="modal_wa_title">WhatsApp वर पावती पाठवा</span>'
    ),
    (
        '<p style="font-size: 0.85rem; color: var(--text-slate); margin-bottom: 14px;">\n                ग्राहकाचा १० अंकी WhatsApp नंबर टाका. बिलाचा संपूर्ण तपशील आणि UPI पेमेंट लिंक थेट त्यांच्या WhatsApp वर उघडेल:\n            </p>',
        '<p style="font-size: 0.85rem; color: var(--text-slate); margin-bottom: 14px;" data-i18n="desc_wa_share">\n                ग्राहकाचा १० अंकी WhatsApp नंबर टाका. बिलाचा संपूर्ण तपशील आणि UPI पेमेंट लिंक थेट त्यांच्या WhatsApp वर उघडेल:\n            </p>'
    ),
    (
        '<label style="font-size: 0.78rem; font-weight: 700; color: var(--text-white);">ग्राहकाचा WhatsApp मोबाईल नंबर:</label>',
        '<label style="font-size: 0.78rem; font-weight: 700; color: var(--text-white);" data-i18n="lbl_wa_phone">ग्राहकाचा WhatsApp मोबाईल नंबर:</label>'
    ),
    (
        '<input type="tel" id="wa-share-phone" class="input-cyber" placeholder="उदा. 9822001122" maxlength="10" style="font-size: 1.1rem; letter-spacing: 1px;">',
        '<input type="tel" id="wa-share-phone" class="input-cyber" data-i18n-ph="ph_wa_phone" placeholder="उदा. 9822001122" maxlength="10" style="font-size: 1.1rem; letter-spacing: 1px;">'
    ),
    (
        '<button class="btn-cyber" style="flex: 1;" onclick="closeModal(\'modal-whatsapp-share\')">रद्द करा</button>',
        '<button class="btn-cyber" style="flex: 1;" onclick="closeModal(\'modal-whatsapp-share\')" data-i18n="btn_cancel">रद्द करा</button>'
    ),
    (
        '🚀 WhatsApp वर पाठवा\n                </button>',
        '<span data-i18n="btn_send_wa">🚀 WhatsApp वर पाठवा</span>\n                </button>'
    ),
    # Move script tag to bottom
    (
        '    <script src="app.js?v=35.0"></script>\n\n    <!-- =====================================================================\n         WHATSAPP BILL SHARE MODAL\n         =====================================================================\n    <div id="modal-whatsapp-share"',
        '    <!-- =====================================================================\n         WHATSAPP BILL SHARE MODAL\n         =====================================================================\n    <div id="modal-whatsapp-share"'
    ),
    (
        '    </div>\n\n</body>',
        '    </div>\n\n    <script src="app.js?v=36.0"></script>\n</body>'
    )
]

applied_count = 0
for src, dst in replacements:
    if src in html:
        html = html.replace(src, dst)
        applied_count += 1
    else:
        print(f"Warning: pattern not found:\n{src[:60]}...")

print(f"Applied {applied_count}/{len(replacements)} HTML replacements.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved updated index.html and public/index.html")


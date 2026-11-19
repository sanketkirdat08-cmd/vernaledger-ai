with open('generate_presentation_script_pdf.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Exact target block for slide 12
old_s12 = """  <!-- ===================================================================== -->
  <!-- SLIDE 12: RESULT 1: SMART MULTIMODAL SCANNER & POS                    -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 12</span>
        Result 1: Smart Multimodal Scanner &amp; POS
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Capabilities On-Screen:</b><br/>
          • Live camera capture of paper receipts with instant canvas preview and Lanczos image sharpening.<br/>
          • Google Gemini reads Marathi and English handwriting, extracting items, quantities, and rates.<br/>
          • Populates an editable on-screen table where the merchant can adjust quantities or prices before saving.<br/>
          • Clicking 'Save' registers the bill, updates customer khata, and deducts sold items from the 50 inventory items.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Respected examiners, Slide 12 showcases Result 1: Our Smart Bill Scanner. When the merchant captures a photo of a handwritten paper receipt, Gemini AI reads all item names, weights, and rates in under 1.5 seconds. The shopkeeper can edit any row on screen, and upon saving, stock is deducted automatically."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          स्क्रीन दाखवून सांगा: "कागदी पावतीचा फोटो काढताच स्क्रीनवर सुंदर टेबल तयार होते. दुकानदाराला बदल करायचा असल्यास करू शकतो, आणि 'सेव्ह' दाबताच दुकानातील ५० साठ्यामधून तेवढा माल आपोआप कमी होतो."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> Can the merchant edit items before saving?<br/>
          <b>Ans:</b> Yes, every detected row has editable input fields for item name, quantity, and rate before final confirmation.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi will now demonstrate our voice billing engine on Slide 13."
        </div>
      </div>
    </div>
  </div>"""

new_s12 = """  <!-- ===================================================================== -->
  <!-- SLIDE 12: RESULT 1: SMART MULTIMODAL SCANNER & POS                    -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-sanket">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 12</span>
        Result 1: Smart Multimodal Scanner &amp; POS
      </div>
      <span class="speaker-badge spk-sanket">👤 वक्ता: SANKET KIRDAT (Team Leader &amp; AI) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Subtitle:</b> AI-Powered Digitization of Handwritten Receipts via Vision Transformers &amp; Native Multimodal Models<br/>
          • <span class="pill-item">1. ViTs</span> <b>Vision Transformers:</b> Patch-based deep visual analysis parses cursive, faint, or misaligned handwritten Devanagari text.<br/>
          • <span class="pill-item">2. Multimodal AI</span> <b>Native Architecture:</b> Directly outputs structured POS JSON (Item, Qty, Rate, Total) in a single neural step.<br/>
          • <span class="pill-item">3. TPUs</span> <b>Google Cloud Acceleration:</b> Sub-2s high-speed inference optimized for mobile camera capture over 4G/5G.<br/>
          • <span class="pill-item">4. Attention</span> <b>Context-Aware Attention:</b> Disambiguates visually indistinct digits ('1' vs '7', '3' vs '8') with 98%+ precision.<br/>
          • <span class="pill-item">5. Document AI</span> <b>Smart Rate Inference:</b> Pre-trained on regional ledgers; infers Rate = Total / Qty and populates distinct POS columns.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Respected examiners, Slide 12 showcases Result 1: Our Smart Multimodal Scanner &amp; POS. Powered by Vision Transformers (ViTs) and Gemini Multimodal AI on Cloud TPUs, our system parses cursive handwritten Marathi receipts in under 2 seconds. The Context-Aware Attention mechanism resolves confusing digits, while our smart rate engine calculates unit rates versus total amounts into an editable POS billing table with zero calculation errors."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          स्क्रीन दाखवून सांगा: "व्हिजन ट्रान्सफॉर्मर्स आणि जेमिनी मल्टिमोडल एआय द्वारे हस्तलिखित मराठी पावती २ सेकंदात स्कॅन होते. अस्पष्ट आकडे संदर्भावरून अचूक ओळखले जातात, तसेच दर (Rate) आणि एकूण किंमत (Total) आपोआप अचूक रकान्यात भरून थेट डिजिटल बिल तयार होते."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How does the system handle blurry handwriting and disambiguate unit rates versus total amounts?<br/>
          <b>Ans:</b> Vision Transformers analyze visual patches alongside Context-Aware Attention, while our rate engine auto-calculates <code>Rate = Total / Qty</code> when shopkeepers only write total line price.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi will now demonstrate our Vernacular Voice Billing engine on Slide 13."
        </div>
      </div>
    </div>
  </div>"""

old_s15 = """  <!-- ===================================================================== -->
  <!-- SLIDE 15: RESULT 4: STORE OPERATIONS & 50 KIRANA ITEMS                -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 15</span>
        Result 4: Store Operations &amp; 50 Kirana Inventory Items
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Live Screenshot &amp; Inventory Capabilities On-Screen:</b><br/>
          • 50 pre-loaded authentic Indian kirana items: wheat, rice, dals, sugar, gul, rawa, oils, ghee, tea, spices, soaps.<br/>
          • Real-time search bar by item name or category, with metric unit conversion (e.g., 500 gm = 0.5 kg).<br/>
          • Automatic stock deduction: Scanning a bill or voice billing auto-deducts sold items (`MAX(0, stock - billed)`).<br/>
          • Red '🚨 कमी साठा' (Low Stock) alert badge when items drop below threshold, plus 1-click 'Reset Defaults' button.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Slide 15 presents Result 4: Store Operations with 50 authentic pre-loaded kirana items. We have grains, dals, oils, spices, and soaps. Whenever a bill is saved, our backend matches the item name and automatically deducts the quantity from stock. If stock drops below threshold, a red 'Low Stock' badge warns the merchant."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          साठा तक्ता दाखवून सांगा: "दुकानातील ५० मूळ किराणा वस्तू आधीच भरलेल्या आहेत. बिल सेव्ह होताच गोदामातील साठा आपोआप कमी होतो, आणि माल संपत आला की लाल अलर्ट मिळतो. १-क्लिकमध्ये साठा पूर्ववत करता येतो."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How does it match spoken item names to database?<br/>
          <b>Ans:</b> Our backend normalizes Marathi and English names, performing token-based fuzzy matching against inventory items.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi will now demonstrate our Verna AI Assistant on Slide 16."
        </div>
      </div>
    </div>
  </div>"""

new_s15 = """  <!-- ===================================================================== -->
  <!-- SLIDE 15: RESULT 4: STORE OPERATIONS & 50 KIRANA ITEMS                -->
  <!-- ===================================================================== -->
  <div class="slide-card">
    <div class="slide-topbar topbar-rushikesh">
      <div class="slide-id-title">
        <span class="slide-pill">SLIDE 15</span>
        Result 4: Store Operations &amp; 50 Kirana Inventory Items
      </div>
      <span class="speaker-badge spk-rushikesh">👤 वक्ता: RUSHIKESH MULIK (Backend &amp; Database) • Slide 5/6</span>
    </div>
    <div class="card-body">
      <div class="box-onscreen">
        <div class="lbl-onscreen">📌 स्लाईडवरील नक्की मजकूर व दृश्य (On-Screen Slide Content)</div>
        <div class="text-onscreen">
          <b>Subtitle:</b> 50 Pre-Seeded Kirana Staples, Live Filter Search &amp; Automatic Stock Deduction Engine<br/>
          • <span class="pill-item">1. 50 Staples</span> <b>Pre-Seeded Catalog:</b> 50 authentic Indian grocery staples (Sugar, Peanut Oil, Toor Dal, Rice, Spices) ready for store billing.<br/>
          • <span class="pill-item">2. Filter Search</span> <b>Live Search &amp; Unit Controls:</b> Instant search (name/category) with precise retail units (kg, ltr, packet, pieces).<br/>
          • <span class="pill-item">3. Auto Deduct</span> <b>Stock Deduction Engine:</b> Real-time inventory decrement (<code>stock_qty = MAX(0, stock_qty - billed_qty)</code>) on saving any bill.<br/>
          • <span class="pill-item">4. Alerts</span> <b>Low-Stock Warnings:</b> Prominent visual badge ('🚨 Low Stock') on critical thresholds with 1-click restore to 50 defaults.
        </div>
      </div>
      <div class="box-en">
        <div class="lbl-en">🗣️ Spoken English Script (काय बोलायचे?)</div>
        <div class="text-en">
          "Respected examiners, Slide 15 presents Result 4: Store Operations &amp; 50 Kirana Inventory Items. We have pre-configured 50 authentic Indian grocery staples with standard unit pricing and live search filtering. Whenever an OCR, voice, or manual bill is saved, our backend automatically decrements inventory in real time using <code>MAX(0, stock_qty - billed_qty)</code>, triggering a red 'Low Stock' alert if inventory drops below safety limits."
        </div>
      </div>
      <div class="box-mr">
        <div class="lbl-mr">📝 मराठीत सोप्या भाषेत अर्थ</div>
        <div class="text-mr">
          साठा तक्ता दाखवून सांगा: "५० अस्सल किराणा वस्तू आधीच सिस्टीममध्ये लोड केलेल्या आहेत. रिअल-टाइम सर्च आणि अचूक युनिट कंट्रोल आहे. कॅमेरा स्कॅन किंवा व्हॉइस बिल सेव्ह होताच साठा आपोआप कमी होतो, आणि माल संपत आला की लाल 'Low Stock' इशारा मिळतो."
        </div>
      </div>
      <div class="bottom-row">
        <div class="qa-mini">
          🎯 <b>Viva Q:</b> How does the inventory engine maintain data integrity during concurrent bill settlements?<br/>
          <b>Ans:</b> SQLite transactions execute atomic updates with <code>MAX(0, stock_qty - billed_qty)</code>, preventing negative stock and syncing instantly across local and cloud storage.
        </div>
        <div class="handover-mini">
          ➡️ <b>Handover to Vaishnavi:</b> "Vaishnavi will now demonstrate our Verna AI Multilingual Voice Assistant on Slide 16."
        </div>
      </div>
    </div>
  </div>"""

print("S12 found?", old_s12 in content)
print("S15 found?", old_s15 in content)

if old_s12 in content and old_s15 in content:
    content = content.replace(old_s12, new_s12)
    content = content.replace(old_s15, new_s15)
    with open('generate_presentation_script_pdf.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated generate_presentation_script_pdf.py successfully!")
else:
    print("Could not find exact blocks.")

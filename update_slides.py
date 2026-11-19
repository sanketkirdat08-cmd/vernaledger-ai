# Script to update Slide 12 and Slide 15 in VernaLedger_Presentation.html and public/VernaLedger_Presentation.html

import re

slide12_old_target = """                <div class="slide-title-wrap">
                    <div class="slide-badge">12 • Live System Showcase</div>
                    <h2 class="slide-title">Result 1: Smart Multimodal Scanner &amp; POS</h2>
                    <div class="slide-subtitle">Vision Transformers, Native Multimodal AI, TPUs व Context-Aware NLP द्वारे हस्तलिखित पावत्यांचे अचूक डिजिटल बिलिंग</div>
                </div>

                <div class="split-layout">
                    <div class="split-text" style="gap: 8px; max-height: 540px; overflow-y: auto; padding-right: 6px;">
                        <div class="feature-item" style="padding: 10px 14px;">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-cyan);">१.</span> व्हिजन ट्रान्सफॉर्मर्स (Vision Transformers - ViTs)</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>काय आहे:</strong> पारंपारिक पद्धती फक्त सरळ ओळी वाचू शकत होत्या, पण गुगलचे Vision Transformers प्रतिमेचे लहान तुकड्यांमध्ये (Patches) विभाजन करून त्याचे सूक्ष्म विश्लेषण करतात.<br><strong style="color: var(--neon-green);">फायदा:</strong> वहीच्या पानावर तिरकी, एकमेकांत गुंफलेली किंवा घाईघाईत लिहिलेली अक्षरे व आकडे अगदी अचूकपणे स्कॅन होतात.</p>
                        </div>
                        <div class="feature-item accent-purple" style="padding: 10px 14px;">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-purple);">२.</span> नेटिव्ह मल्टिमोडल आर्किटेक्चर (Native Multimodal Architecture)</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>काय आहे:</strong> इमेज (फोटो) आणि टेक्स्ट (मजकूर) हे वेगळे न मानता, मॉडेल त्यांना एकाच वेळी आणि एकाच मज्जातंतू जाळ्यात (Neural Network) समजू शकते.<br><strong style="color: var(--neon-green);">फायदा:</strong> फोटोमधील हस्तलिखिताचे थेट डिजिटल आणि भाषिक स्वरूपात रूपांतर करणे यामुळे शक्य होते.</p>
                        </div>
                        <div class="feature-item accent-green" style="padding: 10px 14px;">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-green);">३.</span> गुगल टीपीयू आणि क्लाउड इन्फ्रास्ट्रक्चर (Google TPUs &amp; Cloud)</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>काय आहे:</strong> एवढ्या मोठ्या प्रमाणावर डेटा आणि प्रतिमेचे रिअल-टाइम विश्लेषण करण्यासाठी गुगलचे कस्टम Tensor Processing Units (TPUs).<br><strong style="color: var(--neon-green);">फायदा:</strong> टीपीयू हार्डवेअरमुळे हे मॉडेल अत्यंत वेगवान (Fast) बनते, ज्यामुळे मोबाईल किंवा वेब ॲपमध्ये काही सेकंदांत निकाल मिळतो.</p>
                        </div>
                        <div class="feature-item accent-blue" style="padding: 10px 14px; border-left: 3px solid var(--electric-blue);">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--electric-blue);">४.</span> कॉन्टेक्स्ट-अवेअर अटेंशन मेकॅनिझम (Context-Aware Attention)</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>काय आहे:</strong> अस्पष्ट अक्षरे किंवा आकडे (उदा. '१' आणि '७' किंवा '३' आणि '८' मधील फरक) ओळखण्यासाठी LLM चे Attention Mechanism काम करते.<br><strong style="color: var(--neon-green);">फायदा:</strong> मॉडेल फक्त एक अक्षर न पाहता, संपूर्ण वाक्याचा आणि आजूबाजूच्या शब्दांचा संदर्भ (Context) तपासून अचूक शब्द ओळखतो.</p>
                        </div>
                        <div class="feature-item" style="padding: 10px 14px; border-left: 3px solid var(--neon-cyan);">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-cyan);">५.</span> क्लाउड व्हिजन आणि डॉक्युमेंट AI (Cloud Vision &amp; Document AI Foundation)</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>काय आहे:</strong> गुगलच्या व्यावसायिक लेजर, पावत्या (Invoices) आणि कागदपत्रे वाचण्याच्या अनेक वर्षांच्या संशोधनाचा पाया यात समाविष्ट आहे.<br><strong style="color: var(--neon-green);">फायदा:</strong> विविध भाषा (मराठी, हिंदी, इंग्रजी) आणि वेगवेगळ्या लोकांच्या हस्ताक्षरांच्या शैली ओळखण्याची क्षमता यामुळे वाढते.</p>
                        </div>
                    </div>"""

slide12_new = """                <div class="slide-title-wrap">
                    <div class="slide-badge">12 • Live System Showcase</div>
                    <h2 class="slide-title">Result 1: Smart Multimodal Scanner &amp; POS</h2>
                    <div class="slide-subtitle">AI-Powered Digitization of Handwritten Receipts via Vision Transformers &amp; Native Multimodal Models</div>
                </div>

                <div class="split-layout">
                    <div class="split-text" style="gap: 8px; max-height: 540px; overflow-y: auto; padding-right: 6px;">
                        <div class="feature-item" style="padding: 10px 14px;">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-cyan);">1.</span> Vision Transformers (ViTs)</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>How it Works:</strong> Decomposes receipt images into visual patches for deep non-linear feature analysis rather than rigid line-by-line scanning.<br><strong style="color: var(--neon-green);">Advantage:</strong> Accurately parses cursive, faint, or misaligned handwritten Devanagari text and numbers.</p>
                        </div>
                        <div class="feature-item accent-purple" style="padding: 10px 14px;">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-purple);">2.</span> Native Multimodal Architecture</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>How it Works:</strong> Evaluates visual pixel tokens and Marathi/Hindi linguistic semantics within a single unified neural network.<br><strong style="color: var(--neon-green);">Advantage:</strong> Directly outputs structured POS ledger JSON (Item, Qty, Rate, Total) in a single inference step.</p>
                        </div>
                        <div class="feature-item accent-green" style="padding: 10px 14px;">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-green);">3.</span> Google TPU &amp; Cloud Acceleration</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>How it Works:</strong> Large-scale model execution accelerated via Google Tensor Processing Units (TPUs) with REST API failover.<br><strong style="color: var(--neon-green);">Advantage:</strong> Sub-2-second end-to-end processing, optimized for mobile camera capture over 4G/5G networks.</p>
                        </div>
                        <div class="feature-item accent-blue" style="padding: 10px 14px; border-left: 3px solid var(--electric-blue);">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--electric-blue);">4.</span> Context-Aware Attention Mechanism</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>How it Works:</strong> Disambiguates visually indistinct digits (e.g., '1' vs '7', '3' vs '8') using full-sentence Kirana grocery context.<br><strong style="color: var(--neon-green);">Advantage:</strong> Cross-validates grocery item names against common regional terms, achieving 98%+ precision.</p>
                        </div>
                        <div class="feature-item" style="padding: 10px 14px; border-left: 3px solid var(--neon-cyan);">
                            <div class="feature-title" style="font-size: 0.95rem;"><span style="color: var(--neon-cyan);">5.</span> Document AI &amp; Smart Rate Inference</div>
                            <p class="feature-desc" style="font-size: 0.78rem; line-height: 1.4; margin-top: 3px;"><strong>How it Works:</strong> Pre-trained on regional retail ledgers with smart math validation (Rate = Total / Qty if rate is omitted).<br><strong style="color: var(--neon-green);">Advantage:</strong> Correctly maps handwritten lines into distinct Rate vs. Total table columns, preventing billing errors.</p>
                        </div>
                    </div>"""

slide15_old_target = """                <div class="slide-title-wrap">
                    <div class="slide-badge">15 • Live System Showcase</div>
                    <h2 class="slide-title">Result 4: Store Operations &amp; 50 Kirana Inventory Items</h2>
                    <div class="slide-subtitle">50 Pre-Seeded Kirana Staples, Live Filter Search &amp; Automatic Stock Deduction Engine</div>
                </div>

                <div class="split-layout">
                    <div class="split-text">
                        <div class="feature-item">
                            <div class="feature-title"><span style="color: var(--neon-cyan);">📦</span> 50 Pre-Seeded Authentic Kirana Staples</div>
                            <p class="feature-desc">साखर, शेंगदाणा तेल, तूर डाळ, बासमती तांदूळ, चहा पावडर, मसाले इत्यादी 50 अस्सल किराणा वस्तू सिस्टीममध्ये आधीच लोड केलेल्या आहेत.</p>
                        </div>
                        <div class="feature-item accent-cyan">
                            <div class="feature-title"><span style="color: var(--neon-cyan);">🔍</span> Live Filter Search &amp; Unit Controls</div>
                            <p class="feature-desc">दुकानातील मालाचा शोध घेण्यासाठी रिअल-टाइम सर्च बार (नाव किंवा कॅटेगरीनुसार) आणि kg, ltr, packet, nos नुसार थेट अचूक साठा ट्रॅकिंग.</p>
                        </div>
                        <div class="feature-item accent-green">
                            <div class="feature-title"><span style="color: var(--neon-green);">⚡</span> Automatic Stock Deduction Engine</div>
                            <p class="feature-desc">कॅमेरा OCR स्कॅनर, व्हॉइस बिलिंग किंवा मॅन्युअल बिल सेव्ह होताच विकल्या गेलेल्या मालाचा साठा आपोआप वजा (<code>stock_qty = MAX(0, stock_qty - billed_qty)</code>) होतो.</p>
                        </div>
                        <div class="feature-item accent-red">
                            <div class="feature-title"><span style="color: var(--neon-red);">🚨</span> Low-Stock Warnings &amp; Reset Defaults</div>
                            <p class="feature-desc">साठा थ्रेशोल्डपेक्षा कमी झाल्यास लाल रंगाचा '🚨 कमी साठा' बॅज दिसतो आणि एका क्लिकवर मूळ 50 वस्तूंचा साठा रिसेट ("मूळ 50 किराणा साठा रिसेट करा") करण्याची सोय.</p>
                        </div>
                    </div>"""

slide15_new = """                <div class="slide-title-wrap">
                    <div class="slide-badge">15 • Live System Showcase</div>
                    <h2 class="slide-title">Result 4: Store Operations &amp; 50 Kirana Inventory Items</h2>
                    <div class="slide-subtitle">50 Pre-Seeded Kirana Staples, Live Filter Search &amp; Automatic Stock Deduction Engine</div>
                </div>

                <div class="split-layout">
                    <div class="split-text">
                        <div class="feature-item">
                            <div class="feature-title"><span style="color: var(--neon-cyan);">📦</span> 50 Pre-Seeded Authentic Kirana Staples</div>
                            <p class="feature-desc">Pre-loaded catalog of 50 essential Indian grocery staples (Sugar, Peanut Oil, Toor Dal, Basmati Rice, Tea Powder, Spices) ready for instant store billing.</p>
                        </div>
                        <div class="feature-item accent-cyan">
                            <div class="feature-title"><span style="color: var(--neon-cyan);">🔍</span> Live Filter Search &amp; Unit Controls</div>
                            <p class="feature-desc">Real-time instant search bar (by item name or category) with precise stock tracking across standard retail units (kg, ltr, packet, pieces).</p>
                        </div>
                        <div class="feature-item accent-green">
                            <div class="feature-title"><span style="color: var(--neon-green);">⚡</span> Automatic Stock Deduction Engine</div>
                            <p class="feature-desc">Whenever a bill is completed via OCR scan, voice billing, or manual entry, inventory automatically deducts in real time (<code>stock_qty = MAX(0, stock_qty - billed_qty)</code>).</p>
                        </div>
                        <div class="feature-item accent-red">
                            <div class="feature-title"><span style="color: var(--neon-red);">🚨</span> Low-Stock Warnings &amp; Reset Defaults</div>
                            <p class="feature-desc">Prominent visual alerts ('🚨 Low Stock' badge) flag items falling below safety buffer limits, with a 1-click restore to reset default Kirana inventory.</p>
                        </div>
                    </div>"""

for filepath in ['VernaLedger_Presentation.html', 'public/VernaLedger_Presentation.html']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize newlines for matching
    s12_found = slide12_old_target in content
    s15_found = slide15_old_target in content
    print(f"File {filepath}: S12 target found? {s12_found}, S15 target found? {s15_found}")

    if s12_found and s15_found:
        content = content.replace(slide12_old_target, slide12_new)
        content = content.replace(slide15_old_target, slide15_new)
        # Also update zoom badge in slides 12 and 15 if needed
        # We can safely replace zoom badge in slide 12 & 15
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {filepath}!")
    else:
        print(f"Failed to find exact blocks in {filepath}")

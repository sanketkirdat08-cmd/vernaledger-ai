"""
VernaLedger.AI: Merchant Pro v7.5
Role-Wise Code Defense & Examiner Viva Presentation Guide PDF Generator
Reads code_defense_guide.html and renders to A4 PDF using Playwright Chromium
"""

import os
import sys
import shutil
from playwright.sync_api import sync_playwright

OUTPUT_PDF = os.path.abspath("VernaLedger_AI_Role_Wise_Code_Defense_and_Viva_Guide.pdf")
HTML_FILE = os.path.abspath("code_defense_guide.html")

def generate_pdf():
    print("=" * 70)
    print("🚀 Generating VernaLedger.AI Role-Wise Code Defense & Viva Guide PDF...")
    print("=" * 70)

    if not os.path.exists(HTML_FILE):
        print(f"❌ ERROR: HTML template {HTML_FILE} not found!")
        sys.exit(1)

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    with sync_playwright() as p:
        try:
            if os.path.exists(edge_path):
                browser = p.chromium.launch(executable_path=edge_path, headless=True)
            else:
                browser = p.chromium.launch(headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto(f"file:///{HTML_FILE.replace(os.sep, '/')}", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(600)

        page.pdf(
            path=OUTPUT_PDF,
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        browser.close()

    # Sync to public/
    public_dir = os.path.abspath("public")
    if os.path.exists(public_dir):
        shutil.copy2(OUTPUT_PDF, os.path.join(public_dir, os.path.basename(OUTPUT_PDF)))
        print(f"✅ Synced PDF to public/ folder.")

    if os.path.exists(OUTPUT_PDF):
        size_bytes = os.path.getsize(OUTPUT_PDF)
        print("=" * 70)
        print(f"✅ SUCCESS: PDF generated at: {OUTPUT_PDF}")
        print(f"📊 PDF File Size: {size_bytes:,} bytes")
        print("=" * 70)
    else:
        print("❌ ERROR: Output PDF was not created!")
        sys.exit(1)

if __name__ == "__main__":
    generate_pdf()

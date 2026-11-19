from playwright.sync_api import sync_playwright
import os

print("Starting playwright...")
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
with sync_playwright() as p:
    print("Launching browser...")
    try:
        if os.path.exists(edge_path):
            print("Edge exists, launching edge...")
            browser = p.chromium.launch(executable_path=edge_path, headless=True)
        else:
            print("Edge does not exist, launching default...")
            browser = p.chromium.launch(headless=True)
    except Exception as e:
        print(f"Exception: {e}, fallback...")
        browser = p.chromium.launch(headless=True)
    print("Creating page...")
    page = browser.new_page()
    page.set_content("<h1>Hello World</h1>")
    page.pdf(path="test.pdf")
    browser.close()
    print("Done test.pdf!")

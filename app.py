"""
VernaLedger.AI - Merchant Pro v7.5
Universal ASGI & Vercel Entrypoint
Powered by FastAPI, Gemini 2.5 Flash, Edge TTS, SQLite ACID Ledger, and Responsive Cyberpunk SPA.
"""

import os
import sys
import time
import threading
import webbrowser
import warnings

# Configure UTF-8 encoding for standard I/O on Windows
if sys.platform.startswith("win"):
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Suppress noisy deprecation/future warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load environment variables
try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(root_dir, ".env"))
except Exception:
    pass

from api.index import app

def launch_browser():
    """Wait for FastAPI to initialize and automatically launch browser."""
    time.sleep(1.2)
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception:
        pass

def get_local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    import uvicorn

    # Launch browser automatically on server startup
    threading.Thread(target=launch_browser, daemon=True).start()

    local_ip = get_local_ip()
    print("=" * 70)
    print("  🚀 VernaLedger.AI - Merchant Pro v7.5 (Live Unified Server)")
    print("=" * 70)
    print(f"  💻 Laptop URL:  http://127.0.0.1:8000")
    print(f"  📱 Mobile URL:  http://{local_ip}:8000")
    print("=" * 70)
    print("  👉 मोबाईलवर उघडण्यासाठी: फोन आणि लॅपटॉप एकाच वायफाय/हॉटस्पॉटवर")
    print(f"     कनेक्ट करा आणि फोनच्या क्रोम ब्राऊझरमध्ये http://{local_ip}:8000 उघडा.")
    print("     दोन्ही डिव्हाइसवर एकाच वेळी रिअल-टाईम बदल (Real-Time Live Sync) दिसतील!")
    print("=" * 70)
    # Bind to 0.0.0.0 so both laptop and mobile can access simultaneously
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

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

if __name__ == "__main__":
    import uvicorn

    # Launch browser automatically on server startup
    threading.Thread(target=launch_browser, daemon=True).start()

    print("=" * 65)
    print("VernaLedger.AI - Merchant Pro v7.5 (Starting Server)")
    print("Local Server: http://127.0.0.1:8000")
    print("Opening browser automatically in 1 second...")
    print("API Docs:     http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

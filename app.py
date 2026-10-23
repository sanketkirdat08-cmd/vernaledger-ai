"""
VernaLedger.AI - Merchant Pro v7.5
Universal ASGI & Vercel Entrypoint
Powered by FastAPI, Gemini 2.5 Flash, Edge TTS, SQLite ACID Ledger, and Responsive Cyberpunk SPA.
"""

import time
import threading
import webbrowser
from api.index import app

def launch_browser():
    """Wait for FastAPI to initialize and automatically launch browser."""
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")

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

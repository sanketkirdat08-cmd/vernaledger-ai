"""
VernaLedger.AI - Merchant Pro v7.5
Universal ASGI & Vercel Entrypoint
Powered by FastAPI, Gemini 2.5 Flash, Edge TTS, SQLite ACID Ledger, and Responsive Cyberpunk SPA.
"""

from api.index import app

if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print("VernaLedger.AI - Merchant Pro v7.5 (Starting Server)")
    print("Local Server: http://localhost:8000")
    print("API Docs:     http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)

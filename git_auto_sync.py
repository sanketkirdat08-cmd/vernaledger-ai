"""
VernaLedger.AI - Enterprise GitOps Auto-Sync Engine
Continuously tracks database changes, creates 100% offline-safe Git commits,
and automatically pushes to GitHub (origin/main) every 4 seconds when online.
"""

import os
import sys
import time
import subprocess
import socket
import json
import sqlite3
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "ledger.db")
DATA_DIR = os.path.join(ROOT_DIR, "data")
SNAPSHOT_FILE = os.path.join(DATA_DIR, "live_ledger_snapshot.json")

def is_online(timeout=1.5):
    """Ultra-fast socket test to check if GitHub / internet is reachable."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(("github.com", 443))
        s.close()
        return True
    except Exception:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect(("8.8.8.8", 53))
            s.close()
            return True
        except Exception:
            return False

def export_live_snapshot():
    """Export current SQLite database tables to a human-readable, Git-tracked JSON snapshot."""
    if not os.path.exists(DB_PATH):
        return False
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=2.0)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        receipts = [dict(r) for r in c.execute("SELECT * FROM receipts ORDER BY id DESC").fetchall()]
        for r in receipts:
            if r.get("raw_json"):
                try:
                    r["raw_json"] = json.loads(r["raw_json"])
                except Exception:
                    pass

        khata = [dict(r) for r in c.execute("SELECT * FROM customer_khata ORDER BY id DESC").fetchall()]
        inventory = [dict(r) for r in c.execute("SELECT * FROM shop_inventory ORDER BY id ASC").fetchall()]
        expenses = [dict(r) for r in c.execute("SELECT * FROM business_expenses ORDER BY id DESC").fetchall()]
        tombstones_rec = [dict(r) for r in c.execute("SELECT * FROM deleted_receipts ORDER BY id DESC").fetchall()]
        tombstones_khata = [dict(r) for r in c.execute("SELECT * FROM deleted_khata ORDER BY id DESC").fetchall()] if c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deleted_khata'").fetchone() else []
        conn.close()

        payload = {
            "version": "7.5",
            "last_synced_at": datetime.now().isoformat(),
            "counts": {
                "receipts": len(receipts),
                "khata": len(khata),
                "inventory": len(inventory),
                "expenses": len(expenses)
            },
            "receipts": receipts,
            "khata": khata,
            "inventory": inventory,
            "expenses": expenses,
            "deleted_receipts": tombstones_rec,
            "deleted_khata": tombstones_khata
        }

        new_content = json.dumps(payload, ensure_ascii=False, indent=2)
        if os.path.exists(SNAPSHOT_FILE):
            try:
                with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                    old_content = f.read()
                old_json = json.loads(old_content)
                old_json.pop("last_synced_at", None)
                new_json = json.loads(new_content)
                new_json.pop("last_synced_at", None)
                if old_json == new_json:
                    return False  # No change
            except Exception:
                pass

        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        return False

def sync_cycle():
    """Perform one atomic check-commit-push cycle."""
    # 1. Update snapshot from database
    export_live_snapshot()

    # 2. Check for unstaged or untracked local changes
    status_res = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT_DIR, capture_output=True, text=True)
    has_local_changes = bool(status_res.stdout and status_res.stdout.strip())

    if has_local_changes:
        subprocess.run(["git", "add", "-A"], cwd=ROOT_DIR, capture_output=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"auto-sync: automated state backup [{timestamp}]"
        commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=ROOT_DIR, capture_output=True, text=True)
        if commit_res.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [GitOps 💾] Local commit created (100% Offline Safe)!", flush=True)

    # 3. Check for unpushed commits
    unpushed_res = subprocess.run(["git", "log", "origin/main..HEAD", "--oneline"], cwd=ROOT_DIR, capture_output=True, text=True)
    unpushed_count = len(unpushed_res.stdout.strip().splitlines()) if unpushed_res.stdout.strip() else 0

    if unpushed_count > 0:
        online = is_online()
        ts = datetime.now().strftime("%H:%M:%S")
        if online:
            print(f"[{ts}] [GitOps 🌐] Online detected. Pushing {unpushed_count} commit(s) to GitHub origin/main...", flush=True)
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT_DIR, capture_output=True, text=True)
            if push_res.returncode == 0:
                print(f"[{ts}] [GitOps 🚀] SUCCESS: Pushed to GitHub origin/main seamlessly!", flush=True)
            else:
                print(f"[{ts}] [GitOps ⚠️] Push deferred: {push_res.stderr.strip()[:100]}", flush=True)
        else:
            print(f"[{ts}] [GitOps 🟡] Offline Mode: {unpushed_count} commit(s) safely saved in local Git. Will push automatically once online.", flush=True)

def run_daemon(interval_seconds=4):
    """Continuous GitOps sync loop."""
    print("=" * 70)
    print("  🚀 VernaLedger.AI - Enterprise GitOps Auto-Sync Daemon")
    print(f"  ⏱️ Heartbeat: Every {interval_seconds} seconds")
    print("  📶 Mode: 100% Offline-Safe Local Commits + Online Instant Remote Push")
    print("=" * 70, flush=True)
    while True:
        try:
            sync_cycle()
        except Exception as e:
            print(f"[GitOps Notice]: {e}", flush=True)
        time.sleep(interval_seconds)

def start_background_thread(interval_seconds=4):
    """Start daemon in background thread for seamless single-command execution in app.py."""
    import threading
    t = threading.Thread(target=run_daemon, args=(interval_seconds,), daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    run_daemon(interval_seconds=4)

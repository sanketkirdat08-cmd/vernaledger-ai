import os

css_addition = '''
/* ==========================================================================
   LEDGER MULTI-SELECT & BULK DELETE STYLES
   ========================================================================== */
.cyber-checkbox {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--neon-cyan);
    border-radius: 4px;
    vertical-align: middle;
    transition: transform 0.15s ease;
}

.cyber-checkbox:hover {
    transform: scale(1.15);
}

.cyber-table tr.row-selected {
    background: rgba(0, 242, 254, 0.14) !important;
}

.cyber-table tr.row-selected td {
    color: #ffffff !important;
    border-bottom: 1px solid rgba(0, 242, 254, 0.3) !important;
}

body.light-theme .cyber-table tr.row-selected {
    background: #E0F2FE !important;
}

body.light-theme .cyber-table tr.row-selected td {
    color: #0369A1 !important;
    border-bottom: 1px solid #7DD3FC !important;
}

@keyframes pulseDanger {
    0% {
        box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.6);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(255, 0, 85, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(255, 0, 85, 0);
    }
}
'''

for path in ["style.css", os.path.join("public", "style.css")]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        if "LEDGER MULTI-SELECT" not in c:
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n" + css_addition)
            print(f"Appended styles to {path}")

print("CSS updated!")


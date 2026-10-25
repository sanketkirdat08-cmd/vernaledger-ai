import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx

def examine_tables(filename):
    print(f"\n*** EXAMINING TABLES IN {filename} ***")
    d = docx.Document(filename)
    for t_idx, table in enumerate(d.tables):
        has_match = False
        for r_idx, row in enumerate(table.rows):
            text = " | ".join(c.text.strip() for c in row.cells)
            if any(k in text for k in ["Sanket", "Sakshi", "Vaishnavi", "Rushikesh", "3034", "4060", "Roll"]):
                has_match = True
                break
        if has_match:
            print(f"--- Table {t_idx} (rows: {len(table.rows)}, cols: {len(table.columns)}) ---")
            for r_idx, row in enumerate(table.rows):
                for c_idx, cell in enumerate(row.cells):
                    print(f"  [R{r_idx}, C{c_idx}]: '{cell.text.strip()}'")

examine_tables("VernaLedger_AI_Final_Year_Project_Report.docx")
examine_tables("VernaLedger_AI_Project_Synopsis.docx")

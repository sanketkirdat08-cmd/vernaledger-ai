import shutil
import os

desktop_dir = r"C:\Users\mahan\OneDrive\Desktop"
workspace_dir = r"C:\Users\mahan\OneDrive\Desktop\VernaLedger-AI"

files_to_copy = [
    ("VernaLedger_AI_Final_Year_Project_Report.docx", "VernaLedger_AI_Final_Year_Project_Report.docx"),
    ("VernaLedger_AI_Project_Synopsis.docx", "VernaLedger_AI_Project_Synopsis.docx"),
    ("VERNALEDGER_AI_MERCHANT_PRO_PRESENTATION.pptx", "VERNALEDGER_AI_MERCHANT_PRO_PRESENTATION_UPDATED.pptx"),
    ("VernaLedger_AI_Project_Architecture_and_File_Directory_Guide.pdf", "VernaLedger_AI_Project_Architecture_and_File_Directory_Guide.pdf"),
    ("VernaLedger_Presentation.html", "VERNALEDGER_AI_MERCHANT_PRO_PRESENTATION.html")
]

for src_name, dst_name in files_to_copy:
    src = os.path.join(workspace_dir, src_name)
    dst = os.path.join(desktop_dir, dst_name)
    if os.path.exists(src):
        try:
            shutil.copy2(src, dst)
            print(f"COPIED: {src_name} -> {dst}")
        except Exception as e:
            print(f"FAILED to copy {src_name}: {e}")
    else:
        print(f"MISSING: {src}")

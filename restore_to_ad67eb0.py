import subprocess
import os
import shutil

print("1. Extracting original VernaLedger_Presentation.html from commit ad67eb0...")
cmd = ["git", "show", "ad67eb0:VernaLedger_Presentation.html"]
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if res.returncode != 0:
    print(f"Error getting file from git: {res.stderr.decode('utf-8', errors='ignore')}")
else:
    original_bytes = res.stdout
    print(f"Read {len(original_bytes)} bytes from commit ad67eb0.")
    with open("VernaLedger_Presentation.html", "wb") as f:
        f.write(original_bytes)
    print("Restored VernaLedger_Presentation.html successfully!")
    
    with open("public/VernaLedger_Presentation.html", "wb") as f:
        f.write(original_bytes)
    print("Restored public/VernaLedger_Presentation.html successfully!")

# 2. Clean up temporary files added during the last 2 steps
files_to_remove = [
    "check_funcs.py",
    "check_helpers.py",
    "check_img_dims.py",
    "dump_results_json.py",
    "dump_results_slides.py",
    "extract_and_inspect.py",
    "inspect_all_slides_deep.py",
    "inspect_create_pres.py",
    "list_current_imgs.py",
    "list_html_slides.py",
    "make_industry_level_ppt.py",
    "parse_html_slides.py",
    "results_slides_content.json",
    "test_mac_window.pptx",
    "test_mac_window.py",
    "test_style_inject.py",
    "view_s12.py",
    "list_slides.py"
]

for file_path in files_to_remove:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted temporary file: {file_path}")
        except Exception as e:
            print(f"Could not remove {file_path}: {e}")

if os.path.exists("real_screenshots"):
    try:
        shutil.rmtree("real_screenshots")
        print("Deleted temporary directory: real_screenshots/")
    except Exception as e:
        print(f"Could not remove real_screenshots: {e}")

print("Revert complete!")

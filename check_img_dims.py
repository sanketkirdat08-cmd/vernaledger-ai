import os
from PIL import Image

screenshots = [
    ("Slide 09 (Architecture)", "real_screenshots/slide_img_2_System_Architecture_Diagram.png"),
    ("Slide 10 (Flowchart)", "real_screenshots/slide_img_3_Execution_Pipeline_Flowchart.png"),
    ("Slide 12 (Result 1)", "real_screenshots/slide_img_4_Smart_Multimodal_Scanner_and_L.png"),
    ("Slide 13 (Result 2)", "real_screenshots/slide_img_5_Vernacular_Voice_Billing_Engin.png"),
    ("Slide 14 (Result 3)", "real_screenshots/slide_img_6_Customer_Khata_Module.png"),
    ("Slide 15 (Result 4)", "real_screenshots/slide_img_7_Store_Operations_and_50_Kirana.png"),
    ("Slide 16 (Result 5)", "real_screenshots/slide_img_8_Verna_AI_Multilingual_Voice_As.png"),
    ("Slide 17 (Result 6)", "real_screenshots/slide_img_9_Digital_Ledger_and_Excel_Expor.png"),
    ("Slide 18 (Result 7)", "real_screenshots/slide_img_10_High_Contrast_Kirana_Light_Mod.png"),
    ("Slide 19 (Result 8)", "real_screenshots/slide_img_11_Mobile_First_Responsive_PWA_Ar.png")
]

for label, path in screenshots:
    if os.path.exists(path):
        im = Image.open(path)
        w, h = im.size
        ratio = w / h
        print(f"{label}: {w}x{h} (ratio: {ratio:.2f})")
    else:
        print(f"MISSING: {path}")

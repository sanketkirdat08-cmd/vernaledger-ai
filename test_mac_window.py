import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

slide = prs.slides.add_slide(blank_layout)

# Background
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = RGBColor(6, 12, 28)
bg.line.fill.background()

# Test macOS window frame
frame_x, frame_y, frame_w, frame_h = Inches(6.8), Inches(1.8), Inches(5.8), Inches(4.8)

# Window container
w_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, frame_x, frame_y, frame_w, frame_h)
w_bg.fill.solid()
w_bg.fill.fore_color.rgb = RGBColor(10, 18, 36)
w_bg.line.color.rgb = RGBColor(0, 242, 254)
w_bg.line.width = Pt(1.5)

# Titlebar
tb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, frame_x, frame_y, frame_w, Inches(0.38))
tb.fill.solid()
tb.fill.fore_color.rgb = RGBColor(18, 28, 56)
tb.line.color.rgb = RGBColor(0, 242, 254)
tb.line.width = Pt(1.0)

# Traffic lights
dot_colors = [RGBColor(255, 95, 86), RGBColor(255, 189, 46), RGBColor(39, 201, 63)]
for i, col in enumerate(dot_colors):
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, frame_x + Inches(0.15 + i * 0.22), frame_y + Inches(0.11), Inches(0.14), Inches(0.14))
    dot.fill.solid()
    dot.fill.fore_color.rgb = col
    dot.line.fill.background()

# Window Title
title_tb = slide.shapes.add_textbox(frame_x + Inches(0.85), frame_y + Inches(0.04), Inches(3.4), Inches(0.3))
p = title_tb.text_frame.paragraphs[0]
p.text = "VernaLedger Studio — Live POS Terminal"
p.font.name = "Consolas"
p.font.size = Pt(8.5)
p.font.color.rgb = RGBColor(148, 163, 184)

# Status Pill
pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, frame_x + frame_w - Inches(1.4), frame_y + Inches(0.07), Inches(1.25), Inches(0.24))
pill.fill.solid()
pill.fill.fore_color.rgb = RGBColor(0, 255, 135)
pill.line.fill.background()
p_pill = pill.text_frame.paragraphs[0]
p_pill.text = "● LIVE POS"
p_pill.font.name = "Segoe UI"
p_pill.font.size = Pt(7.5)
p_pill.font.bold = True
p_pill.font.color.rgb = RGBColor(5, 15, 25)
p_pill.alignment = PP_ALIGN.CENTER

# Screenshot
img_path = "real_screenshots/slide_img_4_Smart_Multimodal_Scanner_and_L.png"
if os.path.exists(img_path):
    slide.shapes.add_picture(img_path, frame_x + Inches(0.05), frame_y + Inches(0.42), frame_w - Inches(0.1), frame_h - Inches(0.47))

prs.save("test_mac_window.pptx")
print("Saved test_mac_window.pptx successfully!")

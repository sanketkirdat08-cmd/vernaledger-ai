"""
VernaLedger.AI: Merchant Pro v7.5 - Technical Presentation Generator
Creates a 16:9 Widescreen, 23-slide Cyberpunk Neon Dark Glassmorphism PowerPoint presentation
with bespoke, theme-appropriate contextual background graphics on EVERY slide.
"""

import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Output File Path
OUTPUT_PPTX = r"C:\Users\mahan\OneDrive\Desktop\VERNALEDGER_AI_MERCHANT_PRO_PRESENTATION.pptx"
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Cyberpunk Neon Color Palette
COLOR_BG = RGBColor(5, 11, 20)           # #050B14 Deep Obsidian Navy
COLOR_CARD = RGBColor(10, 17, 40)        # #0A1128 Dark Glass Navy
COLOR_CARD_BORDER = RGBColor(0, 242, 254)# Neon Cyan subtle border
COLOR_CYAN = RGBColor(0, 242, 254)       # #00F2FE Neon Cyan
COLOR_GREEN = RGBColor(0, 255, 135)      # #00FF87 Neon Green
COLOR_PURPLE = RGBColor(176, 38, 255)    # #B026FF Neon Purple
COLOR_BLUE = RGBColor(79, 172, 254)      # #4FACFE Electric Blue
COLOR_RED = RGBColor(255, 0, 85)         # #FF0055 Neon Red / Rose
COLOR_AMBER = RGBColor(255, 170, 0)      # #FFAA00 Amber
COLOR_WHITE = RGBColor(248, 250, 252)    # Pure White text
COLOR_SLATE = RGBColor(148, 163, 184)    # Muted Slate text
COLOR_DIM = RGBColor(100, 116, 139)      # Dim Slate text

FONT_TITLE = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_MONO = "Consolas"
TOTAL_SLIDES = 23

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_slide_theme_background(slide, theme_key):
        """Draws bespoke, theme-appropriate subtle vector graphics in the background behind cards."""
        if theme_key == "cover":
            # 4 Cyberpunk Corner Brackets
            corners = [
                (Inches(0.4), Inches(0.4)),
                (Inches(12.133), Inches(0.4)),
                (Inches(0.4), Inches(6.3)),
                (Inches(12.133), Inches(6.3))
            ]
            for cx, cy in corners:
                c_sh = slide.shapes.add_shape(MSO_SHAPE.CORNER, cx, cy, Inches(0.8), Inches(0.8))
                c_sh.fill.background()
                c_sh.line.color.rgb = RGBColor(0, 180, 220)
                c_sh.line.width = Pt(1.5)
            # Radiant center donut
            d = slide.shapes.add_shape(MSO_SHAPE.DONUT, Inches(4.666), Inches(1.75), Inches(4.0), Inches(4.0))
            d.fill.background()
            d.line.color.rgb = RGBColor(12, 35, 65)
            d.line.width = Pt(1)

        elif theme_key == "intro":
            # Connected Commerce Mesh Network
            nodes = [
                (Inches(1.2), Inches(2.2)), (Inches(12.1), Inches(2.2)),
                (Inches(1.2), Inches(5.8)), (Inches(12.1), Inches(5.8))
            ]
            # Connecting horizontal and diagonal rails
            r1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.2), Inches(10.9), Inches(0.02))
            r1.fill.solid()
            r1.fill.fore_color.rgb = RGBColor(10, 35, 60)
            r1.line.fill.background()

            r2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(5.8), Inches(10.9), Inches(0.02))
            r2.fill.solid()
            r2.fill.fore_color.rgb = RGBColor(10, 35, 60)
            r2.line.fill.background()

            for nx, ny in nodes:
                ov = slide.shapes.add_shape(MSO_SHAPE.OVAL, nx - Inches(0.1), ny - Inches(0.1), Inches(0.2), Inches(0.2))
                ov.fill.solid()
                ov.fill.fore_color.rgb = RGBColor(0, 160, 200)
                ov.line.fill.background()

        elif theme_key == "problems":
            # Crimson Warning Hazard Accents
            for y_off in [Inches(1.6), Inches(4.1)]:
                d1 = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(0.35), y_off, Inches(0.35), Inches(0.35))
                d1.fill.solid()
                d1.fill.fore_color.rgb = RGBColor(35, 10, 20)
                d1.line.color.rgb = RGBColor(140, 20, 45)
                d1.line.width = Pt(1)

                d2 = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(12.633), y_off, Inches(0.35), Inches(0.35))
                d2.fill.solid()
                d2.fill.fore_color.rgb = RGBColor(35, 10, 20)
                d2.line.color.rgb = RGBColor(140, 20, 45)
                d2.line.width = Pt(1)

        elif theme_key == "motivation":
            # Ascending Neon Velocity Rails
            for idx, x_pos in enumerate([Inches(2.5), Inches(6.5), Inches(10.5)]):
                ray = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos, Inches(1.5), Inches(0.03), Inches(5.0))
                ray.fill.solid()
                ray.fill.fore_color.rgb = RGBColor(0, 60, 45) if idx % 2 == 0 else RGBColor(0, 50, 80)
                ray.line.fill.background()

        elif theme_key == "gap":
            # Coordinate Precision Grid Crosshairs
            for cx, cy in [(Inches(0.5), Inches(1.6)), (Inches(12.8), Inches(1.6)), (Inches(0.5), Inches(6.6)), (Inches(12.8), Inches(6.6))]:
                cr = slide.shapes.add_shape(MSO_SHAPE.CROSS, cx, cy, Inches(0.25), Inches(0.25))
                cr.fill.solid()
                cr.fill.fore_color.rgb = RGBColor(0, 120, 140)
                cr.line.fill.background()

        elif theme_key == "objectives":
            # 4-Pillar Foundation Brackets
            for x, y in [(Inches(0.6), Inches(1.6)), (Inches(6.6), Inches(1.6)), (Inches(0.6), Inches(4.1)), (Inches(6.6), Inches(4.1))]:
                crn = slide.shapes.add_shape(MSO_SHAPE.CORNER, x, y, Inches(0.4), Inches(0.4))
                crn.fill.background()
                crn.line.color.rgb = RGBColor(0, 100, 130)
                crn.line.width = Pt(1)

        elif theme_key == "pipeline":
            # Continuous Flowing Data Conduit with Chevrons
            c_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.0), Inches(11.733), Inches(0.04))
            c_line.fill.solid()
            c_line.fill.fore_color.rgb = RGBColor(15, 45, 80)
            c_line.line.fill.background()

            for cx in [Inches(3.6), Inches(6.6), Inches(9.6)]:
                chv = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, cx, Inches(3.85), Inches(0.35), Inches(0.35))
                chv.fill.solid()
                chv.fill.fore_color.rgb = RGBColor(0, 140, 180)
                chv.line.fill.background()

        elif theme_key == "tech":
            # Circuit Board Traces & Solder Nodes
            for tx, ty in [(Inches(0.4), Inches(2.2)), (Inches(12.5), Inches(3.5)), (Inches(0.4), Inches(5.2)), (Inches(12.5), Inches(6.0))]:
                cir = slide.shapes.add_shape(MSO_SHAPE.OVAL, tx, ty, Inches(0.18), Inches(0.18))
                cir.fill.solid()
                cir.fill.fore_color.rgb = RGBColor(0, 200, 120)
                cir.line.fill.background()

                tr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx + Inches(0.08), ty + Inches(0.08), Inches(0.6), Inches(0.02))
                tr.fill.solid()
                tr.fill.fore_color.rgb = RGBColor(0, 100, 80)
                tr.line.fill.background()

        elif theme_key == "arch":
            # 3-Tier Layer Connector Backbone
            backbone = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.0), Inches(3.2), Inches(9.333), Inches(0.03))
            backbone.fill.solid()
            backbone.fill.fore_color.rgb = RGBColor(40, 20, 70)
            backbone.line.fill.background()

        elif theme_key == "flow":
            # 5-Stage Step Connection Rail
            rail = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(4.15), Inches(10.333), Inches(0.02))
            rail.fill.solid()
            rail.fill.fore_color.rgb = RGBColor(0, 80, 110)
            rail.line.fill.background()

        elif theme_key == "perf":
            # Speedometer Gauge Arcs
            for gx in [Inches(2.2), Inches(6.2), Inches(10.2)]:
                arc = slide.shapes.add_shape(MSO_SHAPE.BLOCK_ARC, gx, Inches(2.5), Inches(1.8), Inches(1.8))
                arc.fill.solid()
                arc.fill.fore_color.rgb = RGBColor(10, 25, 45)
                arc.line.color.rgb = RGBColor(0, 100, 130)
                arc.line.width = Pt(1)

        elif theme_key == "login":
            # Cyber Security Hexagon Shield
            hex_sh = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, Inches(8.5), Inches(2.4), Inches(2.4), Inches(2.4))
            hex_sh.fill.background()
            hex_sh.line.color.rgb = RGBColor(0, 120, 150)
            hex_sh.line.width = Pt(1.5)

        elif theme_key == "ocr":
            # Audio Waveform Equalizer Silhouette & Laser Scanline
            for wx, wh in [(Inches(0.4), Inches(0.8)), (Inches(0.55), Inches(1.4)), (Inches(0.7), Inches(2.2)), (Inches(0.85), Inches(1.1))]:
                w_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, wx, Inches(4.5) - wh/2, Inches(0.08), wh)
                w_bar.fill.solid()
                w_bar.fill.fore_color.rgb = RGBColor(0, 100, 140)
                w_bar.line.fill.background()

        elif theme_key == "analytics":
            # Financial Candlestick / Bar Chart Backdrop
            for bx, bh in [(Inches(7.2), Inches(1.0)), (Inches(8.4), Inches(1.6)), (Inches(9.6), Inches(2.3)), (Inches(10.8), Inches(3.1)), (Inches(12.0), Inches(3.8))]:
                f_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx, Inches(6.0) - bh, Inches(0.35), bh)
                f_bar.fill.solid()
                f_bar.fill.fore_color.rgb = RGBColor(12, 32, 50)
                f_bar.line.fill.background()

        elif theme_key == "khata":
            # WhatsApp Dialogue Pulse Rings
            ring = slide.shapes.add_shape(MSO_SHAPE.DONUT, Inches(8.5), Inches(2.8), Inches(2.2), Inches(2.2))
            ring.fill.background()
            ring.line.color.rgb = RGBColor(0, 100, 60)
            ring.line.width = Pt(1.5)

        elif theme_key == "database":
            # ACID Database Cylinders
            can = slide.shapes.add_shape(MSO_SHAPE.CAN, Inches(8.8), Inches(2.5), Inches(1.8), Inches(2.4))
            can.fill.background()
            can.line.color.rgb = RGBColor(0, 120, 140)
            can.line.width = Pt(1.5)

        elif theme_key == "rag":
            # Neural Synaptic AI Network
            center = (Inches(9.5), Inches(3.8))
            for dx, dy in [(Inches(-1.2), Inches(-1.0)), (Inches(1.2), Inches(-1.0)), (Inches(-1.4), Inches(0.8)), (Inches(1.4), Inches(0.8))]:
                n_dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, center[0] + dx, center[1] + dy, Inches(0.2), Inches(0.2))
                n_dot.fill.solid()
                n_dot.fill.fore_color.rgb = RGBColor(176, 38, 255)
                n_dot.line.fill.background()

        elif theme_key == "staff":
            # Multi-User RBAC Hexagon Shield
            shld = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, Inches(8.8), Inches(2.6), Inches(2.0), Inches(2.4))
            shld.fill.background()
            shld.line.color.rgb = RGBColor(40, 80, 140)
            shld.line.width = Pt(1.5)

        elif theme_key == "reports":
            # Thermal Receipt & Barcode Line Stripes
            for bx, bw in [(Inches(7.2), Inches(0.04)), (Inches(7.35), Inches(0.08)), (Inches(7.55), Inches(0.04)), (Inches(7.7), Inches(0.12)), (Inches(7.95), Inches(0.04))]:
                b_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx, Inches(2.2), bw, Inches(3.8))
                b_line.fill.solid()
                b_line.fill.fore_color.rgb = RGBColor(20, 35, 60)
                b_line.line.fill.background()

        elif theme_key == "advantages":
            # Glowing Diamond Polygon Facets
            for dx in [Inches(2.0), Inches(6.2), Inches(10.4)]:
                dia = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, dx, Inches(2.0), Inches(1.2), Inches(1.2))
                dia.fill.background()
                dia.line.color.rgb = RGBColor(0, 120, 70)
                dia.line.width = Pt(1.2)

        elif theme_key == "limitations":
            # Cautionary Cloud Silhouette
            cld = slide.shapes.add_shape(MSO_SHAPE.CLOUD, Inches(9.2), Inches(2.6), Inches(2.8), Inches(1.8))
            cld.fill.background()
            cld.line.color.rgb = RGBColor(120, 20, 45)
            cld.line.width = Pt(1.5)

        elif theme_key == "future":
            # Hyperspace Velocity Warp Rails
            for fx, fy in [(Inches(0.6), Inches(1.5)), (Inches(12.7), Inches(1.5)), (Inches(0.6), Inches(6.5)), (Inches(12.7), Inches(6.5))]:
                arr = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, fx, fy, Inches(0.5), Inches(0.2))
                arr.fill.solid()
                arr.fill.fore_color.rgb = RGBColor(0, 80, 120)
                arr.line.fill.background()

        elif theme_key == "conclusion":
            # Grand Radiant Arch
            g_arch = slide.shapes.add_shape(MSO_SHAPE.BLOCK_ARC, Inches(4.666), Inches(1.5), Inches(4.0), Inches(4.0))
            g_arch.fill.background()
            g_arch.line.color.rgb = RGBColor(0, 180, 100)
            g_arch.line.width = Pt(2)

    def add_hud_header(slide, badge_text, title_text, subtitle_text):
        badge_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(3.4), Inches(0.35))
        badge_box.fill.solid()
        badge_box.fill.fore_color.rgb = RGBColor(12, 25, 55)
        badge_box.line.color.rgb = COLOR_GREEN
        badge_box.line.width = Pt(1)
        tf_b = badge_box.text_frame
        tf_b.word_wrap = False
        p_b = tf_b.paragraphs[0]
        p_b.text = f"●  {badge_text.upper()}"
        p_b.font.name = FONT_MONO
        p_b.font.size = Pt(9.5)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_GREEN
        p_b.alignment = PP_ALIGN.CENTER

        tb_t = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.6))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE

        if subtitle_text:
            p_sub = tf_t.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.name = FONT_BODY
            p_sub.font.size = Pt(11)
            p_sub.font.color.rgb = COLOR_CYAN

    def add_hud_footer(slide, slide_num):
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(25, 40, 70)
        line.line.fill.background()

        tb_f = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(9.0), Inches(0.4))
        tf_f = tb_f.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "Team VernaLedger • Dept. of Computer Engineering • AGCOE Satara • DBATU University"
        p_f.font.name = FONT_MONO
        p_f.font.size = Pt(8.5)
        p_f.font.color.rgb = COLOR_SLATE

        tb_c = slide.shapes.add_textbox(Inches(10.5), Inches(6.95), Inches(2.0), Inches(0.4))
        tf_c = tb_c.text_frame
        p_c = tf_c.paragraphs[0]
        p_c.text = f"{slide_num:02d} / {TOTAL_SLIDES:02d}"
        p_c.alignment = PP_ALIGN.RIGHT
        p_c.font.name = FONT_MONO
        p_c.font.size = Pt(9)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_CYAN

    def create_card(slide, left, top, width, height, accent_color=COLOR_CYAN):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = RGBColor(25, 45, 80)
        card.line.width = Pt(1)

        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Inches(0.1), top, width - Inches(0.2), Inches(0.04))
        accent.fill.solid()
        accent.fill.fore_color.rgb = accent_color
        accent.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: TITLE / COVER SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    add_slide_theme_background(s1, "cover")

    pill1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.666), Inches(0.8), Inches(6.0), Inches(0.4))
    pill1.fill.solid()
    pill1.fill.fore_color.rgb = RGBColor(10, 25, 55)
    pill1.line.color.rgb = COLOR_GREEN
    pill1.line.width = Pt(1.2)
    p = pill1.text_frame.paragraphs[0]
    p.text = "● B.TECH COMPUTER ENGINEERING • MAJOR PROJECT DEFENSE"
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p.alignment = PP_ALIGN.CENTER

    t1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.4), Inches(11.333), Inches(1.4))
    p = t1.text_frame.paragraphs[0]
    p.text = "VernaLedger.AI: Merchant Pro v7.5"
    p.font.name = FONT_TITLE
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN
    p.alignment = PP_ALIGN.CENTER

    p2 = t1.text_frame.add_paragraph()
    p2.text = "Next-Gen Point of Sale & Vernacular Financial Suite with Gemini Flash OCR,\nMarathi Voice Billing & SQLite ACID Ledger"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_WHITE
    p2.alignment = PP_ALIGN.CENTER

    t_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(3.2), Inches(9.733), Inches(1.8))
    t_box.fill.solid()
    t_box.fill.fore_color.rgb = COLOR_CARD
    t_box.line.color.rgb = COLOR_CYAN
    t_box.line.width = Pt(1.5)

    tf = t_box.text_frame
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "PROJECT DEVELOPMENT TEAM"
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p.alignment = PP_ALIGN.CENTER

    names = [
        "1. Sanket Kirdat",
        "2. Sakshi Bhagat",
        "3. Vaishnavi Dhavale",
        "4. Rushikesh Mulik"
    ]
    p_names = tf.add_paragraph()
    p_names.text = "       •  ".join(names)
    p_names.font.name = FONT_BODY
    p_names.font.size = Pt(13)
    p_names.font.bold = True
    p_names.font.color.rgb = COLOR_WHITE
    p_names.alignment = PP_ALIGN.CENTER

    p_sub = tf.add_paragraph()
    p_sub.text = "B.Tech Final Year • Department of Computer Engineering"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_SLATE
    p_sub.alignment = PP_ALIGN.CENTER

    inst_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.2), Inches(5.3), Inches(8.933), Inches(1.2))
    inst_box.fill.solid()
    inst_box.fill.fore_color.rgb = RGBColor(8, 14, 30)
    inst_box.line.color.rgb = RGBColor(40, 60, 100)
    inst_box.line.width = Pt(1)

    tf_i = inst_box.text_frame
    tf_i.margin_top = Inches(0.15)
    p = tf_i.paragraphs[0]
    p.text = "Arvind Gavali College of Engineering, Satara (AGCOE)"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

    p_uni = tf_i.add_paragraph()
    p_uni.text = "Affiliated to Dr. Babasaheb Ambedkar Technological University (DBATU University) • Academic Year 2026 - 2027"
    p_uni.font.name = FONT_MONO
    p_uni.font.size = Pt(9.5)
    p_uni.font.color.rgb = COLOR_CYAN
    p_uni.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: INTRODUCTION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_slide_theme_background(s2, "intro")
    add_hud_header(s2, "02 • Project Overview", "Introduction: VernaLedger.AI Suite", "Next-Gen Vernacular Financial & Point of Sale Intelligence for Grassroots Indian Retail")
    add_hud_footer(s2, 2)

    intro_cards = [
        ("🏪 What is VernaLedger.AI?", "An offline-first, vernacular-native Point of Sale (POS) and smart digital bookkeeping suite engineered specifically for India's 63+ million micro, small, and medium enterprises (MSMEs) and local kirana merchants.", "Empowering 63M+ Indian MSMEs", COLOR_CYAN),
        ("🗣️ The Vernacular Revolution", "Eliminates English-centric digital barriers by empowering merchants to record transactions via natural Marathi and Hindi voice billing, backed by crystal-clear Edge TTS regional audio feedback.", "Native Marathi & Hindi Voice NLP", COLOR_GREEN),
        ("⚡ Multimodal AI Vision & OCR", "Eliminates manual pen-and-paper billing by harnessing Google Gemini Flash multimodal vision to accurately extract items, rates, quantities, and taxes in under 4.5 seconds.", "Sub-4.5s Instant Digitization", COLOR_PURPLE),
        ("🛡️ Resilient ACID SQLite Architecture", "Guarantees 100% operational uptime and zero data loss with a local SQLite database (WAL mode), eliminating expensive cloud subscription fees, vendor lock-in, and broadband dependency.", "Crash-Proof ACID & Zero Platform Tax", COLOR_BLUE)
    ]
    card_w, card_h = Inches(5.6), Inches(2.2)
    positions = [(Inches(0.8), Inches(1.8)), (Inches(6.8), Inches(1.8)),
                 (Inches(0.8), Inches(4.3)), (Inches(6.8), Inches(4.3))]

    for i, (title, desc, tag, col) in enumerate(intro_cards):
        x, y = positions[i]
        create_card(s2, x, y, card_w, card_h, col)
        tb = s2.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"[{tag}]"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(8.5)
        p_t.font.bold = True
        p_t.font.color.rgb = col

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_slide_theme_background(s3, "problems")
    add_hud_header(s3, "03 • Market Realities", "Problem Statement", "The Operational Burden on Local & Rural Retail Merchants")
    add_hud_footer(s3, 3)

    problems = [
        ("✍️ Manual Data Entry", "Writing receipts and ledgers manually consumes ~120s per bill, resulting in math miscalculations, queue backlogs, and lost paper slips.", "Bottleneck: 120s / Bill"),
        ("🌍 Language Barriers", "90% of accounting software (Tally, Zoho) is English-centric, alienating semi-literate rural store owners who communicate exclusively in Marathi or Hindi.", "Exclusion: Non-Vernacular UI"),
        ("📘 Disorganized Udhari", "Tracking informal customer credit on paper books leads to untraceable balances, forgotten dues, and ~15% quarterly revenue leakage.", "Loss: ~15% Uncollected Dues"),
        ("📉 Lack of Analytics", "Kirana store owners have zero visibility into real-time profit/loss, fast-depleting stock thresholds, or sales trends to make restocking decisions.", "Blindspot: Zero Sales Insights")
    ]

    for i, (title, desc, tag) in enumerate(problems):
        x, y = positions[i]
        create_card(s3, x, y, card_w, card_h, COLOR_RED)
        tb = s3.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_RED

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"[{tag}]"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(8.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_RED

    # =========================================================================
    # SLIDE 4: MOTIVATION
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_slide_theme_background(s4, "motivation")
    add_hud_header(s4, "04 • The Vision", "Motivation", "Empowering Rural Grassroots Commerce with Enterprise-Grade Artificial Intelligence")
    add_hud_footer(s4, 4)

    motivations = [
        ("🌉 Bridging the Tech Divide", "Democratizing sophisticated business tooling for tier-2/3 micro-merchants and kirana stores without requiring expensive POS hardware, barcode scanners, or IT literacy.", "Democratizing Enterprise Tech", COLOR_CYAN),
        ("🧠 Harnessing Multimodal AI", "Fusing Google Gemini Flash's sub-second multimodal vision with Microsoft Edge TTS to transform ubiquitous smartphone cameras and regional speech into a complete autonomous POS.", "Multimodal AI + Neural Audio", COLOR_GREEN),
        ("⚡ Removing Digital Friction", "Compressing cumbersome bookkeeping from several stressful minutes into an effortless 4.5-second gesture: snap a photo or speak in Marathi, and let AI structure the ledger.", "Zero-Friction Billing", COLOR_PURPLE)
    ]
    card_w3 = Inches(3.64)
    card_h3 = Inches(4.5)
    for i, (title, desc, tag, col) in enumerate(motivations):
        x = Inches(0.8) + i * Inches(4.0)
        y = Inches(1.9)
        create_card(s4, x, y, card_w3, card_h3, col)
        tb = s4.shapes.add_textbox(x + Inches(0.25), y + Inches(0.3), card_w3 - Inches(0.5), card_h3 - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"\nTarget: {tag}"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(9.5)
        p_t.font.bold = True
        p_t.font.color.rgb = col

    # =========================================================================
    # SLIDE 5: GAP ANALYSIS (MARKET COMPARISON TABLE - NO BHARATPE)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_slide_theme_background(s5, "gap")
    add_hud_header(s5, "05 • Competitive Benchmarks", "Gap Analysis (Market Comparison)", "Head-to-Head Architectural Comparison with Direct Industry Competitors")
    add_hud_footer(s5, 5)

    rows, cols = 8, 6
    tbl_shape = s5.shapes.add_table(rows, cols, Inches(0.8), Inches(1.85), Inches(11.733), Inches(4.7))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(3.2)
    tbl.columns[1].width = Inches(1.7)
    tbl.columns[2].width = Inches(1.7)
    tbl.columns[3].width = Inches(1.7)
    tbl.columns[4].width = Inches(1.7)
    tbl.columns[5].width = Inches(1.733)

    table_data = [
        ["Evaluated Capability", "Khatabook", "OkCredit", "Vyapar App", "TallyPrime", "VernaLedger.AI (v7.5)"],
        ["Marathi Voice Billing", "❌ No", "❌ No", "❌ No", "❌ No", "✔ Native Voice NLP + TTS"],
        ["Multimodal AI OCR Parsing", "❌ No", "❌ No", "❌ No", "❌ No", "✔ Gemini Flash <4.5s"],
        ["Context-Aware RAG Chatbot", "❌ No", "❌ No", "❌ No", "❌ No", "✔ Neural AI Studio (SQL RAG)"],
        ["Offline ACID Database", "❌ Cloud Lock-in", "❌ Cloud Lock-in", "⚠️ Local File", "✔ Proprietary DB", "✔ SQLite 3 (WAL Mode ACID)"],
        ["1-Click WhatsApp Reminders", "⚠️ Paid SMS", "⚠️ Standard SMS", "⚠️ Paid Addon", "❌ No Direct Hook", "✔ 1-Click WhatsApp Direct"],
        ["Security & Audit Logs", "❌ Mobile OTP", "❌ Mobile OTP", "⚠️ Basic PIN", "✔ User Rights", "✔ PBKDF2 & Audit Logs"],
        ["Cost to Small Merchant", "₹2,000 - ₹5,000 / yr", "₹1,500 - ₹3,000 / yr", "₹2,500 - ₹6,000 / yr", "₹22,500+ (Desktop)", "100% Free & Open Architecture"]
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
            p.font.name = FONT_BODY
            p.font.size = Pt(10)
            
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(15, 30, 60)
                p.font.bold = True
                p.font.color.rgb = COLOR_CYAN if c_idx != 5 else COLOR_GREEN
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(8, 14, 32) if c_idx != 5 else RGBColor(12, 35, 45)
                if c_idx == 5:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_GREEN
                elif "✔" in val:
                    p.font.color.rgb = COLOR_CYAN
                elif "❌" in val:
                    p.font.color.rgb = COLOR_RED
                else:
                    p.font.color.rgb = COLOR_SLATE

    # =========================================================================
    # SLIDE 6: PROJECT OBJECTIVES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_slide_theme_background(s6, "objectives")
    add_hud_header(s6, "06 • Core Mission", "Project Objectives", "Four Strategic Engineering Pillars Governing System Architecture")
    add_hud_footer(s6, 6)

    objectives = [
        ("1. Automate Receipt Parsing", "Engineer a sub-4.5s multimodal vision pipeline using Gemini Flash to extract line items, prices, tax, and totals with zero numerical hallucination.", "Performance: <4.5s Processing", COLOR_CYAN),
        ("2. Multi-Lingual Voice Billing", "Enable merchants to speak naturally in Marathi, Hindi, or English to record customer purchases, backed by instant Edge TTS regional audio confirmation.", "Accessibility: Native Regional Speech", COLOR_GREEN),
        ("3. Resilient ACID Storage", "Implement a zero-loss local SQLite engine with Write-Ahead Logging (WAL), atomic transactional commits, and PBKDF2-SHA256 encrypted role security.", "Integrity: Crash-Proof ACID WAL", COLOR_PURPLE),
        ("4. Actionable Intelligence", "Equip merchants with live analytics KPI cards, high-risk credit tracking, 1-click WhatsApp payment reminders, and context-aware RAG querying.", "Business ROI: Accelerated Recovery", COLOR_BLUE)
    ]
    for i, (title, desc, tag, col) in enumerate(objectives):
        x, y = positions[i]
        create_card(s6, x, y, card_w, card_h, col)
        tb = s6.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"[{tag}]"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(8.5)
        p_t.font.bold = True
        p_t.font.color.rgb = col

    # =========================================================================
    # SLIDE 7: PROPOSED SYSTEM
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_slide_theme_background(s7, "pipeline")
    add_hud_header(s7, "07 • Operational Architecture", "Proposed System", "Four-Stage Closed-Loop Multimodal Transaction Processing Pipeline")
    add_hud_footer(s7, 7)

    stages = [
        ("🧑‍💼 1. Merchant Actor", "Interacts via Voice Mic, Live Camera capture, or Direct POS Touch UI.", "Multimodal Input Ingestion", COLOR_CYAN),
        ("🧠 2. AI Parser Module", "Gemini Multimodal Vision & NLP converts raw audio/receipts into validated, strict JSON schemas.", "Strict JSON Enforcement", COLOR_PURPLE),
        ("💾 3. Transaction Engine", "Commits validated records securely to local SQLite tables ensuring ACID atomicity & stock updates.", "ACID Atomic Commit", COLOR_GREEN),
        ("🔊 4. Feedback Loop", "Synthesizes Marathi spoken receipt confirmation via Edge TTS and updates live dashboards.", "Regional Voice Confirmation", COLOR_BLUE)
    ]
    card_w4 = Inches(2.7)
    card_h4 = Inches(4.5)
    for i, (title, desc, tag, col) in enumerate(stages):
        x = Inches(0.8) + i * Inches(3.0)
        y = Inches(1.9)
        create_card(s7, x, y, card_w4, card_h4, col)
        tb = s7.shapes.add_textbox(x + Inches(0.2), y + Inches(0.3), card_w4 - Inches(0.4), card_h4 - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"\nPipeline Role:\n{tag}"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(9)
        p_t.font.bold = True
        p_t.font.color.rgb = col

    # =========================================================================
    # SLIDE 8: TECHNOLOGIES & TOOLS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_slide_theme_background(s8, "tech")
    add_hud_header(s8, "08 • Engineering Stack", "Technologies & Tools", "Modern, Robust, and Scalable Full-Stack Technological Foundation")
    add_hud_footer(s8, 8)

    techs = [
        ("🐍 Frontend & Logic", "• Python 3.10+: Core processing runtime\n• Streamlit Framework: Dynamic reactive UI\n• Custom React Components: Mic audio recording\n• CSS3 Cyberpunk Theme: Dark glassmorphic design system", "Python • Streamlit • React", COLOR_GREEN),
        ("🤖 AI & Audio Engines", "• Google Gemini Flash: Multimodal OCR & NLP\n• Microsoft Edge TTS: Neural Marathi voice synthesis\n• Streamlit Mic Recorder: Real-time audio stream\n• RAG Engine: Dynamic database context injection", "Gemini Flash • Edge TTS • RAG", COLOR_CYAN),
        ("💽 Database & Analytics", "• SQLite3 (WAL Mode): ACID transaction storage\n• PBKDF2-SHA256: Cryptographic password hashing\n• Pandas & Plotly: Real-time business intelligence\n• ReportLab: Localized Marathi PDF & invoice generation", "SQLite • PBKDF2 • Plotly", COLOR_PURPLE)
    ]
    for i, (title, desc, tag, col) in enumerate(techs):
        x = Inches(0.8) + i * Inches(4.0)
        y = Inches(1.9)
        create_card(s8, x, y, card_w3, card_h3, col)
        tb = s8.shapes.add_textbox(x + Inches(0.25), y + Inches(0.3), card_w3 - Inches(0.5), card_h3 - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"\nKey Modules: {tag}"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(9.5)
        p_t.font.bold = True
        p_t.font.color.rgb = col

    # =========================================================================
    # SLIDE 9: SYSTEM ARCHITECTURE
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_slide_theme_background(s9, "arch")
    add_hud_header(s9, "09 • Structural Design", "System Architecture", "Modular 3-Tier Layered Architecture with Strict Separation of Concerns")
    add_hud_footer(s9, 9)

    layers = [
        ("1. PRESENTATION LAYER", "Streamlit UI • Camera Ingestion\nMic Recording • Glassmorphic HUD\nInteractive DataFrames", COLOR_CYAN),
        ("2. INTELLIGENCE LAYER", "Gemini Multimodal OCR Engine\nMarathi Voice NLP Parser • RAG Chat\nEdge TTS Voice Synthesizer", COLOR_PURPLE),
        ("3. PERSISTENCE LAYER", "SQLite Relational Engine (WAL Mode)\nPBKDF2 Password Hashing\nACID Transaction Logging & Audits", COLOR_GREEN)
    ]
    box_w = Inches(3.3)
    box_h = Inches(2.2)
    for i, (title, desc, col) in enumerate(layers):
        x = Inches(0.8) + i * Inches(4.2)
        y = Inches(2.1)
        create_card(s9, x, y, box_w, box_h, col)
        tb = s9.shapes.add_textbox(x + Inches(0.15), y + Inches(0.25), box_w - Inches(0.3), box_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_WHITE

        if i < 2:
            arrow_tb = s9.shapes.add_textbox(x + box_w + Inches(0.1), y + Inches(0.8), Inches(0.7), Inches(0.6))
            p_a = arrow_tb.text_frame.paragraphs[0]
            p_a.text = "➔"
            p_a.font.name = FONT_TITLE
            p_a.font.size = Pt(28)
            p_a.font.bold = True
            p_a.font.color.rgb = COLOR_CYAN
            p_a.alignment = PP_ALIGN.CENTER

    create_card(s9, Inches(0.8), Inches(4.8), Inches(11.733), Inches(1.6), COLOR_CYAN)
    tb_arch = s9.shapes.add_textbox(Inches(1.0), Inches(4.9), Inches(11.333), Inches(1.4))
    tf_a = tb_arch.text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]
    p.text = "CORE ARCHITECTURAL PRINCIPLES:"
    p.font.name = FONT_MONO
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    p_body = tf_a.add_paragraph()
    p_body.text = "The presentation layer is strictly decoupled from the intelligence pipeline. Raw inputs captured via camera or mic are streamed over TLS to Gemini Flash with zero local model overhead. Validated JSON payloads are passed directly to SQLite transactions with Write-Ahead Logging (WAL) enabled, ensuring instantaneous commit speeds (<2ms) and robust crash recovery."
    p_body.font.name = FONT_BODY
    p_body.font.size = Pt(10.5)
    p_body.font.color.rgb = COLOR_SLATE

    # =========================================================================
    # SLIDE 10: WORKING FLOW
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_slide_theme_background(s10, "flow")
    add_hud_header(s10, "10 • Execution Pipeline", "Working Flow (Runtime Execution)", "Step-by-Step Lifecycle of a Transaction Through the VernaLedger System")
    add_hud_footer(s10, 10)

    flow_steps = [
        ("Step 01", "Input Trigger", "Shopkeeper captures receipt photo via camera or speaks bill in Marathi into the mic.", COLOR_CYAN),
        ("Step 02", "Secure Streaming", "Preprocessed audio/image payload is streamed securely via TLS to Gemini Flash API.", COLOR_BLUE),
        ("Step 03", "Schema Parsing", "Gemini LLM normalizes raw content into validated JSON line-items with tax computation.", COLOR_PURPLE),
        ("Step 04", "ACID Commit", "Transaction is committed atomically into SQLite ledger.db with running balance update.", COLOR_GREEN),
        ("Step 05", "Regional Audio", "Edge TTS synthesizes Marathi voice receipt while dashboard graphs update in real-time.", COLOR_AMBER)
    ]
    card_w5 = Inches(2.15)
    card_h5 = Inches(4.5)
    for i, (step, title, desc, col) in enumerate(flow_steps):
        x = Inches(0.8) + i * Inches(2.4)
        y = Inches(1.9)
        create_card(s10, x, y, card_w5, card_h5, col)
        tb = s10.shapes.add_textbox(x + Inches(0.15), y + Inches(0.25), card_w5 - Inches(0.3), card_h5 - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = step
        p.font.name = FONT_MONO
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_SLATE

    # =========================================================================
    # SLIDE 11: PERFORMANCE ANALYSIS
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_slide_theme_background(s11, "perf")
    add_hud_header(s11, "11 • Empirical Evaluation", "Performance Analysis", "Rigorous Quantitative Benchmarks Demonstrating Disruptive Efficiency")
    add_hud_footer(s11, 11)

    metrics = [
        ("96%", "Data Entry Time Reduction", "Average transaction recording time slashed from 120s (manual pen-and-paper writing) down to 4.5s via Gemini AI OCR and Voice Billing.", COLOR_CYAN),
        (">95%", "Regional Parsing Accuracy", "Parsing precision evaluated across handwritten, crumpled, and printed Devanagari bills with Marathi and Hindi item names.", COLOR_GREEN),
        ("<2ms", "SQLite ACID Commit Latency", "Sub-2ms local transactional commit latency enabled by Write-Ahead Logging (WAL) and optimized indexing, guaranteeing zero UI freeze.", COLOR_PURPLE)
    ]
    for i, (val, title, desc, col) in enumerate(metrics):
        x = Inches(0.8) + i * Inches(4.0)
        y = Inches(1.9)
        create_card(s11, x, y, card_w3, card_h3, col)
        tb = s11.shapes.add_textbox(x + Inches(0.2), y + Inches(0.4), card_w3 - Inches(0.4), card_h3 - Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = val
        p.font.name = FONT_TITLE
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE
        p_t.alignment = PP_ALIGN.CENTER

        p_d = tf.add_paragraph()
        p_d.text = f"\n{desc}"
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE
        p_d.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # HELPER FOR RESULT SLIDES (SLIDES 12 - 19)
    # =========================================================================
    def build_result_slide(slide, slide_num, title, subtitle, features, image_name, theme_key):
        set_slide_background(slide)
        add_slide_theme_background(slide, theme_key)
        add_hud_header(slide, f"{slide_num:02d} • Live System Showcase", title, subtitle)
        add_hud_footer(slide, slide_num)

        left_w, left_h = Inches(5.6), Inches(4.5)
        create_card(slide, Inches(0.8), Inches(1.9), left_w, left_h, COLOR_CYAN)
        tb = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), left_w - Inches(0.4), left_h - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True

        for idx, (f_title, f_desc, f_col) in enumerate(features):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f_title
            p.font.name = FONT_TITLE
            p.font.size = Pt(11.5)
            p.font.bold = True
            p.font.color.rgb = f_col

            p_d = tf.add_paragraph()
            p_d.text = f_desc
            p_d.font.name = FONT_BODY
            p_d.font.size = Pt(9.5)
            p_d.font.color.rgb = COLOR_SLATE

        right_x, right_y, right_w, right_h = Inches(6.8), Inches(1.9), Inches(5.733), Inches(4.5)
        create_card(slide, right_x, right_y, right_w, right_h, COLOR_PURPLE)

        img_path = os.path.join(ASSETS_DIR, image_name)
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, right_x + Inches(0.15), right_y + Inches(0.15), right_w - Inches(0.3), right_h - Inches(0.3))
        else:
            tb_ph = slide.shapes.add_textbox(right_x, right_y + Inches(2.0), right_w, Inches(1.0))
            p_ph = tb_ph.text_frame.paragraphs[0]
            p_ph.text = f"[Screenshot: {image_name}]"
            p_ph.alignment = PP_ALIGN.CENTER
            p_ph.font.color.rgb = COLOR_SLATE

    # SLIDE 12: RESULT 1 - LOGIN PORTAL
    s12 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s12, 12,
        "Result 1: Secure Login Portal",
        "Cryptographically Fortified Authentication & Role-Based Access Control",
        [
            ("🔐 PBKDF2-SHA256 Cryptography", "Passwords secured using key stretching and 100,000 hashing iterations with unique salts.", COLOR_CYAN),
            ("🛡️ Role-Based Access Control (RBAC)", "Strict privilege demarcation between Admin master access and restricted Staff accounts.", COLOR_PURPLE),
            ("🔄 Persistent Session State", "Secure local session state management for frictionless auto-login and session persistence.", COLOR_GREEN),
            ("💎 Glassmorphic Cyberpunk Interface", "Modern dark aesthetics with animated background effects and glowing interactive inputs.", COLOR_BLUE)
        ],
        "login.png",
        "login"
    )

    # SLIDE 13: RESULT 2 - OCR & VOICE BILLING
    s13 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s13, 13,
        "Result 2: OCR & Voice Billing Module",
        "Multimodal Bill Capture with Real-Time Audio Feedback & In-Line Editing",
        [
            ("📸 Tri-Mode Bill Capture", "Live camera scan, file upload, or spontaneous vernacular voice recording.", COLOR_GREEN),
            ("⚠️ Duplicate Bill Prevention", "MD5 content hashing detects previously submitted bills to eliminate double charges.", COLOR_CYAN),
            ("🔊 Marathi Neural Audio Confirmation", "Instant Edge TTS audio feedback in Marathi ('बिल यशस्वीरीत्या जोडले गेले').", COLOR_PURPLE),
            ("✏️ In-Line Editable Data Preview", "Interactive data grid enables real-time verification and correction of extracted quantities.", COLOR_RED)
        ],
        "ocr.png",
        "ocr"
    )

    # SLIDE 14: RESULT 3 - MERCHANT ANALYTICS HUB
    s14 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s14, 14,
        "Result 3: Merchant Analytics Hub",
        "Interactive Business Intelligence with Dynamic Vector Visualizations",
        [
            ("📈 Real-Time Revenue KPI Cards", "Live tracking of Gross Sales, Transaction Counts, and Average Ticket Sizes.", COLOR_CYAN),
            ("🥧 Plotly Category Breakdown", "Interactive vector pie charts and bars showing top revenue-generating items.", COLOR_GREEN),
            ("📅 Granular Timeframe Filtering", "Toggle between Today, Last 7 Days, Month-to-Date, and Custom Date Ranges.", COLOR_PURPLE),
            ("⚡ High-Speed Vectorized Computation", "Pandas in-memory aggregations delivering sub-second visual refreshes.", COLOR_BLUE)
        ],
        "analytics.png",
        "analytics"
    )

    # SLIDE 15: RESULT 4 - CUSTOMER KHATA (UDHARI)
    s15 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s15, 15,
        "Result 4: Customer Khata (Udhari)",
        "Digital Credit Ledger with Automated WhatsApp Follow-Up & Risk Scoring",
        [
            ("📘 Digital Credit Ledger", "Instant toggle between Given Credit (उधारी दिली) and Payment Received (जमा).", COLOR_PURPLE),
            ("⏰ Due-Date & Delinquency Alerts", "Visual color badges flag accounts pending beyond 30/60 days to prevent bad debts.", COLOR_RED),
            ("💬 1-Click WhatsApp Payment Links", "Auto-generates localized Marathi payment reminder messages with 1-click WhatsApp delivery.", COLOR_GREEN),
            ("📞 Direct Calling Shortcuts", "Instant lookup by customer name or mobile number with one-tap cellular dialer integration.", COLOR_CYAN)
        ],
        "khata.png",
        "khata"
    )

    # SLIDE 16: RESULT 5 - LEDGER DATABASE EDITOR
    s16 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s16, 16,
        "Result 5: Ledger Database Editor",
        "Full ACID SQLite Control with Live Grid Editing & Multi-Format Exports",
        [
            ("📊 In-Line Dataframe Grid Editing", "Interactive data editor enables cell-by-cell live record updates directly to SQLite.", COLOR_CYAN),
            ("🗑️ Single-Click Audited Deletions", "Secure deletion workflow with confirmation dialogs and audit logging.", COLOR_RED),
            ("📑 Dual-Language PDF & CSV Exports", "One-click generation of localized Marathi PDF statements and standard CSV files.", COLOR_GREEN),
            ("🛡️ ACID Schema Integrity", "Foreign key constraints and WAL logging prevent orphaned data and schema corruption.", COLOR_PURPLE)
        ],
        "database.png",
        "database"
    )

    # SLIDE 17: RESULT 6 - NEURAL AI STUDIO (RAG)
    s17 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s17, 17,
        "Result 6: Neural AI Studio (RAG)",
        "Context-Aware Conversational Intelligence Grounded in Live Merchant Database",
        [
            ("🧠 In-Memory SQL Context RAG", "Chatbot directly queries live sales, credit khata, and stock databases for 100% accurate, hallucination-free answers.", COLOR_PURPLE),
            ("🎙️ Multi-Action Voice & Marathi NLP", "Merchants execute multi-bill recording and ask complex business questions in natural Marathi.", COLOR_CYAN),
            ("⚡ Quick-Action Suggestion Chips", "One-tap prompt chips for pending credit summaries, low stock replenishment lists, and profit trajectories.", COLOR_GREEN),
            ("🧹 Real-Time Memory & Clear Chat", "Maintains conversational memory across transactions with single-click session clearing for staff changeovers.", COLOR_RED)
        ],
        "rag.png",
        "rag"
    )

    # SLIDE 18: RESULT 7 - STAFF MANAGEMENT & AUDIT
    s18 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s18, 18,
        "Result 7: Staff Management & Audit",
        "Granular Permission Matrix & Immutable System Audit Trail",
        [
            ("👥 Granular Role Provisioning", "Easily onboard cashiers and stock clerks with restrictive access to pricing and ledger edits.", COLOR_CYAN),
            ("📜 Immutable Audit Log History", "Tracks every single database mutation with timestamp, username, and event details.", COLOR_PURPLE),
            ("🔒 Zero-Trust Ledger Protection", "Prevents unauthorized staff members from editing historic bills or deleting records.", COLOR_GREEN),
            ("⚡ Instant Access Revocation", "Deactivate compromised or departed staff accounts in a single click with zero downtime.", COLOR_BLUE)
        ],
        "staff.png",
        "staff"
    )

    # SLIDE 19: RESULT 8 - CLEAN REPORTS & EXPORTS
    s19 = prs.slides.add_slide(blank_layout)
    build_result_slide(
        s19, 19,
        "Result 8: Clean Reports & Exports",
        "Auditable Accounting Pipelines & Professional Dual-Language Print Layouts",
        [
            ("📑 Itemized CSV Data Exports", "One-click extraction of complete transaction logs with line-items, tax components, customer IDs, and payment methods for Excel or Tally.", COLOR_CYAN),
            ("📄 Dual-Language Marathi/English Bills", "Generates customer receipts with English titles and Marathi Devanagari translation headers, shop branding, and tax breakdown.", COLOR_GREEN),
            ("🖨️ 1-Click Thermal Print Layout", "Engineered specifically for standard 58mm & 80mm ESC/POS thermal printers with dynamic UPI QR payment codes.", COLOR_PURPLE),
            ("⚖️ Legal & Audit Compliance", "Produces ready-to-audit itemized registers to facilitate effortless quarterly reconciliation and accountant reporting.", COLOR_RED)
        ],
        "reports.png",
        "reports"
    )

    # =========================================================================
    # SLIDE 20: ADVANTAGES & STRENGTHS
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    set_slide_background(s20)
    add_slide_theme_background(s20, "advantages")
    add_hud_header(s20, "20 • Value Proposition", "Advantages & Strengths", "Why VernaLedger.AI Delivers Unmatched Utility for Rural Retailers")
    add_hud_footer(s20, 20)

    advantages = [
        ("🇮🇳 True Vernacular AI", "Bilingual Marathi/English interface coupled with natural voice recognition eliminates the steep digital literacy curve for grassroots shopkeepers.", "Zero Learning Curve", COLOR_CYAN),
        ("⚡ 60% Faster Debt Recovery", "Direct WhatsApp payment reminders and automated due date warnings accelerate customer khata repayments and eliminate awkward debt confrontations.", "Accelerated Working Capital", COLOR_GREEN),
        ("🛡️ Enterprise-Grade Security", "Local SQLite database ensures instant responsiveness and zero downtime even during rural broadband fluctuations, backed by PBKDF2 password security.", "Offline-First Resilience", COLOR_PURPLE)
    ]
    for i, (title, desc, tag, col) in enumerate(advantages):
        x = Inches(0.8) + i * Inches(4.0)
        y = Inches(1.9)
        create_card(s20, x, y, card_w3, card_h3, col)
        tb = s20.shapes.add_textbox(x + Inches(0.25), y + Inches(0.3), card_w3 - Inches(0.5), card_h3 - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"\nROI Metric: {tag}"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(9.5)
        p_t.font.bold = True
        p_t.font.color.rgb = col

    # =========================================================================
    # SLIDE 21: SYSTEM LIMITATIONS
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    set_slide_background(s21)
    add_slide_theme_background(s21, "limitations")
    add_hud_header(s21, "21 • Engineering Constraints", "System Limitations", "Known Technical Boundaries & Operational Dependencies")
    add_hud_footer(s21, 21)

    limitations = [
        ("🌐 AI Internet Dependency", "While core database transactions and manual POS billing run 100% offline, multimodal Gemini Flash OCR parsing and Edge TTS synthesis require an active internet connection to contact cloud endpoints.", "Constraint: Cloud LLM Endpoint"),
        ("📸 Severe Image Distortion", "Extremely crumpled, grease-stained, or faint thermal receipts with severe ink fading can occasionally produce partial OCR extraction, requiring manual operator verification in the preview grid.", "Constraint: Physical Document Quality")
    ]
    card_w21 = Inches(5.6)
    card_h21 = Inches(4.5)
    for i, (title, desc, tag) in enumerate(limitations):
        x = Inches(0.8) if i == 0 else Inches(6.8)
        y = Inches(1.9)
        create_card(s21, x, y, card_w21, card_h21, COLOR_RED)
        tb = s21.shapes.add_textbox(x + Inches(0.25), y + Inches(0.3), card_w21 - Inches(0.5), card_h21 - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_RED

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"\n[{tag}]"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(9.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_RED

    # =========================================================================
    # SLIDE 22: FUTURE ENHANCEMENTS
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    set_slide_background(s22)
    add_slide_theme_background(s22, "future")
    add_hud_header(s22, "22 • Future Roadmap", "Future Enhancements", "Product Evolution, Native Mobile Packaging & Scalability Roadmap")
    add_hud_footer(s22, 22)

    futures = [
        ("📱 Native Android APK", "Packaging the suite as a native Android APK with quantized on-device edge AI models for offline OCR.", "Mobile Native • Edge AI", COLOR_CYAN),
        ("💸 Dynamic UPI QR Codes", "Generating dynamic transaction-specific UPI QR codes directly on invoices with soundbox payment confirmation.", "Instant Payment Hook", COLOR_GREEN),
        ("☁️ Multi-Device Sync", "Implementing encrypted peer-to-peer cloud replication for multi-counter billing and distributed store management.", "Distributed Ledger Sync", COLOR_PURPLE),
        ("🧾 Automated GST Filing", "Automating tax categorization and generating one-click ready-to-file GSTR-1 and GSTR-3B tax compliance spreadsheets.", "Automated Compliance", COLOR_BLUE)
    ]
    for i, (title, desc, tag, col) in enumerate(futures):
        x = Inches(0.8) + i * Inches(3.0)
        y = Inches(1.9)
        create_card(s22, x, y, card_w4, card_h4, col)
        tb = s22.shapes.add_textbox(x + Inches(0.2), y + Inches(0.3), card_w4 - Inches(0.4), card_h4 - Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_SLATE

        p_t = tf.add_paragraph()
        p_t.text = f"\nRoadmap Target:\n{tag}"
        p_t.font.name = FONT_MONO
        p_t.font.size = Pt(9)
        p_t.font.bold = True
        p_t.font.color.rgb = col

    # =========================================================================
    # SLIDE 23: CONCLUSION & Q&A
    # =========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    set_slide_background(s23)
    add_slide_theme_background(s23, "conclusion")

    pill23 = s23.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.166), Inches(0.8), Inches(5.0), Inches(0.4))
    pill23.fill.solid()
    pill23.fill.fore_color.rgb = RGBColor(10, 25, 55)
    pill23.line.color.rgb = COLOR_GREEN
    pill23.line.width = Pt(1.2)
    p = pill23.text_frame.paragraphs[0]
    p.text = "● FINAL DEFENSE • CONCLUDING REMARKS"
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p.alignment = PP_ALIGN.CENTER

    t23 = s23.shapes.add_textbox(Inches(1.0), Inches(1.4), Inches(11.333), Inches(0.8))
    p = t23.text_frame.paragraphs[0]
    p.text = "Conclusion & Q&A"
    p.font.name = FONT_TITLE
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN
    p.alignment = PP_ALIGN.CENTER

    create_card(s23, Inches(1.8), Inches(2.4), Inches(9.733), Inches(1.8), COLOR_CYAN)
    tb_c = s23.shapes.add_textbox(Inches(2.0), Inches(2.55), Inches(9.333), Inches(1.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "EXECUTIVE SUMMARY:"
    p.font.name = FONT_MONO
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    p_d = tf_c.add_paragraph()
    p_d.text = "VernaLedger.AI successfully bridges the deep technological chasm between cutting-edge Artificial Intelligence and India's millions of rural kirana merchants. By marrying multimodal Gemini Flash vision, Marathi voice processing, and a resilient ACID SQLite ledger, we transform complex bookkeeping into a 4.5-second effortless experience."
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(11.5)
    p_d.font.color.rgb = COLOR_WHITE

    qa_box = s23.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.5), Inches(4.5), Inches(8.333), Inches(1.8))
    qa_box.fill.solid()
    qa_box.fill.fore_color.rgb = RGBColor(10, 25, 45)
    qa_box.line.color.rgb = COLOR_GREEN
    qa_box.line.width = Pt(1.5)

    tf_qa = qa_box.text_frame
    tf_qa.margin_top = Inches(0.2)
    p = tf_qa.paragraphs[0]
    p.text = "Thank You! Any Questions?"
    p.font.name = FONT_TITLE
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p.alignment = PP_ALIGN.CENTER

    p_names = tf_qa.add_paragraph()
    p_names.text = "Project Team: Sanket Kirdat • Sakshi Bhagat • Vaishnavi Dhavale • Rushikesh Mulik"
    p_names.font.name = FONT_BODY
    p_names.font.size = Pt(12)
    p_names.font.bold = True
    p_names.font.color.rgb = COLOR_WHITE
    p_names.alignment = PP_ALIGN.CENTER

    p_coll = tf_qa.add_paragraph()
    p_coll.text = "Department of Computer Engineering • Arvind Gavali College of Engineering, Satara • DBATU University"
    p_coll.font.name = FONT_MONO
    p_coll.font.size = Pt(9.5)
    p_coll.font.color.rgb = COLOR_CYAN
    p_coll.alignment = PP_ALIGN.CENTER

    # Save Presentation
    prs.save(OUTPUT_PPTX)
    print(f"Presentation successfully created at: {OUTPUT_PPTX}")

if __name__ == "__main__":
    create_deck()

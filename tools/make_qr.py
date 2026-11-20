#!/usr/bin/env python3
"""Branded, print-ready QR code for Maid Lifestyle.

Usage (run AFTER the site is live on its final domain):
    pip install qrcode pillow
    python3 tools/make_qr.py https://www.your-final-domain.com

Creates:  maid-lifestyle-qr.png  (2400x2900 px, ~8in @ 300dpi — scales down cleanly for cards/flyers)
          maid-lifestyle-qr-plain.png (QR only, for designers)
"""
import sys, os
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

if len(sys.argv) < 2 or not sys.argv[1].startswith("https://"):
    sys.exit("Give the FINAL published URL, e.g.  python3 tools/make_qr.py https://www.maidlifestyle.com")
url = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GREEN, DARK, GOLD = (27, 107, 51), (15, 61, 30), (201, 162, 74)

qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=40, border=2)
qr.add_data(url); qr.make(fit=True)
code = qr.make_image(fill_color=DARK, back_color="white").convert("RGB")
code.save("maid-lifestyle-qr-plain.png")

W, H = 2400, 2900
card = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(card)
d.rounded_rectangle((40, 40, W - 40, H - 40), radius=120, outline=GREEN, width=28)
d.rounded_rectangle((90, 90, W - 90, H - 90), radius=90, outline=GOLD, width=6)

logo = Image.open(os.path.join(ROOT, "assets/img/logo-tagline.png")).convert("RGBA")
logo.thumbnail((1500, 820))
card.paste(logo, ((W - logo.width) // 2, 170), logo)

code = code.resize((1500, 1500), Image.NEAREST)
top = 170 + logo.height + 60
card.paste(code, ((W - 1500) // 2, top))

def font(size):
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "/Library/Fonts/Georgia Bold.ttf", "C:/Windows/Fonts/georgiab.ttf"]:
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()
cap = "Scan to Visit Maid Lifestyle"
f = font(120)
tw = d.textlength(cap, font=f)
d.text(((W - tw) / 2, top + 1500 + 60), cap, fill=DARK, font=f)
card.save("maid-lifestyle-qr.png", dpi=(300, 300))
print("Saved maid-lifestyle-qr.png and maid-lifestyle-qr-plain.png ->", url)

"""Draw the crawler's favicon (SVG + 180 px PNG) and the 1200x630 link preview image.

  python make_icons.py      (writes favicon.svg, apple-touch-icon.png, og.png next to this script)
The creature is drawn the way the page draws it: gridded square plates down a curved spine,
long jointed legs fanning out, longer toward the tail, dots at the joints.
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BG = (5, 6, 8)
LEG, JOINT, PLATE, CELL = (95, 174, 69), (216, 242, 58), (232, 210, 58), (244, 224, 74)


def spine(n, cx, cy, length, bend):
    """Points along a gentle S-curve, head first."""
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = cx + (t - 0.5) * length
        y = cy + math.sin(t * math.pi * 1.2 + 0.4) * bend
        pts.append((x, y))
    return pts


def creature(draw, pts, plate, leg_len, width=2, joint_r=3):
    n = len(pts)
    for i in range(1, n):  # legs first, under the plates
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        ang = math.atan2(y0 - y1, x0 - x1)
        t = (i - 1) / max(1, n - 2)
        for side in (-1, 1):
            nx, ny = -math.sin(ang) * side, math.cos(ang) * side
            fan = 0.6 - 1.05 * t
            dx = nx * math.cos(fan) + math.cos(ang) * math.sin(fan)
            dy = ny * math.cos(fan) + math.sin(ang) * math.sin(fan)
            L = leg_len * (0.85 + 0.55 * t) * (1.15 if i == n - 1 else 1)
            hip = (x1 + nx * plate * 0.45, y1 + ny * plate * 0.45)
            knee = (hip[0] + dx * L * 0.45 + nx * L * 0.12, hip[1] + dy * L * 0.45 + ny * L * 0.12)
            foot = (hip[0] + dx * L, hip[1] + dy * L)
            draw.line([hip, knee, foot], fill=LEG, width=width)
            for p in (hip, knee, foot):
                draw.ellipse([p[0] - joint_r, p[1] - joint_r, p[0] + joint_r, p[1] + joint_r], fill=JOINT)
    for i, (x, y) in enumerate(reversed(pts)):  # plates, tail first so the head sits on top
        s = plate * (1.1 if i == n - 1 else 1 - 0.3 * (1 - i / n))
        box = [x - s / 2, y - s / 2, x + s / 2, y + s / 2]
        draw.rectangle(box, fill=BG, outline=PLATE, width=width)
        draw.line([x, y - s / 2, x, y + s / 2], fill=PLATE, width=max(1, width - 1))
        draw.line([x - s / 2, y, x + s / 2, y], fill=PLATE, width=max(1, width - 1))
        if i % 3 == 0 or i == n - 1:
            q = s / 2 - 3
            draw.rectangle([x - s / 2 + 3, y - s / 2 + 3, x - s / 2 + 3 + q - 3, y - s / 2 + 3 + q - 3], fill=CELL)


def glow(img):
    """Soft neon bloom: a blurred copy added under the sharp drawing."""
    blur = img.filter(ImageFilter.GaussianBlur(6))
    return Image.eval(Image.blend(blur, img, 0.6), lambda v: min(255, int(v * 1.25)))


# ---- link preview, 1200 x 630 ----
W, H = 1200, 630
og = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(og)
for x in range(0, W, 120):
    d.line([x, 0, x, H], fill=(16, 18, 24))
for y in range(0, H, 120):
    d.line([0, y, W, y], fill=(16, 18, 24))
creature(d, spine(15, 660, 370, 600, 60), plate=34, leg_len=125, width=3, joint_r=4)
og = glow(og)
d = ImageDraw.Draw(og)
try:
    title = ImageFont.truetype("georgiab.ttf", 72)
    mono = ImageFont.truetype("consola.ttf", 26)
except OSError:
    title = mono = ImageFont.load_default()
d.text((64, 70), "SPECIMEN · FIELD NOTES", font=mono, fill=(108, 113, 126))
d.text((64, 108), "Crawler Field Notes", font=title, fill=(233, 235, 242))
d.text((64, 540), "A many-legged creature that walks the page", font=mono, fill=(169, 173, 184))
og.save(os.path.join(HERE, "og.png"), optimize=True)

# ---- touch icon, 180 x 180 ----
ic = Image.new("RGB", (180, 180), BG)
creature(ImageDraw.Draw(ic), spine(6, 92, 90, 104, 8), plate=20, leg_len=34, width=3, joint_r=3)
glow(ic).save(os.path.join(HERE, "apple-touch-icon.png"), optimize=True)

# ---- favicon, SVG (crisp at any size) ----
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">',
       '<rect width="64" height="64" rx="12" fill="#050608"/>',
       '<g stroke="#5fae45" stroke-width="2.4" stroke-linecap="round" fill="none">']
for i, x in enumerate((18, 27, 36, 45)):
    k = 4 + i * 2.5
    svg.append(f'<path d="M{x} 32 L{x - 6 + i} {32 - 10 - k} L{x - 10 + i} {32 - 18 - k / 2}"/>')
    svg.append(f'<path d="M{x} 32 L{x - 6 + i} {32 + 10 + k} L{x - 10 + i} {32 + 18 + k / 2}"/>')
svg.append('</g><g fill="#050608" stroke="#e8d23a" stroke-width="2.4">')
for x in (14, 23, 32, 41, 50):
    svg.append(f'<rect x="{x - 4.5}" y="27.5" width="9" height="9"/>')
svg.append('</g><circle cx="50" cy="32" r="2.4" fill="#f4e04a"/></svg>')
open(os.path.join(HERE, "favicon.svg"), "w", encoding="utf8").write("".join(svg))
print("wrote og.png, apple-touch-icon.png, favicon.svg")

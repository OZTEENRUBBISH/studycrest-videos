"""Shared StudyCrest brand helpers: fonts, real logo (from the app's SVG), emoji, colours."""
import os
BASE = os.path.dirname(os.path.abspath(__file__))
from PIL import Image, ImageDraw, ImageFont

_fc = {}
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-%sVariable.ttf"
CAVEAT = BASE + "/fonts/caveat/fonts/ttf/Caveat-%s.ttf"
def font(weight, size):
    """Inter weights by name; 'Serif'/'SerifBold'/'SerifItalic' = Lora; 'Hand'/'HandBold' = Caveat."""
    k = (weight, int(size))
    if k not in _fc:
        if weight.startswith("Serif"):
            f = ImageFont.truetype(LORA % ("Italic-" if "Italic" in weight else ""), int(size))
            f.set_variation_by_name(("Bold Italic" if "Bold" in weight else "SemiBold Italic") if "Italic" in weight else ("Bold" if "Bold" in weight else "SemiBold"))
        elif weight.startswith("Hand"): f = ImageFont.truetype(CAVEAT % ("Bold" if "Bold" in weight else "Regular"), int(size))
        else: f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-%s.otf" % weight, int(size))
        _fc[k] = f
    return _fc[k]
TICKFONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLUE, BLUE2 = (58, 99, 230), (30, 58, 168)      # #3A63E6 -> #1E3AA8, the app's logo gradient
RED, GREEN = (228, 62, 62), (20, 150, 95)
THEMES = {
    "navy":  dict(bg=(12, 16, 40),    fg=(255, 255, 255), mute=(160, 170, 205), acc=(96, 132, 255), card=(248, 249, 253), ink=(22, 26, 48)),
    "light": dict(bg=(244, 246, 255), fg=(16, 20, 48),    mute=(96, 104, 140),  acc=BLUE,           card=(255, 255, 255), ink=(22, 26, 48)),
    "paper": dict(bg=(247, 245, 240), fg=(20, 22, 31),    mute=(107, 112, 128), acc=(47, 86, 214),  card=(255, 255, 255), ink=(20, 22, 31)),
    "ink":   dict(bg=(16, 18, 28),    fg=(244, 242, 236), mute=(150, 156, 176), acc=(122, 152, 255), card=(255, 255, 255), ink=(20, 22, 31)),
    "blue":  dict(bg=(42, 74, 214),   fg=(255, 255, 255), mute=(205, 214, 255), acc=(255, 214, 74), card=(255, 255, 255), ink=(22, 26, 48)),
}
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def mix(a, b, t): t = max(0.0, min(1.0, t)); return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

_lc = {}
def logo(size):
    """The StudyCrest app icon, redrawn from the SVG served by app.studycrest.app (viewBox 5 5 90 90)."""
    if size in _lc: return _lc[size]
    S = size * 4; k = S / 90.0; P = lambda x, y: ((x - 5) * k, (y - 5) * k)
    grad = Image.new("RGB", (S, S)); px = grad.load()
    for y in range(S):
        for x in range(0, S):
            px[x, y] = mix(BLUE, BLUE2, (x + y) / (2.0 * S))
    mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), int(21 * k), fill=255)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); im.paste(grad, (0, 0), mask); d = ImageDraw.Draw(im)
    d.polygon([P(30, 40), P(30, 24), P(40, 32), P(50, 20), P(60, 32), P(70, 24), P(70, 40)], fill=(255, 255, 255))
    pts = [P(30, 60), P(44, 73), P(70, 48)]; w = int(9 * k)
    d.line(pts, fill=(255, 255, 255), width=w, joint="curve")
    for (x, y) in pts: d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=(255, 255, 255))
    _lc[size] = im.resize((size, size), Image.LANCZOS); return _lc[size]

_ec = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _ec:
        f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((12, 12), ch, font=f, embedded_color=True)
        _ec[k] = im.crop(im.getbbox()).resize((size, size), Image.LANCZOS)
    return _ec[k]

def fit(d, text, weight, size, maxw, floor=30):
    while size > floor and d.textlength(text, font=font(weight, size)) > maxw: size -= 2
    return font(weight, size)

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines

def centered(d, W, y, text, f, fill):
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)

def header(im, d, T, W, y=140, size=76):
    f = font("ExtraBold", int(size * 0.84)); w = d.textlength("StudyCrest", font=f); x = int((W - w - size - 22) / 2)
    im.paste(logo(size), (x, y), logo(size))
    d.text((x + size + 22, y + size * 0.06), "StudyCrest", font=f, fill=T["fg"])

def rounded(img, radius):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.size[0] - 1, img.size[1] - 1), radius, fill=255)
    out = img.convert("RGBA"); out.putalpha(m); return out

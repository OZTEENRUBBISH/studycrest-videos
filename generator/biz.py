"""StudyCrest Business swipe posts (1080x1350): editorial layout, real photos, serif headlines.

Usage:  python3 biz.py            -> render every post in biz_posts.json
        python3 biz.py <slug>...  -> render only those posts
Output: ../queue/business/posts/<slug>/slide-N.jpg

Posts are data (biz_posts.json). Photos live in biz_photos/ (see biz_photos/credits.json).
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
from brand import BASE, font, logo, wrap, rounded, mix

W, H = 1080, 1350
PAPER, INK, BLUE, SKY = (246, 243, 236), (14, 24, 54), (58, 99, 230), (150, 180, 255)
MUTE, RULE, CARD, RED, GREEN = (104, 110, 130), (221, 216, 204), (255, 255, 255), (206, 60, 60), (22, 140, 92)
M = 72                                   # side margin
PHOTOS = BASE + "/biz_photos/"
OUT = os.path.normpath(BASE + "/../queue/business/posts") + "/"
HANDLE = "@studycrestbusiness"


def photo(name, w, h, focus=0.5):
    """Cover-crop a library photo to w x h. focus = horizontal centre of the crop (0..1)."""
    im = Image.open(PHOTOS + name + ".jpg").convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x = int((im.width - w) * focus); y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def shadow_card(im, box, radius=28, fill=CARD, outline=None):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 10, x1, y1 + 14), radius, fill=(14, 24, 54, 46))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).rounded_rectangle(box, radius, fill=fill, outline=outline)


def rich(d, x, y, text, f, fill, maxw, lh, hl=SKY, underline=True, hl_fill=None):
    """Wrapped text; words inside *asterisks* get an accent underline. Returns the y after the last line."""
    words = []
    on = False
    for tok in text.split():
        start = tok.startswith("*"); end = tok.rstrip(".,?!:;").endswith("*")
        if start: on = True
        words.append((tok.replace("*", ""), on))
        if end: on = False
    lines, cur = [], []
    for wd in words:
        t = " ".join(w for w, _ in cur + [wd])
        if d.textlength(t, font=f) <= maxw or not cur: cur.append(wd)
        else: lines.append(cur); cur = [wd]
    if cur: lines.append(cur)
    sp = d.textlength(" ", font=f)
    asc, desc = f.getmetrics()
    for ln in lines:
        cx = x; run = None
        for wd, h in ln:
            wl = d.textlength(wd, font=f)
            if h:
                run = [cx if run is None else run[0], cx + wl]
            if (not h) and run:
                d.rectangle((run[0], y + asc + 4, run[1], y + asc + 4 + max(6, f.size // 11)), fill=hl); run = None
            cx += wl + sp
        if run: d.rectangle((run[0], y + asc + 4, run[1], y + asc + 4 + max(6, f.size // 11)), fill=hl)
        cx = x
        for wd, h in ln:
            d.text((cx, y), wd, font=f, fill=(hl_fill if (h and hl_fill) else fill)); cx += d.textlength(wd, font=f) + sp
        y += lh
    return y


def brandmark(im, d, x, y, fill, size=46, label="StudyCrest Business"):
    im.paste(logo(size), (x, y), logo(size))
    d.text((x + size + 14, y + size / 2), label, font=font("SemiBold", int(size * 0.56)), fill=fill, anchor="lm")


def footer(im, d, i, n, source=None, dark=False):
    fg = (190, 198, 224) if dark else MUTE
    y = H - 104
    d.line((M, y, W - M, y), fill=(52, 64, 104) if dark else RULE, width=2)
    brandmark(im, d, M, y + 26, (255, 255, 255) if dark else INK, 40)
    d.text((W - M, y + 46), f"{i + 1} / {n}", font=font("SemiBold", 24), fill=fg, anchor="rm")
    if source:
        d.text((M, y - 22), source, font=font("Regular", 21), fill=fg, anchor="lm")


def kicker(d, x, y, text, fill=BLUE):
    f = font("Bold", 24); cx = x
    for ch in text.upper():
        d.text((cx, y), ch, font=f, fill=fill); cx += d.textlength(ch, font=f) + 3.2
    return y + 44


# ───────────────────────── slide types ─────────────────────────

def s_cover(s, i, n):
    im = Image.new("RGB", (W, H), INK); PH = 800
    im.paste(photo(s["photo"], W, PH, s.get("focus", 0.5)), (0, 0))
    # fade the photo into the navy panel, and darken the top edge for the brand mark
    g = Image.new("L", (1, PH), 0)
    for y in range(PH):
        a = 0
        if y < 240: a = int(215 * (1 - y / 240) ** 1.5)
        if y > PH - 330: a = max(a, int(255 * ((y - (PH - 330)) / 330) ** 1.5))
        g.putpixel((0, y), a)
    im.paste(Image.new("RGB", (W, PH), INK), (0, 0), g.resize((W, PH)))
    d = ImageDraw.Draw(im)
    brandmark(im, d, M, 64, (255, 255, 255), 52)
    y = kicker(d, M, 742, s["kicker"], SKY) + 6
    size = s.get("size", 82)
    while size > 60 and len(wrap(d, s["title"].replace("*", ""), font("SerifBold", size), W - 2 * M)) > 3: size -= 2
    f = font("SerifBold", size)
    y = rich(d, M, y, s["title"], f, (255, 255, 255), W - 2 * M, int(f.size * 1.14), hl=BLUE)
    if s.get("sub"):
        fs = font("Regular", 33)
        for ln in wrap(d, s["sub"], fs, W - 2 * M): d.text((M, y + 34), ln, font=fs, fill=(196, 204, 230)); y += 46
    d.text((M, H - 86), HANDLE, font=font("Medium", 26), fill=(160, 172, 210), anchor="lm")
    fa = font("SemiBold", 26); t = "Swipe"; tw = d.textlength(t, font=fa)
    d.text((W - M - 58 - tw, H - 86), t, font=fa, fill=(255, 255, 255), anchor="lm")
    d.line((W - M - 44, H - 86, W - M, H - 86), fill=(255, 255, 255), width=3)
    d.line((W - M - 14, H - 98, W - M, H - 86, W - M - 14, H - 74), fill=(255, 255, 255), width=3, joint="curve")
    return im


def s_role(s, i, n):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    PW, PH = W - 2 * 48, 560
    ph = rounded(photo(s["photo"], PW, PH, s.get("focus", 0.5)), 30); im.paste(ph, (48, 48), ph)
    lab = s["label"]; f = font("Bold", 24); tw = d.textlength(lab, font=f)
    d.rounded_rectangle((76, 76, 76 + tw + 40, 76 + 50), 25, fill=(255, 255, 255)); d.text((96, 101), lab, font=f, fill=INK, anchor="lm")
    y = 660
    ft = font("SerifBold", s.get("size", 66))
    for ln in wrap(d, s["title"], ft, W - 2 * M): d.text((M, y), ln, font=ft, fill=INK); y += int(ft.size * 1.13)
    y += 14; fb = font("Regular", 33)
    for b in s["lines"]:
        d.rectangle((M, y + 22, M + 22, y + 25), fill=BLUE)
        for ln in wrap(d, b, fb, W - 2 * M - 44): d.text((M + 44, y), ln, font=fb, fill=(52, 60, 86)); y += 46
        y += 10
    # stat card, centred in the space left above the source line
    bottom = H - 104 - 52; ch = 176; cy = max(y + 26, y + (bottom - y - ch) // 2)
    shadow_card(im, (M, cy, W - M, cy + ch)); d = ImageDraw.Draw(im)
    fs = font("SerifBold", 96)
    d.text((M + 40, cy + ch / 2 - 4), s["stat"], font=fs, fill=INK, anchor="lm")
    sw = d.textlength(s["stat"], font=fs)
    fl = font("Medium", 27); ly = cy + ch / 2 - 36
    for ln in s["stat_label"].split("|"): d.text((M + 40 + sw + 30, ly), ln, font=fl, fill=MUTE); ly += 38
    footer(im, d, i, n, s.get("source"))
    return im


def s_concept(s, i, n, off=0):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    y = kicker(d, M, 96 + off, s["label"]) + 10
    ft = font("SerifBold", s.get("size", 78))
    for ln in wrap(d, s["title"], ft, W - 2 * M): d.text((M, y), ln, font=ft, fill=INK); y += int(ft.size * 1.12)
    y += 34
    # formula card
    ff = font("SerifItalic", 46); flines = s["formula"].split("|")
    ch = 96 + len(flines) * 64
    shadow_card(im, (M, y, W - M, y + ch)); d = ImageDraw.Draw(im)
    d.text((M + 40, y + 30), "FORMULA", font=font("Bold", 20), fill=MUTE)
    fy = y + 66
    for ln in flines: d.text((M + 40, fy), ln, font=ff, fill=INK); fy += 64
    y += ch + 34
    # worked example card (navy)
    elines = s["example"].split("|"); eh = 96 + len(elines) * 56
    shadow_card(im, (M, y, W - M, y + eh), fill=INK); d = ImageDraw.Draw(im)
    d.text((M + 40, y + 30), "WORKED EXAMPLE", font=font("Bold", 20), fill=SKY)
    ey = y + 68
    for k, ln in enumerate(elines):
        last = k == len(elines) - 1
        d.text((M + 40, ey), ln, font=font("SemiBold" if last else "Regular", 38), fill=(255, 255, 255) if last else (206, 214, 240)); ey += 56
    y += eh + 44
    d.text((M, y), "WHAT IT TELLS YOU", font=font("Bold", 20), fill=BLUE); y += 38
    fb = font("Regular", 34)
    for ln in wrap(d, s["tells"], fb, W - 2 * M): d.text((M, y), ln, font=fb, fill=(52, 60, 86)); y += 48
    footer(im, d, i, n, s.get("source"))
    return im, y


def s_mistake(s, i, n, off=0):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    y = kicker(d, M, 96 + off, s["label"]) + 10
    ft = font("SerifBold", s.get("size", 72))
    for ln in wrap(d, s["title"], ft, W - 2 * M): d.text((M, y), ln, font=ft, fill=INK); y += int(ft.size * 1.12)
    y += 20; fb = font("Regular", 33)
    for ln in wrap(d, s["body"], fb, W - 2 * M): d.text((M, y), ln, font=fb, fill=(52, 60, 86)); y += 47
    y += 36
    for tag, col, text in (("THE SLIP", RED, s["wrong"]), ("THE FIX", GREEN, s["right"])):
        lines = text.split("|"); ch = 84 + len(lines) * 54
        shadow_card(im, (M, y, W - M, y + ch)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((M, y, M + 12, y + ch), 6, fill=col)
        d.text((M + 44, y + 28), tag, font=font("Bold", 20), fill=col)
        ly = y + 62
        for ln in lines: d.text((M + 44, ly), ln, font=font("Medium", 36), fill=INK); ly += 54
        y += ch + 30
    footer(im, d, i, n, s.get("source"))
    return im, y


def s_working(s, i, n, off=0):
    """A worked answer on a card. 'flag' = index of the wrong line (shown only when reveal is true)."""
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    y = kicker(d, M, 96 + off, s["label"]) + 10
    ft = font("SerifBold", s.get("size", 66))
    y = rich(d, M, y, s["title"], ft, INK, W - 2 * M, int(ft.size * 1.13), hl=SKY) + 18
    fq = font("Regular", 32)
    for ln in wrap(d, s["question"], fq, W - 2 * M): d.text((M, y), ln, font=fq, fill=(52, 60, 86)); y += 46
    y += 30
    rows = s["lines"]; rh = 104; ch = 40 + len(rows) * rh
    shadow_card(im, (M, y, W - M, y + ch)); d = ImageDraw.Draw(im)
    reveal = s.get("reveal", False); flag = s.get("flag", -1)
    for k, ln in enumerate(rows):
        ry = y + 20 + k * rh; bad = reveal and k == flag
        if bad: d.rounded_rectangle((M + 14, ry + 6, W - M - 14, ry + rh - 6), 18, fill=(253, 236, 234))
        d.ellipse((M + 34, ry + 30, M + 78, ry + 74), fill=RED if bad else (236, 239, 250))
        d.text((M + 56, ry + 52), str(k + 1), font=font("Bold", 24), fill=(255, 255, 255) if bad else BLUE, anchor="mm")
        d.text((M + 104, ry + 52), ln, font=font("Medium", 37), fill=RED if bad else INK, anchor="lm")
        if k < len(rows) - 1: d.line((M + 104, ry + rh, W - M - 34, ry + rh), fill=(236, 233, 224), width=2)
    y += ch + 36
    if reveal:
        lines = s["fix"].split("|"); fh = 84 + len(lines) * 54
        shadow_card(im, (M, y, W - M, y + fh), fill=INK); d = ImageDraw.Draw(im)
        d.text((M + 40, y + 28), "CORRECTED", font=font("Bold", 20), fill=SKY); ly = y + 62
        for k, ln in enumerate(lines):
            d.text((M + 40, ly), ln, font=font("SemiBold" if k == len(lines) - 1 else "Regular", 37), fill=(255, 255, 255)); ly += 54
        y += fh
    elif s.get("prompt"):
        fp = font("SerifItalic", 40)
        for ln in wrap(d, s["prompt"], fp, W - 2 * M): d.text((M, y), ln, font=fp, fill=BLUE); y += 54
    footer(im, d, i, n)
    return im, y


def s_statement(s, i, n, off=0):
    dark = s.get("dark", True)
    im = Image.new("RGB", (W, H), INK if dark else PAPER); d = ImageDraw.Draw(im)
    fg = (255, 255, 255) if dark else INK
    y = kicker(d, M, 110 + off, s["label"], SKY if dark else BLUE) + 24
    ft = font("SerifBold", s.get("size", 76))
    y = rich(d, M, y, s["title"], ft, fg, W - 2 * M, int(ft.size * 1.16), hl=BLUE if dark else SKY) + 30
    fb = font("Regular", 35)
    for para in s.get("body", []):
        for ln in wrap(d, para, fb, W - 2 * M): d.text((M, y), ln, font=fb, fill=(206, 214, 240) if dark else (52, 60, 86)); y += 50
        y += 22
    footer(im, d, i, n, dark=dark)
    return im, y


def s_app(s, i, n, off=0):
    """A real StudyCrest screen (from app/) on a card, with a headline and one line under it."""
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    y = kicker(d, M, 96 + off, s["label"]) + 10
    ft = font("SerifBold", s.get("size", 68))
    y = rich(d, M, y, s["title"], ft, INK, W - 2 * M, int(ft.size * 1.13), hl=SKY) + 30
    shot = Image.open(BASE + "/app/" + s["shot"]).convert("RGB")
    if s.get("crop"): shot = shot.crop(tuple(s["crop"]))
    cw = W - 2 * M - 40; sc = min(cw / shot.width, s.get("max_h", 560) / shot.height)
    shot = shot.resize((int(shot.width * sc), int(shot.height * sc)), Image.LANCZOS)
    ch = shot.height + 40
    shadow_card(im, (M, y, W - M, y + ch)); d = ImageDraw.Draw(im)
    r = rounded(shot, 14); im.paste(r, (M + (W - 2 * M - shot.width) // 2, y + 20), r)
    y += ch + 40; fb = font("Regular", 34)
    for para in s.get("body", []):
        d.rectangle((M, y + 22, M + 22, y + 25), fill=BLUE)
        for ln in wrap(d, para, fb, W - 2 * M - 44): d.text((M + 44, y), ln, font=fb, fill=(52, 60, 86)); y += 48
        y += 12
    footer(im, d, i, n)
    return im, y


def s_cta(s, i, n):
    im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
    # soft blue glow behind the logo
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((W / 2 - 330, 40, W / 2 + 330, 560), fill=(58, 99, 230, 70))
    gl = gl.filter(ImageFilter.GaussianBlur(120)); im.paste(gl, (0, 0), gl); d = ImageDraw.Draw(im)
    L = logo(132); im.paste(L, ((W - 132) // 2, 150), L)
    y = 340; ft = font("SerifBold", 82)
    for ln in ["Try StudyCrest", "free for 30 days"]:
        d.text((W / 2, y), ln, font=ft, fill=(255, 255, 255), anchor="ma"); y += 96
    y += 44
    rows = ["$0 for your first 30 days", "Cancel before day 30 and you're never charged", "Promo code in the bio at @studycrestapp"]
    fr = font("Medium", 34)
    for r in rows:
        d.ellipse((M + 20, y + 4, M + 64, y + 48), fill=BLUE)
        d.line((M + 32, y + 27, M + 40, y + 35, M + 53, y + 18), fill=(255, 255, 255), width=4, joint="curve")
        d.text((M + 88, y + 26), r, font=fr, fill=(232, 236, 250), anchor="lm"); y += 78
    y += 30
    fb = font("Bold", 36); t = "studycrest.app"; tw = d.textlength(t, font=fb)
    d.rounded_rectangle(((W - tw) / 2 - 56, y, (W + tw) / 2 + 56, y + 92), 46, fill=(255, 255, 255))
    d.text((W / 2, y + 46), t, font=fb, fill=INK, anchor="mm")
    d.text((W / 2, y + 140), s.get("note", "Checks every line of your working while you write."), font=font("Regular", 28), fill=(160, 172, 210), anchor="ma")
    footer(im, d, i, n, dark=True)
    return im


TYPES = {"cover": s_cover, "role": s_role, "concept": s_concept, "mistake": s_mistake, "working": s_working,
         "statement": s_statement, "app": s_app, "cta": s_cta}


def render(slug, post):
    os.makedirs(OUT + slug, exist_ok=True); n = len(post["slides"])
    for i, s in enumerate(post["slides"]):
        out = TYPES[s["type"]](s, i, n)
        if isinstance(out, tuple):                      # centre the content block vertically
            slack = (H - 104 - 70) - out[1]
            out = TYPES[s["type"]](s, i, n, int(slack * 0.42))[0] if slack > 60 else out[0]
        out.save(f"{OUT}{slug}/slide-{i + 1}.jpg", quality=93, subsampling=0)
    return n


if __name__ == "__main__":
    posts = json.load(open(BASE + "/biz_posts.json"))
    for slug in (sys.argv[1:] or posts):
        print(slug, render(slug, posts[slug]), "slides")

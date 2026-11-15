"""StudyCrest 'Spot the mistake' ad, v2 (15 Nov 2026): built to hold attention.
The hook is on screen in the first frame (a finished answer stamped WRONG), a 3-2-1 countdown gives the viewer a job,
then the flag, the fix and the offer. Dark, high-contrast look, big one-chunk captions, everything inside TikTok's
safe area (nothing in the top 150 px, the bottom 380 px or the right 150 px).
Uses the SPOTS data in pilot.py.  Usage: pilot2.py stills <key> [t ...] | pilot2.py render <key> <out.mp4>"""
import os, sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from brand import *
import pilot as P

BASE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
NAVY, NAVY2, WHITE, MUTE = (10, 14, 38), (26, 38, 96), (255, 255, 255), (168, 178, 214)
YEL, RED, GRN, BLU, INK = (255, 214, 74), (255, 72, 72), (22, 160, 100), (58, 99, 230), (20, 22, 31)
FLAG, PEACH, HINT, HANDINK, GREY = (214, 52, 30), (255, 238, 228), (158, 52, 18), (28, 36, 96), (178, 182, 198)
CARD = (50, 520, 940, 1372)              # stays left of TikTok's buttons
CAP_Y = 1408                              # captions: one big chunk at a time

HOOKS = {   # opening headline (two lines, second in red) and what the voice says over it
    "default": (("This answer", "is WRONG."), "This answer is wrong! Can you spot why?"),
    "one-line": (("One line here", "is WRONG."), "One line here is wrong! Can you find it?"),
    "marks": (("This slip costs", "the whole question."), "This one slip costs the whole question! See it?"),
}

def times(S):
    c0, c1 = 2.55, 5.25; check = [c1 + 0.12 + 0.22 * i for i in range(3)]; flag = check[S["wrong"]]
    pay = check[2] + 3.75; end = pay + 2.6
    return dict(stamp=0.30, count=(c0, c1), check=check, hint=flag + 0.5, fix=flag + 1.55, final=flag + 2.45, pay=pay, end=end, total=end + 3.3)

def script(S):
    """Voice lines as (start, text, speed). Short, loud, and the first word lands in the first tenth of a second."""
    T = times(S); c0, c1 = T["count"]; st = (c1 - c0) / 3
    return [(0.04, HOOKS[S.get("hook", "default")][1], 1.2),
            (c0 + 0.02, "Three!", 1.15), (c0 + st + 0.02, "Two!", 1.15), (c0 + 2 * st + 0.02, "One!", 1.15),
            (T["check"][S["wrong"]] + 0.22, S["say_flag"], 1.22),
            (T["pay"] + 0.08, "StudyCrest catches it while you're still writing!", 1.2),
            (T["end"] + 0.22, "Try it free for thirty days! Promo code in bio!", 1.2)]

_bg = None
def background():
    global _bg
    if _bg is None:                       # navy with a soft blue glow behind the card
        g = Image.new("L", (W // 8, H // 8), 0); ImageDraw.Draw(g).ellipse((-20, 40, W // 8 + 20, 200), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(26)).resize((W, H), Image.BICUBIC)
        _bg = Image.composite(Image.new("RGB", (W, H), NAVY2), Image.new("RGB", (W, H), NAVY), g)
    return _bg

def badge(im, d):
    """Brand and offer, top-left, from the first frame to the last."""
    lg = logo(64); im.paste(lg, (56, 168), lg); d.text((136, 166), "StudyCrest", font=font("ExtraBold", 40), fill=WHITE)
    d.text((137, 214), "Free for 30 days · code in bio", font=font("SemiBold", 25), fill=MUTE)

_static = {}
def card_base(S):
    if S["tag"] in _static: return _static[S["tag"]]
    im = background().copy(); d = ImageDraw.Draw(im); badge(im, d); x0, y0, x1, y1 = CARD; cw, ch = x1 - x0, y1 - y0
    sh, pad = P.shadowed((cw, ch), 40, alpha=150); im.paste(sh, (x0 - pad, y0 - pad), sh)
    card = Image.new("RGB", (cw, ch), WHITE); cd = ImageDraw.Draw(card)
    for gx in range(0, cw, 48): cd.line((gx, 0, gx, ch), fill=(236, 239, 250), width=2)
    for gy in range(0, ch, 48): cd.line((0, gy, cw, gy), fill=(236, 239, 250), width=2)
    cd.rectangle((0, 0, cw, 236), fill=WHITE); cd.line((0, 236, cw, 236), fill=(226, 229, 240), width=2)
    tf = font("Bold", 25); tw = cd.textlength(S["tag"], font=tf) + 34
    cd.rounded_rectangle((40, 32, 40 + tw, 76), 10, fill=(232, 238, 255)); cd.text((57, 39), S["tag"], font=tf, fill=BLU)
    qf = font("SemiBold", 35); y = 92
    for l in wrap(cd, S["q"], qf, cw - 80)[:3]: cd.text((40, y), l, font=qf, fill=INK); y += 45
    c = rounded(card, 40); im.paste(c, (x0, y0), c); _static[S["tag"]] = im; return im

def hand(im, text, xy, size, fill, progress=1.0, maxw=690):
    return P.hand(im, text, xy, size, fill, progress, maxw)

def headline(d, parts, t, size=104):
    """Heavy sans headline that snaps in. parts = [(text, colour)]."""
    for i, (text, col) in enumerate(parts):
        a = ease((t - 0.06 * i) / 0.22); f = fit(d, text, "Black", size, 850, 56)
        d.text((56, 268 + i * int(size * 1.08) + (1 - a) * 34), text, font=f, fill=mix(NAVY, col, a))

def stamp(im, text, cx, cy, t, col=FLAG, size=92):
    """Rubber stamp that slams down: starts big, lands in 0.14 s."""
    if t < 0: return
    f = font("Black", size); d0 = ImageDraw.Draw(im); tw = int(d0.textlength(text, font=f)); w, h = tw + 70, size + 56
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((5, 5, w - 6, h - 6), 18, outline=col + (255,), width=10); ld.text((35, 18), text, font=f, fill=col + (255,))
    s = 1 + 1.5 * (1 - ease(t / 0.14)); lay = lay.rotate(-9, expand=True, resample=Image.BICUBIC)
    if s > 1.01: lay = lay.resize((int(lay.size[0] * s), int(lay.size[1] * s)), Image.BICUBIC)
    a = min(1.0, t / 0.08)
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

def tick(d, cx, cy, a, col=BLU):
    d.line([(cx - 20, cy), (cx - 6, cy + 14), (cx + 22, cy - 16)], fill=mix(WHITE, col, a), width=9, joint="curve")
def flagmark(d, cx, cy, a):
    r = int(32 * (0.5 + 0.5 * a) * (1 + 0.5 * max(0, 1 - a))); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(WHITE, FLAG, a))
    d.text((cx - 7, cy - 27), "!", font=font("Black", 44), fill=WHITE)

def end_card(t):
    im = background().copy(); d = ImageDraw.Draw(im); badge(im, d)
    lg = logo(170); a = ease(t / 0.3); im.paste(lg, ((W - 170) // 2, int(430 + (1 - a) * 30)), lg)
    for i, (txt, col) in enumerate([("Try it FREE", WHITE), ("for 30 days.", YEL)]):
        aa = ease((t - 0.08 * i) / 0.3); centered(d, W, 650 + i * 128 + (1 - aa) * 30, txt, font("Black", 116), mix(NAVY, col, aa))
    b = ease((t - 0.35) / 0.35)
    centered(d, W, 940, "$0 for your first 30 days.", font("Bold", 50), mix(NAVY, WHITE, b))
    centered(d, W, 1010, "Cancel before day 30 and you're never charged.", font("Medium", 33), mix(NAVY, MUTE, b))
    c = ease((t - 0.6) / 0.35); pf = font("ExtraBold", 48); bw = d.textlength("Promo code in bio", font=pf) + 110
    pulse = 1 + 0.03 * math.sin(max(0, t - 0.9) * 7); bw *= pulse
    d.rounded_rectangle(((W - bw) / 2, 1100, (W + bw) / 2, 1206), 53, fill=mix(NAVY, YEL, c)); centered(d, W, 1123, "Promo code in bio", pf, mix(NAVY, NAVY, c))
    e = ease((t - 1.0) / 0.4); centered(d, W, 1262, "Did you get it? Comment the line.", font("Bold", 42), mix(NAVY, WHITE, e))
    centered(d, W, 1322, "A new one every day. Follow to play.", font("Medium", 34), mix(NAVY, MUTE, e)); return im

def compose(S, t):
    T = times(S)
    if t >= T["end"]: return end_card(t - T["end"])
    im = card_base(S).copy(); d = ImageDraw.Draw(im); x0, y0, x1, y1 = CARD; wr = S["wrong"]; chk = T["check"]; c0, c1 = T["count"]
    hk = HOOKS[S.get("hook", "default")][0]
    if t < c0: headline(d, [(hk[0], WHITE), (hk[1], RED)], t + 0.4)
    elif t < chk[0]: headline(d, [("Which line", WHITE), ("is the mistake?", YEL)], t - c0)
    elif t < T["pay"]: headline(d, [("StudyCrest flagged", WHITE), ("line %d." % (wr + 1), RED)], t - chk[0])
    else: headline(d, [("Caught while", WHITE), ("you're still writing.", YEL)], t - T["pay"])
    ly = [y0 + 246 + i * 104 for i in range(3)]; widths = []
    for i, text in enumerate(S["lines"]):                         # the finished working is there from the first frame
        p = (t + 0.42 - 0.1 * i) / 0.3; col = HANDINK
        if i == wr and t >= chk[i] + 0.1: col = mix(HANDINK, FLAG, (t - chk[i] - 0.1) / 0.25)
        if i > wr and t >= T["fix"]: col = mix(HANDINK, GREY, (t - T["fix"]) / 0.4)
        w = hand(im, text, (x0 + 48, ly[i]), 74, col, p); widths.append(w)
        if i >= wr and t >= T["fix"]:
            pp = ease((t - T["fix"]) / 0.3); d.line((x0 + 40, ly[i] + 58, x0 + 40 + (w + 16) * pp, ly[i] + 50), fill=FLAG if i == wr else GREY, width=7)
    # hook: red ring round the final answer and a WRONG stamp
    if T["stamp"] <= t < chk[0] + 0.3:
        fade = 1 - ease((t - chk[0]) / 0.3) if t > chk[0] else 1.0; a = ease((t - T["stamp"]) / 0.25); col = mix(WHITE, FLAG, fade)
        if fade > 0.05:
            bx = (x0 + 26, ly[2] - 8, x0 + 48 + widths[2] + 30, ly[2] + 104)
            d.arc(bx, -100, -100 + int(360 * a), fill=col, width=8)
            lay = im.copy(); stamp(lay, "WRONG", x1 - 230, ly[2] + 250, t - T["stamp"]); im.paste(Image.blend(im, lay, fade)); d = ImageDraw.Draw(im)
    # countdown: huge digit and a draining bar
    if c0 <= t < c1:
        p = (t - c0) / (c1 - c0); k = min(2, int(p * 3)); lt = (p * 3 - k); by = y1 - 78
        f = font("Black", int(190 * (1 + 0.35 * (1 - ease(lt / 0.25))))); num = str(3 - k); nw = d.textlength(num, font=f)
        d.text((x0 + 150 - nw / 2, ly[2] + 250 - f.size * 0.62), num, font=f, fill=BLU)
        d.rounded_rectangle((x0 + 48, by, x1 - 48, by + 20), 10, fill=(228, 231, 244))
        d.rounded_rectangle((x0 + 48, by, x0 + 48 + (x1 - x0 - 96) * (1 - p), by + 20), 10, fill=mix(BLU, FLAG, p))
    # the check: ticks and the flag, as in the app
    for i in range(3):
        if t < chk[i] or i > wr: continue
        a = ease((t - chk[i]) / 0.2); cx, cy = x1 - 74, ly[i] + 56
        flagmark(d, cx, cy, a) if i == wr else tick(d, cx, cy, a)
    if t >= T["hint"]:
        a = ease((t - T["hint"]) / 0.3); hy = ly[2] + 112; hf = fit(d, S["hint"], "SemiBold", 34, x1 - x0 - 180, 20)
        d.rounded_rectangle((x0 + 40, hy, x1 - 40, hy + 68), 20, fill=mix(WHITE, PEACH, a))
        d.ellipse((x0 + 60, hy + 18, x0 + 92, hy + 50), outline=mix(PEACH, HINT, a), width=5)
        d.text((x0 + 110, hy + 34 - hf.size * 0.62), S["hint"], font=hf, fill=mix(PEACH, HINT, a))
    if t >= T["fix"] + 0.1:
        fy = ly[2] + 190; hand(im, S["fix"], (x0 + 48, fy), 72, GRN, (t - T["fix"] - 0.1) / 0.7)
        if t >= T["fix"] + 0.85: tick(d, x1 - 74, fy + 54, ease((t - T["fix"] - 0.85) / 0.2), GRN)
    if t >= T["final"]:
        fy = ly[2] + 190 + 94; hand(im, S["final"], (x0 + 48, fy), 72, GRN, (t - T["final"]) / 0.7)
        if t >= T["final"] + 0.75: tick(d, x1 - 74, fy + 54, ease((t - T["final"] - 0.75) / 0.2), GRN)
    return im

_tm = {}
def timings(key):
    if key not in _tm:
        p = f"{BASE}/timings/v2-{key}.json"; _tm[key] = json.load(open(p)) if os.path.exists(p) else []
    return _tm[key]

def chunks(words, maxc=15):
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and (sum(len(x[1]) + 1 for x in cur) + len(w) > maxc or cur[-1][1][-1] in "!?.,"): out.append(cur); cur = []
        cur.append((i, w))
    if cur: out.append(cur)
    return out

def captions(im, key, t):
    """One short chunk of the voice line at a time, large, the spoken word in yellow."""
    for st, dur, text in timings(key):
        if text in ("Three!", "Two!", "One!"): continue
        if st - 0.03 <= t < st + dur + 0.25: break
    else: return
    words = text.split(); wts = [len(w) + 2 for w in words]; tot = float(sum(wts)); acc = 0; cur = len(words) - 1
    for i, wgt in enumerate(wts):
        if (t - st) < dur * (acc + wgt) / tot: cur = i; break
        acc += wgt
    ch = next(c for c in chunks(words) if c[-1][0] >= cur); d = ImageDraw.Draw(im); size = 76; sp = 20
    while size > 48 and sum(d.textlength(w, font=font("Black", size)) for _, w in ch) + sp * (len(ch) - 1) > 800: size -= 2
    f = font("Black", size); tw = sum(d.textlength(w, font=f) for _, w in ch) + sp * (len(ch) - 1); x = (W - tw) / 2
    pop = 1 - ease((t - st) / 0.12) if ch[0][0] == 0 else 0
    for i, w in ch:
        ww = d.textlength(w, font=f); y = CAP_Y + pop * 14
        d.text((x, y), w, font=f, fill=YEL if i == cur else WHITE, stroke_width=8, stroke_fill=NAVY); x += ww + sp

def shake(im, dt, amp):
    if not 0 <= dt < 0.28: return im
    k = (1 - dt / 0.28) ** 2 * amp; return ImageChops.offset(im, int(k * math.sin(dt * 95)), int(k * math.cos(dt * 80)))

def frame(S, t, key=None):
    T = times(S); im = compose(S, t); tf = T["check"][S["wrong"]]
    if tf <= t < min(tf + 1.5, T["end"]):                         # punch in on the flagged line, then ease back
        z = 1 + 0.12 * (ease((t - tf) / 0.16) if t < tf + 1.05 else 1 - ease((t - tf - 1.05) / 0.45))
        cx, cy = W / 2, CARD[1] + 246 + S["wrong"] * 104 + 56; w, h = W / z, H / z
        x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h); im = im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    im = shake(shake(im, t - T["stamp"], 16), t - tf, 20)
    if key: captions(im, key, t)
    d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 9), fill=(40, 48, 96)); d.rectangle((0, 0, W * min(1.0, t / T["total"]), 9), fill=YEL); return im

if __name__ == "__main__":
    key = sys.argv[2]; S = P.SPOTS[key]; T = times(S)
    if sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[3:]] or [0.1, 0.45, 1.5, 3.0, 4.9, 5.75, 6.6, 7.9, 9.0, 10.2, 12.4, 14.5]
        sheet = Image.new("RGB", (360 * min(6, len(ts)), 640 * ((len(ts) + 5) // 6)))
        for i, t in enumerate(ts): sheet.paste(frame(S, t, key).resize((360, 640), Image.LANCZOS), ((i % 6) * 360, (i // 6) * 640))
        sheet.save(f"{BASE}/pilot2-{key}.jpg", quality=88)
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", sys.argv[3]], stdin=subprocess.PIPE)
        for i in range(int(T["total"] * FPS)): p.stdin.write(frame(S, i / FPS, key).tobytes())
        p.stdin.close(); sys.exit(p.wait())

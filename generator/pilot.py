"""StudyCrest 'Spot the mistake' ad: paper look, handwritten working, a countdown, then the app-style check.
Usage: pilot.py stills <key> | pilot.py render <key> <out.mp4>"""
import os
BASE = os.path.dirname(os.path.abspath(__file__))
import subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
from brand import *

W, H, FPS = 1080, 1920, 30
PAPER, INK, MUTE, BLU = (247, 245, 240), (20, 22, 31), (107, 112, 128), (47, 86, 214)
FLAG, OK, PEACH, HINT = (200, 62, 26), (30, 142, 90), (255, 240, 230), (158, 52, 18)
HANDINK = (28, 36, 96)

def Q(a, b): return [(a, "Serif", INK), (b, "SerifItalic", BLU)]
def Q3(a, b, c): return [(a, "Serif", INK), (b, "Serif", INK), (c, "SerifItalic", BLU)]
SPOTS = {
 "nursing": dict(tag="NURSING · DRUG CALCULATIONS", q="1 L of saline is to run over 8 hours. The giving set delivers 20 drops/mL. Find the drip rate.",
    lines=["rate = volume × drop factor ÷ time", "= 1000 × 20 ÷ 8", "= 2500 drops/min"], wrong=1,
    hint="Hint: should the time be in hours or minutes?", fix="= 1000 × 20 ÷ 480", final="≈ 42 drops/min",
    say_flag="It's line two! Eight hours is four hundred and eighty minutes!"),
 "maths-product-rule": dict(tag="MATHS · PRODUCT RULE", q="Differentiate y = x² sin x with respect to x.",
    lines=["u = x²,   v = sin x", "u′ = 2x,   v′ = −cos x", "dy/dx = 2x sin x − x² cos x"], wrong=1,
    hint="Hint: what's the derivative of sin x?", fix="u′ = 2x,   v′ = cos x", final="dy/dx = 2x sin x + x² cos x",
    say_flag="It's line two! The derivative of sine is cosine, not minus cosine!"),
 "engineering": dict(tag="ENGINEERING · AXIAL STRESS", q="A 50 kN axial load acts on a steel rod of radius 10 mm. Find the stress in the rod.",
    lines=["A = 3.14 × (0.01)² = 0.000314 m²", "stress = 50 ÷ 0.000314", "= 159 000 Pa"], wrong=1,
    hint="Hint: what is 50 kN in newtons?", fix="stress = 50 000 ÷ 0.000314", final="= 159 MPa",
    say_flag="It's line two! Fifty kilonewtons is fifty thousand newtons!"),
 "law": dict(tag="LAW · DAMAGES", q="Damages are assessed at $240,000. The plaintiff is found 25% contributorily negligent. Calculate the award.",
    lines=["damages = $240,000", "award = 240,000 × 0.25", "award = $60,000"], wrong=1,
    hint="Hint: reduced BY 25%, or TO 25%?", fix="award = 240,000 × 0.75", final="award = $180,000",
    say_flag="It's line two! You keep seventy-five percent, not twenty-five!"),
 "maths-expanding": dict(tag="MATHS · EXPANDING BRACKETS", q="Expand and simplify (2x − 3)².",
    lines=["(2x − 3)(2x − 3)", "= 4x² − 6x − 6x − 9", "= 4x² − 12x − 9"], wrong=1,
    hint="Hint: what is −3 × −3?", fix="= 4x² − 6x − 6x + 9", final="= 4x² − 12x + 9",
    say_flag="It's line two! Minus three times minus three is plus nine!",
    intro=Q3("Are you constantly", "losing marks", "to silly mistakes?"), intro_say="Are you constantly losing marks to silly mistakes?"),
 "physics": dict(tag="PHYSICS · PROJECTILE MOTION", q="A ball is thrown straight up at 12 m/s. Find its displacement after 3 s. Take g = 9.8 m/s².",
    lines=["s = ut + ½at²", "s = 12(3) + ½(−9.8)(3)", "s = 36 − 14.7 = 21.3 m"], wrong=1,
    hint="Hint: is the time squared in your substitution?", fix="s = 12(3) + ½(−9.8)(3)²", final="s = 36 − 44.1 = −8.1 m",
    say_flag="It's line two! The time has to be squared!",
    intro=Q3("Ever lost", "a whole question", "to one wrong line?"), intro_say="Ever lost a whole question to one wrong line?"),
 "chemistry": dict(tag="CHEMISTRY · pH", q="Find the pH of a solution with a hydrogen ion concentration of 0.00025 M.",
    lines=["pH = −log[H+]", "= −log(0.00025)", "= 4.60"], wrong=2,
    hint="Hint: put −log(0.00025) through your calculator again.", fix="= 3.60", final="pH = 3.60, so it's acidic",
    say_flag="It's line three! The answer is three point six, not four point six!",
    intro=Q3("Do you check", "your working", "and still miss it?"), intro_say="Do you check your working, and still miss the error?"),
 "business": dict(tag="BUSINESS · COMPOUND INTEREST", q="$5,000 is invested at 6% p.a., compounded monthly, for 3 years. Find the final amount.",
    lines=["A = P(1 + r/n)^(nt)", "A = 5000(1 + 0.06)^36", "A = $40,736"], wrong=1,
    hint="Hint: what is the interest rate per month?", fix="A = 5000(1 + 0.005)^36", final="A = $5,983.40",
    say_flag="It's line two! Six percent a year is half a percent a month!",
    intro=Q3("Know the content", "but keep", "dropping marks?"), intro_say="Know the content, but keep dropping marks?"),
 "test-predictor": dict(feature=True, scenes=[
    (2.9, Q3("Wish you could", "sit the test", "before the test?"), None, "", "Wish you could sit the test, before the test?"),
    (4.6, Q("Test Predictor writes", "a practice test like yours."), ("tp_landing.png", (0, 0, 1045, 784), (8, 214, 768, 784), (940, 705)), "Add your test notice and a past paper.", "StudyCrest's Test Predictor writes a practice test built just like your real one!"),
    (4.6, Q("Same marks. Same timing.", "Brand new questions."), ("tp_sample.png", (0, 0, 1300, 531), (0, 36, 1150, 506), (940, 384)), "Sit it against the clock, then get it marked.", "Same marks, same timing, brand new questions. Sit it, then get it marked!")]),
 "practice-questions": dict(feature=True, scenes=[
    (5.4, Q("One question in.", "A fresh one out."), ("pq.png", [(30, 30, 736, 208), (832, 30, 1538, 208)]), "Same topic and skills. New situation, new numbers.", "Give StudyCrest a question you've already done, and it writes you a fresh one!"),
    (4.0, Q("Never run out of", "practice questions."), ("pq.png", [(30, 30, 736, 208), (832, 30, 1538, 208)]), "Pick how many, and how hard.", "Same skills, new numbers. You'll never run out of practice questions!")]),
}
# timeline (seconds)
T_WRITE = [0.4, 1.4, 2.4]; T_COUNT = (3.4, 5.6); T_CHECK = [5.8, 6.2, 6.6]; T_HINT = 6.9; T_FIX = 8.3; T_FINAL = 9.3
T_PAY = 10.4; T_END = 12.6; T_TOTAL = 17.2; T_INTRO = 2.9; T_ENDCARD = 4.6
CARD = (60, 470, 1020, 1480)

def shadowed(size, radius, blur=38, offset=18, alpha=70):
    w, h = size; pad = blur * 3; sh = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + offset, pad + w, pad + h + offset), radius, fill=(30, 32, 60, alpha))
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad

_static = {}
def card_base(S):
    """Paper background + notebook card with grid, tag and the question (drawn once)."""
    if S["tag"] in _static: return _static[S["tag"]]
    im = Image.new("RGB", (W, H), PAPER); x0, y0, x1, y1 = CARD
    sh, pad = shadowed((x1 - x0, y1 - y0), 40); im.paste(sh, (x0 - pad, y0 - pad), sh)
    card = Image.new("RGB", (x1 - x0, y1 - y0), (255, 255, 255)); cd = ImageDraw.Draw(card)
    for gx in range(0, x1 - x0, 48): cd.line((gx, 0, gx, y1 - y0), fill=(238, 240, 250), width=2)
    for gy in range(0, y1 - y0, 48): cd.line((0, gy, x1 - x0, gy), fill=(238, 240, 250), width=2)
    cd.rectangle((0, 0, x1 - x0, 250), fill=(255, 255, 255)); cd.line((0, 250, x1 - x0, 250), fill=(228, 230, 240), width=2)
    tf = font("Bold", 26); tw = cd.textlength(S["tag"], font=tf) + 36
    cd.rounded_rectangle((44, 40, 44 + tw, 86), 10, fill=(234, 239, 255)); cd.text((62, 47), S["tag"], font=tf, fill=BLU)
    qf = font("Serif", 40); y = 110
    for l in wrap(cd, S["q"], qf, x1 - x0 - 90)[:3]: cd.text((44, y), l, font=qf, fill=INK); y += 52
    c = rounded(card, 40); im.paste(c, (x0, y0), c)
    d = ImageDraw.Draw(im); lg = logo(60); im.paste(lg, (64, 96), lg); d.text((140, 104), "StudyCrest", font=font("Bold", 42), fill=INK)
    _static[S["tag"]] = im; return im

def hand(im, text, xy, size, fill, progress=1.0, maxw=730):
    """Handwritten line revealed left to right."""
    d = ImageDraw.Draw(im)
    while size > 40 and d.textlength(text, font=font("HandBold", size)) > maxw: size -= 2
    f = font("HandBold", size); w = int(d.textlength(text, font=f)) + 8
    layer = Image.new("RGBA", (w, int(size * 1.4)), (0, 0, 0, 0)); ImageDraw.Draw(layer).text((2, 0), text, font=f, fill=fill + (255,))
    cut = max(1, int(w * max(0.0, min(1.0, progress)))); part = layer.crop((0, 0, cut, layer.size[1])); im.paste(part, xy, part); return w

def tick(d, cx, cy, a, col=BLU):
    d.line([(cx - 20, cy), (cx - 6, cy + 14), (cx + 22, cy - 16)], fill=mix((255, 255, 255), col, a), width=8, joint="curve")
def flag(d, cx, cy, a):
    r = int(30 * (0.6 + 0.4 * a)); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix((255, 255, 255), FLAG, a))
    d.text((cx - 7, cy - 27), "!", font=font("Black", 44), fill=(255, 255, 255))

def headline(d, y, parts, t, size=98):
    """Serif headline, words rise in. parts = [(text, weight, colour)] one per line."""
    for i, (text, weight, col) in enumerate(parts):
        a = ease((t - 0.10 * i) / 0.5); f = fit(d, text, weight, size, W - 150, 60)
        d.text((72, y + i * int(size * 1.12) + (1 - a) * 26), text, font=f, fill=mix(PAPER, col, a))

def total(S):
    if S.get("feature"): return sum(sc[0] for sc in S["scenes"]) + T_ENDCARD
    return T_TOTAL + (T_INTRO if S.get("intro") else 0)

def blank():
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im); lg = logo(60); im.paste(lg, (64, 96), lg)
    d.text((140, 104), "StudyCrest", font=font("Bold", 42), fill=INK); return im, d

def intro_frame(parts, t):
    """Pain-question opener with red-pen marks landing beside it."""
    im, d = blank(); headline(d, 470, parts, t, size=118)
    for k, (txt, x, y, st) in enumerate([("−2", 700, 960, 0.55), ("−1", 430, 1110, 0.95), ("−3", 760, 1250, 1.35)]):
        if t < st: continue
        a = ease((t - st) / 0.25); hand(im, txt, (x, y), 150, FLAG, a)
        d.arc((x - 40, y - 10, x + 190, y + 190), 20, 20 + int(340 * a), fill=FLAG, width=7)
    return im

_sh = {}
def feature_frame(F, t):
    acc = 0
    for dur, parts, shot, cap, _ in F["scenes"]:
        if t < acc + dur: break
        acc += dur
    else: return end_card(t - acc)
    tl = t - acc; im, d = blank(); a = ease(tl / 0.5)
    if shot is None:
        headline(d, 560, parts, tl, size=118); return im
    headline(d, 196, parts, tl)
    name = shot[0]; src = _static.setdefault(name, Image.open(BASE + "/app/" + name).convert("RGB")); y = 520 + int((1 - a) * 40)
    if isinstance(shot[1], list):
        for k, box in enumerate(shot[1]):
            st = 0.3 + k * 1.3
            if tl < st: continue
            aa = ease((tl - st) / 0.5); w = 940; h = int(w * (box[3] - box[1]) / (box[2] - box[0])); x = (W - w) // 2; yy = 540 + k * (h + 150) + int((1 - aa) * 40)
            key = (w + 28, h + 28); sh, pad = _sh.setdefault(key, shadowed(key, 44)); im.paste(sh, (x - 14 - pad, yy - 14 - pad), sh)
            d.rounded_rectangle((x - 14, yy - 14, x + w + 14, yy + h + 14), 44, fill=(236, 240, 255)); c = rounded(src.resize((w, h), Image.BICUBIC, box=box), 32); im.paste(c, (x, yy), c)
            if k == 0 and tl >= 1.2:
                ab = ease((tl - 1.2) / 0.3); cy = yy + h + 75; d.ellipse((W / 2 - 44, cy - 44, W / 2 + 44, cy + 44), fill=mix(PAPER, BLU, ab))
                d.line((W / 2, cy - 22, W / 2, cy + 20), fill=(255, 255, 255), width=9); d.line((W / 2 - 18, cy + 4, W / 2, cy + 22, W / 2 + 18, cy + 4), fill=(255, 255, 255), width=9, joint="curve")
        cy2 = 540 + 2 * (int(940 * 178 / 706) + 150) - 60
    else:
        _, r0, r1, win = shot; p = ease(max(0, tl - 0.6) / (dur - 1.0)); r = tuple(r0[i] + (r1[i] - r0[i]) * p for i in range(4)); x = (W - win[0]) // 2
        key = (win[0] + 28, win[1] + 28); sh, pad = _sh.setdefault(key, shadowed(key, 44)); im.paste(sh, (x - 14 - pad, y - 14 - pad), sh)
        d.rounded_rectangle((x - 14, y - 14, x + win[0] + 14, y + win[1] + 14), 44, fill=(255, 255, 255)); c = rounded(src.resize(win, Image.BICUBIC, box=r), 32); im.paste(c, (x, y), c)
        cy2 = y + win[1] + 60
    lf = font("SemiBold", 30); lab = "Real screen from the StudyCrest app"; d.text((72, cy2), lab, font=lf, fill=mix(PAPER, BLU, a))
    return im

def compose(S, t):
    if S.get("feature"): return feature_frame(S, t)
    if S.get("intro"):
        if t < T_INTRO: return intro_frame(S["intro"], t)
        t -= T_INTRO
    if t >= T_END: return end_card(t - T_END)
    im = card_base(S).copy(); d = ImageDraw.Draw(im); x0, y0, x1, y1 = CARD
    # top headline changes with the beat of the ad
    if t < T_CHECK[0] - 0.1: headline(d, 196, [("Spot the mistake", "Serif", INK), ("before the AI does.", "SerifItalic", BLU)], t)
    elif t < T_PAY: headline(d, 196, [("StudyCrest found it", "Serif", INK), ("in line %d." % (S["wrong"] + 1), "SerifItalic", FLAG)], t - T_CHECK[0] + 0.1)
    else: headline(d, 196, [("Every line gets", "Serif", INK), ("a tick or a flag.", "SerifItalic", BLU)], t - T_PAY)
    # handwritten working
    ly = [y0 + 282 + i * 128 for i in range(3)]
    for i, text in enumerate(S["lines"]):
        if t < T_WRITE[i]: continue
        p = (t - T_WRITE[i]) / 0.8; col = HANDINK
        if i == S["wrong"] and t >= T_CHECK[i] + 0.25: col = mix(HANDINK, FLAG, (t - T_CHECK[i] - 0.25) / 0.3)
        if i > S["wrong"] and t >= T_FIX: col = mix(HANDINK, (178, 182, 198), (t - T_FIX) / 0.4)
        w = hand(im, text, (x0 + 52, ly[i]), 80, col, p)
        if i == S["wrong"] and t >= T_FIX:
            pp = ease((t - T_FIX) / 0.35); d.line((x0 + 44, ly[i] + 62, x0 + 44 + (w + 16) * pp, ly[i] + 54), fill=FLAG, width=7)
        if i > S["wrong"] and t >= T_FIX:
            pp = ease((t - T_FIX) / 0.35); d.line((x0 + 44, ly[i] + 62, x0 + 44 + (w + 16) * pp, ly[i] + 54), fill=(178, 182, 198), width=6)
    # countdown: "found it?" timer bar
    if T_COUNT[0] <= t < T_CHECK[0]:
        a = ease((t - T_COUNT[0]) / 0.3); p = min(1.0, (t - T_COUNT[0]) / (T_COUNT[1] - T_COUNT[0])); by = y1 - 110
        d.text((x0 + 52, by - 62), "Found it?", font=font("SemiBold", 40), fill=mix((255, 255, 255), INK, a))
        n = max(1, 3 - int(p * 3)) if p < 1 else 0; ns = str(n) if n else ""
        d.text((x1 - 100, by - 80), ns, font=font("Serif", 64), fill=mix((255, 255, 255), BLU, a))
        d.rounded_rectangle((x0 + 52, by, x1 - 52, by + 16), 8, fill=(232, 234, 244))
        d.rounded_rectangle((x0 + 52, by, x0 + 52 + (x1 - x0 - 104) * (1 - p), by + 16), 8, fill=mix((255, 255, 255), BLU, a))
    # the check: ticks and the flag, as in the app
    for i in range(3):
        if t < T_CHECK[i] or (i > S["wrong"] and t < T_FINAL): continue
        a = ease((t - T_CHECK[i]) / 0.25); cx, cy = x1 - 96, ly[i] + 60
        if i == S["wrong"]: flag(d, cx, cy, a)
        elif i < S["wrong"]: tick(d, cx, cy, a)
    if t >= T_HINT and t < T_PAY + 9:
        a = ease((t - T_HINT) / 0.35); hy = ly[2] + 132; hf = fit(d, S["hint"], "SemiBold", 38, x1 - x0 - 190)
        d.rounded_rectangle((x0 + 44, hy, x1 - 44, hy + 84), 22, fill=mix((255, 255, 255), PEACH, a))
        d.ellipse((x0 + 68, hy + 24, x0 + 104, hy + 60), outline=mix(PEACH, HINT, a), width=5)
        d.text((x0 + 124, hy + 42 - hf.size * 0.62), S["hint"], font=hf, fill=mix(PEACH, HINT, a))
    if t >= T_FIX + 0.2:
        fy = ly[2] + 238; hand(im, S["fix"], (x0 + 52, fy), 76, OK, (t - T_FIX - 0.2) / 0.8)
        if t >= T_FIX + 1.0: tick(d, x1 - 96, fy + 56, ease((t - T_FIX - 1.0) / 0.25), OK)
    if t >= T_FINAL:
        fy = ly[2] + 238 + 106; hand(im, S["final"], (x0 + 52, fy), 76, OK, (t - T_FINAL) / 0.8)
        if t >= T_FINAL + 0.8: tick(d, x1 - 96, fy + 56, ease((t - T_FINAL - 0.8) / 0.25), OK)
    # lower third
    return im

import json, os
_tm = {}
def timings(key):
    if key not in _tm:
        p = f"{BASE}/timings/{key}.json"; _tm[key] = json.load(open(p)) if os.path.exists(p) else []
    return _tm[key]

def captions(im, key, t):
    """Word-by-word captions synced to the voice: the word being spoken sits in a blue pill."""
    for st, dur, text in timings(key):
        if st - 0.05 <= t < st + dur + 0.3: break
    else: return
    d = ImageDraw.Draw(im); f = font("ExtraBold", 56); words = text.split(); wts = [len(w) + 2 for w in words]; tot = float(sum(wts)); acc = 0; cur = len(words) - 1
    for i, wgt in enumerate(wts):
        if (t - st) < dur * (acc + wgt) / tot: cur = i; break
        acc += wgt
    rows, row, roww = [], [], 0; sp = 18
    for i, w in enumerate(words):
        ww = d.textlength(w, font=f)
        if row and roww + sp + ww > W - 170: rows.append((row, roww)); row, roww = [], 0
        roww += (sp if row else 0) + ww; row.append((i, w, ww))
    rows.append((row, roww)); y = 1548
    for row, roww in rows[:3]:
        x = (W - roww) / 2
        for i, w, ww in row:
            if i == cur: d.rounded_rectangle((x - 14, y - 6, x + ww + 14, y + 74), 18, fill=BLU)
            d.text((x, y), w, font=f, fill=(255, 255, 255) if i == cur else (INK if i < cur else (150, 152, 162))); x += ww + sp
        y += 86

def frame(S, t, key=None):
    im = compose(S, t); tt = total(S)
    if not S.get("feature"):
        tl = t - (T_INTRO if S.get("intro") else 0); tf = T_CHECK[S["wrong"]]
        if tf <= tl < tf + 1.9 and tl < T_END:      # push in on the flagged line, then ease back out
            z = 1 + 0.11 * (ease((tl - tf) / 0.22) if tl < tf + 1.4 else 1 - ease((tl - tf - 1.4) / 0.5))
            cx, cy = W / 2, CARD[1] + 282 + S["wrong"] * 128 + 60; w, h = W / z, H / z
            x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h); im = im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    if key: captions(im, key, t)
    d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 9), fill=(228, 226, 220)); d.rectangle((0, 0, W * min(1.0, t / tt), 9), fill=BLU); return im

_end = {}
def end_card(t):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im); a = ease(t / 0.5)
    lg = logo(150); im.paste(lg, ((W - 150) // 2, 470), lg); centered(d, W, 650, "StudyCrest", font("Bold", 60), INK)
    for i, (txt, wt, col) in enumerate([("Try it free", "Serif", INK), ("for 30 days.", "SerifItalic", BLU)]):
        aa = ease((t - 0.1 * i) / 0.5); centered(d, W, 810 + i * 124 + (1 - aa) * 24, txt, font(wt, 112), mix(PAPER, col, aa))
    b = ease((t - 0.5) / 0.5)
    centered(d, W, 1110, "$0 for your first 30 days.", font("SemiBold", 50), mix(PAPER, INK, b))
    centered(d, W, 1182, "Cancel before day 30 and you're never charged.", font("Medium", 36), mix(PAPER, MUTE, b))
    c = ease((t - 0.9) / 0.5); pf = font("SemiBold", 46); bw = d.textlength("Promo code in bio", font=pf) + 110
    d.rounded_rectangle(((W - bw) / 2, 1290, (W + bw) / 2, 1392), 51, fill=mix(PAPER, BLU, c)); centered(d, W, 1312, "Promo code in bio", pf, mix(PAPER, (255, 255, 255), c))
    centered(d, W, 1450, "iPad  ·  iPhone  ·  Mac  ·  Web", font("Medium", 38), mix(PAPER, MUTE, c))
    e = ease((t - 1.6) / 0.5); centered(d, W, 250, "Did you get it? Comment the line.", font("SemiBold", 44), mix(PAPER, INK, e))
    centered(d, W, 312, "A new one every day. Follow to play.", font("Medium", 38), mix(PAPER, MUTE, e)); return im

if __name__ == "__main__":
    S = SPOTS[sys.argv[2]]
    if sys.argv[1] == "stills":
        tt = total(S); ts = [float(x) for x in sys.argv[3:]] or [0.9, 3.9, 5.6, 8.9, 11.7, 13.2, 16.5]; sheet = Image.new("RGB", (270 * len(ts), 480))
        for i, t in enumerate(ts): sheet.paste(frame(S, t, sys.argv[2]).resize((270, 480), Image.LANCZOS), (i * 270, 0))
        sheet.save(f"{BASE}/pilot-{sys.argv[2]}.jpg", quality=88)
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", sys.argv[3]], stdin=subprocess.PIPE)
        for i in range(int(total(S) * FPS)): p.stdin.write(frame(S, i / FPS, sys.argv[2]).tobytes())
        p.stdin.close(); sys.exit(p.wait())

"""StudyCrest swipe posts (carousels) and image posts: 1080x1350 JPGs.  Usage: posts.py"""
import os
BASE = os.path.dirname(os.path.abspath(__file__))
import os
from PIL import Image, ImageDraw
from brand import *

W, H = 1080, 1350
OUT = BASE + "/posts2/"
APP = BASE + "/app/"
C = lambda d, y, text, f, fill: centered(d, W, y, text, f, fill)

def base(theme):
    T = THEMES[theme]; im = Image.new("RGB", (W, H), T["bg"]); d = ImageDraw.Draw(im); header(im, d, T, W, y=70, size=64); return im, d, T

def dots(d, T, i, n):
    x0 = W / 2 - (n * 34 - 14) / 2
    for k in range(n):
        d.ellipse((x0 + k * 34, H - 78, x0 + k * 34 + 20, H - 58), fill=T["fg"] if k == i else mix(T["bg"], T["fg"], 0.3))

def swipe(d, T):
    f = font("Bold", 40); t = "Swipe  →"; w = d.textlength(t, font=f) + 70
    d.rounded_rectangle((W - w - 60, H - 170, W - 60, H - 96), 37, fill=T["acc"])
    d.text((W - w - 25, H - 158), t, font=f, fill=(22, 26, 48) if T["acc"] == (255, 214, 74) else (255, 255, 255))

def block(d, T, y, text, weight, size, maxw=W - 160, fill=None, lh=1.2, accent_words=()):
    f = fit(d, max(text.split(), key=len), weight, size, maxw); lines = wrap(d, text, f, maxw)
    for l in lines:
        C(d, y, l, f, fill or T["fg"]); y += int(f.size * lh)
    return y

def cover(theme, emo, title, sub, i, n, accent=None):
    im, d, T = base(theme); e = emoji(emo, 150); im.paste(e, ((W - 150) // 2, 300), e)
    y = block(d, T, 520, title, "Serif", 100)
    if accent: y = block(d, T, y + 6, accent, "SerifItalic", 100, fill=T["acc"])
    block(d, T, y + 40, sub, "Medium", 46, fill=T["mute"])
    swipe(d, T); dots(d, T, i, n); return im

def point(theme, num, emo, title, body, i, n, tag=None):
    im, d, T = base(theme)
    d.rounded_rectangle((70, 210, W - 70, H - 150), 44, fill=T["card"], outline=(226, 224, 218), width=2)
    d.ellipse((120, 262, 230, 372), fill=BLUE); nf = font("Bold", 58); s = str(num)
    d.text((175 - d.textlength(s, font=nf) / 2, 277), s, font=nf, fill=(255, 255, 255))
    d.line((130, 420, W - 130, 420), fill=(228, 226, 220), width=3)
    f = fit(d, max(title.split(), key=len), "Serif", 92, W - 260); y = 500
    for l in wrap(d, title, f, W - 260): d.text((130, y), l, font=f, fill=T["ink"]); y += int(f.size * 1.16)
    y += 40; bf = font("Medium", 54)
    for l in wrap(d, body, bf, W - 270): d.text((130, y), l, font=bf, fill=(70, 78, 110)); y += 76
    if tag:
        tf = font("Bold", 40); tw = d.textlength(tag, font=tf) + 60
        d.rounded_rectangle((130, y + 30, 130 + tw, y + 104), 37, fill=(232, 238, 255)); d.text((160, y + 42), tag, font=tf, fill=BLUE)
    dots(d, T, i, n); return im

def salary(theme, emo, job, pay, note, i, n):
    im, d, T = base(theme)
    d.rounded_rectangle((70, 210, W - 70, H - 150), 44, fill=T["card"], outline=(226, 224, 218), width=2)
    lf = font("Bold", 30); lab = "MEDIAN PAY  ·  UNITED STATES"; C(d, 290, lab, lf, BLUE)
    d.line((W / 2 - 60, 350, W / 2 + 60, 350), fill=(228, 226, 220), width=3)
    y = 420; f = fit(d, max(job.split(), key=len), "Serif", 84, W - 240)
    for l in wrap(d, job, f, W - 240): C(d, y, l, f, T["ink"]); y += int(f.size * 1.14)
    C(d, y + 30, pay, font("SerifBold", 150), T["ink"])
    C(d, y + 232, "median pay per year", font("SemiBold", 42), (70, 78, 110))
    yy = y + 312
    for l in wrap(d, note, font("Medium", 40), W - 260): C(d, yy, l, font("Medium", 40), (96, 104, 140)); yy += 54
    C(d, H - 215, "Source: U.S. Bureau of Labor Statistics, May 2025", font("Medium", 30), (130, 138, 170))
    dots(d, T, i, n); return im

def cta_slide(theme, i, n, top="Try StudyCrest free for 30 days", kicker=None):
    im, d, T = base(theme)
    if kicker: block(d, T, 215, kicker, "Bold", 50, fill=T["acc"])
    y = block(d, T, 300 if kicker else 270, top, "Serif", 100)
    y = block(d, T, y + 50, "You pay $0 for the first 30 days.", "Bold", 56)
    y = block(d, T, y + 6, "Cancel before day 30 and you're never charged.", "Medium", 40, fill=T["mute"])
    pf = font("Bold", 56); pill = "Promo code in bio"; bw = d.textlength(pill, font=pf) + 120
    d.rounded_rectangle(((W - bw) / 2, y + 70, (W + bw) / 2, y + 190), 60, fill=T["acc"])
    C(d, y + 95, pill, pf, (22, 26, 48) if T["acc"] == (255, 214, 74) else (255, 255, 255))
    C(d, y + 250, "iPad  ·  iPhone  ·  Mac  ·  Web", font("SemiBold", 46), T["mute"])
    C(d, y + 320, "@studycrestapp", font("Medium", 44), T["mute"])
    dots(d, T, i, n); return im

def shot_slide(theme, title, name, box, caption, i, n, stack=None):
    im, d, T = base(theme); y = block(d, T, 200, title, "Serif", 80) + 40
    src = Image.open(APP + name).convert("RGB")
    for b in (stack or [box]):
        w = 960; h = int(w * (b[3] - b[1]) / (b[2] - b[0])); s = rounded(src.resize((w, h), Image.LANCZOS, box=b), 34); x = (W - w) // 2
        d.rounded_rectangle((x - 14, y - 14, x + w + 14, y + h + 14), 46, fill=(236, 240, 255) if stack else (255, 255, 255)); im.paste(s, (x, y), s); y += h + 56
    lf = font("Bold", 32); lab = "Real screen from the app"; lw = d.textlength(lab, font=lf) + 44
    d.rounded_rectangle(((W - lw) / 2, y - 16, (W + lw) / 2, y + 40), 26, fill=BLUE if theme != "blue" else (22, 26, 48)); d.text(((W - lw) / 2 + 22, y - 9), lab, font=lf, fill=(255, 255, 255))
    block(d, T, y + 80, caption, "SemiBold", 48)
    dots(d, T, i, n); return im

def steps_slide(theme, title, steps, i, n):
    im, d, T = base(theme); y = block(d, T, 200, title, "Serif", 80) + 50
    for k, (a, b) in enumerate(steps):
        d.rounded_rectangle((70, y, W - 70, y + 190), 32, fill=T["card"], outline=(226, 224, 218), width=2)
        d.ellipse((104, y + 50, 194, y + 140), fill=BLUE); nf = font("Bold", 46); s = str(k + 1)
        d.text((149 - d.textlength(s, font=nf) / 2, y + 63), s, font=nf, fill=(255, 255, 255))
        d.text((226, y + 38), a, font=fit(d, a, "Bold", 48, W - 330), fill=T["ink"])
        d.text((226, y + 104), b, font=fit(d, b, "Medium", 36, W - 330, 24), fill=(70, 78, 110)); y += 214
    dots(d, T, i, n); return im

def question(theme, emo, q, a_text):
    im, d, T = base(theme); e = emoji(emo, 200); im.paste(e, ((W - 200) // 2, 230), e)
    y = block(d, T, 490, q, "Serif", 100)
    y = block(d, T, y + 50, a_text, "Bold", 56, fill=T["acc"])
    block(d, T, y + 40, "You pay $0 for the first 30 days. Cancel before day 30 and you're never charged.", "Medium", 40, fill=T["mute"])
    C(d, H - 130, "Promo code in bio  ·  @studycrestapp", font("SemiBold", 40), T["fg"]); return im

BLS = "Source: U.S. Bureau of Labor Statistics"
POSTS = {
 "A-5-ways-to-improve-your-study": lambda n=7: [
    cover("paper", "📚", "5 ways to improve", "Small changes that add up before exams.", 0, n, accent="your study"),
    point("paper", 1, "🧠", "Test yourself, don't re-read", "Close the notes and try to recall it. Retrieval beats re-reading.", 1, n),
    point("paper", 2, "🗓️", "Space it out", "Three short sessions across a week beat one long cram.", 2, n),
    point("paper", 3, "⏱️", "Do past papers on the clock", "Practise the way you'll be tested: timed, no notes.", 3, n),
    point("paper", 4, "📝", "Keep a mistake list", "Write down every error you make and redo those questions first.", 4, n),
    point("paper", 5, "✅", "Use StudyCrest", "It checks every line of your working, predicts your next test and writes new practice questions.", 5, n, tag="Free for 30 days"),
    cta_slide("paper", 6, n)],
 "B-business-degree-5-jobs": lambda n=7: [
    cover("ink", "💼", "Doing or thinking of doing a business degree?", "Here are 5 jobs and what they pay.", 0, n),
    salary("ink", "📈", "Financial Analyst", "$103,570", "Guides investment decisions for businesses and individuals.", 1, n),
    salary("ink", "📋", "Project Management Specialist", "$102,320", "Keeps budgets, people and deadlines on track.", 2, n),
    salary("ink", "🧩", "Management Analyst", "$101,860", "Also called a management consultant.", 3, n),
    salary("ink", "🧾", "Accountant or Auditor", "$83,680", "Prepares and examines financial records.", 4, n),
    salary("ink", "🔍", "Market Research Analyst", "$78,760", "Studies customers and competitors to guide what a business sells.", 5, n),
    cta_slide("ink", 6, n, kicker="First, you have to pass the degree.")],
 "C-could-you-improve-your-study": lambda n=2: [
    question("paper", "🤔", "Do you think you could improve your study?", "Try StudyCrest free for 30 days and find out."),
    cta_slide("paper", 1, n)],
 "D-zero-dollars-for-30-days": lambda n=3: [
    cover("ink", "🎁", "$0 for your first", "Here's exactly how it works.", 0, n, accent="30 days"),
    steps_slide("ink", "How the free 30 days work", [("Use the promo code in our bio", "Enter it when you sign up"), ("Use StudyCrest free for 30 days", "You pay $0 in that time"), ("Cancel before day 30", "and you're never charged"), ("Keep it? Do nothing", "Your paid plan starts after day 30")], 1, n),
    cta_slide("ink", 2, n)],
 "E-test-predictor": lambda n=5: [
    cover("paper", "🔮", "Sit the test", "StudyCrest's Test Predictor writes a practice test built like your real one.", 0, n, accent="before the test"),
    steps_slide("paper", "How Test Predictor works", [("Add the notice and a past paper", "Scan them, choose photos or add a PDF"), ("Get your predicted test", "Same number of questions and marks"), ("Sit it like the real thing", "Type, write with your pen, or photograph it"), ("See your marks", "The mistakes to fix and what to study next")], 1, n),
    shot_slide("paper", "Your predicted test, ready to sit", "tp_landing.png", (8, 420, 788, 690), "Built from your test notice and a past paper.", 2, n),
    shot_slide("paper", "Timed like the real thing", "tp_sample.png", (0, 40, 1300, 380), "Then marked question by question.", 3, n),
    cta_slide("paper", 4, n)],
 "F-practice-questions": lambda n=4: [
    cover("ink", "🔁", "Run out of", "StudyCrest writes fresh ones from questions you've already done.", 0, n, accent="practice questions?"),
    shot_slide("ink", "Your question in, a new one out", "pq.png", None, "Same topic and skills. New situation, new numbers.", 1, n, stack=[(30, 30, 736, 208), (832, 30, 1538, 208)]),
    steps_slide("ink", "Make them your way", [("Add questions you've done", "Photos, a PDF, or type them in"), ("Pick how many", "3, 5 or 8 at a time"), ("Pick the difficulty", "Easier, the same, or harder")], 2, n),
    cta_slide("ink", 3, n)],
}

if __name__ == "__main__":
    for slug, make in POSTS.items():
        os.makedirs(OUT + slug, exist_ok=True)
        for k, im in enumerate(make()): im.save(f"{OUT}{slug}/slide-{k + 1}.jpg", quality=92)
    # review sheets
    for slug in POSTS:
        fs = sorted(os.listdir(OUT + slug)); s = Image.new("RGB", (270 * len(fs), 338), (0, 0, 0))
        for k, f in enumerate(fs): s.paste(Image.open(f"{OUT}{slug}/{f}").resize((270, 338)), (k * 270, 0))
        s.save(f"{BASE}/postsheet2-{slug[0]}.jpg", quality=85)

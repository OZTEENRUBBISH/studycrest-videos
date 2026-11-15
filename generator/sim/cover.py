"""Designed TikTok covers, and baking a cover into a video as its first frames.
  cover.py make <page> <t> <out.jpg> "<kicker>" "<title with *accent words* and | line breaks>"
      films a clean frame of sim page <page> at time t (no captions or HUD) and lays the title over it
  cover.py bake <video.mp4> <cover.jpg> <out.mp4>
      puts the cover on screen for the first 0.3 s, so TikTok's grid shows it (also pass thumbnailOffset 100 to Buffer)"""
import sys, os, io, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
BASE = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920
XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; SB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
def clean_frame(page, t):
    os.environ["SIMQ"] = "?clean=1"; sys.path.insert(0, BASE); import render
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b, pg = render.open_page(p, page); d = render.shot(pg, t); b.close()
    return Image.open(io.BytesIO(d)).convert("RGB")
def compose(bg, kicker, title, out):
    bg = ImageEnhance.Contrast(bg.resize((W, H))).enhance(1.08); bg = ImageEnhance.Color(bg).enhance(1.12)
    sh = Image.new("L", (1, H)); px = sh.load()
    for y in range(H):
        u = y / H; band = max(0.0, 1 - abs(u - 0.5) / 0.3); px[0, y] = int(255 * min(0.86, 0.22 + 0.4 * band ** 1.4 + 0.34 * max(0.0, (u - 0.62) / 0.38)))
    bg = Image.composite(Image.new("RGB", (W, H), (6, 9, 24)), bg, sh.resize((W, H)))
    d = ImageDraw.Draw(bg)
    # title: fit the largest size whose lines stay inside 930 px
    lines = [l.strip() for l in title.split("|")]
    def segs(line):
        out, acc = [], False
        for i, part in enumerate(line.split("*")):
            if part: out.append((part, i % 2 == 1))
        return out
    size = 150
    while size > 60:
        f = ImageFont.truetype(XB, size)
        if max(sum(d.textlength(s, font=f) for s, _ in segs(l)) for l in lines) <= 930: break
        size -= 4
    f = ImageFont.truetype(XB, size); lh = int(size * 1.1); total = lh * len(lines); y0 = 960 - total // 2 + 30
    kf = ImageFont.truetype(XB, 40); kw = d.textlength(kicker, font=kf) + 26 * len(kicker) * 0.0 + 64; ky = y0 - 120
    d.rounded_rectangle([W / 2 - kw / 2, ky, W / 2 + kw / 2, ky + 74], radius=37, fill=(255, 214, 74)); d.text((W / 2, ky + 37), kicker, font=kf, fill=(12, 16, 40), anchor="mm")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for pas, layer in ((0, gd), (1, d)):
        y = y0
        for l in lines:
            x = W / 2 - sum(d.textlength(s, font=f) for s, _ in segs(l)) / 2
            for s, acc in segs(l):
                if pas == 0: layer.text((x, y + 8), s, font=f, fill=(0, 0, 0, 230))
                else: layer.text((x, y), s, font=f, fill=(255, 214, 74) if acc else (255, 255, 255))
                x += d.textlength(s, font=f)
            y += lh
        if pas == 0: bg.paste(glow.filter(ImageFilter.GaussianBlur(14)), (0, 0), glow.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(bg)
    # brand line
    by = y0 + total + 70; lg = 84; nf = ImageFont.truetype(XB, 50); nw = d.textlength("StudyCrest", font=nf); x = W / 2 - (lg + 20 + nw) / 2
    logo = Image.new("RGBA", (lg, lg), (0, 0, 0, 0)); ld = ImageDraw.Draw(logo); ld.rounded_rectangle([0, 0, lg - 1, lg - 1], radius=20, fill=(46, 84, 214)); k = lg / 90
    ld.polygon([((px_ - 5) * k, (py_ - 5) * k) for px_, py_ in [(30, 40), (30, 24), (40, 32), (50, 20), (60, 32), (70, 24), (70, 40)]], fill="white")
    ld.line([((30 - 5) * k, (60 - 5) * k), ((44 - 5) * k, (73 - 5) * k), ((70 - 5) * k, (48 - 5) * k)], fill="white", width=int(9 * k), joint="curve")
    bg.paste(logo, (int(x), by), logo); d.text((x + lg + 20, by + lg / 2), "StudyCrest", font=nf, fill="white", anchor="lm")
    bg.save(out, quality=92); return out
def bake(video, cover, out, hold=0.3):
    tmp = out + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-loop", "1", "-t", str(hold), "-i", cover, "-i", video, "-filter_complex",
        f"[0:v]scale={W}:{H},format=yuv420p,setsar=1[c];[1:v]fps=30,scale={W}:{H},format=yuv420p,setsar=1[v];[c][v]concat=n=2:v=1[o];[1:a]adelay={int(hold * 1000)}:all=1[a]",
        "-map", "[o]", "-map", "[a]", "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out); return out
if __name__ == "__main__":
    if sys.argv[1] == "make": compose(clean_frame(sys.argv[2], float(sys.argv[3])), sys.argv[5], sys.argv[6], sys.argv[4]); print("cover", sys.argv[4])
    else: bake(sys.argv[2], sys.argv[3], sys.argv[4]); print("baked", sys.argv[4])

"""Cover images for the reels (1080x1920 JPEG; the key content sits in the centre square so it survives the grid crop).
Usage: covers.py <key> <out.jpg>"""
import os, sys
from PIL import Image, ImageDraw
from brand import *
import pilot as P

W, H = 1080, 1920
def cover(key):
    S = P.SPOTS[key]; im = Image.new("RGB", (W, H), P.PAPER); d = ImageDraw.Draw(im)
    lg = logo(84); f = font("Bold", 58); w = d.textlength("StudyCrest", font=f); x = int((W - w - 84 - 22) / 2)
    im.paste(lg, (x, 470), lg); d.text((x + 106, 478), "StudyCrest", font=f, fill=P.INK)
    if S.get("feature"):
        parts = S["scenes"][0][1]; y = 660; size = min(fit(d, t, wt, 128, W - 160, 60).size for t, wt, _ in parts)
        for t, wt, col in parts: centered(d, W, y, t, font(wt, size), col); y += int(size * 1.15)
        tag = key.replace("-", " ").upper(); cy = y + 90
    else:
        centered(d, W, 640, "Spot the", font("Serif", 150), P.INK); centered(d, W, 800, "mistake.", font("SerifItalic", 150), P.BLU)
        sh, pad = P.shadowed((920, 210), 40); im.paste(sh, (80 - pad, 1030 - pad), sh); d.rounded_rectangle((80, 1030, 1000, 1240), 40, fill=(255, 255, 255))
        P.hand(im, S["lines"][0], (130, 1076), 92, P.HANDINK, 1.0, maxw=700)      # first line only: the cover must not give the answer away
        d.ellipse((880, 1095, 960, 1175), fill=P.BLU); d.text((920 - d.textlength("?", font=font("Black", 52)) / 2, 1102), "?", font=font("Black", 52), fill=(255, 255, 255))
        tag = S["tag"]; cy = 1310
    tf = font("Bold", 34); tw = d.textlength(tag, font=tf) + 60
    d.rounded_rectangle(((W - tw) / 2, cy, (W + tw) / 2, cy + 70), 16, fill=(226, 233, 255)); centered(d, W, cy + 14, tag, tf, P.BLU)
    return im

if __name__ == "__main__":
    os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True); cover(sys.argv[1]).save(sys.argv[2], quality=92)

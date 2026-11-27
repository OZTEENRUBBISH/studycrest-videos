"""Soundtrack + narration for the Mount St. Helens simulation. Writes work/sthelens.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 53.2
LINES = [(0.4, "Mount St. Helens, second by second."),
 (2.6, "In nineteen eighty, this volcano didn't blow its top. Its north side slid away, and the blast shot out sideways."),
 (9.8, "May eighteenth, eight thirty two a.m. For two months, magma has pushed the north face out into a bulge. A magnitude five point one earthquake shakes it loose."),
 (20.1, "Seconds later, the north face collapses: the largest landslide in recorded history."),
 (25.3, "Like uncorking a shaken bottle, the pressure is released. Gas and rock blast out sideways at around five hundred kilometres an hour."),
 (33.3, "The blast overtakes the landslide and flattens about six hundred square kilometres of forest."),
 (39.0, "Then ash climbs about twenty four kilometres in fifteen minutes."),
 (42.9, "Fifty seven people died."),
 (45.0, "By evening, the mountain is about four hundred metres shorter."),
 (48.6, "It didn't blow its top. It lost its side."),
 (51.3, "Follow for more.")]
CHUNKS = [[], ["In <em>1980</em>, this volcano", "didn't <em>blow its top</em>.", "Its <em>north side</em><br>slid away,", "and the blast shot out<br><em>sideways</em>."],
 ["May 18th, 8:32 a.m.", "For two months,", "magma has pushed<br>the north face out", "into a <em>bulge</em>.", "A magnitude <em>5.1</em><br>earthquake", "shakes it loose."],
 ["Seconds later,", "the north face <em>collapses</em>:", "the <em>largest landslide</em>", "in recorded history."],
 ["Like uncorking<br>a shaken bottle,", "the <em>pressure</em> is released.", "Gas and rock blast out<br><em>sideways</em>", "at around<br><em>500 kilometres an hour</em>."],
 ["The blast <em>overtakes</em><br>the landslide", "and flattens about", "<em>600 square kilometres</em><br>of forest."],
 ["Then ash climbs", "about <em>24 kilometres</em>", "in fifteen minutes."],
 ["<em>57</em> people died."],
 ["By evening, the mountain", "is about <em>400 metres</em><br>shorter."],
 ["It didn't blow its top.", "It <em>lost its side</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(1980)
    def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
    def noise(d): return rng.normal(0, 1, int(d * SR))
    def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
    def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
    def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
    def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
    def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
        return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
    def wind(d, lvl=0.04):
        t = np.arange(int(d * SR)) / SR; return bp(noise(d), 200, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t + 1) ** 2) * lvl * env(d, 0.6, 0.6)
    def boom(f=46, d=1.8, lvl=0.5):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
    def whoosh(d=0.7, lvl=0.09):
        m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 500, 6000) * 0.6 * np.sin(np.pi * t / d) ** 2 * lvl
    def riser(d=2.0, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
    def shimmer(d, lvl=0.022, notes=("C5", "E5", "G5", "B5", "D6")):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(notes)) * env(d, 0.8, 1.0) * lvl
    def tick(f=1100, lvl=0.12): t = np.arange(int(0.09 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + rng.normal(0, .25, len(t)) * np.exp(-t * 500)) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * lvl
    def rocks(d, lvl=0.12): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 90, 900) * (0.5 + 0.5 * np.abs(lp(noise(d), 14))) * 2 + lp(noise(d), 90, 3) * 3) * env(d, 0.5, 1.2) * lvl
    def thunder(d=2.6, lvl=0.3): t = np.arange(int(d * SR)) / SR; return (lp(noise(d), 120, 3) * 4 * np.exp(-t * 1.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t) ** 2) + bp(noise(d), 200, 1800) * np.exp(-t * 9) * 0.6) * lvl
    def roar(d, lvl=0.1): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 60, 1200) * 1.2 + lp(noise(d), 80, 3) * 3) * env(d, 0.25, 0.8) * lvl
    def birds(d, lvl=0.014, seed=5):
        r = np.random.default_rng(seed); out = np.zeros(int(d * SR)); t0 = 0.3
        while t0 < d - 0.6:
            for j in range(r.integers(2, 5)):
                dd = r.uniform(0.07, 0.14); m = int(dd * SR); tt = np.arange(m) / SR; f = r.uniform(2600, 4200) * (1 + 0.25 * np.sin(np.pi * tt / dd)); ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dd) ** 2; a = int((t0 + j * 0.16) * SR)
                if a + m < len(out): out[a:a + m] += ch * r.uniform(0.4, 1)
            t0 += r.uniform(0.7, 1.8)
        return out * lvl
    def bell(f=880, d=2.2, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.8) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: calm morning, the flash-forward, the bulge, the quake, the slide, the blast, the forest, the column, the toll, the evening
    place(bed, wind(2.6, 0.03), 0.0); place(bed, birds(2.3, 0.014, 3), 0.1, pan=0.3); place(bed, pad(["D2", "A2", "F#3", "A3"], 2.8, 0.4, 0.5, 0.034), 0.0)
    place(bed, pad(["D2", "A2", "F3", "C4"], 7.4, 0.3, 0.5, 0.04), 2.4); place(bed, rumble(4.6, 0.09) * env(4.6, 1.0, 0.4), 5.2)
    place(bed, wind(8.0, 0.035), 9.6); place(bed, birds(6.8, 0.014, 8), 9.9, pan=-0.3); place(bed, pad(["E2", "B2", "G3", "D4"], 7.8, 0.6, 0.6, 0.032), 9.6); place(bed, rumble(4.6, 0.03) * env(4.6, 3.0, 0.3), 12.6)
    place(bed, rumble(3.8, 0.16) * env(3.8, 0.1, 0.8), 16.4); place(bed, pad(["C2", "G2", "Eb3"], 3.8, 0.2, 0.4, 0.046), 16.4)
    place(bed, pad(["B1", "F#2", "D3", "F3"], 5.4, 0.3, 0.5, 0.044), 20.0); place(bed, rocks(5.2, 0.12), 20.1)
    place(bed, pad(["A1", "E2", "C3", "Eb3"], 8.2, 0.3, 0.5, 0.046), 25.2); place(bed, roar(7.2, 0.1), 26.1)
    place(bed, pad(["D2", "A2", "D3", "F3"], 5.8, 0.4, 0.6, 0.042), 33.2); place(bed, roar(5.6, 0.06), 33.2); place(bed, wind(5.6, 0.05), 33.3)
    place(bed, pad(["F2", "C3", "A3", "C4"], 4.0, 0.4, 0.5, 0.04), 38.9); place(bed, rumble(3.9, 0.1) * env(3.9, 0.4, 0.6), 38.9)
    place(bed, pad(["A1", "E2", "A2", "C3"], 2.3, 0.4, 0.6, 0.04), 42.7)
    place(bed, wind(8.2, 0.035), 44.9); place(bed, pad(["D2", "A2", "D3", "F#3", "A3", "E4"], 8.3, 0.6, 2.2, 0.036), 44.9); place(bed, shimmer(5.6, 0.012, ("D5", "F#5", "A5", "C#6")), 45.2)
    # effects
    for ts in [2.4, 9.6, 20.0, 25.2, 28.6, 33.2, 38.9, 44.9]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
    place(fx, rocks(2.0, 0.1), 5.6); place(fx, riser(1.0, 0.05), 6.3); place(fx, boom(40, 2.6, 0.55), 7.3); place(fx, thunder(2.2, 0.26), 7.35)
    place(fx, riser(0.5, 0.04), 9.15)
    for k in range(5): place(fx, tick(900, 0.03), 12.2 + k * 0.8)
    place(fx, boom(52, 1.4, 0.5), 16.4); place(fx, thunder(2.0, 0.2), 16.45); place(fx, boom(48, 1.0, 0.25), 17.8)
    place(fx, boom(42, 2.0, 0.4), 20.4); place(fx, thunder(2.6, 0.2), 21.6, pan=0.3); place(fx, boom(46, 1.6, 0.3), 23.3)
    place(fx, riser(0.9, 0.08), 25.2); place(fx, boom(32, 4.0, 0.95), 26.1); place(fx, boom(80, 0.6, 0.45), 26.12); place(fx, thunder(3.4, 0.4), 26.15)
    place(fx, thunder(2.4, 0.22), 29.4, pan=-0.3); place(fx, riser(2.6, 0.09), 30.4); place(fx, boom(36, 2.2, 0.6), 32.9)
    for k in range(9): place(fx, tick(500 + 40 * (k % 3), 0.035), 34.2 + k * 0.46, pan=(k % 3 - 1) * 0.5)
    place(fx, boom(40, 2.6, 0.5), 39.0); place(fx, thunder(3.0, 0.3), 39.1); place(fx, riser(2.0, 0.05), 40.2)
    place(fx, boom(44, 2.0, 0.22), 42.75); place(fx, bell(440, 2.0, 0.03), 42.9)
    place(fx, bell(660, 2.0, 0.018), 46.9, pan=0.3); place(fx, riser(1.0, 0.035), 50.2)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/sthelens.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

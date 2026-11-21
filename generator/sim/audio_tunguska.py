"""Soundtrack + narration for the Tunguska simulation. Writes work/tunguska.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 57.2
LINES = [(0.4, "Tunguska, second by second."),
 (2.5, "Siberia, the thirtieth of June, nineteen oh eight. Just after seven in the morning, a rock from space, around sixty metres wide, hits the air at fifteen kilometres a second."),
 (13.1, "It never reaches the ground. Five to ten kilometres up, the air ahead of it piles up so hard that the rock breaks apart, and explodes."),
 (21.6, "The blast is hundreds of times stronger than the Hiroshima bomb. The shock wave hits the forest from above, then races outward."),
 (29.6, "Around eighty million trees go down, across two thousand square kilometres. Every trunk points away from the centre."),
 (37.1, "Seismographs in western Europe pick it up. For nights afterwards, the sky over Europe glows."),
 (43.1, "Scientists reach the site in nineteen twenty seven. They find a swamp, fallen trees, and no crater. No piece of the rock has ever been found."),
 (51.9, "It flattened a forest, without ever touching the ground."),
 (55.0, "Follow for more.")]
CHUNKS = [[], ["Siberia, the 30th of June, <em>1908</em>.", "Just after seven in the morning,", "a rock from space,", "around <em>60 metres</em> wide,", "hits the air at<br><em>15 kilometres a second</em>."],
 ["It <em>never</em> reaches the ground.", "Five to ten kilometres up,", "the air ahead of it<br>piles up so hard", "that the rock breaks apart,", "and <em>explodes</em>."],
 ["The blast is hundreds of times<br>stronger than the Hiroshima bomb.", "The shock wave hits the forest<br>from <em>above</em>,", "then races outward."],
 ["Around <em>80 million</em> trees go down,", "across 2,000 square kilometres.", "Every trunk points<br><em>away from the centre</em>."],
 ["Seismographs in western Europe<br>pick it up.", "For nights afterwards,", "the sky over Europe <em>glows</em>."],
 ["Scientists reach the site in <em>1927</em>.", "They find a swamp, fallen trees,", "and <em>no crater</em>.", "No piece of the rock<br>has ever been found."],
 ["It flattened a forest,", "without ever <em>touching the ground</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(23)
    def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
    def noise(d): return rng.normal(0, 1, int(d * SR))
    def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
    def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
    def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
    def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
    def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
        return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
    def surf(d, lvl=0.05, per=5.3):
        t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 250, 2600); sw = 0.45 + 0.55 * np.sin(2 * np.pi * t / per - 1) ** 2; return x * sw * lvl * env(d, 0.6, 0.6)
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
    def bell(f=880, d=2.2, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.8) * lvl
    def creak(d=0.6, lvl=0.02):
        m = int(d * SR); t = np.arange(m) / SR; f = 180 + 60 * np.sin(2 * np.pi * 2.2 * t); return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * lp(noise(d), 900) * np.sin(np.pi * t / d) ** 2 * lvl
    def gulls(d, lvl=0.02, seed=5):
        r = np.random.default_rng(seed); out = np.zeros(int(d * SR)); t0 = 0.4
        while t0 < d - 0.6:
            for j in range(r.integers(2, 4)):
                dd = r.uniform(0.18, 0.3); m = int(dd * SR); tt = np.arange(m) / SR; f = r.uniform(1500, 2100) * (1 + 0.35 * np.sin(np.pi * tt / dd)); ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dd) ** 2; a = int((t0 + j * 0.33) * SR)
                if a + m < len(out): out[a:a + m] += ch * r.uniform(0.4, 1)
            t0 += r.uniform(1.4, 3.0)
        return out * lvl
    def wind(d, lvl=0.04, f=(180, 1400)):
        t = np.arange(int(d * SR)) / SR; return bp(noise(d), f[0], f[1]) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 4.1 + 1)) * lvl * env(d, 0.8, 0.8)
    def crack(lvl=0.1):
        t = np.arange(int(0.25 * SR)) / SR; return (bp(rng.normal(0, 1, len(t)), 600, 5000) * np.exp(-t * 40) + np.sin(2 * np.pi * 140 * t) * np.exp(-t * 18) * 0.6) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: the trading post, the fall through the air, the blast, the forest going down, Europe at night, 1927, the last look
    place(bed, wind(7.4, 0.03), 0.0); place(bed, gulls(4.2, 0.012, 4), 0.5, pan=0.3); place(bed, pad(["A2", "E3", "A3", "C4"], 7.4, 1.0, 0.6, 0.03), 0.0)
    place(bed, rumble(13.8, 0.05) * np.linspace(0.15, 1.0, int(13.8 * SR)) ** 2, 6.8); place(bed, pad(["D2", "A2", "F3"], 13.8, 0.6, 0.3, 0.04), 6.8)
    place(bed, riser(13.4, 0.05), 7.1)
    place(bed, rumble(16.6, 0.11) * env(16.6, 0.05, 6.0), 20.5); place(bed, pad(["C2", "G2", "D#3"], 16.6, 0.4, 1.2, 0.04), 20.5)
    place(bed, pad(["E2", "B2", "E3", "G3", "D4"], 6.2, 0.8, 0.8, 0.036), 36.8); place(bed, shimmer(5.8, 0.016, ("E5", "G5", "B5", "D6")), 37.0); place(bed, bell(440, 2.6, 0.02), 37.4, pan=-0.3)
    place(bed, wind(9.0, 0.045, (140, 900)), 42.8); place(bed, pad(["F2", "C3", "A3"], 9.0, 0.8, 0.8, 0.032), 42.8)
    place(bed, wind(5.5, 0.04), 51.6); place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], 5.6, 0.5, 1.8, 0.034), 51.6)
    # effects
    place(fx, whoosh(1.6, 0.06), 4.8, pan=0.4)
    for ts in [7.0, 12.9, 29.4, 32.9, 36.9, 42.9, 51.7]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
    for k in range(5): place(fx, crack(0.05), 19.0 + k * 0.3, pan=(k % 3 - 1) * 0.4)
    place(fx, boom(34, 4.5, 0.9), 20.5); place(fx, boom(60, 1.2, 0.5), 20.5); place(fx, boom(38, 3.0, 0.55), 24.2); place(fx, boom(44, 1.2, 0.25), 29.4)
    r2 = np.random.default_rng(9)
    for k in range(70): place(fx, crack(float(r2.uniform(0.03, 0.09))), 24.4 + float(r2.uniform(0, 8.3)), pan=float(r2.uniform(-0.7, 0.7)))
    place(fx, riser(1.2, 0.04), 50.6)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/tunguska.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

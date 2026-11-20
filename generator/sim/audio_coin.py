"""Soundtrack + narration for the empty-space-in-coin simulation. Writes work/coin.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 47.2
LINES = [(0.4, "What if you dropped a coin from the top of a skyscraper?"),
 (3.3, "You're four hundred metres up. People say a coin dropped from here would hit like a bullet."),
 (8.8, "With no air, they'd be right. It would land at three hundred and twenty kilometres an hour."),
 (13.9, "But there is air. And a coin is flat and light. After about fifteen metres, the air pushes up as hard as gravity pulls down. So it stops speeding up."),
 (22.9, "It flutters down like a leaf, at about forty kilometres an hour."),
 (26.7, "A physicist tested it, with coins dropped from balloons. Getting hit felt like a flick on the forehead."),
 (32.8, "Now drop a pen. It's narrow, and heavy for its size, so it falls like an arrow, several times faster. Fast enough to chip the pavement."),
 (40.9, "It's not the height that makes a fall dangerous. It's the shape."), (44.9, "Follow for more.")]
CHUNKS = [[], ["You're <em>400 metres</em> up.", "People say a coin<br>dropped from here", "would hit like a <em>bullet</em>."],
 ["With <em>no air</em>,<br>they'd be right.", "It would land at<br><em>320 km/h</em>."],
 ["But there <em>is</em> air.", "And a coin is<br><em>flat and light</em>.", "After about <em>15 metres</em>,", "the air pushes up as hard<br>as gravity pulls down.", "So it <em>stops</em><br>speeding up."],
 ["It flutters down<br>like a <em>leaf</em>,", "at about <em>40 km/h</em>."],
 ["A physicist tested it,", "with coins dropped<br>from <em>balloons</em>.", "Getting hit felt like<br>a <em>flick on the forehead</em>."],
 ["Now drop a <em>pen</em>.", "It's narrow, and heavy<br>for its size,", "so it falls like an <em>arrow</em>,", "several times faster.", "Fast enough to<br><em>chip the pavement</em>."],
 ["It's not the <em>height</em> that<br>makes a fall dangerous.", "It's the <em>shape</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(17)
    def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
    def noise(d): return rng.normal(0, 1, int(d * SR))
    def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
    def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
    def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
    def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
    def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
        return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
    def boom(f=46, d=1.8, lvl=0.5):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
    def whoosh(d=0.7, lvl=0.09):
        m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 500, 6000) * 0.6 * np.sin(np.pi * t / d) ** 2 * lvl
    def riser(d=2.0, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
    def shimmer(d, lvl=0.022, notes=("C5", "E5", "G5", "B5", "D6")):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(notes)) * env(d, 0.8, 1.0) * lvl
    def clicks(d, rate, lvl=0.06, seed=3, f0=2400, f1=5200):
        """Geiger-style clicks at `rate` per second (random, like real decays)."""
        out = np.zeros(int(d * SR)); r = np.random.default_rng(seed); t0 = 0.0
        while True:
            t0 += r.exponential(1 / rate)
            if t0 > d - 0.03: break
            tt = np.arange(int(0.012 * SR)) / SR; c = np.sin(2 * np.pi * r.uniform(f0, f1) * tt) * np.exp(-tt * 600) * r.uniform(0.5, 1); i = int(t0 * SR); out[i:i + len(c)] += c
        return out * lvl
    def zap(lvl=0.1):
        d = 0.28; m = int(d * SR); t = np.arange(m) / SR; return (np.sin(2 * np.pi * np.cumsum(np.linspace(3200, 500, m)) / SR) * 0.6 + hp(noise(d), 3000) * 0.4) * np.exp(-t * 16) * lvl
    def room(d, lvl=0.012): return (lp(noise(d), 160, 2) * 2 + np.sin(2 * np.pi * 50 * np.arange(int(d * SR)) / SR) * 0.35) * env(d, 0.5, 0.5) * lvl
    def city(d, lvl=0.03): return (lp(noise(d), 300, 2) * 2.2 + bp(noise(d), 300, 1500) * 0.25) * env(d, 0.6, 1.2) * lvl
    def klaxon(d, lvl=0.05):
        t = np.arange(int(d * SR)) / SR; return np.sign(np.sin(2 * np.pi * 520 * t)) * (np.sin(2 * np.pi * 1.45 * t) > 0) * lp(np.ones(len(t)), 800) * lvl * env(d, 0.05, 0.1)
    def beep(f=2525, d=0.25, lvl=0.035): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t) * env(d, 0.005, 0.02) * lvl
    def hiss(d, lvl=0.08, a=0.02, r=0.6): return hp(noise(d), 2500) * env(d, a, r, 1.5) * lvl
    def whir(d, lvl=0.04):
        t = np.arange(int(d * SR)) / SR; f = 60 + 160 * np.minimum(1, t / 1.2); return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 3) / SR)) * env(d, 0.3, 0.4) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * lvl
    def radio(d, lvl=0.012): return bp(noise(d), 600, 2600) * env(d, 0.05, 0.1) * lvl
    def splash(lvl=0.2):
        d = 1.6; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 300, 5000) * np.exp(-t * 3.2) + lp(noise(d), 200) * np.exp(-t * 5) * 1.5) * np.minimum(1, t / 0.02) * lvl
    def wind(d, lvl=0.05, f0=300, f1=1800): t = np.arange(int(d * SR)) / SR; return bp(noise(d), f0, f1) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.31 * t + 1) ** 2) * env(d, 0.5, 0.5) * lvl
    def ting(f=3100, d=0.5, lvl=0.07): t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 11) * lvl
    def crack(lvl=0.2): d = 0.5; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 700, 6000) * np.exp(-t * 16) + lp(noise(d), 160) * np.exp(-t * 6) * 2) * lvl
    def fall(d, lvl=0.06): m = int(d * SR); t = np.arange(m) / SR; return np.sin(2 * np.pi * np.cumsum(np.linspace(1500, 380, m)) / SR) * (t / d) ** 1.5 * env(d, 0.05, 0.03) * lvl + bp(noise(d), 800, 5000) * (t / d) ** 2 * lvl * 0.8
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: skyline, rooftop wind, the no-air drop, the slow close-up, the street test, the pen, the ending
    place(bed, pad(["D2", "A2", "D3", "F3"], 8.8, 0.8, 0.8, 0.036), 0.0); place(bed, wind(8.6, 0.05), 0.0); place(bed, shimmer(3.2, 0.014), 0.2)
    place(bed, pad(["C2", "G2", "Eb3", "G3"], 5.3, 0.3, 0.5, 0.042), 8.5); place(bed, wind(3.6, 0.03), 8.6); place(bed, city(1.6, 0.03), 12.1)
    place(bed, pad(["F2", "C3", "A3", "E4"], 9.2, 0.5, 0.7, 0.036), 13.6); place(bed, wind(9.0, 0.035, 500, 2600), 13.7); place(bed, shimmer(8.6, 0.013, ("C5", "E5", "A5", "B5", "E6")), 13.9)
    place(bed, pad(["G2", "D3", "B3", "D4"], 4.0, 0.3, 0.5, 0.036), 22.6); place(bed, wind(3.8, 0.045), 22.7)
    place(bed, pad(["A2", "E3", "A3", "C#4"], 6.3, 0.4, 0.6, 0.034), 26.4); place(bed, city(6.1, 0.03), 26.5)
    place(bed, pad(["B1", "F#2", "D3", "A3"], 8.3, 0.3, 0.6, 0.044), 32.5); place(bed, wind(4.4, 0.04, 600, 3200), 32.6); place(bed, city(3.9, 0.028), 36.9)
    place(bed, pad(["D2", "A2", "D3", "F#3", "A3", "E4"], 6.6, 0.5, 2.0, 0.038), 40.6); place(bed, wind(6.0, 0.03), 40.7); place(bed, shimmer(6.0, 0.016), 40.8)
    # effects
    place(fx, boom(70, 0.7, 0.2), 0.03); place(fx, whoosh(0.6, 0.07), 3.0); place(fx, ting(3300, 0.4, 0.04), 4.4); place(fx, riser(1.6, 0.05), 7.0)
    place(fx, whoosh(0.6, 0.09), 8.4); place(fx, ting(3300, 0.3, 0.05), 9.1); place(fx, fall(3.2, 0.07), 9.1); place(fx, boom(42, 1.6, 0.6), 12.3); place(fx, crack(0.3), 12.3); place(fx, crack(0.16), 12.5, pan=0.4)
    place(fx, whoosh(0.7, 0.09), 13.5); place(fx, boom(60, 0.5, 0.16), 13.7); place(fx, ting(3300, 0.3, 0.05), 14.1)
    for k in range(14): place(fx, ting(2500 + (k % 3) * 300, 0.18, 0.012), 15.0 + k * 0.55, pan=(-0.3 if k % 2 else 0.3))
    place(fx, beep(1500, 0.1, 0.025), 19.6); place(fx, boom(70, 0.5, 0.16), 21.2)
    place(fx, whoosh(0.6, 0.08), 22.5); place(fx, whoosh(0.6, 0.08), 26.3)
    for k, ts in enumerate([29.9, 30.1, 30.9, 31.5, 32.0]): place(fx, ting(3000 + k * 170, 0.4, 0.04), ts, pan=(k - 2) * 0.25)
    place(fx, ting(2400, 0.25, 0.06), 30.48); place(fx, whoosh(0.6, 0.09), 32.4); place(fx, boom(55, 0.6, 0.2), 32.6)
    place(fx, fall(4.6, 0.09), 33.1); place(fx, riser(1.0, 0.07), 36.7); place(fx, boom(48, 1.2, 0.5), 37.7); place(fx, crack(0.32), 37.7); place(fx, crack(0.14), 37.95, pan=-0.4); place(fx, ting(1800, 0.3, 0.04), 38.15)
    place(fx, whoosh(0.6, 0.08), 40.5); place(fx, boom(60, 0.7, 0.18), 40.7); place(fx, whoosh(0.4, 0.09), 42.1); place(fx, riser(1.4, 0.04), 43.2)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/coin.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

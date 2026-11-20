"""Soundtrack + narration for the oxygen-vanished simulation. Writes work/oxygen.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 48.6
LINES = [(0.4, "What if all the oxygen vanished for five seconds?"),
 (3.3, "The viral answer says buildings crumble to dust. They wouldn't."),
 (6.7, "You're on a street. A fifth of the air is oxygen. Now it's gone."),
 (10.6, "The air pressure drops by a fifth, as if you'd been lifted two kilometres up. Your ears pop."),
 (16.1, "Every candle and gas flame goes out. Engines cut. Cars stall at the lights."),
 (21.4, "Above you, a jet's engines flame out, and thinner air means less lift. It sags, but it glides."),
 (27.2, "And you? You'd probably stay awake. Your blood holds a few seconds of oxygen."),
 (31.9, "Five. The oxygen is back."),
 (33.8, "So where do crumbling buildings come from? From deleting every oxygen atom: in concrete, water and rock. But you're more than sixty percent oxygen too."),
 (43.3, "Oxygen isn't just in the air. It's most of you."), (46.3, "Follow for more.")]
CHUNKS = [[], ["The viral answer says<br>buildings <em>crumble to dust</em>.", "They <em>wouldn't</em>."],
 ["You're on a street.", "A <em>fifth</em> of the air<br>is oxygen.", "Now it's <em>gone</em>."],
 ["The air pressure<br>drops by a <em>fifth</em>,", "as if you'd been lifted<br><em>two kilometres</em> up.", "Your ears <em>pop</em>."],
 ["Every candle and gas flame<br><em>goes out</em>.", "Engines <em>cut</em>.", "Cars <em>stall</em> at the lights."],
 ["Above you, a jet's engines<br><em>flame out</em>,", "and thinner air<br>means <em>less lift</em>.", "It sags,", "but it <em>glides</em>."],
 ["And you?", "You'd probably<br><em>stay awake</em>.", "Your blood holds a few<br>seconds of oxygen."],
 ["<em>Five.</em>", "The oxygen is <em>back</em>."],
 ["So where do crumbling<br>buildings come from?", "From deleting every<br>oxygen <em>atom</em>:", "in concrete,<br>water and rock.", "But you're more than<br><em>60% oxygen</em> too."],
 ["Oxygen isn't just<br>in the air.", "It's <em>most of you</em>."], []]
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
    G0, BK = 9.5, 32.3   # oxygen gone / back
    # beds: skyline, street, the five silent seconds (thin, airless), the return, the atoms, the ending
    place(bed, pad(["D2", "A2", "D3", "F3"], 6.9, 0.8, 0.8, 0.036), 0.0); place(bed, city(6.6, 0.03), 0.0); place(bed, shimmer(3.0, 0.014), 0.2)
    place(bed, pad(["A2", "E3", "A3", "C4"], 3.2, 0.3, 0.4, 0.034), 6.5); place(bed, city(3.0, 0.045), 6.5)
    place(bed, pad(["C2", "G2", "Eb3", "G3"], BK - G0 + 0.3, 0.2, 0.6, 0.04), G0); place(bed, wind(BK - G0, 0.022, 900, 3600), G0); place(bed, shimmer(BK - G0, 0.01, ("C5", "Eb5", "G5", "Bb5", "D6")), G0)
    place(bed, pad(["F2", "C3", "A3", "E4"], 2.2, 0.2, 0.5, 0.036), BK - 0.2); place(bed, city(2.0, 0.04), BK)
    place(bed, pad(["B1", "F2", "D3", "A3"], 9.8, 0.3, 0.6, 0.042), 33.6); place(bed, rumble(5.6, 0.05) * env(5.6, 1.0, 1.0)[:, None][:, 0], 34.2)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 5.6, 0.5, 2.0, 0.038), 43.0); place(bed, city(5.2, 0.028), 43.2); place(bed, shimmer(5.2, 0.016), 43.2)
    # effects
    place(fx, boom(70, 0.7, 0.2), 0.03); place(fx, whoosh(0.6, 0.07), 3.0); place(fx, rumble(1.9, 0.12) * env(1.9, 0.5, 0.4), 3.6); place(fx, crack(0.14), 4.3); place(fx, crack(0.1), 4.8, pan=0.4)
    place(fx, zap(0.09), 5.6); place(fx, boom(60, 0.5, 0.2), 5.65); place(fx, whoosh(0.6, 0.08), 6.4)
    for k in range(6): place(fx, ting(2600 + (k % 3) * 400, 0.25, 0.014), 7.9 + k * 0.22, pan=(-0.4 if k % 2 else 0.4))
    place(fx, riser(1.2, 0.06), G0 - 1.2); place(fx, boom(44, 1.5, 0.5), G0); place(fx, hiss(1.4, 0.07, 0.01, 1.2), G0); place(fx, whoosh(0.5, 0.08), 10.4)
    place(fx, ting(1700, 0.5, 0.05), 14.9); place(fx, ting(1700, 0.5, 0.05), 15.05, pan=0.5); place(fx, whoosh(0.6, 0.08), 15.9)
    place(fx, hiss(1.6, 0.06, 0.02, 1.4), 16.6); place(fx, hiss(0.7, 0.04, 0.02, 0.6), 17.4, pan=0.4); place(fx, whoosh(0.5, 0.08), 18.6)
    t = np.arange(int(2.2 * SR)) / SR; f = 95 * np.exp(-t * 1.5) + 12; place(fx, (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + lp(noise(2.2), 200) * 0.8) * np.exp(-t * 1.3) * 0.07, 18.5)
    place(fx, whoosh(0.6, 0.08), 21.2); m = int(4.5 * SR); t = np.arange(m) / SR; place(fx, (np.sin(2 * np.pi * np.cumsum(np.linspace(900, 260, m)) / SR) * 0.4 + bp(noise(4.5), 300, 2500) * 0.6) * env(4.5, 0.3, 1.5) * 0.05, 21.6)
    place(fx, wind(3.0, 0.05, 400, 2200), 24.5); place(fx, whoosh(0.6, 0.07), 27.0)
    for k, ts in enumerate([28.0, 28.9, 29.8, 30.7]): place(fx, boom(52, 0.25, 0.1), ts); place(fx, boom(46, 0.2, 0.07), ts + 0.22)
    place(fx, riser(1.2, 0.06), BK - 1.2); place(fx, boom(60, 1.0, 0.4), BK); place(fx, shimmer(1.8, 0.03), BK)
    place(fx, whoosh(0.6, 0.09), 33.6); place(fx, crack(0.18), 35.2); place(fx, crack(0.12), 36.0, pan=-0.4); place(fx, crack(0.1), 37.0, pan=0.3)
    for k, ts in enumerate([37.6, 38.3, 38.9]): place(fx, ting(2200 + k * 300, 0.4, 0.04), ts)
    place(fx, whoosh(0.6, 0.09), 40.2); place(fx, boom(50, 0.9, 0.3), 40.4); place(fx, ting(3000, 0.5, 0.05), 41.2)
    place(fx, whoosh(0.6, 0.08), 43.0); place(fx, boom(60, 0.7, 0.18), 43.2); place(fx, riser(1.3, 0.04), 45.0)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/oxygen.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

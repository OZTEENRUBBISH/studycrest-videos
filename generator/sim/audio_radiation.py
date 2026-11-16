"""Soundtrack + narration for the see-radiation simulation. Writes work/radiation.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 47.0
LINES = [(0.4, "What if you could see radiation?"), (2.6, "You're in your kitchen. Every time an atom decays, you see a flash."),
 (6.4, "The first thing glowing, is you. Around seven thousand atoms decay inside your body, every second."),
 (12.5, "It's mostly potassium and carbon. You've been radioactive since before you were born."),
 (17.6, "The banana sparkles too. About fifteen flashes a second."),
 (21.1, "The brightest thing in the room is the smoke alarm. Up to thirty seven thousand flashes a second. But its particles only travel a few centimetres."),
 (30.2, "Now step outside. Streaks rain down from the sky. Cosmic rays. One or two pass through your hand, every second."),
 (37.2, "None of this is new. Life has always lived inside this glow."),
 (40.8, "Radiation isn't rare. What matters is the dose."), (44.1, "Follow for more.")]
CHUNKS = [[], ["You're in<br>your kitchen.", "Every time<br>an atom decays,", "you see a <em>flash</em>."],
 ["The first thing glowing", "is <em>you</em>.", "Around <em>seven thousand</em><br>atoms decay", "inside your body,", "every second."],
 ["It's mostly<br><em>potassium</em> and <em>carbon</em>.", "You've been radioactive", "since before<br>you were born."],
 ["The <em>banana</em><br>sparkles too.", "About fifteen flashes<br>a second."],
 ["The brightest thing<br>in the room", "is the <em>smoke alarm</em>.", "Up to thirty-seven thousand<br>flashes a second.", "But its particles only travel", "a <em>few centimetres</em>."],
 ["Now step outside.", "Streaks rain down<br>from the sky.", "<em>Cosmic rays</em>.", "One or two pass<br>through your hand,", "every second."],
 ["None of this is new.", "Life has always lived<br>inside this <em>glow</em>."],
 ["Radiation isn't rare.", "What matters<br>is the <em>dose</em>."], []]
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
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: a warm kitchen, then the dark "vision" pad, then the open street
    place(bed, pad(["F2", "C3", "A3", "E4"], 4.8, 0.6, 0.8, 0.036), 0.0); place(bed, room(4.6), 0.0)
    place(bed, pad(["D2", "A2", "F3"], 8.6, 0.6, 0.8, 0.04), 4.2); place(bed, shimmer(8.2, 0.014), 4.4)
    place(bed, pad(["A1", "F2", "D3", "A3"], 5.5, 0.6, 0.8, 0.038), 12.4); place(bed, shimmer(5.0, 0.012, ("D5", "F5", "A5", "C6")), 12.6)
    place(bed, pad(["C2", "G2", "E3"], 3.9, 0.4, 0.6, 0.036), 17.5)
    place(bed, pad(["A1", "E2", "C3", "G3"], 9.5, 0.6, 0.8, 0.042), 21.0)
    place(bed, pad(["D2", "A2", "D3", "F3"], 7.4, 0.5, 0.8, 0.04), 30.1); place(bed, city(7.2), 30.2)
    place(bed, pad(["F2", "C3", "A3", "E4"], 4.0, 0.5, 0.8, 0.04), 37.1); place(bed, city(4.0, 0.02), 37.1)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 6.4, 0.5, 2.0, 0.038), 40.7); place(bed, shimmer(6.0, 0.016), 40.8)
    # effects: the counter clicks faster for brighter things
    place(fx, whoosh(0.6, 0.07), 2.35); place(fx, riser(1.2, 0.05), 3.1); place(fx, boom(52, 1.4, 0.38), 4.3)
    place(fx, clicks(2.0, 9, 0.035, 1), 4.4); place(fx, clicks(6.2, 34, 0.04, 2), 6.3); place(fx, clicks(5.2, 26, 0.03, 3), 12.4)
    place(fx, whoosh(0.5, 0.06), 17.35); place(fx, clicks(3.5, 15, 0.06, 4, 1800, 3200), 17.6)
    place(fx, whoosh(0.5, 0.06), 20.85); place(fx, clicks(5.4, 60, 0.035, 5, 3200, 6000), 21.2); place(fx, whoosh(0.5, 0.06), 26.35); place(fx, clicks(3.5, 90, 0.03, 6, 3200, 6000), 26.6)
    place(fx, riser(1.0, 0.05), 29.2); place(fx, boom(46, 1.8, 0.4), 30.2); place(fx, whoosh(0.7, 0.09), 30.0)
    for k, tt in enumerate(np.random.default_rng(9).uniform(31.0, 44.0, 60)): place(fx, zap(0.035), float(tt), 1.0, float(np.random.default_rng(k).uniform(-0.7, 0.7)))
    place(fx, whoosh(0.5, 0.06), 33.15)
    for tt in [33.75, 34.4, 34.85, 35.6, 36.05, 36.75]: place(fx, zap(0.13), tt)
    place(fx, whoosh(0.6, 0.08), 36.95); place(fx, riser(1.4, 0.05), 39.4); place(fx, boom(46, 1.8, 0.36), 40.8)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/radiation.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

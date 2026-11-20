"""Soundtrack + narration for the empty-space-in-Chicago Pile-1 simulation. Writes work/coin.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 55.4
LINES = [(0.4, "The first nuclear chain reaction, minute by minute."),
 (3.4, "Chicago, December the second, nineteen forty two. Under a football stadium, in a squash court, sits a pile of graphite bricks, seeded with uranium."),
 (12.3, "No shielding. No cooling. Just cadmium rods that soak up neutrons. And a man with an axe, ready to cut a rope and drop a safety rod."),
 (20.5, "Eleven thirty five. A safety rod slams in by itself. It was set too cautiously. Enrico Fermi says: I'm hungry. Let's go to lunch."),
 (29.3, "Around three twenty five, the last rod slides out one more foot. The counters click faster, and faster, and this time they don't level off."),
 (37.4, "Each splitting atom now sets off another. Fermi says: the reaction is self-sustaining."),
 (42.7, "Its power? About half a watt. A kettle uses thousands of times more. After twenty eight minutes, they shut it down."),
 (49.5, "The atomic age began with a pile of bricks, and a lunch break."), (53.1, "Follow for more.")]
CHUNKS = [[], ["Chicago, <em>2 December 1942</em>.", "Under a football stadium,", "in a <em>squash court</em>,", "sits a pile of<br>graphite bricks,", "seeded with <em>uranium</em>."],
 ["No shielding.", "No cooling.", "Just <em>cadmium rods</em><br>that soak up neutrons.", "And a man with an <em>axe</em>,", "ready to cut a rope and<br>drop a safety rod."],
 ["<em>11:35</em>.", "A safety rod slams in<br><em>by itself</em>.", "It was set too cautiously.", "Enrico Fermi says:", "<em>“I'm hungry.</em>", "<em>Let's go to lunch.”</em>"],
 ["Around <em>3:25</em>,", "the last rod slides out<br><em>one more foot</em>.", "The counters click faster,", "and faster,", "and this time they<br><em>don't level off</em>."],
 ["Each splitting atom now<br>sets off <em>another</em>.", "Fermi says:", "<em>“The reaction is<br>self-sustaining.”</em>"],
 ["Its power?", "About <em>half a watt</em>.", "A kettle uses thousands<br>of times more.", "After <em>28 minutes</em>,", "they shut it down."],
 ["The atomic age began with<br>a <em>pile of bricks</em>,", "and a <em>lunch break</em>."], []]
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
    def thud(lvl=0.5): d = 0.7; t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 7) + bp(noise(d), 300, 3000) * np.exp(-t * 25) * 0.6) * lvl
    def slide(d=1.2, lvl=0.035): t = np.arange(int(d * SR)) / SR; return bp(noise(d), 900, 3200) * env(d, 0.1, 0.2) * lvl * (0.7 + 0.3 * np.sin(2 * np.pi * 13 * t))
    def steps(d, lvl=0.03):
        out = np.zeros(int(d * SR)); r = np.random.default_rng(5)
        for k in np.arange(0.1, d - 0.2, 0.27): tt = np.arange(int(0.08 * SR)) / SR; c = lp(r.normal(0, 1, len(tt)), 500) * np.exp(-tt * 60) * r.uniform(0.5, 1); i = int((k + r.uniform(0, 0.08)) * SR); out[i:i + len(c)] += c
        return out * lvl * 6 * env(d, 0.2, 1.2)
    def ramp(d, r0, r1, lvl=0.05, seed=3):
        """Counter clicks whose rate climbs from r0 to r1 per second."""
        out = np.zeros(int(d * SR)); r = np.random.default_rng(seed); t0 = 0.0
        while True:
            rate = r0 * (r1 / r0) ** (t0 / d); t0 += r.exponential(1 / rate)
            if t0 > d - 0.03: break
            tt = np.arange(int(0.012 * SR)) / SR; c = np.sin(2 * np.pi * r.uniform(2400, 5200) * tt) * np.exp(-tt * 600) * r.uniform(0.5, 1); i = int(t0 * SR); out[i:i + len(c)] += c
        return out * lvl
    def clink(lvl=0.03):
        out = np.zeros(int(0.8 * SR)); tt = np.arange(int(0.3 * SR)) / SR
        for k, f in enumerate([1900, 2300, 1700]): i = int(k * 0.11 * SR); out[i:i + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 18)
        return out * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: the street, the court, the wait, lunch, the climb, the diagram, the half watt, the toast
    place(bed, city(7.2, 0.03), 0.0); place(bed, pad(["D2", "A2", "D3", "F3"], 7.4, 0.8, 0.8, 0.036), 0.0)
    place(bed, room(13.6, 0.016), 6.9); place(bed, pad(["C2", "G2", "Eb3", "G3"], 5.6, 0.4, 0.6, 0.04), 6.9); place(bed, clicks(13.4, 2.2, 0.03, 4), 7.0)
    place(bed, pad(["Bb1", "F2", "Db3", "F3"], 8.5, 0.5, 0.6, 0.04), 12.1)
    place(bed, room(9.0, 0.016), 20.3); place(bed, pad(["A1", "E2", "C3", "E3"], 4.6, 0.3, 0.5, 0.042), 20.3); place(bed, clicks(2.2, 5, 0.03, 6), 20.4)
    place(bed, pad(["F2", "C3", "A3", "C4"], 4.6, 0.4, 0.6, 0.032), 24.7); place(bed, steps(2.6, 0.03), 26.4)
    place(bed, room(8.4, 0.016), 29.1); place(bed, pad(["D2", "A2", "D3", "F3"], 8.4, 0.5, 0.4, 0.04), 29.1); place(bed, ramp(6.6, 3, 90, 0.04), 30.7)
    place(bed, pad(["E2", "B2", "G#3", "B3", "E4"], 5.5, 0.3, 0.6, 0.04), 37.2); place(bed, shimmer(5.0, 0.016), 37.4); place(bed, clicks(5.2, 90, 0.016, 8), 37.3)
    place(bed, room(7.0, 0.014), 42.5); place(bed, pad(["G2", "D3", "B3", "D4"], 7.0, 0.4, 0.6, 0.034), 42.5); place(bed, clicks(4.5, 90, 0.014, 9), 42.6)
    place(bed, pad(["D2", "A2", "D3", "F#3", "A3", "E4"], 6.2, 0.5, 2.0, 0.038), 49.3); place(bed, room(5.8, 0.012), 49.4); place(bed, shimmer(5.6, 0.016), 49.5)
    # effects
    place(fx, boom(70, 0.7, 0.2), 0.03); place(fx, whoosh(0.6, 0.07), 3.1); place(fx, riser(1.4, 0.05), 5.6); place(fx, boom(46, 1.4, 0.34), 7.0)
    for ts in [12.0, 14.5, 17.2, 20.2, 24.6, 27.1]: place(fx, whoosh(0.55, 0.07), ts)
    place(fx, slide(1.6, 0.03), 15.2); place(fx, riser(1.2, 0.05), 21.3); place(fx, thud(0.6), 22.5); place(fx, boom(50, 0.9, 0.3), 22.5)
    place(fx, boom(60, 0.6, 0.18), 29.2); place(fx, slide(1.3, 0.04), 30.2); place(fx, whoosh(0.55, 0.07), 32.2); place(fx, riser(2.6, 0.07), 34.5)
    place(fx, boom(44, 1.3, 0.36), 37.3)
    for k in range(5): place(fx, zap(0.05), 37.65 + k * 0.62); place(fx, boom(80, 0.3, 0.12), 37.65 + k * 0.62)
    place(fx, whoosh(0.55, 0.07), 40.1); place(fx, boom(55, 0.9, 0.24), 40.3); place(fx, whoosh(0.55, 0.07), 42.4); place(fx, beep(1500, 0.1, 0.025), 44.6)
    place(fx, whoosh(0.55, 0.07), 46.1); place(fx, riser(0.8, 0.05), 46.3); place(fx, thud(0.55), 47.3); place(fx, boom(50, 1.0, 0.3), 47.3)
    place(fx, whoosh(0.6, 0.07), 49.2); place(fx, boom(60, 0.7, 0.16), 49.4); place(fx, clink(0.03), 50.9); place(fx, riser(1.4, 0.04), 51.5)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/pile.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

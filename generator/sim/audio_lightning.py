"""Soundtrack + narration for the lightning-strikes-your-plane simulation. Writes work/lightning.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 48.2
LINES = [(0.4, "What if lightning struck your plane?"),
 (2.4, "It will. An airliner gets hit about once or twice a year. And almost every time, it just flies on."),
 (8.5, "You're in your seat, inside a storm cloud. The plane itself often sets the bolt off."),
 (13.65, "It strikes the nose. A flash. A bang."),
 (16.0, "But the current doesn't come inside. It runs through the metal skin, around you, and leaves from the tail."),
 (21.8, "That bolt heats the air hotter than the surface of the Sun. And you're sitting safely in the middle of it."),
 (27.4, "It wasn't always this safe. In 1963, lightning ignited fuel vapour in a jet's wing tank. Eighty-one people died."),
 (36.3, "Fuel tanks were redesigned, and every airliner design now has to pass lightning tests."),
 (42.0, "Lightning doesn't miss planes. Planes are built to be hit."), (45.4, "Follow for more.")]
CHUNKS = [[], ["It <em>will</em>.", "An airliner gets hit", "about <em>once or twice</em><br>a year.", "And almost every time,", "it just <em>flies on</em>."],
 ["You're in your seat,", "inside a <em>storm cloud</em>.", "The plane itself", "often <em>sets the bolt off</em>."],
 ["It strikes the <em>nose</em>.", "A flash.", "A bang."],
 ["But the current<br><em>doesn't come inside</em>.", "It runs through<br>the <em>metal skin</em>,", "around you,", "and leaves<br>from the <em>tail</em>."],
 ["That bolt heats the air", "<em>hotter</em> than the<br>surface of the Sun.", "And you're sitting <em>safely</em>", "in the middle of it."],
 ["It wasn't always<br>this safe.", "In <em>1963</em>,", "lightning ignited<br><em>fuel vapour</em>", "in a jet's wing tank.", "Eighty-one people died."],
 ["Fuel tanks were<br><em>redesigned</em>,", "and every airliner design", "now has to pass<br><em>lightning tests</em>."],
 ["Lightning doesn't<br><em>miss</em> planes.", "Planes are<br><em>built to be hit</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(31)
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
    def ting(f=3100, d=0.5, lvl=0.07): t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 11) * lvl
    def ding(lvl=0.05): return ting(1320, 0.9, lvl) + ting(1760, 0.9, lvl * 0.5)
    def waves(d, lvl=0.05): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 300, 2600) * (0.35 + 0.65 * np.sin(2 * np.pi * 0.21 * t) ** 2) + lp(noise(d), 200) * 0.8) * env(d, 0.5, 0.6) * lvl
    def gull(lvl=0.03): d = 0.45; t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * np.cumsum(2300 - 900 * (t / d) + 250 * np.sin(2 * np.pi * 9 * t)) / SR) * np.sin(np.pi * t / d) ** 2 * lvl
    def deep(d, lvl=0.05, f=180): t = np.arange(int(d * SR)) / SR; return (lp(noise(d), f, 4) * 3 + np.sin(2 * np.pi * 41 * t) * 0.25 * (1 + 0.5 * np.sin(2 * np.pi * 0.13 * t))) * env(d, 0.6, 0.8) * lvl
    def bubbles(d, lvl=0.05, rate=9):
        m = int(d * SR); x = np.zeros(m)
        for _ in range(int(d * rate)):
            i = int(rng.uniform(0, m - 4000)); L = int(rng.uniform(0.03, 0.09) * SR); t = np.arange(L) / SR; f0 = rng.uniform(380, 1500)
            x[i:i + L] += np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.6 * t / t[-1])) / SR) * np.sin(np.pi * t / t[-1]) ** 2 * rng.uniform(0.3, 1)
        return lp(x, 3000) * env(d, 0.1, 0.5) * lvl
    def splash(lvl=0.12): d = 1.1; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 400, 5000) * np.exp(-t * 5) + lp(noise(d), 250) * np.exp(-t * 3) * 1.5) * lvl
    def sonar(lvl=0.05, f=1180): d = 1.6; t = np.arange(int(d * SR)) / SR; x = np.sin(2 * np.pi * f * t) * np.exp(-t * 4) * lvl; e = np.zeros_like(x); k = int(0.33 * SR); e[k:] = x[:-k] * 0.35; return x + e
    def creak(lvl=0.08, d=1.2): m = int(d * SR); t = np.arange(m) / SR; return (np.sign(np.sin(2 * np.pi * np.cumsum(np.linspace(58, 34, m)) / SR)) * 0.3 + lp(noise(d), 120, 3) * 2) * env(d, 0.15, 0.6) * lvl
    def squeeze(d=1.4, lvl=0.06): m = int(d * SR); t = np.arange(m) / SR; return np.sin(2 * np.pi * np.cumsum(np.linspace(700, 190, m)) / SR) * env(d, 0.05, 0.4) * lvl + bubbles(d, lvl * 0.8, 14)
    def heart(lvl=0.16): d = 0.5; t = np.arange(int(d * SR)) / SR; x = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 22); k = int(0.16 * SR); y = x.copy(); y[k:] += x[:-k] * 0.7; return lp(y, 160) * lvl
    def alarm(lvl=0.035, f=880): d = 0.22; t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t)) * np.sin(np.pi * t / d) ** 2 * lvl
    def gasp(lvl=0.07, d=0.8): m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 700, 4200) * np.sin(np.pi * t / d) ** 1.5 * lvl
    def puff(lvl=0.04): return gasp(lvl, 0.22)
    def thud(lvl=0.2): d = 0.3; t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * 70 * t) * np.exp(-t * 18) * lvl
    def kids(d, lvl=0.012): t = np.arange(int(d * SR)) / SR; return bp(noise(d), 900, 3200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t) ** 2) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t + 1) ** 4) * env(d, 0.4, 0.5) * lvl
    def thunder(d=3.2, lvl=0.5):
        t = np.arange(int(d * SR)) / SR; return (lp(noise(d), 110, 3) * 5 * np.exp(-t * 1.5) * (1 + 0.6 * np.sin(2 * np.pi * 3.1 * t) * np.exp(-t)) + boom(42, d, 0.9)[: len(t)]) * lvl * 0.5
    def crack(lvl=0.3): d = 0.5; t = np.arange(int(d * SR)) / SR; return (hp(noise(d), 1800) * np.exp(-t * 16) + bp(noise(d), 300, 2500) * np.exp(-t * 7) * 0.8) * lvl
    def zap(d=0.25, lvl=0.08): t = np.arange(int(d * SR)) / SR; return hp(noise(d), 2500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 110 * t))) * np.exp(-t * 9) * lvl
    def buzz(d, lvl=0.035): t = np.arange(int(d * SR)) / SR; return (np.sign(np.sin(2 * np.pi * 100 * t)) * 0.4 + hp(noise(d), 3000) * 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 13 * t)) * env(d, 0.15, 0.4) * lvl
    def drone(d, lvl=0.05): t = np.arange(int(d * SR)) / SR; return (lp(noise(d), 240, 3) * 2.2 + np.sin(2 * np.pi * 87 * t) * 0.3 + np.sin(2 * np.pi * 131 * t) * 0.14) * env(d, 0.5, 0.6) * lvl
    def rainb(d, lvl=0.02): return hp(noise(d), 2200) * env(d, 0.5, 0.6) * lvl
    def hall(d, lvl=0.012): return bp(noise(d), 150, 900) * env(d, 0.4, 0.5) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: storm flight, cabin, strike, slow motion, the bolt, 1963, the laboratory, flying on
    place(bed, pad(["D2", "A2", "F3", "A3"], 8.6, 0.3, 0.6, 0.036), 0.0); place(bed, drone(8.5, 0.05), 0.0); place(bed, rainb(8.4, 0.02), 0.0)
    place(bed, pad(["C2", "G2", "E3", "G3"], 5.3, 0.4, 0.5, 0.036), 8.4); place(bed, drone(5.2, 0.036), 8.4); place(bed, rainb(5.1, 0.012), 8.4)
    place(bed, pad(["A1", "E2", "C3", "E3"], 2.6, 0.1, 0.4, 0.04), 13.5); place(bed, drone(2.5, 0.05), 13.5)
    place(bed, pad(["D2", "A2", "D3", "F3", "C4"], 6.0, 0.4, 0.6, 0.042), 15.8); place(bed, buzz(5.7, 0.03), 15.95); place(bed, shimmer(5.6, 0.014), 16.0)
    place(bed, pad(["F2", "C3", "A3", "E4"], 5.7, 0.3, 0.6, 0.038), 21.6); place(bed, drone(5.5, 0.045), 21.7); place(bed, rainb(5.4, 0.016), 21.7)
    place(bed, pad(["A1", "E2", "A2", "C3"], 9.1, 0.8, 1.6, 0.05), 27.1); place(bed, drone(6.6, 0.03), 27.2); place(bed, rainb(6.6, 0.014), 27.2)
    place(bed, pad(["G2", "D3", "B3", "E4"], 5.9, 0.5, 0.6, 0.036), 36.0); place(bed, hall(5.7, 0.016), 36.1)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 6.5, 0.4, 2.0, 0.04), 41.7); place(bed, drone(6.3, 0.045), 41.8); place(bed, shimmer(5.8, 0.016), 42.0)
    # effects
    place(fx, boom(70, 0.7, 0.2), 0.03); place(fx, crack(0.3), 0.75); place(fx, thunder(1.7, 0.42), 0.8); place(fx, whoosh(0.5, 0.07), 2.05)
    place(fx, ding(0.045), 4.3); place(fx, thunder(2.2, 0.16), 3.5, pan=-0.5); place(fx, thunder(2.0, 0.14), 5.3, pan=0.5); place(fx, thunder(1.4, 0.12), 7.0, pan=-0.3)
    place(fx, whoosh(0.5, 0.09), 8.3); place(fx, ding(0.04), 9.0); place(fx, thunder(1.6, 0.1), 9.4, pan=0.4); place(fx, thunder(1.3, 0.09), 10.7, pan=-0.4)
    place(fx, whoosh(0.5, 0.08), 11.15)
    for k in range(9): place(fx, zap(0.18, 0.03 + 0.006 * k), 11.6 + k * 0.21, pan=(-1) ** k * 0.4)
    place(fx, riser(1.7, 0.06), 11.9)
    place(fx, crack(0.42), 13.72); place(fx, thunder(2.3, 0.5), 13.76); place(fx, zap(0.4, 0.09), 13.74)
    place(fx, whoosh(0.5, 0.09), 15.8); place(fx, boom(46, 1.0, 0.3), 15.95)
    for k in range(12): place(fx, ting(900 + 110 * k, 0.3, 0.014), 16.3 + k * 0.4, pan=0.7 - k * 0.12)
    place(fx, zap(0.4, 0.07), 18.4, pan=-0.6); place(fx, riser(1.2, 0.04), 20.4)
    place(fx, crack(0.36), 21.7); place(fx, thunder(3.0, 0.42), 21.74); place(fx, ding(0.04), 23.1)
    place(fx, whoosh(0.5, 0.08), 24.65); place(fx, thud(0.16), 24.8); place(fx, thunder(1.8, 0.14), 24.85); place(fx, ding(0.045), 25.3)
    place(fx, whoosh(0.7, 0.07), 27.05); place(fx, boom(40, 1.6, 0.26), 27.2); place(fx, thunder(1.4, 0.07), 28.0, pan=-0.4); place(fx, thunder(1.4, 0.07), 29.6, pan=0.4)
    place(fx, crack(0.26), 30.9); place(fx, thunder(3.0, 0.34), 30.94); place(fx, boom(36, 2.6, 0.3), 34.0)
    place(fx, whoosh(0.6, 0.08), 35.95); place(fx, ding(0.045), 36.5)
    for k in range(8): place(fx, zap(0.2, 0.085), 38.2 + k * 0.42); place(fx, crack(0.1), 38.2 + k * 0.42)
    place(fx, ding(0.05), 38.9)
    place(fx, whoosh(0.6, 0.09), 41.65); place(fx, crack(0.3), 42.35); place(fx, thunder(2.4, 0.36), 42.39); place(fx, ding(0.05), 43.5); place(fx, riser(1.0, 0.035), 44.2); place(fx, thunder(1.2, 0.06), 44.2, pan=0.5)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/lightning.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

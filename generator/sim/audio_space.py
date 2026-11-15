"""Soundtrack + narration for the space-without-a-suit simulation. Writes work/space.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 50.4
LINES = [(0.4, "What if you stepped into space, without a suit?"), (3.0, "You're outside the space station. And your suit is gone."),
 (6.1, "You don't explode. And you don't freeze. A vacuum is an insulator."),
 (10.2, "First rule: breathe out. Hold your breath, and the expanding air tears your lungs."),
 (14.8, "The saliva on your tongue starts to boil. Not from heat. With no pressure, water boils at body temperature."),
 (21.2, "Your body swells, up to twice its size. But your skin holds."),
 (25.2, "After about ten seconds, you black out. The blood reaching your brain carries no oxygen."),
 (30.5, "But you're not dead. In nineteen sixty six, this happened to a NASA technician in a vacuum chamber. The air rushed back in, and he recovered."),
 (38.8, "Get back inside within about ninety seconds, and you would probably live."),
 (43.2, "Space doesn't crush you, or freeze you. It just takes the air away."), (47.6, "Follow for more.")]
CHUNKS = [[], ["You're outside<br>the space station.", "And your suit<br>is <em>gone</em>."],
 ["You don't <em>explode</em>.", "And you don't <em>freeze</em>.", "A vacuum is<br>an insulator."],
 ["First rule:<br><em>breathe out</em>.", "Hold your breath,", "and the expanding air<br>tears your lungs."],
 ["The saliva on your tongue<br>starts to <em>boil</em>.", "Not from heat.", "With no pressure,", "water boils at<br><em>body temperature</em>."],
 ["Your body swells,", "up to <em>twice</em> its size.", "But your skin holds."],
 ["After about <em>ten seconds</em>,<br>you black out.", "The blood reaching your brain<br>carries no oxygen."],
 ["But you're <em>not dead</em>.", "In 1966, this happened<br>to a NASA technician", "in a vacuum chamber.", "The air rushed back in,", "and he <em>recovered</em>."],
 ["Get back inside within<br>about <em>ninety seconds</em>,", "and you would<br>probably live."],
 ["Space doesn't crush you,<br>or freeze you.", "It just takes<br>the <em>air</em> away."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(16)
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
    def whoosh(d=0.7, lvl=0.09, up=True):
        m = int(d * SR); t = np.arange(m) / SR; x = noise(d); return bp(x, 500, 6000) * 0.6 * np.sin(np.pi * t / d) ** 2 * lvl
    def riser(d=2.0, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
    def tick(f=1100, lvl=0.12): t = np.arange(int(0.09 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + rng.normal(0, .25, len(t)) * np.exp(-t * 500)) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * lvl
    def shimmer(d, lvl=0.022):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(["C5", "E5", "G5", "B5", "D6"])) * env(d, 0.8, 1.0) * lvl
    def hiss(d, lvl=0.08, a=0.02, r=0.6): return hp(noise(d), 2500) * env(d, a, r, 1.5) * lvl
    def heart(d, bpm0, bpm1, lvl=0.3):
        out = np.zeros(int(d * SR)); t0 = 0.1
        while t0 < d - 0.5:
            for off, g in ((0, 1.0), (0.16, 0.7)):
                tt = np.arange(int(0.22 * SR)) / SR; b = np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 22) * g; i = int((t0 + off) * SR); out[i:i + len(b)] += b[: len(out) - i]
            t0 += 60 / (bpm0 + (bpm1 - bpm0) * t0 / d)
        return out * lvl
    def fizz(d, lvl=0.05):
        out = np.zeros(int(d * SR)); r = np.random.default_rng(4)
        for _ in range(int(d * 26)):
            i = r.integers(0, len(out) - 2000); tt = np.arange(900) / SR; out[i:i + 900] += np.sin(2 * np.pi * r.uniform(1800, 5200) * tt * (1 + 3 * tt)) * np.exp(-tt * 260) * r.uniform(0.3, 1)
        return out * lvl * env(d, 0.4, 0.5)
    def klaxon(d, lvl=0.05):
        t = np.arange(int(d * SR)) / SR; return np.sign(np.sin(2 * np.pi * 520 * t)) * (np.sin(2 * np.pi * 1.45 * t) > 0) * lp(np.ones(len(t)), 800) * lvl * env(d, 0.05, 0.1)
    def beep(f=880, d=0.12, lvl=0.05): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t) * env(d, 0.005, 0.03) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: the hush of orbit, a slowing heartbeat, the chamber, the rescue, and orbit again
    place(bed, pad(["D2", "A2", "D3", "F3"], 6.4, 1.2, 0.8, 0.04), 0.0); place(bed, shimmer(6.2, 0.016), 0.2); place(bed, rumble(6.2, 0.02) * env(6.2, 1, 1), 0.0)
    place(bed, pad(["C2", "G2", "E3"], 9.2, 0.8, 0.8, 0.036), 6.0); place(bed, heart(8.8, 96, 120, 0.22), 6.2)
    place(bed, pad(["B1", "F2", "D3"], 10.8, 0.8, 0.8, 0.04), 14.6); place(bed, heart(10.4, 120, 92, 0.24), 14.8); place(bed, fizz(6.0, 0.06), 15.2)
    place(bed, pad(["A1", "E2", "C3"], 6.9, 0.6, 1.5, 0.045), 25.1); place(bed, heart(6.4, 80, 44, 0.3) * env(6.4, 0.1, 2.5), 25.3)
    place(bed, rumble(7.0, 0.05) * env(7.0, 0.2, 0.6), 31.8); place(bed, pad(["E2", "B2", "G3"], 7.0, 0.3, 0.8, 0.03), 31.8)
    place(bed, pad(["F2", "C3", "A3", "E4"], 4.6, 0.3, 0.6, 0.04), 38.7); place(bed, heart(4.2, 50, 76, 0.22), 38.9)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 7.2, 0.5, 1.8, 0.036), 43.1); place(bed, shimmer(7.0, 0.016), 43.2)
    # effects
    place(fx, whoosh(0.6, 0.07), 2.75); place(fx, hiss(1.6, 0.12, 0.02, 1.4), 4.4); place(fx, boom(50, 1.2, 0.3), 4.45)
    place(fx, hiss(2.4, 0.09, 0.05, 2.0), 11.0); place(fx, whoosh(0.5, 0.06), 14.55); place(fx, whoosh(0.5, 0.05), 21.0)
    for k in range(10): place(fx, tick(1000, 0.035), 4.6 + k * 2.07)                # one tick per story second
    place(fx, riser(1.4, 0.06), 23.9); place(fx, boom(40, 2.6, 0.5), 26.6)
    place(fx, whoosh(0.6, 0.08), 31.65); place(fx, klaxon(3.7, 0.035), 32.4); place(fx, boom(70, 0.5, 0.3), 33.4)
    place(fx, hiss(2.6, 0.2, 0.15, 2.2), 36.2); place(fx, boom(60, 1.0, 0.25), 36.2); place(fx, beep(660, 0.14), 37.6); place(fx, beep(990, 0.2), 37.85)
    place(fx, whoosh(0.6, 0.08), 38.55); place(fx, riser(1.6, 0.05), 41.4); place(fx, boom(46, 1.6, 0.35), 43.2); place(fx, hiss(1.0, 0.1, 0.3, 0.3), 42.3)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/space.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

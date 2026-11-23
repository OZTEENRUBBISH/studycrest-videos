"""Soundtrack + narration for the Pompeii simulation. Writes work/pompeii.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 48.6
LINES = [(0.4, "Pompeii, hour by hour."),
 (2.0, "No lava ever reached Pompeii. And most of its people got out alive."),
 (6.5, "About one in the afternoon, Vesuvius explodes. A column of ash and pumice climbs about thirty kilometres, and spreads out like a pine tree."),
 (15.3, "The town goes dark. Pumice rains down for about eighteen hours. Roofs cave in under the weight. But thousands of people use that time to leave."),
 (24.0, "Then, the next morning, the column collapses. A cloud of gas and ash, as hot as three hundred degrees, pours down the mountain at over a hundred kilometres an hour."),
 (33.7, "It reaches Pompeii soon after seven. No one still in the town survives."),
 (38.5, "A teenager watched from across the bay, and later wrote it all down. That's how we know."),
 (43.6, "Lava never touched Pompeii. It was buried by a cloud."), (47.0, "Follow for more.")]
CHUNKS = [[], ["<em>No lava</em> ever<br>reached Pompeii.", "And most of its people<br>got out <em>alive</em>."],
 ["About <em>one in the afternoon</em>,", "Vesuvius <em>explodes</em>.", "A column of<br>ash and pumice", "climbs about<br><em>30 kilometres</em>,", "and spreads out<br>like a <em>pine tree</em>."],
 ["The town goes <em>dark</em>.", "Pumice rains down<br>for about <em>18 hours</em>.", "Roofs cave in<br>under the weight.", "But <em>thousands</em> of people", "use that time to <em>leave</em>."],
 ["Then, the next morning,", "the column <em>collapses</em>.", "A cloud of gas and ash,", "as hot as <em>300 degrees</em>,", "pours down the mountain", "at over <em>100 km/h</em>."],
 ["It reaches Pompeii<br>soon after <em>seven</em>.", "No one still in the town<br>survives."],
 ["A <em>teenager</em> watched<br>from across the bay,", "and later wrote<br>it all down.", "That's how we know."],
 ["<em>Lava</em> never<br>touched Pompeii.", "It was buried<br>by a <em>cloud</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(24)
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
    def room(d, lvl=0.012): return (lp(noise(d), 160, 2) * 2 + np.sin(2 * np.pi * 50 * np.arange(int(d * SR)) / SR) * 0.35) * env(d, 0.5, 0.5) * lvl
    def city(d, lvl=0.03): return (lp(noise(d), 300, 2) * 2.2 + bp(noise(d), 300, 1500) * 0.25) * env(d, 0.6, 1.2) * lvl
    def crowd(d, lvl=0.02): t = np.arange(int(d * SR)) / SR; return bp(noise(d), 250, 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t) ** 2) * env(d, 0.6, 0.6) * lvl
    def whir(d, lvl=0.04, f0=60, f1=220):
        t = np.arange(int(d * SR)) / SR; f = f0 + (f1 - f0) * np.minimum(1, t / d); return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 3) / SR)) * env(d, 0.2, 0.2) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * env(d, 0.1, 0.3) * lvl
    def wind(d, lvl=0.05, f0=300, f1=1800): t = np.arange(int(d * SR)) / SR; return bp(noise(d), f0, f1) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.31 * t + 1) ** 2) * env(d, 0.5, 0.5) * lvl
    def ting(f=3100, d=0.5, lvl=0.07): t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 11) * lvl
    def crack(lvl=0.2): d = 0.5; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 700, 6000) * np.exp(-t * 16) + lp(noise(d), 160) * np.exp(-t * 6) * 2) * lvl
    def twang(f=180, lvl=0.14): d = 0.9; t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f * (1 + 1.5 * np.exp(-t * 9))) / SR) + 0.5 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t * 6) * lvl + hp(noise(d), 3000) * np.exp(-t * 30) * lvl
    def screech(d, lvl=0.06): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 2200, 5200) * 0.8 + np.sin(2 * np.pi * np.cumsum(np.linspace(2600, 900, len(t))) / SR) * 0.5) * env(d, 0.03, d * 0.6) * lvl
    def fall(d, lvl=0.06): m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 300, 3000) * (t / d) ** 1.6 * env(d, 0.05, 0.05) * lvl + np.sin(2 * np.pi * np.cumsum(np.linspace(90, 240, m)) / SR) * (t / d) ** 2 * env(d, 0.05, 0.05) * lvl * 0.7
    def prop(d, lvl=0.05): m = int(d * SR); t = np.arange(m) / SR; return (np.sign(np.sin(2 * np.pi * 95 * t)) * 0.3 + np.sin(2 * np.pi * 47 * t) + lp(noise(d), 400) * 0.6) * (t / d) ** 2 * lvl
    def ding(lvl=0.05): return ting(1320, 0.9, lvl) + ting(1760, 0.9, lvl * 0.5)
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    place(bed, pad(["D2", "A2", "D3", "F3"], 6.6, 0.6, 0.6, 0.04), 0.0); place(bed, rumble(6.2, 0.05), 0.0); place(bed, wind(6.0, 0.035, 200, 1200), 0.1)
    place(bed, pad(["F2", "C3", "A3", "E4"], 2.8, 0.4, 0.4, 0.03), 6.2); place(bed, crowd(2.6, 0.035), 6.3); place(bed, shimmer(2.4, 0.012), 6.3)
    place(bed, pad(["C2", "G2", "Eb3", "G3"], 6.9, 0.2, 0.6, 0.046), 8.6); place(bed, rumble(6.6, 0.11), 8.7)
    place(bed, pad(["A1", "E2", "C3", "G3"], 9.0, 0.6, 0.6, 0.044), 15.1); place(bed, hp(noise(8.8), 2500) * env(8.8, 0.6, 0.6) * 0.016 * np.ones(1), 15.2); place(bed, rumble(8.6, 0.05), 15.2)
    place(bed, pad(["B1", "F#2", "D3", "A3"], 9.9, 0.5, 0.5, 0.046), 23.8); place(bed, rumble(9.6, 0.1), 24.0); place(bed, wind(9.4, 0.04, 150, 900), 24.0)
    place(bed, pad(["C2", "G2", "Eb3", "Bb3"], 5.0, 0.3, 1.2, 0.046), 33.5); place(bed, rumble(4.6, 0.16), 33.6)
    place(bed, pad(["G2", "D3", "B3", "E4"], 5.3, 0.6, 0.7, 0.034), 38.3); place(bed, wind(5.0, 0.03), 38.4); place(bed, shimmer(5.0, 0.012, ("C5", "E5", "A5", "B5", "E6")), 38.5)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 5.2, 0.5, 2.0, 0.04), 43.4); place(bed, wind(5.0, 0.035, 200, 1000), 43.5)
    place(fx, boom(60, 0.9, 0.25), 0.03); place(fx, whoosh(0.6, 0.08), 6.1); place(fx, riser(1.2, 0.05), 7.5)
    place(fx, boom(38, 2.6, 0.75), 8.7); place(fx, crack(0.35), 8.7); place(fx, boom(52, 1.6, 0.3), 9.5, pan=-0.3); place(fx, boom(44, 1.8, 0.3), 11.2, pan=0.3)
    place(fx, whoosh(0.6, 0.08), 15.0); 
    for k, ts in enumerate([16.9, 18.3, 19.4, 21.8]): place(fx, crack(0.14), ts, pan=(k - 1.5) * 0.3); place(fx, boom(70, 0.5, 0.14), ts + 0.03)
    place(fx, whoosh(0.5, 0.07), 20.4); place(fx, whoosh(0.6, 0.08), 23.7); place(fx, boom(36, 2.8, 0.6), 26.3); place(fx, riser(3.0, 0.06), 30.4)
    place(fx, whoosh(0.5, 0.09), 33.5); place(fx, riser(2.6, 0.08), 34.2); place(fx, boom(40, 2.2, 0.6), 36.8)
    place(fx, whoosh(0.7, 0.08), 38.2); place(fx, ting(1760, 0.8, 0.03), 38.5); place(fx, whoosh(0.6, 0.08), 43.3); place(fx, boom(60, 0.8, 0.18), 43.5); place(fx, riser(1.2, 0.04), 45.6)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/pompeii.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

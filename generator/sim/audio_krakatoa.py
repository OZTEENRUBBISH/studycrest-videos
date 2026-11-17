"""Soundtrack + narration for the Krakatoa simulation. Writes work/krakatoa.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 54.8
LINES = [(0.4, "Krakatoa, hour by hour."),
 (2.3, "In eighteen eighty three, one island made a sound heard nearly five thousand kilometres away."),
 (8.1, "August twenty sixth, one p.m. You're on a ship in the Sunda Strait. The volcano erupts. Within an hour, ash towers twenty seven kilometres high."),
 (17.6, "All night it goes on. Then, next morning, four colossal explosions."),
 (22.1, "The third, at two minutes past ten, is the loudest sound ever measured."),
 (26.1, "People hear it in Perth, and on Rodrigues island, four thousand eight hundred kilometres away. The sound needs about four hours to get there."),
 (34.6, "The pressure wave circles the planet three and a half times."),
 (38.0, "Waves over thirty metres high strike the nearby coasts. More than thirty six thousand people die."),
 (44.5, "Two thirds of the island is gone. For months, sunsets turn red around the world."),
 (49.5, "One island shook the air of a whole planet."),
 (52.3, "Follow for more.")]
CHUNKS = [[], ["In <em>1883</em>, one island", "made a sound heard", "nearly <em>5,000 kilometres</em> away."],
 ["August 26th, 1 p.m.", "You're on a ship<br>in the Sunda Strait.", "The volcano <em>erupts</em>.", "Within an hour,", "ash towers<br><em>27 kilometres</em> high."],
 ["All night it goes on.", "Then, next morning,", "four <em>colossal</em> explosions."],
 ["The third,<br>at two minutes past ten,", "is the <em>loudest sound</em><br>ever measured."],
 ["People hear it in <em>Perth</em>,", "and on <em>Rodrigues</em> island,", "4,800 kilometres away.", "The sound needs about<br><em>four hours</em> to get there."],
 ["The pressure wave<br>circles the planet", "<em>three and a half</em> times."],
 ["Waves over <em>30 metres</em> high", "strike the nearby coasts.", "More than <em>36,000</em><br>people die."],
 ["Two thirds of the island<br>is <em>gone</em>.", "For months, sunsets turn <em>red</em>", "around the world."],
 ["One island shook the air", "of a <em>whole planet</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(29)
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
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    def thunder(d=2.6, lvl=0.3): t = np.arange(int(d * SR)) / SR; return (lp(noise(d), 120, 3) * 4 * np.exp(-t * 1.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t) ** 2) + bp(noise(d), 200, 1800) * np.exp(-t * 9) * 0.6) * lvl
    def horn(d=1.1, lvl=0.03): t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * 174 * t) + 0.5 * np.sin(2 * np.pi * 261 * t) + 0.2 * np.sin(2 * np.pi * 348 * t)) * env(d, 0.08, 0.3) * lvl
    # beds: calm strait, eruption, night, morning, the blast, the globe, the coast, the aftermath
    place(bed, surf(12.2, 0.045), 0.0); place(bed, gulls(7.0, 0.016, 4), 1.0, pan=0.3); place(bed, pad(["A2", "E3", "A3", "C4"], 12.0, 1.2, 0.6, 0.03), 0.0); place(bed, horn(), 9.9, pan=-0.3)
    place(bed, rumble(10.2, 0.1) * env(10.2, 0.3, 1.0), 12.0); place(bed, pad(["D2", "A2", "F3"], 5.8, 0.3, 0.6, 0.042), 12.0)
    place(bed, pad(["C2", "G2", "C3", "D3"], 4.6, 0.4, 0.5, 0.044), 17.5); place(bed, pad(["B1", "F2", "B2"], 4.2, 0.2, 0.4, 0.046), 22.0); place(bed, rumble(4.0, 0.12) * env(4.0, 0.05, 2.0), 22.3)
    place(bed, pad(["E2", "B2", "E3", "G3"], 8.8, 0.5, 0.6, 0.036), 26.0); place(bed, shimmer(8.2, 0.012), 26.2); place(bed, pad(["F2", "C3", "A3"], 3.6, 0.3, 0.4, 0.04), 34.5)
    place(bed, surf(6.6, 0.06, 3.1), 37.9); place(bed, pad(["A1", "E2", "A2", "C3"], 6.6, 0.5, 0.8, 0.046), 37.9); place(bed, rumble(4.0, 0.06) * env(4.0, 1.5, 0.3), 38.2)
    place(bed, surf(10.4, 0.04), 44.4); place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 10.4, 0.6, 2.0, 0.036), 44.4); place(bed, shimmer(5.0, 0.012, ("D5", "F5", "A5", "C6")), 46.9)
    # effects
    for ts in [2.2, 13.4, 17.5, 19.6, 26.0, 34.5, 37.9, 44.4, 46.9]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
    place(fx, riser(1.0, 0.06), 11.0); place(fx, boom(40, 3.2, 0.7), 12.0); place(fx, thunder(3.0, 0.3), 12.1); place(fx, boom(46, 2.0, 0.35), 14.6)
    place(fx, thunder(2.2, 0.2), 18.0, pan=-0.3); place(fx, thunder(2.0, 0.16), 19.0, pan=0.4)
    place(fx, boom(44, 1.6, 0.5), 19.9); place(fx, thunder(1.6, 0.2), 19.95); place(fx, boom(42, 1.6, 0.55), 20.8); place(fx, thunder(1.6, 0.22), 20.85)
    place(fx, riser(1.3, 0.1), 21.0); place(fx, boom(32, 4.2, 0.95), 22.3); place(fx, boom(80, 0.6, 0.5), 22.32); place(fx, thunder(3.6, 0.4), 22.35)
    for k in range(6): place(fx, tick(1000, 0.04), 26.6 + k * 0.9)
    place(fx, bell(880, 1.6, 0.02), 29.3, pan=0.4); place(fx, bell(660, 1.8, 0.022), 31.0, pan=-0.4)
    for k in range(7): place(fx, whoosh(0.4, 0.045), 34.7 + k * 0.44)
    place(fx, riser(2.6, 0.06), 38.4); place(fx, boom(40, 2.4, 0.3), 41.0); place(fx, riser(1.2, 0.04), 50.4)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/krakatoa.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

"""Soundtrack + narration for the Hindenburg simulation. Writes work/hindenburg.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 55.4
LINES = [(0.4, "Hindenburg, second by second."),
 (2.5, "Lakehurst, New Jersey. The sixth of May, nineteen thirty seven. After a day of thunderstorms, an airship two hundred and forty five metres long comes in to land."),
 (12.4, "Sixteen cells of hydrogen hold it up."), (14.9, "Seven twenty one p.m. The landing ropes drop."), (18.2, "Seven twenty five. A flame appears near the tail."),
 (21.2, "Hydrogen burns fast, and it burns upward. The tail sinks. The nose rears into the sky. Fire runs the length of the ship."),
 (29.4, "About thirty four seconds after the first flame, it is on the ground."),
 (33.6, "Ninety seven people were on board. Thirty five of them died, and one man on the ground. Sixty two survived."),
 (40.4, "The flames rose away from them, and many jumped clear as the ship came down."),
 (44.9, "The likely cause: leaking hydrogen, lit by a spark of static electricity."),
 (49.6, "It ended the age of the passenger airship."), (52.7, "Follow for more.")]
CHUNKS = [[], ["Lakehurst, New Jersey.", "The sixth of May, 1937.", "After a day of<br>thunderstorms,", "an airship<br><em>245 metres</em> long", "comes in to land."],
 ["Sixteen cells of <em>hydrogen</em><br>hold it up."], ["7:21 p.m.", "The landing ropes drop."], ["7:25.", "A <em>flame</em> appears<br>near the tail."],
 ["Hydrogen burns fast,", "and it burns <em>upward</em>.", "The tail sinks.", "The nose rears<br>into the sky.", "Fire runs the length<br>of the ship."],
 ["About <em>thirty four seconds</em><br>after the first flame,", "it is on the ground."],
 ["Ninety seven people<br>were on board.", "Thirty five of them died,", "and one man<br>on the ground.", "<em>Sixty two survived.</em>"],
 ["The flames rose<br><em>away</em> from them,", "and many jumped clear<br>as the ship came down."],
 ["The likely cause:", "leaking hydrogen,", "lit by a spark of<br><em>static electricity</em>."],
 ["It ended the age of<br>the passenger airship."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(37)
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
    def wind(d, lvl=0.07):
        t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 180, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 3.7 + 1) ** 2) + bp(noise(d), 900, 2400) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 2.3)); return x * lvl * env(d, 0.8, 0.8)
    def drone(d, lvl=0.05):
        t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * f * t * (1 + 0.003 * np.sin(2 * np.pi * 0.4 * t + k))) / (k + 1) for k, f in enumerate([55, 82.5, 110, 165, 220])); return x * (0.8 + 0.2 * np.sin(2 * np.pi * 9 * t)) * lvl * env(d, 1.0, 1.0)
    def thunder(d=3.5, lvl=0.22):
        t = np.arange(int(d * SR)) / SR; return lp(noise(d), 110, 3) * 3 * np.exp(-t * 0.9) * (0.6 + 0.4 * np.sin(2 * np.pi * 2.1 * t) ** 2) * lvl
    def fire(d, lvl=0.2, a=0.5, r=1.0):
        t = np.arange(int(d * SR)) / SR; x = lp(noise(d), 500, 2) * 2.2 + bp(noise(d), 500, 3000) * 0.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 5.3 * t) * np.sin(2 * np.pi * 1.7 * t)); cr = (rng.random(len(t)) > 0.9993) * rng.normal(0, 6, len(t)); return (x + hp(lp(cr, 6000), 1200) * 1.3) * lvl * env(d, a, r)
    def groan(d=2.2, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; f = 95 + 40 * np.sin(2 * np.pi * 0.5 * t) - 18 * t; return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR)) * env(d, 0.3, 0.8) * lvl
    def zap(lvl=0.12):
        d = 0.35; t = np.arange(int(d * SR)) / SR; return hp(noise(d), 3000) * (np.sin(2 * np.pi * 60 * t) > 0.2) * np.exp(-t * 7) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: evening field with engines overhead, then the fire, then the quiet after
    place(bed, wind(18.6, 0.045), 0.0); place(bed, drone(18.4, 0.05), 0.0); place(bed, pad(["D2", "A2", "F3"], 18.4, 1.5, 1.0, 0.03), 0.0)
    place(bed, fire(15.6, 0.07, 0.4, 2.5), 18.3); place(bed, fire(8.6, 0.17, 2.2, 1.6), 21.0); place(bed, pad(["C2", "G2", "Eb3"], 15.4, 0.6, 1.5, 0.045), 18.2); place(bed, rumble(11.6, 0.06) * env(11.6, 1.5, 2), 21.0)
    place(bed, pad(["A1", "E2", "C3", "E3"], 7.2, 0.8, 1.0, 0.04), 33.4); place(bed, wind(7.0, 0.03), 33.5)
    place(bed, fire(4.6, 0.1, 0.3, 0.6), 40.3); place(bed, pad(["F2", "C3", "Ab3"], 4.7, 0.4, 0.6, 0.035), 40.3)
    place(bed, wind(4.8, 0.04), 44.8); place(bed, drone(4.8, 0.035), 44.8); place(bed, pad(["E2", "B2", "G3"], 4.8, 0.4, 0.6, 0.035), 44.8)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3"], 5.8, 0.5, 1.8, 0.04), 49.5); place(bed, wind(5.6, 0.035), 49.6); place(bed, fire(5.6, 0.035, 0.5, 2.0), 49.6)
    # effects
    place(fx, thunder(3.6, 0.16), 5.6, pan=-0.4); place(fx, thunder(3.0, 0.1), 10.0, pan=0.5)
    for ts in [12.2, 14.7, 33.4, 40.2, 44.7, 49.4]: place(fx, whoosh(0.55, 0.07), ts - 0.05)
    place(fx, whoosh(0.9, 0.05), 16.0); place(fx, boom(70, 0.4, 0.12), 17.0); place(fx, boom(72, 0.4, 0.1), 17.25)        # ropes hit the ground
    place(fx, riser(1.0, 0.04), 18.9); place(fx, boom(58, 1.6, 0.4), 19.9); place(fx, whoosh(1.2, 0.1), 19.9)
    place(fx, boom(44, 2.8, 0.6), 21.3); place(fx, boom(40, 2.4, 0.5), 23.6); place(fx, groan(2.2, 0.06), 24.2); place(fx, boom(38, 2.6, 0.5), 26.0); place(fx, groan(2.4, 0.06), 26.8)
    place(fx, boom(34, 3.2, 0.7), 29.2); place(fx, rumble(2.6, 0.12) * env(2.6, 0.05, 2.0), 29.3)
    place(fx, zap(0.14), 47.2); place(fx, zap(0.1), 47.6); place(fx, zap(0.12), 48.3)
    place(fx, riser(1.2, 0.04), 51.2)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/hindenburg.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)

"""Soundtrack + narration for the Moon-at-space-station-height simulation. Writes work/moonclose.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 46.6
LINES = [(0.4, "What if the Moon orbited as close as the space station?"),
 (3.5, "You'd never enjoy the view. It couldn't stay a moon."),
 (6.4, "You're on the beach. The Moon is four hundred kilometres up, and it covers over half the sky."),
 (11.8, "It laps the Earth in about two hours. Beneath it, you'd weigh a tenth less, and the sea heaves up to meet it."),
 (18.0, "But the Moon has it worse. Earth pulls its near side much harder than its far side. This close, that stretch beats the Moon's own gravity."),
 (26.3, "It comes apart, and spreads into a ring. Some of it falls on us."),
 (30.5, "That line is the Roche limit. Saturn's rings lie inside Saturn's."),
 (35.2, "The real Moon is safe: it's drifting away, about four centimetres a year."),
 (39.7, "Get too close to a planet, and you're not a moon. You're a ring."), (43.3, "Follow for more.")]
CHUNKS = [[], ["You'd never<br>enjoy the view.", "It <em>couldn't stay</em><br>a moon."],
 ["You're on the beach.", "The Moon is<br><em>400 kilometres</em> up,", "and it covers<br><em>over half the sky</em>."],
 ["It laps the Earth", "in about <em>two hours</em>.", "Beneath it, you'd weigh<br><em>a tenth less</em>,", "and the sea heaves up", "to meet it."],
 ["But the Moon<br>has it <em>worse</em>.", "Earth pulls its near side", "<em>much harder</em><br>than its far side.", "This close, that stretch", "beats the Moon's<br><em>own gravity</em>."],
 ["It comes <em>apart</em>,", "and spreads<br>into a <em>ring</em>.", "Some of it falls on us."],
 ["That line is<br>the <em>Roche limit</em>.", "Saturn's rings", "lie inside Saturn's."],
 ["The real Moon is <em>safe</em>:", "it's drifting away,", "about <em>four centimetres</em><br>a year."],
 ["Get too close<br>to a planet,", "and you're not a moon.", "You're a <em>ring</em>."], []]
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
    # beds: beach night, space, beach, lap, beach tide, the pull, break-up, Roche, the real Moon, the ring
    place(bed, pad(["D2", "A2", "F3", "A3"], 3.5, 0.3, 0.5, 0.04), 0.0); place(bed, waves(3.4, 0.05), 0.0)
    place(bed, pad(["C2", "G2", "E3", "B3"], 3.1, 0.3, 0.5, 0.04), 3.2); place(bed, deep(3.0, 0.035), 3.3)
    place(bed, pad(["D2", "A2", "F3", "C4"], 5.6, 0.4, 0.6, 0.038), 6.1); place(bed, waves(5.5, 0.05), 6.1); place(bed, shimmer(5.0, 0.012), 6.5)
    place(bed, pad(["E2", "B2", "G3", "D4"], 2.9, 0.2, 0.4, 0.04), 11.5); place(bed, deep(2.8, 0.035), 11.5)
    place(bed, pad(["F2", "C3", "A3", "E4"], 3.7, 0.3, 0.5, 0.038), 14.2); place(bed, waves(3.6, 0.075), 14.2)
    place(bed, pad(["A1", "E2", "C3", "E3"], 8.5, 0.5, 0.8, 0.045), 17.7); place(bed, deep(8.3, 0.045), 17.8)
    place(bed, pad(["G1", "D2", "B2", "D3"], 4.4, 0.2, 0.6, 0.05), 26.0); place(bed, deep(4.3, 0.06, 140), 26.0)
    place(bed, pad(["C2", "G2", "E3", "G3", "D4"], 4.9, 0.4, 0.6, 0.04), 30.2); place(bed, shimmer(4.6, 0.016), 30.3)
    place(bed, pad(["F2", "C3", "A3", "E4"], 4.7, 0.4, 0.6, 0.038), 34.9); place(bed, shimmer(4.4, 0.014), 35.0)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 7.2, 0.4, 2.0, 0.042), 39.4); place(bed, waves(7.0, 0.045), 39.4); place(bed, shimmer(6.0, 0.016), 39.6)
    # effects
    place(fx, boom(60, 1.4, 0.3), 0.05); place(fx, riser(1.2, 0.04), 2.0); place(fx, gull(0.02), 1.4, pan=-0.5)
    place(fx, whoosh(0.5, 0.09), 3.15); place(fx, boom(46, 1.2, 0.26), 3.3); place(fx, ding(0.045), 5.0)
    place(fx, whoosh(0.5, 0.08), 6.05); place(fx, ding(0.04), 8.9); place(fx, boom(40, 1.6, 0.2), 9.6)
    place(fx, whoosh(0.6, 0.09), 11.45); place(fx, riser(2.4, 0.045), 11.7)
    for k in range(9): place(fx, ting(1500 + 90 * k, 0.25, 0.012), 11.9 + k * 0.27, pan=np.sin(k) * 0.6)
    place(fx, whoosh(0.5, 0.08), 14.15); place(fx, ding(0.045), 15.4); place(fx, splash(0.1), 16.3); place(fx, splash(0.07), 17.1, pan=0.4)
    place(fx, whoosh(0.5, 0.09), 17.65); place(fx, boom(44, 1.3, 0.26), 17.8); place(fx, ding(0.04), 20.2); place(fx, ding(0.04), 21.6)
    place(fx, creak(0.09, 1.4), 22.7); place(fx, creak(0.1, 1.3), 24.0, pan=-0.3); place(fx, riser(1.8, 0.06), 24.3); place(fx, creak(0.12, 1.0), 25.2, pan=0.3)
    place(fx, crack(0.34), 26.08); place(fx, thunder(3.0, 0.45), 26.1); place(fx, boom(38, 2.6, 0.4), 26.12)
    for k in range(14): place(fx, thud(0.07 + 0.01 * (k % 3)), 26.5 + k * 0.24, pan=np.sin(k * 1.7) * 0.7)
    for k in range(6): place(fx, boom(52, 0.8, 0.13), 28.9 + k * 0.3, pan=np.cos(k * 2.1) * 0.6)
    place(fx, whoosh(0.5, 0.08), 30.15); place(fx, ding(0.05), 31.0); place(fx, ding(0.04), 33.0)
    place(fx, whoosh(0.6, 0.08), 34.85); place(fx, ding(0.045), 37.4)
    place(fx, whoosh(0.6, 0.09), 39.35); place(fx, boom(44, 1.6, 0.24), 39.5); place(fx, ding(0.05), 42.0); place(fx, riser(1.0, 0.03), 42.2)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/moonclose.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)


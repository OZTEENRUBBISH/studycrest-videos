"""Soundtrack + narration for the gravity simulation. Writes work/gravity.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vo import speak, SR, BASE
from soundlib import place, N
DUR = 53.6; n = int(DUR * SR); rng = np.random.default_rng(11)
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
def noise(d): return rng.normal(0, 1, int(d * SR))
def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
    t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
    return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
def surf(d, lvl=0.05):
    t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 250, 2600); sw = 0.55 + 0.45 * np.sin(2 * np.pi * t / 5.3 - 1) ** 2; return x * sw * lvl * env(d, 0.6, 0.6)
def boom(f=46, d=1.8, lvl=0.5):
    t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
def whoosh(d=0.7, lvl=0.09, up=True):
    m = int(d * SR); t = np.arange(m) / SR; x = noise(d); f = np.linspace(400, 5000, m) if up else np.linspace(5000, 400, m); ph = np.cumsum(f) / SR
    return (bp(x, 500, 6000) * 0.6 + np.sin(2 * np.pi * ph) * 0.05) * np.sin(np.pi * t / d) ** 2 * lvl
def riser(d=2.0, lvl=0.07):
    m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
def tick(f=1100, lvl=0.12): t = np.arange(int(0.09 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + rng.normal(0, .25, len(t)) * np.exp(-t * 500)) * lvl
def rumble(d, lvl=0.3):
    t = np.arange(int(d * SR)) / SR; x = lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5; return x * lvl
def crack(lvl=0.2):
    d = 0.5; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 700, 6000) * np.exp(-t * 16) + lp(noise(d), 160) * np.exp(-t * 6) * 2) * lvl
def shimmer(d, lvl=0.022):
    t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(["C5", "E5", "G5", "B5", "D6"])) * env(d, 0.8, 1.0) * lvl
def tape(d=1.5, lvl=0.07):
    m = int(d * SR); t = np.arange(m) / SR; f = 2200 * np.exp(-t * 1.2) + 300 + 250 * np.sin(2 * np.pi * 9 * t); return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + bp(noise(d), 800, 5000)) * env(d, 0.05, 0.2) * lvl * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 14 * t)))
LINES = [(0.4, "What if gravity switched off, for five seconds?"), (3.2, "You're at the beach. In three seconds, gravity switches off. Everywhere."), (7.4, "You'd expect this. Everything floating away."), (11.1, "But that's not what happens."),
 (12.9, "Gravity was squeezing the whole planet. At the centre, the pressure is over three and a half million atmospheres."), (19.1, "Switch gravity off, and the Earth springs outward, like a released spring. Rock, ocean and air, all together."),
 (25.8, "The ground pushes up on your feet exactly as hard as before. So you feel, nothing."), (30.8, "But after five seconds, the ground beneath you is rising at a hundred and seventy six kilometres an hour."),
 (37.0, "Then gravity returns. And the whole planet is still moving."), (40.4, "The ground heaves kilometres upward, then snaps back. The crust cracks on every continent at once. And the oceans follow."),
 (47.9, "Gravity doesn't just hold you down. It holds the Earth together."), (51.7, "Follow for more.")]
bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
# beds
place(bed, surf(7.2), 0.0); place(bed, surf(11.4, 0.035), 25.5); place(bed, pad(["A2", "E3", "A3"], 7.4, 1.5, 0.8, 0.03), 0.0)
place(bed, shimmer(4.2), 7.0); place(bed, pad(["F2", "C3", "A3"], 4.4, 0.4, 0.6, 0.02), 7.0)
place(bed, pad(["D2", "A2", "F3"], 13.2, 1.0, 1.0, 0.04), 12.6); place(bed, rumble(13.0, 0.045) * env(13.0, 2, 1), 12.6)
place(bed, pad(["E2", "B2", "E3", "G3"], 11.6, 1.0, 0.4, 0.034), 25.4)
place(bed, pad(["D2", "A2", "D3", "F3"], 3.8, 0.2, 0.5, 0.045), 36.8)
q = rumble(7.6, 0.2); q *= np.minimum(1, np.arange(len(q)) / SR / 1.5) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.9 * np.arange(len(q)) / SR)); place(bed, q * env(7.6, 0.05, 0.25), 40.2)
roar = bp(noise(6.0), 150, 2600) * (np.arange(int(6.0 * SR)) / SR / 6.0) ** 2 * 0.22; place(bed, roar * env(6.0, 0.05, 0.12), 41.6, pan=-0.3)
place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], 6.0, 0.5, 1.6, 0.034), 47.6)
# effects
for k, ts in enumerate([4.0, 5.0, 6.0]): place(fx, tick(1000 + k * 120), ts)
place(fx, riser(1.8), 5.2); place(fx, boom(), 7.0); place(fx, whoosh(0.9), 7.05); place(fx, tape(1.5), 11.0); place(fx, boom(60, 0.9, 0.25), 12.6)
for ts in [12.8, 22.6, 25.6, 30.6, 47.6]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
place(fx, boom(52, 1.4, 0.3), 19.9); place(fx, whoosh(1.2, 0.08), 19.9)
for k in range(1, 5): place(fx, tick(820, 0.07), 12.6 + k * 4.84)      # one soft tick per slowed second
place(fx, riser(2.4, 0.09), 34.4); place(fx, boom(40, 2.6, 0.6), 36.8); place(fx, boom(44, 2.0, 0.5), 40.2)
for ts in [40.5, 41.1, 41.9, 42.6, 43.4, 44.0, 44.9, 45.7, 46.5]: place(fx, crack(0.16 + rng.uniform(0, 0.1)), ts, pan=rng.uniform(-0.6, 0.6))
rep = []
for k, (ts, txt) in enumerate(LINES):
    v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
    rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
with wave.open(BASE + "/work/gravity.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
